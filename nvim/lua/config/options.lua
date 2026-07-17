-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here

vim.g.mapleader = ","

-- Pin the LazyVim picker explicitly. Both the `editor.fzf` and
-- `editor.telescope` extras are enabled; without this pin whichever loads
-- first wins (and LazyVim warns about the conflict). Change to "telescope"
-- to switch. Telescope stays installed either way for custom mappings.
vim.g.lazyvim_picker = "fzf"
