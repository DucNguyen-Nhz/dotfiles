return {
  "nvim-tree/nvim-tree.lua",
  version = "*",
  lazy = false,
  dependencies = {
    "nvim-tree/nvim-web-devicons",
  },
	keys = {
    { "<leader>t", "<cmd>NvimTreeToggle<CR>", desc = "Toggle NvimTree" },
  },
  config = function()
	
	local on_attach = function (bufnr)
		local api = require('nvim-tree.api')

		local function opts(desc)
			return { desc = "nvim-tree: " .. desc, buffer = bufnr, noremap = true, silent = true, nowait = true }
		end

		api.map.on_attach.default(bufnr)
		vim.keymap.set("n", "<leader>r", function()
			require("nvim-tree.api").tree.find_file({ open = true })
		end, { desc = "Reveal file in NvimTree" })

	end

    require("nvim-tree").setup {
		on_attach = on_attach

	}
  end,
}
