-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua

-- keymap: jk to Esc
vim.keymap.set("i", "jk", "<Esc>")

-- keymap: swap ; and :
vim.keymap.set("n", ";", ":")
vim.keymap.set("n", ":", ";")

-- keymap: vim-tmux-navigator
vim.keymap.set("n", "<C-h>", "<Cmd>NvimTmuxNavigateLeft<CR>", { silent = true })
vim.keymap.set("n", "<C-j>", "<Cmd>NvimTmuxNavigateDown<CR>", { silent = true })
vim.keymap.set("n", "<C-k>", "<Cmd>NvimTmuxNavigateUp<CR>", { silent = true })
vim.keymap.set("n", "<C-l>", "<Cmd>NvimTmuxNavigateRight<CR>", { silent = true })
vim.keymap.set("n", "<C-\\>", "<Cmd>NvimTmuxNavigateLastActive<CR>", { silent = true })
vim.keymap.set("n", "<C-Space>", "<Cmd>NvimTmuxNavigateNavigateNext<CR>", { silent = true })

-- keymap: %% to current file directory
vim.keymap.set("c", "%%", "<C-R>=expand('%:h').'/'<CR>")

-- keymap: leader-S to sort the selected lines.
vim.keymap.set("v", "<leader>S", ":sort<CR>")

-- keymap: leader-O to open the current directory in a Finder window
vim.keymap.set("n", "<leader>o", ":exe '!open '.expand('%:h').'/'<CR>")

-- keymap: <leader><leader> to toggle Neotree
vim.keymap.set("n", "<leader><leader>", ":Neotree<CR>")

-- :Serve — start miniserve on port 8000 from a directory chosen by context:
--   * inside a Neotree buffer: the node under the cursor (file → its parent)
--   * elsewhere: the current buffer's dir, or cwd if no buffer
-- Any existing process on port 8000 is killed first, so re-running restarts.
local function serve()
  local path

  if vim.bo.filetype == "neo-tree" then
    local ok, manager = pcall(require, "neo-tree.sources.manager")
    if ok then
      local state = manager.get_state("filesystem")
      if state and state.tree then
        local node = state.tree:get_node()
        if node then
          path = node.path
          if node.type == "file" then
            path = vim.fn.fnamemodify(path, ":h")
          end
        end
      end
    end
  end

  if not path then
    local bufname = vim.api.nvim_buf_get_name(0)
    path = bufname ~= "" and vim.fn.fnamemodify(bufname, ":h") or vim.fn.getcwd()
  end

  vim.fn.system("fuser -k 8000/tcp 2>/dev/null")

  local job = vim.fn.jobstart({ "miniserve", "--port", "8000", path }, { detach = true })
  if job > 0 then
    vim.notify("Serving " .. path .. " on http://127.0.0.1:8000")
  else
    vim.notify("Failed to start miniserve", vim.log.levels.ERROR)
  end
end

vim.api.nvim_create_user_command("Serve", serve, {})
vim.keymap.set("n", "<leader>s", serve, { silent = true, desc = "Serve dir under cursor" })

-- :ServeStop — kill whatever's on port 8000 (typically the :Serve miniserve)
vim.api.nvim_create_user_command("ServeStop", function()
  local out = vim.fn.system("fuser -k 8000/tcp 2>&1")
  if vim.v.shell_error == 0 then
    vim.notify("Stopped server on :8000")
  else
    vim.notify("Nothing was running on :8000", vim.log.levels.INFO)
  end
end, {})
