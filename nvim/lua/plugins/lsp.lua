return {
	"neovim/nvim-lspconfig",
	config = function()
		local lspconfig = require("lspconfig")
		local ok, cmp_nvim_lsp = pcall(require, "cmp_nvim_lsp")
		if not ok then
			return
		end

		local capabilities = vim.lsp.protocol.make_client_capabilities() 

		capabilities = cmp_nvim_lsp.default_capabilities(capabilities)

		local on_attach = function(_, bufnr)
			local opts = { buffer = bufnr, silent = true }
			vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)
			vim.keymap.set("n", "gr", vim.lsp.buf.reference, opts)
			vim.keymap.set("n", "K", vim.lsp.buf.hover, opts)
		end

		lspconfig.pyright.setup({
			capabilities = capabilities,
			on_attach = on_attach,
		})
		
		lspconfig.ts_ls.setup({
			capabilities = capabilities,
			on_attach = on_attach,
		})
		
		lspconfig.gopls.setup({
			capabilities = capabilities,
			on_attach = on_attach,
			settings = {
				gopls = {
					analyses = { unusedparams = true },
					staticcheck = true
				}
			}
		})

	end,
}
