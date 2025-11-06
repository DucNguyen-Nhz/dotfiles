return {
	"neovim/nvim-lspconfig",
	config = function()
		local ok, cmp_nvim_lsp = pcall(require, "cmp_nvim_lsp")
		if not ok then
			return
		end

		local capabilities = vim.lsp.protocol.make_client_capabilities() 

		capabilities = cmp_nvim_lsp.default_capabilities(capabilities)

		local on_attach = function(client, bufnr)
			local opts = { buffer = bufnr, silent = true }
			vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)
			vim.keymap.set("n", "gr", vim.lsp.buf.references, opts)
			vim.keymap.set("n", "K", vim.lsp.buf.hover, opts)
			vim.keymap.set('n', '<leader>e', vim.diagnostic.open_float, opts)


			if client.name == "gopls" then
				vim.api.nvim_create_autocmd("BufWritePre", {
					group = vim.api.nvim_create_augroup("GoFormat", { clear = true }),
					buffer = bufnr,
					callback = function()
						vim.lsp.buf.format({ async = false })
					end,
				})
			else
				vim.api.nvim_create_autocmd("BufWritePre", {
					buffer = bufnr,
					callback = function()
						vim.lsp.buf.format()
					end,
				})
			end
		end

		vim.lsp.config("pyright", {
			capabilities = capabilities,
			on_attach = on_attach,
			inlayHints = {
				variableTypes = true,
				functionReturnTypes = true,
				parameterTypes = true
			}
		})
		
		vim.lsp.config("ts_ls", {
			capabilities = capabilities,
			on_attach = on_attach,
		})
		
		vim.lsp.config("gopls", {
			capabilities = capabilities,
			on_attach = on_attach,
			settings = {
				gopls = {
					analyses = { unusedparams = true },
					staticcheck = true
				}
			}
		})
		
		vim.lsp.enable({"pyright", "gopls", "ts_ls"})

	end,
}
