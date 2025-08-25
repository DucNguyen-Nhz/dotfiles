-- Keymaps for moving code blocks in and visual modes
vim.keymap.set("v", "J", ":m '>+1<CR>gv=gv", { noremap = true, silent = true })
vim.keymap.set("v", "K", ":m '<-2<CR>gv=gv", { noremap = true, silent = true })

-- auto format a file
vim.keymap.set("n", "<leader>f>", "gg=G", { noremap = true, silent = true })
