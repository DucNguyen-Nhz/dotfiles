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
			vim.keymap.set("n", "gd", function() vim.lsp.buf.definition() end, opts)
			vim.keymap.set("n", "gr", function() vim.lsp.buf.reference() end, opts)
			vim.keymap.set("n", "K", function() vim.lsp.buf.hover() end, opts)

			vim.api.nvim_create_autocmd("BufWritePre", {
				buffer = bufnr,
				callback = function()
					vim.lsp.buf.format()
				end,
			})
		end

		lspconfig.pyright.setup({
			capabilities = capabilities,
			on_attach = on_attach,
			inlayHints = {
				variableTypes = true,
				functionReturnTypes = true,
				parameterTypes = true
			}
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
