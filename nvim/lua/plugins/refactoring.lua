-- refactoring.nvim moved its async impl to lewis6991/async.nvim,
-- but the pinned LazyVim spec only declares plenary as a dep.
-- Add the missing dep here.
return {
  {
    "ThePrimeagen/refactoring.nvim",
    dependencies = { "lewis6991/async.nvim" },
  },
}
