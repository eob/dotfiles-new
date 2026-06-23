-- Kaya Language Support (Tree-sitter Syntax Highlighting & Language Server Protocol)
return {
  -- 1. Set up Filetype Detection for .kaya files
  {
    "nvim-treesitter/nvim-treesitter",
    opts = function(_, opts)
      opts = opts or {}
      -- Automatically detect .kaya files as the 'kaya' filetype
      vim.filetype.add({
        extension = {
          kaya = "kaya",
        },
      })
      return opts
    end,
  },

  -- 2. Extend nvim-lspconfig to configure the editor-agnostic Kaya LSP
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        kaya = {
          -- Execute using node from the compiled package output
          cmd = { "node", "/mnt/disks/data/kaya-web/robotbookclub-prod/packages/kaya_vscode_server/out/server.js", "--stdio" },
          filetypes = { "kaya" },
          root_dir = function(fname)
            local util = require("lspconfig.util")
            return util.root_pattern(".git")(fname) or vim.fn.getcwd()
          end,
          single_file_support = true,
        },
      },
      setup = {
        kaya = function(_, opts)
          local configs = require("lspconfig.configs")
          -- Dynamically define the custom 'kaya' server schema in lspconfig
          if not configs.kaya then
            configs.kaya = {
              default_config = opts,
            }
          end
          -- Return false to let LazyVim's default setup logic complete the initialization
          return false
        end,
      },
    },
  },
}
