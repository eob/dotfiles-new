# Post-Setup Fixes (Claude, read this on new machines)

This is a working notebook for Claude. After running the normal dotfiles installer on a new machine, several things commonly still need attention before nvim and tmux work cleanly. This file is the institutional memory of what tends to break and how to fix it — written so you can adapt to the host (macOS, Debian/Ubuntu, fresh devbox) rather than copy-paste shell commands verbatim.

Use this as a diagnostic checklist, not a runbook. Verify each section's symptom first; only fix what's actually broken on this machine. Always confirm with the user before doing anything destructive (rm, package removal, sudo).

---

## How to use this file

1. Run through the sections in order. Each one starts with **Detect** — actually verify the symptom on this machine before applying any fix.
2. Prefer the user-local install path (`~/.local/`) over system-wide installs whenever possible. It keeps the system clean and lets fixes work without sudo on devboxes where sudo may be restricted.
3. For toolchains (Go, Rust, Ruby, Node), prefer official tarballs/installers from the language's own site rather than the OS package manager — distro packages are often years out of date and break newer plugins.
4. On macOS, Homebrew typically has fresh versions of everything; lean on `brew install` first.
5. After each fix, do the verification step before moving on. Several of these issues mask each other.

---

## 1. Stray self-referential symlinks in the dotfiles tree

**Symptom:** Directories like `~/.dotfiles/nvim/nvim`, `~/.dotfiles/ghostty/ghostty`, `~/.dotfiles/kitty/kitty` exist as symlinks pointing back at their own parent. Recursive `find` loops; `git status` shows them as untracked.

**Root cause:** Accidental `ln -s . <name>` (or similar) from a past setup step. They are not created by any installer script.

**Fix:** Remove the self-referential links. They are not referenced by anything.

**Verify:** `find ~/.dotfiles -maxdepth 2 -type l` should not show any links whose target is their own parent directory.

---

## 2. Neovim is too old for the LazyVim config

**Symptom:** Opening nvim spews lua errors immediately, mentioning `lazy.nvim requires Neovim >= X.X` or similar. Many "lua faults" on startup.

**Root cause:** This dotfiles config uses LazyVim, which requires a modern Neovim (currently ≥0.9, in practice ≥0.10 for the latest LazyVim). Debian stable (bookworm) ships Neovim 0.7.x and that's the version on PATH after `apt install neovim`. Other distros may have similar lag.

**Fix approach:**
- Check the current Neovim version on the machine (`nvim --version`).
- Cross-check against what LazyVim/lazy.nvim require by reading the error or checking the LazyVim README.
- If too old, install a recent Neovim into `~/.local/` (not via the system package manager):
  - macOS: `brew install neovim` is usually current enough.
  - Linux: download the official static tarball (`nvim-linux-x86_64.tar.gz`) from the Neovim GitHub releases, extract into `~/.local/nvim/`, symlink the binary into `~/.local/bin/nvim`. Verify `~/.local/bin` is on PATH.
- Avoid the AppImage on devboxes — many lack FUSE.
- After upgrading, **wipe the stale plugin state** (`~/.local/share/nvim/lazy`, `~/.cache/nvim`, `~/.local/share/nvim/shada`, `~/.local/share/nvim/swap`) before relaunching, since plugins may have been partially bootstrapped against the old version.

**Verify:** `nvim --version` reports a modern release; `nvim --headless -c 'qa' 2>&1` produces zero output.

---

## 3. Tree-sitter CLI requires a newer glibc than the host has

**Symptom:** `:checkhealth` shows treesitter parsers failing to compile with `tree-sitter: ... libc.so.6: version 'GLIBC_2.XX' not found`. Many parsers report "0/N languages installed" or similar.

**Root cause:** Mason (and nvim-treesitter) download the **latest** prebuilt `tree-sitter` CLI binary from GitHub, which is built against a glibc newer than what the host provides. This bites on stable Linux distros where glibc lags. macOS is not affected.

**Fix approach:**
- Check the host's glibc version (`ldd --version`).
- Download an older `tree-sitter` CLI release (e.g. v0.22.x) that was built against an older glibc. The 0.22.x line works on Debian bookworm's glibc 2.36.
- Place the binary at `~/.local/bin/tree-sitter`.
- **Also replace Mason's copy of the binary** with a symlink to your working one — Mason caches its own at `~/.local/share/nvim/mason/packages/tree-sitter-cli/tree-sitter-linux-x64` and will keep using that incompatible version otherwise.

