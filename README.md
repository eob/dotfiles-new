# Dotfiles

## Dotfiles included

* **.config/nvim**: neovim configuration
* **.tmux.conf**: tmux configuration
* **.gitignore**: global git ignore for macOS
* **.gitconfig**: git and GitHub configuration
* **.hushlogin**: no MOTD

## Usage

*Warning:* Running `make` will overwrite your dotfiles!

    $ git clone git://github.com/eob/dotfiles-new.git ~/.dotfiles
    $ cd ~/.dotfiles && make

## Key Bindings

### tmux

cmd+t → new window (C-a c)
cmd+d → split horizontal (C-a %)
cmd+shift+d → split vertical (C-a ")
cmd+w → kill pane (C-a x)
cmd+[ / cmd+] (and shift variants) → prev/next window
shift+enter → literal newline

C-h / C-j / C-k / C-l to move between panes.

### Shortcuts

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
