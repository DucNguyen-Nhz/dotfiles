return {
  "nvim-treesitter/nvim-treesitter",
  branch = "main",
  lazy = false,
  build = ":TSUpdate",
  config = function()
    local ts = require("nvim-treesitter")
    ts.install({
      "vimdoc", "vim", "lua", "bash", "python", "go", "gomod", "gosum",
      "javascript", "typescript", "tsx", "jsdoc", "vue", "html", "css",
      "json", "yaml", "toml", "csv", "sql", "markdown", "markdown_inline",
      "c", "cpp", "d", "glsl", "templ", "make", "dockerfile", "nginx",
      "gitignore", "requirements", "ssh_config", "udev",
    })

    -- main branch doesn't auto-enable highlight/indent; start them per buffer
    vim.api.nvim_create_autocmd("FileType", {
      callback = function(args)
        -- Replaces auto_install: fetch a missing parser, then start once it's built
        local lang = vim.treesitter.language.get_lang(vim.bo[args.buf].filetype)
        if lang and vim.tbl_contains(ts.get_available(), lang)
            and not vim.tbl_contains(ts.get_installed(), lang) then
          ts.install(lang):await(function()
            if vim.api.nvim_buf_is_valid(args.buf) then
              pcall(vim.treesitter.start, args.buf)
            end
          end)
          return
        end
        if not pcall(vim.treesitter.start, args.buf) then
          return
        end
        vim.bo[args.buf].indentexpr = "v:lua.require'nvim-treesitter'.indentexpr()"
        -- Was additional_vim_regex_highlighting = { "markdown" }
        if vim.bo[args.buf].filetype == "markdown" then
          vim.bo[args.buf].syntax = "on"
        end
      end,
    })
  end
}
