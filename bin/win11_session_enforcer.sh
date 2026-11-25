#!/usr/bin/env bash
# ==============================================================================
#  Windows 11 Dark Green Session Enforcer — Made by Muheeb
#  Runs automatically at every login so Kali ALWAYS opens in exact Win11 mode:
#   - Kills duplicate nm-applet / blueman tray applets (managed inside Quick Settings)
#   - Enforces 96-DPI original Windows 11 font/icon/cursor/window theme & wallpaper
#   - Starts xcape so solo Windows key tap opens Win11 Start Menu cleanly
# ==============================================================================
INSTALL_DIR="$HOME/.local/share/win11-muheeb"
WALL_DARK="$INSTALL_DIR/wallpapers/win11-muheeb-dark.png"

# 1. Stop separate Linux Wi-Fi / Bluetooth tray icons (managed inside Win+A Quick Settings)
pkill -f nm-applet >/dev/null 2>&1 || true
pkill -f blueman-applet >/dev/null 2>&1 || true
pkill -f blueman-tray >/dev/null 2>&1 || true

# 2. Enforce exact Windows 11 96-DPI theme, icons, cursors & fonts
xfconf-query -c xsettings -p /Net/ThemeName -n -t string -s "Win11-Muheeb-Green-Dark" 2>/dev/null || true
xfconf-query -c xsettings -p /Net/IconThemeName -n -t string -s "Win11-green-dark" 2>/dev/null || true
xfconf-query -c xsettings -p /Gtk/CursorThemeName -n -t string -s "Win11-Cursors-Dark" 2>/dev/null || true
xfconf-query -c xsettings -p /Gtk/CursorThemeSize -n -t int -s 24 2>/dev/null || true
xfconf-query -c xsettings -p /Gtk/FontName -n -t string -s "Inter 9.5" 2>/dev/null || true
xfconf-query -c xsettings -p /Xft/DPI -n -t int -s 96 2>/dev/null || true
xfconf-query -c xfwm4 -p /general/theme -n -t string -s "Win11-Muheeb-Green-Dark" 2>/dev/null || true

gsettings set org.gnome.desktop.interface gtk-theme 'Win11-Muheeb-Green-Dark' 2>/dev/null || true
gsettings set org.gnome.desktop.interface icon-theme 'Win11-green-dark' 2>/dev/null || true
gsettings set org.gnome.desktop.interface cursor-theme 'Win11-Cursors-Dark' 2>/dev/null || true
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark' 2>/dev/null || true
gsettings set org.gnome.desktop.interface font-name 'Inter 9.5' 2>/dev/null || true

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
