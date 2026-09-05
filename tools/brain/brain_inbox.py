#!/usr/bin/env python3
"""
brain_inbox.py: Asynchronous Linear intake bridge for cognitive brain repositories.

Enables asynchronous ticket triage, deep research execution (researchfu/reportfu),
and persistent discussion queuing directly from Linear.

Usage:
  brain inbox status
  brain inbox list [--team <key>]
  brain inbox next [--team <key>]
  brain inbox handle <issue-id>
  brain inbox close <issue-id> --summary "<text>" [--trigger "<text>"] [--report "<path>"]
  brain inbox comment <issue-id> "<comment-body>"
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brain_repo import get_brain_root

REPO_ROOT = get_brain_root()
LINEAR_GRAPHQL_URL = "https://api.linear.app/graphql"


def get_linear_api_key() -> str | None:
    """Resolve LINEAR_API_KEY from environment or mcp_config.json."""
    if key := os.environ.get("LINEAR_API_KEY"):
        return key.strip()

    # Fallback: check ~/.gemini/config/mcp_config.json
    mcp_config_path = Path.home() / ".gemini" / "config" / "mcp_config.json"
    if mcp_config_path.exists():
        try:
            with open(mcp_config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # check mcpServers.linear.env.LINEAR_API_KEY
                servers = data.get("mcpServers", {})
                for server_name in ["linear", "linear-mcp", "linear-server"]:
                    if server_name in servers:
                        env = servers[server_name].get("env", {})
                        if k := env.get("LINEAR_API_KEY"):
                            return k.strip()
        except Exception:
            pass

    # Fallback: check ~/.config/linear/api_key
    linear_cfg = Path.home() / ".config" / "linear" / "api_key"
    if linear_cfg.exists():
        try:
            return linear_cfg.read_text(encoding="utf-8").strip()
        except Exception:
            pass

    return None


def execute_graphql(query: str, variables: dict | None = None) -> dict:
    """Execute a GraphQL query or mutation against Linear API."""
    api_key = get_linear_api_key()
    if not api_key:
        print("ERROR: LINEAR_API_KEY not found.", file=sys.stderr)
        print("Set LINEAR_API_KEY in your environment, or configure it in ~/.gemini/config/mcp_config.json", file=sys.stderr)
        print("Generate a Personal API Key at: https://linear.app/settings/api", file=sys.stderr)
        sys.exit(1)

    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request(
        LINEAR_GRAPHQL_URL,
        data=payload,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
            "User-Agent": "Brain-Inbox-Agent/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "errors" in data:
                print(f"GraphQL Errors: {json.dumps(data['errors'], indent=2)}", file=sys.stderr)
                sys.exit(1)
            return data.get("data", {})
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"HTTP Error {e.code}: {err_msg}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Network error communicating with Linear: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_status(args: argparse.Namespace) -> None:
    """Verify Linear API connectivity and report viewer + teams."""
    query = """
    query GetViewerAndTeams {
      viewer {
        id
        name
        email
      }
      teams {
        nodes {
          id
          name
          key
          states {
            nodes {
              id
              name
              type
            }
          }
          labels {
            nodes {
              id
              name
            }
          }
        }
      }
    }
    """
    data = execute_graphql(query)
    viewer = data.get("viewer", {})
    teams = data.get("teams", {}).get("nodes", [])

    print(f"Connected to Linear as: {viewer.get('name')} ({viewer.get('email')})")
    print("\nTeams available:")
    for t in teams:
        print(f"  [{t.get('key')}] {t.get('name')} (ID: {t.get('id')})")
        states = [f"{s.get('name')} ({s.get('type')})" for s in t.get("states", {}).get("nodes", [])]
        labels = [l.get("name") for l in t.get("labels", {}).get("nodes", [])]
        print(f"    States: {', '.join(states[:6])}...")
        print(f"    Labels: {', '.join(labels[:8])}...")


def fetch_open_issues(team_key: str | None = None) -> list[dict]:
    """Fetch unhandled issues in triage or backlog states."""
    filter_clause = 'state: { type: { in: ["triage", "backlog", "unstarted"] } }'
    if team_key:
        filter_clause += f', team: {{ key: {{ eq: "{team_key}" }} }}'

    query = f"""
    query GetInboxIssues {{
      issues(
        filter: {{ {filter_clause} }}
        first: 30
        orderBy: createdAt
      ) {{
        nodes {{
          id
          identifier
          title
          description
          url
          createdAt
          dueDate
          priority
          state {{
            id
            name
            type
          }}
          team {{
            id
            name
            key
          }}
          labels {{
            nodes {{
              id
              name
            }}
          }}
        }}
      }}
    }}
    """
    data = execute_graphql(query)
    return data.get("issues", {}).get("nodes", [])


def cmd_list(args: argparse.Namespace) -> None:
    """List open issues in the inbox."""
    issues = fetch_open_issues(args.team)
    if not issues:
        print("Inbox is empty! Zero open tickets in triage or backlog.")
        return

    print(f"Found {len(issues)} open ticket(s) in inbox:\n")
    for issue in issues:
        labels = [l.get("name") for l in issue.get("labels", {}).get("nodes", [])]
        label_str = f" [{', '.join(labels)}]" if labels else ""
        print(f"* {issue.get('identifier')}: {issue.get('title')}{label_str}")
        print(f"  State: {issue.get('state', {}).get('name')} | URL: {issue.get('url')}")
        if issue.get("dueDate"):
            print(f"  Due / Trigger Date: {issue.get('dueDate')}")
        print()


def classify_intent(issue: dict) -> tuple[str, str]:
    """Infer intent: 'future-convo', 'deep-research', 'capture', or 'unclear'."""
    labels = [l.get("name", "").lower() for l in issue.get("labels", {}).get("nodes", [])]
    title = issue.get("title", "").lower()
    desc = (issue.get("description") or "").lower()
    combined = f"{title} {desc}"

    if "future-convo" in labels or "convo" in labels or "discussion" in labels:
        return "future-convo", "Explicit 'future-convo' label"
    if "deep-research" in labels or "research" in labels or "report" in labels:
        return "deep-research", "Explicit 'deep-research' label"
    if "capture" in labels or "concept" in labels or "seed" in labels:
        return "capture", "Explicit 'capture' label"

    if any(k in combined for k in ["discuss", "talk about", "future conversation", "chat about"]):
        return "future-convo", "Inferred from discussion intent in title/description"
    if any(k in combined for k in ["research", "investigate", "audit", "report on", "compare"]):
        return "deep-research", "Inferred from research/investigation intent"
    if "http" in combined or "link" in combined:
        return "capture", "Inferred web link capture"

    return "unclear", "No matching labels or intent keywords found"


def cmd_next(args: argparse.Namespace) -> None:
    """Pull the next unhandled ticket from the inbox."""
    issues = fetch_open_issues(args.team)
    if not issues:
        print(json.dumps({"status": "empty", "message": "No open inbox tickets found."}))
        return

    next_issue = issues[0]
    intent, reason = classify_intent(next_issue)
    labels = [l.get("name") for l in next_issue.get("labels", {}).get("nodes", [])]

    result = {
        "status": "ticket_available",
        "id": next_issue.get("id"),
        "identifier": next_issue.get("identifier"),
        "title": next_issue.get("title"),
        "description": next_issue.get("description"),
        "url": next_issue.get("url"),
        "createdAt": next_issue.get("createdAt"),
        "dueDate": next_issue.get("dueDate"),
        "labels": labels,
        "team": next_issue.get("team", {}).get("key"),
        "state": next_issue.get("state", {}).get("name"),
        "classifiedIntent": intent,
        "intentReason": reason,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Next Ticket: {result['identifier']} — {result['title']}")
        print(f"URL: {result['url']}")
        print(f"Labels: {', '.join(labels) if labels else 'none'}")
        print(f"Classified Intent: {intent} ({reason})")
        if result["dueDate"]:
            print(f"Due / Trigger Date: {result['dueDate']}")
        print(f"\nDescription:\n{result['description'] or '(empty)'}")
        print(f"\nTo process this ticket, run:")
        print(f"  python3 agent/tools/brain-inbox.py handle {result['identifier']}")


def fetch_issue_by_identifier(identifier: str) -> dict | None:
    """Fetch full issue details by Linear identifier (e.g. BRN-42)."""
    query = """
    query GetIssueByIdentifier($id: String!) {
      issue(id: $id) {
        id
        identifier
        title
        description
        url
        dueDate
        team {
          id
          key
          states {
            nodes {
              id
              name
              type
            }
          }
        }
        state {
          id
          name
          type
        }
        labels {
          nodes {
            id
            name
          }
        }
        comments {
          nodes {
            id
            body
            createdAt
            user {
              name
            }
          }
        }
      }
    }
    """
    data = execute_graphql(query, {"id": identifier})
    return data.get("issue")



def close_issue_in_linear(issue_id: str, team_id: str, comment_body: str) -> bool:
    """Transition issue to 'Done'/'Completed' and post resolution comment."""
    # 1. Find 'completed' state for this team
    query = """
    query GetTeamStates($teamId: String!) {
      team(id: $teamId) {
        states {
          nodes {
            id
            name
            type
          }
        }
      }
    }
    """
    team_data = execute_graphql(query, {"teamId": team_id})
    states = team_data.get("team", {}).get("states", {}).get("nodes", [])
    done_state = next((s for s in states if s.get("type") == "completed"), None)

    if not done_state:
        # fallback to state with name matching Done/Closed
        done_state = next((s for s in states if s.get("name").lower() in ["done", "closed", "completed"]), None)

    if not done_state:
        print(f"Warning: Could not find completed/done state for team {team_id}", file=sys.stderr)
        state_id = None
    else:
        state_id = done_state.get("id")

    # 2. Update state
    if state_id:
        update_mutation = """
        mutation UpdateIssueState($id: String!, $stateId: String!) {
          issueUpdate(id: $id, input: { stateId: $stateId }) {
            success
          }
        }
        """
        execute_graphql(update_mutation, {"id": issue_id, "stateId": state_id})

    # 3. Add comment
    comment_mutation = """
    mutation AddComment($issueId: String!, $body: String!) {
      commentCreate(input: { issueId: $issueId, body: $body }) {
        success
      }
    }
    """
    execute_graphql(comment_mutation, {"issueId": issue_id, "body": comment_body})
    return True


def cmd_comment(args: argparse.Namespace) -> None:
    """Add a comment to an issue."""
    issue = fetch_issue_by_identifier(args.issue_id)
    if not issue:
        print(f"Error: Ticket {args.issue_id} not found.", file=sys.stderr)
        sys.exit(1)

    comment_mutation = """
    mutation AddComment($issueId: String!, $body: String!) {
      commentCreate(input: { issueId: $issueId, body: $body }) {
        success
      }
    }
    """
    execute_graphql(comment_mutation, {"issueId": issue["id"], "body": args.body})
    print(f"Comment posted to {args.issue_id}.")


def cmd_close(args: argparse.Namespace) -> None:
    """Manually close an issue with summary and optional trigger."""
    issue = fetch_issue_by_identifier(args.issue_id)
    if not issue:
        print(f"Error: Ticket {args.issue_id} not found.", file=sys.stderr)
        sys.exit(1)

    comment_lines = [
        f"### Handled by Jarvis (Brain Intake)",
        f"",
        f"**Summary of Findings / Filing**:",
        f"{args.summary}",
    ]
    if args.report:
        comment_lines.extend(["", f"**Artifact / Report**: `{args.report}`"])
    if args.trigger:
        comment_lines.extend(["", f"**When to Bring This Up**: {args.trigger}"])

    comment_body = "\n".join(comment_lines)
    close_issue_in_linear(issue["id"], issue["team"]["id"], comment_body)
    print(f"Ticket {args.issue_id} closed in Linear with resolution note.")


def cmd_inspect(args: argparse.Namespace) -> None:
    """Inspect full ticket details, description, and comment history."""
    issue = fetch_issue_by_identifier(args.issue_id)
    if not issue:
        print(f"Error: Ticket {args.issue_id} not found.", file=sys.stderr)
        sys.exit(1)

    labels = [l.get("name") for l in issue.get("labels", {}).get("nodes", [])]
    intent, reason = classify_intent(issue)
    comments = issue.get("comments", {}).get("nodes", [])

    print(f"=== {issue['identifier']}: {issue['title']} ===")
    print(f"State: {issue['state']['name']} | URL: {issue['url']}")
    print(f"Labels: {', '.join(labels) if labels else 'none'} (Intent: {intent})")
    if issue.get("dueDate"):
        print(f"Due / Trigger Date: {issue['dueDate']}")
    print(f"\n--- Description ---\n{issue.get('description') or '(empty)'}\n")

    if comments:
        print(f"--- Comments ({len(comments)}) ---")
        for c in comments:
            author = c.get("user", {}).get("name", "Unknown")
            created = c.get("createdAt", "")[:10]
            print(f"[{created}] {author}:\n{c.get('body')}\n")
    else:
        print("--- Comments: None ---")


def cmd_state(args: argparse.Namespace) -> None:
    """Transition an issue to a named state (e.g. 'In Progress', 'Done', 'Inbox')."""
    issue = fetch_issue_by_identifier(args.issue_id)
    if not issue:
        print(f"Error: Ticket {args.issue_id} not found.", file=sys.stderr)
        sys.exit(1)

    team_states = issue.get("team", {}).get("states", {}).get("nodes", [])
    target_state = next((s for s in team_states if s.get("name").lower() == args.state_name.lower()), None)
    if not target_state:
        valid_names = [s.get("name") for s in team_states]
        print(f"Error: State '{args.state_name}' not found for team. Valid states: {', '.join(valid_names)}", file=sys.stderr)
        sys.exit(1)

    mutation = """
    mutation UpdateIssueState($id: String!, $stateId: String!) {
      issueUpdate(id: $id, input: { stateId: $stateId }) {
        success
        issue {
          identifier
          state {
            name
          }
        }
      }
    }
    """
    execute_graphql(mutation, {"id": issue["id"], "stateId": target_state["id"]})
    print(f"Updated {issue['identifier']} state to '{target_state['name']}'.")



def cmd_handle(args: argparse.Namespace) -> None:
    """Handle an issue based on its classified intent."""
    issue = fetch_issue_by_identifier(args.issue_id)
    if not issue:
        print(f"Error: Ticket {args.issue_id} not found.", file=sys.stderr)
        sys.exit(1)

    intent, reason = classify_intent(issue)
    print(f"Handling {issue['identifier']}: {issue['title']}")
    print(f"Intent: {intent} ({reason})")

    if intent == "future-convo":
        # Scaffold discussion topic in discussions/
        slug = re.sub(r"[^a-z0-9]+", "-", issue["title"].lower()).strip("-")
        disc_file = REPO_ROOT / "discussions" / f"{slug}.md"
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        if not disc_file.exists():
            content = f"""---
