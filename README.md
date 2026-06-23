# Dotfiles

## Dotfiles included

* **.config/nvim**: neovim configuration
* **zellij**: terminal multiplexer (uses built-in defaults — no config file)
* **.gitignore**: global git ignore for macOS
* **.gitconfig**: git and GitHub configuration
* **.hushlogin**: no MOTD

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

### Shortcuts

z → zellij-launch (attach to / create the default zellij session)
c → claude --dangerously-skip-permissions (YOLO Claude)
v → nvim . (or a file)
vdot → cd to ~/.dotfiles and open nvim
editzsh / sourcezsh — edit/reload zshrc
Git: gs (status -sb), gc (commit -av), gco / gcob, gb, gp (push current), gpf (force push current)
l → eza (or exa/ls fallback)

### Git Hacks

fastrebase [upstream] — squashes all commits since the merge-base into one, backs up the branch to kern/backups/<timestamp>, then rebases onto upstream. Default upstream: origin/master.
irebase [upstream] — same backup safety + interactive rebase from merge-base.
Both stash automatically if dirty. The backup branch is your escape hatch.


## License

`@eob/dotfiles-new` is released under the [BSD 3-Clause license](https://github.com/kern/dotfiles/blob/master/LICENSE).
