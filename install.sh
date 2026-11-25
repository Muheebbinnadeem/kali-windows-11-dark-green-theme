#!/usr/bin/env bash
# ==============================================================================
#  Windows 11 Pro (Dark Green Edition) for Kali Linux — Made by Muheeb
#  One-Command Installer (./install.sh)
# ==============================================================================
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/share/win11-muheeb"
BACKUP_DIR="$INSTALL_DIR/backup"
BIN_DIR="$HOME/.local/bin"

GREEN='\033[1;32m'
EMERALD='\033[38;5;42m'
RESET='\033[0m'

echo -e "${EMERALD}==================================================================${RESET}"
echo -e "${GREEN}  ⊞ Windows 11 Pro (Dark Green Edition) — Made by Muheeb${RESET}"
echo -e "${EMERALD}  Kali Linux XFCE Complete Theme & Shell Installer${RESET}"
echo -e "${EMERALD}==================================================================${RESET}"

# 1. Check / Install minimal required packages if missing on a fresh Kali install
MISSING_PKGS=()
for cmd_pkg in "xfconf-query:xfce4-settings" "python3:python3" "rofi:rofi" "notify-send:libnotify-bin" "xcape:xcape" "xclip:xclip"; do
    cmd="${cmd_pkg%%:*}"
    pkg="${cmd_pkg##*:}"
    if ! command -v "$cmd" >/dev/null 2>&1; then
        MISSING_PKGS+=("$pkg")
    fi
done
if ! python3 -c "import gi, cairo, PIL" >/dev/null 2>&1; then
    MISSING_PKGS+=("python3-gi" "python3-gi-cairo" "gir1.2-gtk-3.0" "python3-pil")
fi

if [ "${#MISSING_PKGS[@]}" -gt 0 ]; then
    echo "[*] Installing missing dependencies: ${MISSING_PKGS[*]}"
    sudo apt-get update -qq && sudo apt-get install -y "${MISSING_PKGS[@]}"
fi

mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$HOME/.themes" "$HOME/.local/share/icons" "$HOME/.config/gtk-3.0" "$HOME/.config/gtk-4.0" "$HOME/.config/Thunar"

# 2. Backup original user configuration (only once so original state is always safe)
if [ ! -f "$BACKUP_DIR/.backed_up" ]; then
    echo "[*] Backing up your current Kali XFCE configuration to $BACKUP_DIR..."
    mkdir -p "$BACKUP_DIR/xfce4-xfconf" "$BACKUP_DIR/gtk-3.0" "$BACKUP_DIR/Thunar"
    cp -rf "$HOME/.config/xfce4/xfconf/xfce-perchannel-xml/." "$BACKUP_DIR/xfce4-xfconf/" 2>/dev/null || true
    cp -rf "$HOME/.config/xfce4/panel" "$BACKUP_DIR/xfce4-panel-dir" 2>/dev/null || true
    [ -f "$HOME/.config/gtk-3.0/gtk.css" ] && cp -f "$HOME/.config/gtk-3.0/gtk.css" "$BACKUP_DIR/gtk-3.0/gtk.css"
    [ -f "$HOME/.config/gtk-3.0/bookmarks" ] && cp -f "$HOME/.config/gtk-3.0/bookmarks" "$BACKUP_DIR/gtk-3.0/bookmarks"
    [ -f "$HOME/.config/Thunar/uca.xml" ] && cp -f "$HOME/.config/Thunar/uca.xml" "$BACKUP_DIR/Thunar/uca.xml"
    date -Iseconds > "$BACKUP_DIR/.backed_up"
fi

# 3. Install Dark Green GTK/XFWM4 Themes, Win11 Green Icons & Win11 Cursors
echo "[*] Installing Windows 11 Dark Green GTK/XFWM4 themes, icons, and cursors..."
rm -rf "$HOME/.themes/Win11-Muheeb-Green-Dark" "$HOME/.themes/Win11-Muheeb-Green-Light"
cp -a "$REPO_DIR/themes/Win11-Muheeb-Green-Dark" "$HOME/.themes/"
cp -a "$REPO_DIR/themes/Win11-Muheeb-Green-Light" "$HOME/.themes/"

rm -rf "$HOME/.local/share/icons/Win11-green" "$HOME/.local/share/icons/Win11-green-dark" \
       "$HOME/.local/share/icons/Win11-Cursors" "$HOME/.local/share/icons/Win11-Cursors-Dark"
cp -a "$REPO_DIR/icons/Win11-green" "$HOME/.local/share/icons/"
cp -a "$REPO_DIR/icons/Win11-green-dark" "$HOME/.local/share/icons/"
cp -a "$REPO_DIR/cursors/Win11-Cursors" "$HOME/.local/share/icons/"
cp -a "$REPO_DIR/cursors/Win11-Cursors-Dark" "$HOME/.local/share/icons/"

# Ensure Kali start/places icons resolve cleanly
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/Win11-green" >/dev/null 2>&1 || true
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/Win11-green-dark" >/dev/null 2>&1 || true

# 4. Install Shell Flyouts, Wallpapers, Assets & Helper Scripts
echo "[*] Installing Windows 11 Shell (Start Menu, Control Bar, Notification Center, Widgets)..."
rm -rf "$INSTALL_DIR/shell" "$INSTALL_DIR/bin" "$INSTALL_DIR/assets" "$INSTALL_DIR/wallpapers" "$INSTALL_DIR/config"
cp -a "$REPO_DIR/shell" "$INSTALL_DIR/"
cp -a "$REPO_DIR/bin" "$INSTALL_DIR/"
cp -a "$REPO_DIR/assets" "$INSTALL_DIR/"
cp -a "$REPO_DIR/wallpapers" "$INSTALL_DIR/"
cp -a "$REPO_DIR/config" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/shell/"*.py "$INSTALL_DIR/bin/"*

