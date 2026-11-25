#!/usr/bin/env bash
# ==============================================================================
#  One-Command Public GitHub Publisher with Full SEO Metadata — Made by Muheeb
# ==============================================================================
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

REPO_NAME="${1:-kali-windows-11-dark-green-theme}"
DESCRIPTION="Windows 11 Pro (Dark Green Edition) Theme for Kali Linux XFCE — Complete Centered Taskbar, Start Menu, In-Panel Wi-Fi & Bluetooth Quick Settings, Notification Center, Explorer & Shortcuts. Made by Muheeb."
HOMEPAGE="https://muheebbinnadeem.cv"

export PATH="$HOME/.local/bin:$PATH"
if ! command -v gh >/dev/null 2>&1; then
    echo "[*] Downloading official GitHub CLI (gh) to ~/.local/bin..."
    mkdir -p "$HOME/.local/bin"
    GH_URL=$(curl -fsSL https://api.github.com/repos/cli/cli/releases/latest | python3 -c "import sys,json; d=json.load(sys.stdin); print(next(a['browser_download_url'] for a in d['assets'] if 'linux_amd64.tar.gz' in a['name']))")
    curl -fsSL "$GH_URL" | tar -xz -C /tmp
    cp -f /tmp/gh_*_linux_amd64/bin/gh "$HOME/.local/bin/gh"
    chmod +x "$HOME/.local/bin/gh"
fi

if ! gh auth status >/dev/null 2>&1; then
    echo "=================================================================="
    echo "  GitHub Login Required (One-Time Browser Authentication)"
    echo "=================================================================="
    gh auth login --git-protocol https --web
fi

if git remote get-url origin >/dev/null 2>&1; then
    echo "[*] Pushing latest commits to existing origin..."
    git push -u origin main
else
    echo "[*] Creating PUBLIC GitHub repository '$REPO_NAME' and pushing..."
    gh repo create "$REPO_NAME" \
        --public \
        --source=. \
        --remote=origin \
        --description "$DESCRIPTION" \
        --homepage "$HOMEPAGE" \
        --push
fi

echo "[*] Applying GitHub SEO Topics..."
gh repo edit \
    --description "$DESCRIPTION" \
    --homepage "$HOMEPAGE" \
    --add-topic "kali-linux" \
    --add-topic "windows-11" \
    --add-topic "windows-11-theme" \
    --add-topic "xfce-theme" \
    --add-topic "kali-undercover" \
    --add-topic "linux-customization" \
    --add-topic "gtk-theme" \
    --add-topic "dark-green-theme" \
    --add-topic "thunar" \
    --add-topic "unixporn" \
    --add-topic "dotfiles" \
    --add-topic "muheeb" || true

REPO_URL="$(gh repo view --json url -q .url 2>/dev/null || git remote get-url origin)"
echo "=================================================================="
echo "  ✓ Public GitHub Repository Live: $REPO_URL"
echo "=================================================================="