**Verify:** `:TSUpdate` (or running nvim on a fresh repo's first open) installs all parsers without GLIBC errors. `:checkhealth nvim-treesitter` reports "Installed N/N languages".

---

## 4. CLI tools LazyVim relies on are missing

**Symptom:** LazyVim's picker, file-finder, and git UI don't work, or `:checkhealth` reports `ripgrep`, `fd-find`, `fzf`, `lazygit` not found.

**Root cause:** Pure installer hygiene — these aren't bundled. LazyVim assumes they're on PATH.

**Fix approach:**
- macOS: `brew install ripgrep fd fzf lazygit`.
- Debian/Ubuntu: `apt install ripgrep fd-find fzf` covers the first three. (On Debian, `fd` is named `fdfind` — LazyVim handles this.) `lazygit` is usually not packaged on Debian stable; grab a release tarball from its GitHub and drop the binary in `~/.local/bin/`.

**Verify:** `which rg fdfind fzf lazygit` (or `which fd` on macOS) all resolve. Reopen nvim and confirm the picker (`<leader>ff`) works.

---

## 5. LazyVim's pinned `refactoring.nvim` spec is missing the `async.nvim` dependency

**Symptom:** On nvim open: `Failed to run 'config' for refactoring.nvim ... module 'async' not found`.

**Root cause:** `refactoring.nvim` moved its async impl to `lewis6991/async.nvim`, but the (older) LazyVim spec for the refactoring extra only declares `plenary.nvim` as a dep. If the lazy-lock.json has not been refreshed since that upstream change, the dependency is missing locally.

**Fix:** Add a per-user override in `~/.dotfiles/nvim/lua/plugins/refactoring.lua` that declares the missing dep:

```lua
return {
  {
    "ThePrimeagen/refactoring.nvim",
    dependencies = { "lewis6991/async.nvim" },
  },
}
```

Then `:Lazy sync` (or restart nvim). This file is already in the dotfiles repo on this machine — preserve it.

**Verify:** Opening any source file no longer prints the `module 'async' not found` error.

---

## 6. Copilot requires a very recent Node.js

**Symptom:** `[Copilot.lua] Node.js version XX or newer required but found YY.YY.YY` in `:messages` or as a startup notification. Copilot LSP exits with code 24.

**Root cause:** Copilot's LSP binary needs a recent Node (currently ≥22.13 at the time these notes were written; this floor moves over time). Distro Node is usually old (Debian bookworm ships Node 18); even older Node 22.x point releases don't satisfy the floor.

**Fix approach:**
- macOS: `brew install node@22` (or whatever current LTS satisfies the floor) and ensure it's on PATH ahead of any older Node.
- Linux: download the latest 22.x (or current LTS) tarball from `https://nodejs.org/dist/latest-v22.x/`, extract into `~/.local/node22/`, symlink `node`, `npm`, `npx` into `~/.local/bin/`.
- Check the exact required floor against the LSP log (`~/.local/state/nvim/lsp.log`) — the error message tells you what version Copilot needs right now.

**Verify:** Open nvim and check `:messages`. Copilot should report a status (Online/Offline due to auth) rather than a node version error.

---

## 7. Language toolchains needed by Mason-installed LSP servers

**Symptom:** On nvim startup, errors appear and "resolve themselves." `:Mason` shows packages stuck in install-loops. `:checkhealth` reports missing language servers. LSP servers fail to attach to buffers.

**Root cause:** Mason installs many LSP servers by *running the language's own toolchain* (e.g. `go install` for gopls, `gem install` for ruby-lsp, `cargo install` for some Rust tools). If the toolchain is absent or too old, Mason silently fails on each startup, retries next time, and the user sees recurring transient errors.

The LazyVim extras enabled in `nvim/lazyvim.json` on this machine include: `clangd`, `docker`, `go`, `json`, `markdown`, `ruby`, `rust`, `toml`, `typescript`, plus linting/formatting. Each language extra implicitly requires its toolchain.

**Fix approach** — for each language extra enabled, confirm the toolchain is present and modern enough:

- **Go**: Check `go version`. gopls' `go.mod` requires increasingly modern Go (currently ≥1.21, sometimes pulling 1.26+ via Go's `toolchain` directive). If too old, install a current Go from `https://go.dev/dl/` into `~/.local/go/`, symlink `go` and `gofmt` into `~/.local/bin/`. Don't rely on the distro `golang-go` package.
- **Ruby**: Check `ruby --version` and `gem --version`. If absent, install via the OS package manager (`apt install ruby ruby-dev`, `brew install ruby`). Bookworm's Ruby 3.1 is fine for current ruby-lsp.
- **Rust**: Check `cargo --version`. If absent, install via `rustup` (`curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`). Note: `rust-analyzer` itself ships as a static binary via Mason — it does NOT need Rust installed — but some Rust formatters do.
- **C/C++**: `clangd` ships as a static binary from Mason; needs nothing on the host. `gcc` is usually preinstalled on Linux.
- **TypeScript/JavaScript**: `vtsls` ships as a npm-installed binary; needs Node (covered in §6).

After installing each missing toolchain, run a sequential Mason install for the packages that were failing — see §9 for the right way to do this in headless mode.

**Verify:** `:Mason` shows packages green/installed, no install loops. `:LspInfo` in a buffer of each language type shows the server attached.

