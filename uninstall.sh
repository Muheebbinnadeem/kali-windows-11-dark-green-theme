#!/usr/bin/env bash
# ==============================================================================
#  Uninstall / Restore Original Kali XFCE Desktop
#  Windows 11 Pro (Dark Green Edition) — Made by Muheeb
# ==============================================================================
set -euo pipefail

INSTALL_DIR="$HOME/.local/share/win11-muheeb"
BACKUP_DIR="$INSTALL_DIR/backup"

echo "[*] Restoring original Kali Linux XFCE desktop configuration..."

# Remove Win11 autostart overrides so original Kali applets return cleanly
rm -f "$HOME/.config/autostart/win11-muheeb-session.desktop" \
      "$HOME/.config/autostart/nm-applet.desktop" \
      "$HOME/.config/autostart/blueman.desktop" \
      "$HOME/.config/gtk-3.0/settings.ini" \
      "$HOME/.config/gtk-4.0/settings.ini" \
      "$HOME/.icons/default/index.theme"

if [ -d "$BACKUP_DIR/xfce4-xfconf" ]; then
    xfce4-panel -q >/dev/null 2>&1 || true
    killall xfconfd >/dev/null 2>&1 || true
    sleep 0.5
    cp -rf "$BACKUP_DIR/xfce4-xfconf/." "$HOME/.config/xfce4/xfconf/xfce-perchannel-xml/"
    if [ -d "$BACKUP_DIR/xfce4-panel-dir" ]; then
        rm -rf "$HOME/.config/xfce4/panel"
        cp -rf "$BACKUP_DIR/xfce4-panel-dir" "$HOME/.config/xfce4/panel"
    fi
fi

if [ -f "$BACKUP_DIR/gtk-3.0/gtk.css" ]; then
    cp -f "$BACKUP_DIR/gtk-3.0/gtk.css" "$HOME/.config/gtk-3.0/gtk.css"
else
    rm -f "$HOME/.config/gtk-3.0/gtk.css"
fi

[ -f "$BACKUP_DIR/gtk-3.0/bookmarks" ] && cp -f "$BACKUP_DIR/gtk-3.0/bookmarks" "$HOME/.config/gtk-3.0/bookmarks"
[ -f "$BACKUP_DIR/Thunar/uca.xml" ] && cp -f "$BACKUP_DIR/Thunar/uca.xml" "$HOME/.config/Thunar/uca.xml"
rm -f "$HOME/Desktop/Win11-Made-by-Muheeb.desktop" "$HOME/.local/bin/winver" "$HOME/.local/bin/win11-muheeb"

for rc in "$HOME/.zshrc" "$HOME/.bashrc"; do
    if [ -f "$rc" ]; then
        sed -i '/# WIN11_MUHEEB_BANNER/,+5d' "$rc" 2>/dev/null || true
    fi
done

if [ -n "${DISPLAY:-}" ]; then
    nohup xfce4-panel >/dev/null 2>&1 &
    nohup nm-applet >/dev/null 2>&1 &
    xfdesktop --reload >/dev/null 2>&1 || true
    thunar -q >/dev/null 2>&1 || true
fi

echo "[✓] Original Kali XFCE configuration restored!"
