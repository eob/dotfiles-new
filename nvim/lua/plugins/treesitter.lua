-- Pin nvim-treesitter to the `master` branch.
-- LazyVim still calls `require("nvim-treesitter.query_predicates")`, which
-- only exists on `master`; the new `main` branch is a v1.0 rewrite that
-- removed it. Remove this override once LazyVim migrates to main.
return {
  { "nvim-treesitter/nvim-treesitter", branch = "master" },
}