# 5. Render GTK3 & GTK4 CSS with Explorer 'Made by Muheeb' vector badge path
BADGE_PATH="$INSTALL_DIR/assets/badges/explorer-muheeb-dark.svg"
sed "s|__EXPLORER_BADGE__|$BADGE_PATH|g" "$REPO_DIR/config/gtk-3.0/win11-muheeb.css.tpl" > "$HOME/.config/gtk-3.0/gtk.css"

# 6. Merge Windows 11 'Made by Muheeb' Context Menu Actions into Thunar uca.xml safely
python3 - <<'PY'
import os, xml.etree.ElementTree as ET

uca_path = os.path.expanduser("~/.config/Thunar/uca.xml")
install_dir = os.path.expanduser("~/.local/share/win11-muheeb")
shell_py = os.path.join(install_dir, "shell", "win11_shell.py")

if os.path.isfile(uca_path):
    try:
        tree = ET.parse(uca_path)
        root = tree.getroot()
    except Exception:
        root = ET.Element("actions")
else:
    root = ET.Element("actions")

# Remove previous win11-muheeb actions before re-adding
for act in list(root.findall("action")):
    uid = act.findtext("unique-id", "")
    if uid.startswith("991100"):
        root.remove(act)

new_actions = [
    {
        "icon": os.path.join(install_dir, "assets", "icons", "win11-terminal.svg"),
        "name": "Open in Windows Terminal",
        "unique-id": "9911001",
        "command": "sh -c 'cd %f && (qterminal || xfce4-terminal || x-terminal-emulator)'",
        "description": "Open current folder in Terminal",
        "directories": True,
    },
    {
        "icon": os.path.join(install_dir, "assets", "icons", "win11-start.svg"),
        "name": "Windows 11 Pro • Made by Muheeb",
        "unique-id": "9911002",
        "command": f"python3 '{shell_py}' winver",
        "description": "About Windows 11 Dark Green Theme — Made by Muheeb",
        "directories": True,
    },
]

for spec in new_actions:
    el = ET.SubElement(root, "action")
    ET.SubElement(el, "icon").text = spec["icon"]
    ET.SubElement(el, "name").text = spec["name"]
    ET.SubElement(el, "submenu").text = ""
    ET.SubElement(el, "unique-id").text = spec["unique-id"]
    ET.SubElement(el, "command").text = spec["command"]
    ET.SubElement(el, "description").text = spec["description"]
    ET.SubElement(el, "range").text = "*"
    ET.SubElement(el, "patterns").text = "*"
    if spec.get("directories"):
        ET.SubElement(el, "directories")

os.makedirs(os.path.dirname(uca_path), exist_ok=True)
ET.ElementTree(root).write(uca_path, encoding="UTF-8", xml_declaration=True)
PY

# 7. Install CLI launchers (winver & win11-muheeb) and Terminal Banner
ln -sf "$INSTALL_DIR/bin/win11-muheeb" "$BIN_DIR/win11-muheeb"
cat > "$BIN_DIR/winver" <<EOF
#!/usr/bin/env bash
exec python3 "$INSTALL_DIR/shell/win11_shell.py" winver "\$@"
EOF
chmod +x "$BIN_DIR/winver" "$INSTALL_DIR/bin/win11-muheeb"

for rc in "$HOME/.zshrc" "$HOME/.bashrc"; do
    if [ -f "$rc" ] && ! grep -q "WIN11_MUHEEB_BANNER" "$rc"; then
        cat >> "$rc" <<'RCEOF'

# WIN11_MUHEEB_BANNER
export PATH="$HOME/.local/bin:$PATH"
if [ -t 1 ]; then
    printf "\033[38;5;42m⊞ Windows 11 Pro (Dark Green)\033[0m • \033[1;32mMade by Muheeb\033[0m\n"
fi
RCEOF
    fi
done

# 8. Apply XFCE4 Panel, XFWM4, Wallpaper, Shortcuts & Explorer Configuration
if [ -n "${DISPLAY:-}" ]; then
    echo "[*] Applying live Windows 11 Dark Green Desktop layout..."
    python3 "$INSTALL_DIR/bin/configure_xfce_win11.py"
    notify-send -i "$INSTALL_DIR/assets/icons/win11-start.svg" \
        "Windows 11 Dark Green • Made by Muheeb" \
        "Theme, Taskbar, Explorer, Control Bar & Notification Center installed!" 2>/dev/null || true
else
    echo "[!] No active X11 DISPLAY detected; run 'win11-muheeb apply' inside your desktop session."
fi

echo -e "${EMERALD}==================================================================${RESET}"
echo -e "${GREEN}  ✓ Installation Complete! — Made by Muheeb${RESET}"
echo -e "  • Start Menu:         Click ⊞ Start or press Super (Windows key)"
echo -e "  • Control Bar:        Click Wi-Fi/Sound/Battery pill (or Super+A)"
echo -e "  • Notification Bar:   Click Clock/Date/Bell pill (or Super+N)"
echo -e "  • Widgets Board:      Click Weather/Muheeb left pill (or Super+W)"
echo -e "  • About Dialog:       Run 'winver' or click 'Win11 • Made by Muheeb'"
echo -e "  • Restore Original:   Run './uninstall.sh' or 'win11-muheeb restore'"
echo -e "${EMERALD}==================================================================${RESET}"
