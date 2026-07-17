-- Kaya language support: tree-sitter syntax highlighting for .kaya files.
--
-- NOTE: the Kaya LSP is not published yet. When it is, add a
-- `neovim/nvim-lspconfig` spec here pointing `cmd` at the published server
-- (npm binary / npx), NOT a machine-specific path.
return {
  -- 1. Filetype detection + tree-sitter parser for .kaya files.
  --
  -- nvim-treesitter is on the `main` branch (v1.0 rewrite). It reloads its
  -- parsers table from disk on every update, which wipes a direct
  -- `parsers.kaya = {...}` assignment (the snippet in the mirror repo's README
  -- is for the old `master` API and does NOT work here). The sanctioned way is
  -- to (re)register inside a `User TSUpdate` autocmd — the plugin fires that
  -- event right before it reads the parser list, so the entry is always present.
  {
    "nvim-treesitter/nvim-treesitter",
    opts = function(_, opts)
      opts = opts or {}

      -- Detect .kaya files as the 'kaya' filetype.
      vim.filetype.add({ extension = { kaya = "kaya" } })

      -- Register the custom parser (mirror of the Kaya monorepo grammar).
      -- `main` compiles src/parser.c automatically, so no `files` key is needed.
      vim.api.nvim_create_autocmd("User", {
        pattern = "TSUpdate",
        callback = function()
          require("nvim-treesitter.parsers").kaya = {
            install_info = {
              url = "https://github.com/eob/kaya-nvim-treesitter",
              branch = "main",
            },
          }
        end,
      })

      -- Install kaya alongside the rest (opts_extend merges this list).
      opts.ensure_installed = opts.ensure_installed or {}
      table.insert(opts.ensure_installed, "kaya")

      return opts
    end,
  },
}