---

## 8. Disk space exhaustion silently breaks Mason installs

**Symptom:** Mason package installs fail with `No space left on device`, `compile: writing output: ...`, `mkdir: ...`, or wget exit code 3 from clangd's release download. These look like network or build errors but are actually disk-full.

**Root cause:** Devboxes often have small root partitions (~10GB). Installing modern toolchains (Rust ~1.4GB, Go ~270MB, Node ~200MB) plus Mason packages and Go module caches can fill the disk. When `/tmp` and `~/.local/share` are on the same partition (typical), Mason builds quietly fail mid-stream.

**Fix approach:**
- Check disk usage *first* before any large toolchain install (`df -h ~`).
- If tight, free space before installing:
  - `apt clean` (Linux) or `brew cleanup` (macOS) recovers package-manager caches.
  - `go clean -modcache` reclaims the Go module cache (`~/go/pkg/mod`) — often hundreds of MB.
  - `rustup component remove rust-docs` removes Rust's offline docs (~700MB) — generally not needed on a devbox.
  - Clear `~/.cache` if very stale.
- Re-run failed Mason installs once you have at least 1-2GB free.

**Verify:** `df -h ~` shows at least a few hundred MB free at the end of all installs.

---

## 9. Mason installs need real time to complete, headlessly

**Symptom:** Running `nvim --headless -c 'MasonInstall ...' -c 'qa'` prints `Neovim is exiting while packages are still installing. Installation was aborted.`

**Root cause:** Mason installs are async; `qa` fires before the install dispatchers finish. The packages re-attempt on each nvim startup, which is exactly the "errors that resolve themselves" the user reports.

**Fix approach:** When installing Mason packages headlessly, use the Lua API with a synchronous `vim.wait` per package:

```lua
-- Pseudocode skeleton
local registry = require("mason-registry")
registry.refresh()
vim.wait(10000, function() return #registry.get_all_package_names() > 0 end, 200)
for _, name in ipairs({ "gopls", "ruby-lsp", "clangd", "codelldb", ... }) do
  local p = registry.get_package(name)
  if not p:is_installed() then
    local handle = p:install()
    vim.wait(360000, function() return p:is_installed() or handle:is_closed() end, 500)
    -- log whether it actually installed (handle closing != success)
  end
end
vim.cmd("qa!")
```

Important nuances:
- A handle can close without the package being installed (e.g. disk full, missing toolchain). Always check `p:is_installed()` after the wait, not just `handle:is_closed()`.
- Capture `stderr` from the install handle to diagnose failures — most failures are toolchain-version or disk-space issues, not bugs.
- Install sequentially, not in parallel — parallel installs compete for disk and network and you lose the ability to know which one failed.
- Give each package up to several minutes (gopls and codelldb are large).

---

## 10. Verifying the whole stack at the end

After applying any subset of the above, do these end-to-end checks:

1. `nvim --headless -c 'qa' 2>&1` — should produce zero output (no errors, no warnings).
2. `nvim --headless <some-source-file> -c 'sleep 3' -c 'qa' 2>&1` — should produce zero output. Re-test for each language type the user edits (a `.go`, `.rb`, `.rs`, `.ts`, etc.).
3. `:checkhealth` — review the remaining errors. Most that remain on a clean install are acceptable:
   - Image-rendering tools (`magick`, `gs`, `tectonic`, `mmdc`) — only matter for image preview, irrelevant over SSH.
   - Terminal graphics protocol (`kitty`, `wezterm`, `ghostty`) — irrelevant over SSH.
   - Trash CLI (`trash`, `gio`) — only for trash-on-delete.
   - `luarocks` / `hererocks` — only matters if a plugin requires luarocks; LazyVim defaults don't.
4. Open a file in each language and confirm the LSP attaches (`:LspInfo`).

If the user reports any startup errors that "resolve themselves," that's the §7/§8/§9 pattern — a Mason package that can't install. Find which one, find what's missing on the host, install it, and re-run §9.

---

## Per-machine artifacts to expect

After running through this on a Linux devbox, the machine will end up with:
- `~/.local/nvim/` — Neovim binary tree
- `~/.local/bin/{nvim,tree-sitter,lazygit,node,npm,npx,go,gofmt,cargo,rustc}` — symlinks/binaries
- `~/.local/go/` — Go toolchain
- `~/.local/node<XX>/` — Node toolchain
- `~/.rustup/`, `~/.cargo/` — Rust toolchain (rustup-managed)
- `~/.local/share/nvim/mason/` — Mason packages and binaries

On macOS, most of the above are replaced by Homebrew-managed copies, but the Mason layout is the same.

Nothing here needs to be checked into the dotfiles repo. The `refactoring.lua` override (§5) is the only repo-tracked artifact from these fixes — and it's already committed (or pending commit) in `nvim/lua/plugins/`.
