CWD := $(shell pwd)

.PHONY: install
install:
	mkdir -p ~/.config
	mkdir -p ~/.config/alacritty
	mkdir -p ~/.config/zellij
	mkdir -p ~/.config/zellij/layouts
	- ln -is $(CWD)/nvim ~/.config/nvim
	- ln -is $(CWD)/kitty ~/.config/kitty
	- ln -is $(CWD)/ghostty ~/.config/ghostty
	- ln -is $(CWD)/zellij/config.kdl ~/.config/zellij/config.kdl
	- ln -is $(CWD)/zellij/layouts/default.kdl ~/.config/zellij/layouts/default.kdl
	- ln -is $(CWD)/zsh/zshrc ~/.zshrc
	- ln -is $(CWD)/other/hushlogin ~/.hushlogin
	- ln -is $(CWD)/git/gitignore ~/.gitignore
	- cp -n $(CWD)/git/gitconfig ~/.gitconfig
	- ln -is $(CWD)/alacritty/alacritty.yml ~/.config/alacritty/alacritty.yml
	- ln -is $(CWD)/alacritty/tokyo-night.yml ~/.config/alacritty/tokyo-night.yml
	- [ -d ~/.config/base16-shell ] || git clone https://github.com/chriskempson/base16-shell.git ~/.config/base16-shell
	- $(CURDIR)/scripts/macos-defaults.sh
	- $(CURDIR)/scripts/brew-install.sh
	- $(CURDIR)/scripts/go-install.sh

.PHONY: update/kitty
update/kitty:
	wget "https://raw.githubusercontent.com/dexpota/kitty-themes/master/themes/gruvbox_dark.conf" \
		-P ~/.config/kitty/kitty-themes/themes

.PHONY: install/listen-on-camera
install/listen-on-camera:
	- mkdir -p ~/Library/Kern.io
	- mkdir -p ~/Library/LaunchAgents
	- ln -is $(CWD)/automation/io.kern.listen-on-camera.plist ~/Library/LaunchAgents/io.kern.listen-on-camera.plist
	- launchctl load ~/Library/LaunchAgents/io.kern.listen-on-camera.plist

.PHONY: install/listen-on-camera/upload
install/listen-on-camera/unload:
	- launchctl unload ~/Library/LaunchAgents/io.kern.listen-on-camera.plist
