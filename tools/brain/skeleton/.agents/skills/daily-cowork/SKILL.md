---
name: daily-cowork
description: Manage the daily cowork rhythm. Initialize the morning agenda, roll forward pending tasks from yesterday, track active reminders, and log progress throughout the day.
---

# Daily Cowork Protocol

Use this skill to support {{USER_NAME}}'s daily focus and momentum.

## 1. Morning Startup
Run:
```sh
brain today
```
This generates or opens `cowork/YYYY/YYYY-MM-DD.md`, rolling forward any unchecked tasks from the previous session and surfacing any reminders scheduled for today.

## 2. In-Session Logging
During active cowork sessions:
- Check off completed items as progress is made: `- [x] Done task`.
- Record unexpected discoveries or blockers directly in today's log.

## 3. End-of-Day Wrapup
1. Review pending tasks: decide whether to drop, complete, or leave them to roll forward tomorrow.
2. Schedule future reminders if needed:
   ```sh
   brain remind "<date>" "<reminder text>"
   ```
3. Run `brain sync` to index changes and push to origin/main.
