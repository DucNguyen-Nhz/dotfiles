setup:
# 	ln -s ../dotfiles/tmux.conf ~/.tmux.conf
	mkdir -p ~/.tmux/plugins

	if [ ! -d ~/.tmux/plugins/tpm ]; then git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm; fi

	if [ ! -d ~/.tmux/plugins/catppuccin/tmux ]; then git clone -b v2.1.3 https://github.com/catppuccin/tmux.git ~/.tmux/plugins/catppuccin/tmux; fi

	cp -r ../dotfiles/tmux.conf ~/.tmux.conf