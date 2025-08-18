local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
    vim.fn.system(
        {"git", "clone", "--filter=blob:none", "https://github.com/folke/lazy.nvim.git", "--branch=stable", -- latest stable release
         lazypath})
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup({
    spec = "plugins",
    defaults = {},
    install = {},
    performance = {},
    rocks = {
        enabled = false
    }
})

-- {
--     spec = {{
--         "nvim-treesitter/nvim-treesitter",
--         build = ":TSUpdate"
--     }, {"neovim/nvim-lspconfig"}, {
--         "nvim-telescope/telescope.nvim",
--         dependencies = {"nvim-lua/plenary.nvim"}
--     }, {
--         "christoomey/vim-tmux-navigator",
--         cmd = {"TmuxNavigateLeft", "TmuxNavigateDown", "TmuxNavigateUp", "TmuxNavigateRight", "TmuxNavigatePrevious",
--                "TmuxNavigatorProcessList"},
--         keys = {{"<c-h>", "<cmd><C-U>TmuxNavigateLeft<cr>"}, {"<c-j>", "<cmd><C-U>TmuxNavigateDown<cr>"},
--                 {"<c-k>", "<cmd><C-U>TmuxNavigateUp<cr>"}, {"<c-l>", "<cmd><C-U>TmuxNavigateRight<cr>"},
--                 {"<c-\\>", "<cmd><C-U>TmuxNavigatePrevious<cr>"}}
--     }},
--     defaults = {},
--     install = {},
--     performance = {},
--     rocks = {
--         enabled = false
--     }
-- })
