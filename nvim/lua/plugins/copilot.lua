return {
  "github/copilot.vim",
  cmd = { "Copilot", "Copilot status", "Copilot file" },
  event = "VeryLazy",
  config = function()
    -- Define a toggle function
    vim.keymap.set("n", "<leader>cc", function()
      local status = vim.fn["copilot#Enabled"]()
      if status == 1 then
        vim.cmd("Copilot disable")
        print("Copilot Disabled")
      else
        vim.cmd("Copilot enable")
        print("Copilot Enabled")
      end
    end, { desc = "Toggle Copilot" })

    -- Other useful bindings
    vim.keymap.set("n", "<leader>cf", "<cmd>Copilot file<cr>", { desc = "Copilot File" })
    vim.keymap.set("n", "<leader>cs", "<cmd>Copilot status<cr>", { desc = "Copilot Status" })
  end,
}