created: {today}
status: growing
tags: [discussions, open-discussions, linear-intake]
linear_ticket: {issue['identifier']}
linear_url: {issue['url']}
---

# {issue['title']}

## Core question & premise

From Linear ticket [{issue['identifier']}]({issue['url']}):
> {issue.get('description') or issue['title']}

---

## Current frontier (where we left off)

Enqueued asynchronously via Linear by Ted. Ready for live collaborative dialogue.

---

## Established ground & core observations

* Filed from Linear ticket {issue['identifier']}.

---

## Open threads & discussion angles

1. What is the core leverage or insight here?
2. How does this connect to active priorities, projects, or recurring practices?

---

## Chronological session log

### {today} (Session 1): Intake from Linear
- Enqueued via ticket {issue['identifier']}.
"""
            disc_file.write_text(content, encoding="utf-8")
            print(f"Created open discussion file: {disc_file.relative_to(REPO_ROOT)}")

        trigger_text = f"Bring up when discussing {issue['title']} or during weekly review."
        if issue.get("dueDate"):
            trigger_text = f"Scheduled for {issue['dueDate']}."

        close_body = f"""### Handled by Jarvis (Brain Intake)

* **Action**: Queued as persistent open discussion in `brain`.
* **Discussion File**: [`discussions/{slug}.md`](https://github.com/eob/brain/blob/main/discussions/{slug}.md)
* **When to Bring This Up**: {trigger_text}
"""
        close_issue_in_linear(issue["id"], issue["team"]["id"], close_body)
        print(f"Closed {issue['identifier']} in Linear with discussion link.")

    elif intent == "deep-research":
        print(f"Ticket requires deep research (researchfu / reportfu).")
        print(f"Please review the brief and run research agents:")
        print(f"  Title: {issue['title']}")
        print(f"  Description: {issue.get('description')}")
        print(f"Once complete, use `brain-inbox.py close {issue['identifier']} --summary '...' --report '...'`")

    elif intent == "capture":
        slug = re.sub(r"[^a-z0-9]+", "-", issue["title"].lower()).strip("-")
        ref_file = REPO_ROOT / "notes" / "references" / f"{slug}.md"
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        if not ref_file.exists():
            content = f"""---
created: {today}
status: seed
tags: [references, linear-intake]
linear_ticket: {issue['identifier']}
linear_url: {issue['url']}
---

# {issue['title']}

- **Source / Ticket**: [{issue['identifier']}]({issue['url']})

## Captured summary

{issue.get('description') or 'No description provided.'}
"""
            ref_file.write_text(content, encoding="utf-8")
            print(f"Created reference note: {ref_file.relative_to(REPO_ROOT)}")

        close_body = f"""### Handled by Jarvis (Brain Intake)

* **Action**: Captured into brain reference library.
* **Note Path**: [`notes/references/{slug}.md`](https://github.com/eob/brain/blob/main/notes/references/{slug}.md)
"""
        close_issue_in_linear(issue["id"], issue["team"]["id"], close_body)
        print(f"Closed {issue['identifier']} in Linear with reference note link.")

    else:
        print(f"Intent unclear for {issue['identifier']}. Leaving in inbox for manual triage.")
        comment_mutation = """
        mutation AddComment($issueId: String!, $body: String!) {
          commentCreate(input: { issueId: $issueId, body: $body }) {
            success
          }
        }
        """
        body = "Jarvis intake: Unsure how to handle this ticket automatically. Please tag with `future-convo`, `deep-research`, or `capture`."
        execute_graphql(comment_mutation, {"issueId": issue["id"], "body": body})
        print("Posted clarification comment to Linear.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Brain Linear Inbox Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # status
    p_status = subparsers.add_parser("status", help="Check Linear connectivity and viewer")
    p_status.set_defaults(func=cmd_status)

    # list
    p_list = subparsers.add_parser("list", help="List pending inbox tickets")
    p_list.add_argument("--team", help="Filter by team key (e.g. BRN)")
    p_list.set_defaults(func=cmd_list)

    # next
    p_next = subparsers.add_parser("next", help="Get next ticket to handle")
    p_next.add_argument("--team", help="Filter by team key (e.g. BRN)")
    p_next.add_argument("--json", action="store_true", help="Output in machine-readable JSON")
    p_next.set_defaults(func=cmd_next)

    # handle
    p_handle = subparsers.add_parser("handle", help="Handle an issue by identifier")
    p_handle.add_argument("issue_id", help="Linear issue identifier (e.g. BRN-12)")
    p_handle.set_defaults(func=cmd_handle)

    # comment
    p_comment = subparsers.add_parser("comment", help="Add a comment to an issue")
    p_comment.add_argument("issue_id", help="Linear issue identifier")
    p_comment.add_argument("body", help="Comment text")
    p_comment.set_defaults(func=cmd_comment)

    # inspect
    p_inspect = subparsers.add_parser("inspect", help="Inspect full ticket details and comment history")
    p_inspect.add_argument("issue_id", help="Linear issue identifier (e.g. BRN-12)")
    p_inspect.set_defaults(func=cmd_inspect)

    # state
    p_state = subparsers.add_parser("state", help="Transition issue to a named state")
    p_state.add_argument("issue_id", help="Linear issue identifier")
    p_state.add_argument("state_name", help="Target state name (e.g. 'In Progress', 'Done', 'Inbox')")
    p_state.set_defaults(func=cmd_state)

    # close
    p_close = subparsers.add_parser("close", help="Close an issue with summary and metadata")
    p_close.add_argument("issue_id", help="Linear issue identifier")
    p_close.add_argument("--summary", required=True, help="High-level summary of findings")
    p_close.add_argument("--trigger", help="When Jarvis should bring this up (topic or time)")
    p_close.add_argument("--report", help="Relative path to report or artifact in brain")
    p_close.set_defaults(func=cmd_close)


    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
