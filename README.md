# Dotfiles

## Dotfiles included

* **.config/nvim**: neovim configuration
* **zellij**: terminal multiplexer (defaults + theme + copy/paste settings, see `zellij/config.kdl`)
* **.gitignore**: global git ignore for macOS
* **.gitconfig**: git and GitHub configuration
* **.hushlogin**: no MOTD
* **skills**: modular AI agent skills (Claude Code, Google Antigravity, etc.)
* **kaya**: the Kaya CLI + `kayad` daemon in `~/.kaya`, via the official [kaya-lang.org](https://kaya-lang.org/install) installer (`install.d/shared/09_kaya.sh`)
* **rex**: Superlogical's self-contained Mac app (`scripts/rex-install.sh`)

## Usage

*Warning:* Running `make` will overwrite your dotfiles!

    $ git clone git://github.com/eob/dotfiles-new.git ~/.dotfiles
    $ cd ~/.dotfiles && make

## Key Bindings

### zellij

Uses zellij's built-in default keybinds. Ghostty maps macOS shortcuts onto them:

cmd+t → new tab (Ctrl-t n)
cmd+d → split right (Ctrl-p r)
cmd+shift+d → split down (Ctrl-p d)
cmd+w → close pane (Ctrl-p x)
cmd+[ / cmd+] (and shift variants) → prev/next tab (Ctrl-t h / l)
shift+enter → literal newline

Native zellij defaults: Ctrl-p (pane mode), Ctrl-t (tab mode), Ctrl-n (resize),
Ctrl-s (scroll/search), Ctrl-o (session), Ctrl-q (quit). Alt+h/j/k/l move
focus between panes; Alt+n opens a new pane.

### Copy & paste (zellij on the devbox, over mosh)

- Paste into a pane: Ctrl+Shift+V (or Omarchy's Super+V).
- Copy from a pane: drag-select with the mouse, then **Alt+c**. Selecting alone
  no longer copies — zellij 0.44.x can re-copy pane text on mere mouse
  movement and clobber the clipboard (why in `zellij/config.kdl`).
- Hold **Shift** while dragging to select with the terminal itself instead of
  zellij (spans pane borders; Ctrl+Shift+C / middle-click then work as usual).
- Both directions use OSC 52 / bracketed paste through mosh: mosh >= 1.4 on
  both ends, and the terminal must allow OSC 52 clipboard writes.

### Shortcuts

z → zellij-launch (attach to / create the default zellij session)
a → agy --dangerously-skip-permissions (YOLO Antigravity)
c → claude --dangerously-skip-permissions (YOLO Claude)
x → codex --yolo (YOLO Codex)
v → nvim . (or a file)
vdot → cd to ~/.dotfiles and open nvim
brain → AI cognitive OS CLI (inbox triage, vector search, cowork agenda, sync)
editzsh / sourcezsh — edit/reload zshrc
devbox → mosh into the devbox (UDP; roams across sleep/wifi changes)
devbox-ssh → SSH over TCP with dev ports forwarded (captive/airplane wifi); reaps
  any stale forwarder holding the local ports first, so reconnecting always works.
  Both read DEVBOX_IP / DEVBOX_USERNAME from ~/.zshrc.local (see .zshrc.local.example).
devbox-repair → repair and verify the macOS Homebrew mosh / protobuf / abseil libraries.
Git: gs (status -sb), gc (commit -av), gco / gcob, gb, gp (push current), gpf (force push current)
l → eza (or exa/ls fallback)

### Git Hacks

fastrebase [upstream] — squashes all commits since the merge-base into one, backs up the branch to eob/backups/<timestamp>, then rebases onto upstream. Default upstream: origin/master.
irebase [upstream] — same backup safety + interactive rebase from merge-base.
Both stash automatically if dirty. The backup branch is your escape hatch.

## Devbox client repair

If `devbox` reports a missing `libabsl_*.dylib` or another local Mosh startup
failure, run this **on the Mac**:

```sh
git -C ~/.dotfiles pull --ff-only
bash ~/.dotfiles/bin/devbox-repair
devbox
```

The repair updates Homebrew, reinstalls `abseil`, `protobuf`, and `mosh`, then
checks their library links and starts `mosh-client --version`. It stops if a
step fails. Do not symlink libraries with different version numbers together.
`devbox-ssh` provides immediate SSH access while Mosh is unavailable.

## Superlogical Rex

Rex for Mac includes its own local server and can run the existing devbox
commands in a terminal. On the Mac:

```sh
git -C ~/.dotfiles pull --ff-only
bash ~/.dotfiles/scripts/rex-install.sh
bash ~/.dotfiles/bin/devbox-repair
open -a Rex
```

The installer uses the official preview download linked from the beta invite,
installs to `~/Applications/Rex.app`, and leaves an existing installation in
place. The macOS dotfiles bootstrap also runs it. Beta invite links stay out
of git.

In Rex, run `devbox` or `devbox-ssh`. These commands use the existing SSH/Mosh
connection settings. The Mosh connection still resumes the remote Zellij
session. Rex's local terminal and panes do not require a Linux Rex server.

Rex's **Add Remote Host…** feature is a separate connection to a Rex server.
The [installation docs](https://www.superlogical.com/rex/docs/installation)
describe the Linux server as testing; this setup uses only the Mac app.
The [configuration docs](https://www.superlogical.com/rex/docs/customize/config)
explain `~/.config/rex/init.lua`. Rex does not need a config file to start.
The existing zsh config falls back to `xterm-256color` when a remote host lacks
the terminal's terminfo entry.

`make test` runs the shell regression tests without changing packages or
connecting to a devbox.


## License

`@eob/dotfiles-new` is released under the [BSD 3-Clause license](https://github.com/kern/dotfiles/blob/master/LICENSE).
