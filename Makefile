setup:
	if [ -d ~/.config/nvim.bak ]; then rm -rf ~/.config/nvim.bak; fi
	mv ~/.config/nvim ~/.config/nvim.bak

	mkdir -p ~/.tmux/plugins
	mkdir -p ~/.config/nvim

	if [ ! -d ~/.tmux/plugins/tpm ]; then git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm; fi

	if [ ! -d ~/.tmux/plugins/catppuccin/tmux ]; then git clone -b v2.1.3 https://github.com/catppuccin/tmux.git ~/.tmux/plugins/catppuccin/tmux; fi

	if [ ! -d ~/.config/nvim ]; then git clone https://github.com/LazyVim/starter ~/.config/nvim; fi
	
	rm -rf ~/.config/nvim/.git
	cp -r ../dotfiles/tmux.conf ~/.tmux.conf
	cp -r nvim/ ~/.config/nvim


	