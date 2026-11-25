#!/usr/bin/env bash
# ==============================================================================
#  Windows 11 Dark Green Session Enforcer (125% Scale Default) — Made by Muheeb
# ==============================================================================
INSTALL_DIR="$HOME/.local/share/win11-muheeb"
WALL_DARK="$INSTALL_DIR/wallpapers/win11-muheeb-dark.png"
SETTINGS_JSON="$HOME/.config/win11-muheeb/settings.json"

# 1. Stop separate Linux Wi-Fi / Bluetooth tray icons (managed inside Win+A Quick Settings)
pkill -f nm-applet >/dev/null 2>&1 || true
pkill -f blueman-applet >/dev/null 2>&1 || true
pkill -f blueman-tray >/dev/null 2>&1 || true

# Read user's chosen scale percentage (defaults to 125% -> 120 DPI)
DPI_VAL=$(python3 - <<'PY'
import json, os
p = os.path.expanduser("~/.config/win11-muheeb/settings.json")
scale = 125
if os.path.isfile(p):
    try:
        scale = int(json.load(open(p)).get("scale_pct", 125))
    except Exception:
        pass
print(max(96, min(168, int(round(96 * scale / 100.0)))))
PY
)

# 2. Enforce Windows 11 125% (120 DPI) theme, icons, cursors & fonts
xfconf-query -c xsettings -p /Net/ThemeName -n -t string -s "Win11-Muheeb-Green-Dark" 2>/dev/null || true
xfconf-query -c xsettings -p /Net/IconThemeName -n -t string -s "Win11-green-dark" 2>/dev/null || true
xfconf-query -c xsettings -p /Gtk/CursorThemeName -n -t string -s "Win11-Cursors-Dark" 2>/dev/null || true
xfconf-query -c xsettings -p /Gtk/CursorThemeSize -n -t int -s 28 2>/dev/null || true
xfconf-query -c xsettings -p /Gtk/FontName -n -t string -s "Inter 10.5" 2>/dev/null || true
xfconf-query -c xsettings -p /Xft/DPI -n -t int -s "$DPI_VAL" 2>/dev/null || true
xfconf-query -c xfwm4 -p /general/theme -n -t string -s "Win11-Muheeb-Green-Dark" 2>/dev/null || true

gsettings set org.gnome.desktop.interface gtk-theme 'Win11-Muheeb-Green-Dark' 2>/dev/null || true
gsettings set org.gnome.desktop.interface icon-theme 'Win11-green-dark' 2>/dev/null || true
gsettings set org.gnome.desktop.interface cursor-theme 'Win11-Cursors-Dark' 2>/dev/null || true
gsettings set org.gnome.desktop.interface cursor-size 28 2>/dev/null || true
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark' 2>/dev/null || true
gsettings set org.gnome.desktop.interface font-name 'Inter 10.5' 2>/dev/null || true

# 3. Ensure Wallpaper stays locked to Win11 Dark Green (Made by Muheeb)
if [ -f "$WALL_DARK" ]; then
    for prop in $(xfconf-query -c xfce4-desktop -l 2>/dev/null | grep -E '/last-image$|/image-path$'); do
        xfconf-query -c xfce4-desktop -p "$prop" -n -t string -s "$WALL_DARK" 2>/dev/null || true
    done
fi

# 4. Ensure Windows Key solo tap triggers <Primary>Escape -> Windows 11 Start Menu
if command -v xcape >/dev/null 2>&1; then
    pkill -x xcape >/dev/null 2>&1 || true
    xcape -e 'Super_L=Control_L|Escape;Super_R=Control_L|Escape' >/dev/null 2>&1 &
fi
