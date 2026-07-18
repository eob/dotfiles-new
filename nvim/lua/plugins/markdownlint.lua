-- nvim-lint runs markdownlint-cli2 via stdin (`markdownlint-cli2 -`), and in
-- stdin mode markdownlint-cli2 only looks for a config in the *exact* cwd — it
-- does not walk up the directory tree. That means our ~/.markdownlint-cli2.yaml
-- is ignored unless nvim happens to be launched from $HOME.
--
-- Fix: pass the config path explicitly with --config so it applies everywhere,
-- regardless of the working directory. (~/.markdownlint-cli2.yaml is symlinked
-- from other/markdownlint-cli2.yaml by the Makefile.)
return {
  "mfussenegger/nvim-lint",
  opts = {
    linters = {
      ["markdownlint-cli2"] = {
        args = { "--config", vim.fn.expand("~/.markdownlint-cli2.yaml"), "-" },
      },
    },
  },
}
