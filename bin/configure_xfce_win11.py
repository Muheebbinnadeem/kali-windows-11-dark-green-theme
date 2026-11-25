#!/usr/bin/env python3
"""
Configure Kali Linux XFCE 4.20 to exact original 96-DPI Windows 11 Dark Green specifications:
  - Always boots into Windows 11 Dark Green ('Made by Muheeb') via ~/.config/autostart & GTK settings.ini
  - Hides duplicate Linux nm-applet & blueman tray icons (managed directly inside Win+A Quick Settings)
  - Renders crisp monochrome 16px Fluent tray icons & customizable Search Box via Cairo genmon pills
  - Maps ALL Windows 11 keyboard shortcuts (Win, Win+S, Win+A, Win+N, Win+W, Win+E, Win+I, Win+R,
    Win+X, Win+Shift+S, Print, Win+Print, Win+L, Win+D, Win+Tab, Win+V, Win+Arrows Aero Snap,
    Ctrl+Shift+Esc Task Manager, Alt+F4, Ctrl+Win+Left/Right/D/F4 Virtual Desktops)
"""
import os
import shutil
import subprocess


def sh(cmd):
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def xfset(channel, prop, vtype, val):
    subprocess.run(
        ["xfconf-query", "-c", channel, "-p", prop, "-n", "-t", vtype, "-s", str(val)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def xfreset(channel, prop):
    subprocess.run(
        ["xfconf-query", "-c", channel, "-p", prop, "-r", "-R"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def create_launcher(plugin_id, name, comment, exec_cmd, icon_path):
    ldir = os.path.expanduser(f"~/.config/xfce4/panel/launcher-{plugin_id}")
    os.makedirs(ldir, exist_ok=True)
    dfile = f"win11-{plugin_id}.desktop"
    with open(os.path.join(ldir, dfile), "w", encoding="utf-8") as f:
        f.write(
            f"[Desktop Entry]\n"
            f"Version=1.0\n"
            f"Type=Application\n"
            f"Name={name}\n"
            f"Comment={comment}\n"
            f"Exec={exec_cmd}\n"
            f"Icon={icon_path}\n"
            f"Terminal=false\n"
            f"StartupNotify=false\n"
        )
    xfreset("xfce4-panel", f"/plugins/plugin-{plugin_id}")
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}", "string", "launcher")
    subprocess.run(
        [
            "xfconf-query", "-c", "xfce4-panel", "-p", f"/plugins/plugin-{plugin_id}/items",
            "-n", "-a", "-t", "string", "-s", dfile,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def create_genmon(plugin_id, cmd, period_ms=3000):
    xfreset("xfce4-panel", f"/plugins/plugin-{plugin_id}")
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}", "string", "genmon")
    rc_dir = os.path.expanduser("~/.config/xfce4/panel")
    os.makedirs(rc_dir, exist_ok=True)
    with open(os.path.join(rc_dir, f"genmon-{plugin_id}.rc"), "w", encoding="utf-8") as f:
        f.write(f"Command={cmd}\nUseLabel=0\nText=\nUpdatePeriod={period_ms}\nFont=Inter 9\n")
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}/command", "string", cmd)
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}/use-label", "bool", "false")
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}/update-period", "int", str(period_ms))
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}/enable-single-row", "bool", "true")


def create_separator(plugin_id, expand=True):
    xfreset("xfce4-panel", f"/plugins/plugin-{plugin_id}")
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}", "string", "separator")
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}/expand", "bool", "true" if expand else "false")
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}/style", "int", "0")


def configure_permanent_persistence(install_dir):
    """Ensure theme, icons, cursors, and hidden duplicate applets persist across EVERY reboot."""
    # 1. GTK3 & GTK4 settings.ini + ~/.icons/default/index.theme
    for gdir in ("~/.config/gtk-3.0", "~/.config/gtk-4.0"):
        p = os.path.expanduser(gdir)
        os.makedirs(p, exist_ok=True)
        with open(os.path.join(p, "settings.ini"), "w", encoding="utf-8") as f:
            f.write(
                "[Settings]\n"
                "gtk-theme-name=Win11-Muheeb-Green-Dark\n"
                "gtk-icon-theme-name=Win11-green-dark\n"
                "gtk-cursor-theme-name=Win11-Cursors-Dark\n"
                "gtk-cursor-theme-size=28\n"
                "gtk-font-name=Inter 10.5\n"
                "gtk-application-prefer-dark-theme=1\n"
                "gtk-decoration-layout=icon:minimize,maximize,close\n"
            )

    def_cur = os.path.expanduser("~/.icons/default")
    os.makedirs(def_cur, exist_ok=True)
    with open(os.path.join(def_cur, "index.theme"), "w", encoding="utf-8") as f:
        f.write("[Icon Theme]\nName=Default\nInherits=Win11-Cursors-Dark\n")

    # 2. Autostart overrides: disable separate nm-applet & blueman tray icons, enable Win11 Enforcer
    auto_dir = os.path.expanduser("~/.config/autostart")
    os.makedirs(auto_dir, exist_ok=True)
    for hidden_app in ("nm-applet.desktop", "blueman.desktop"):
        with open(os.path.join(auto_dir, hidden_app), "w", encoding="utf-8") as f:
            f.write(f"[Desktop Entry]\nType=Application\nName={hidden_app}\nHidden=true\n")

    enforcer = os.path.join(install_dir, "bin", "win11_session_enforcer.sh")
    with open(os.path.join(auto_dir, "win11-muheeb-session.desktop"), "w", encoding="utf-8") as f:
        f.write(
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Windows 11 Dark Green Session (Made by Muheeb)\n"
            "Comment=Always apply exact Windows 11 theme, sizing, and shortcuts on login\n"
            f"Exec=bash '{enforcer}'\n"
            "Terminal=false\n"
            "X-GNOME-Autostart-enabled=true\n"
        )

    # Stop active separate nm-applet / blueman-applet icons immediately
    sh("pkill -f nm-applet")
    sh("pkill -f blueman-applet")
    sh("pkill -f blueman-tray")


def configure_all_win11_shortcuts(shell_py):
    """Configure full authentic Windows 11 shortcut suite in XFCE + XFWM4."""
    # Remove raw Super_L binding so Super+<Key> chords never conflict;
    # use xcape -> <Primary>Escape for solo Windows key tap!
    xfreset("xfce4-keyboard-shortcuts", "/commands/custom/Super_L")

    shortcuts = {
        "<Primary>Escape": f"python3 '{shell_py}' start",         # Solo Win key (via xcape) & Ctrl+Esc
        "<Super>s": f"python3 '{shell_py}' search",               # Win + S -> Customizable Search
        "<Super>q": f"python3 '{shell_py}' search",               # Win + Q -> Search
        "<Super>a": f"python3 '{shell_py}' control",              # Win + A -> Wi-Fi/BT Quick Settings
        "<Super>n": f"python3 '{shell_py}' notifications",        # Win + N -> Notifications & Calendar
        "<Super>w": f"python3 '{shell_py}' widgets",              # Win + W -> Widgets Board
        "<Super>e": "thunar",                                     # Win + E -> File Explorer
        "<Super>i": f"python3 '{shell_py}' settings",             # Win + I -> Win11 Settings
        "<Super>r": f"python3 '{shell_py}' run",                  # Win + R -> Win11 Run Dialog
        "<Super>x": f"python3 '{shell_py}' winx",                 # Win + X -> Power User Menu
        "<Super><Shift>s": f"python3 '{shell_py}' snip",          # Win + Shift + S -> Snipping Tool
        "Print": f"python3 '{shell_py}' snip",                    # PrtScn -> Win11 Snipping Tool Bar
        "<Super>Print": f"python3 '{shell_py}' snip-full",        # Win + PrtScn -> Instant Fullscreen Screenshot
        "<Super>l": "xflock4",                                    # Win + L -> Lock Screen
        "<Super>v": "xfce4-popup-clipman",                        # Win + V -> Clipboard History
        "<Super>Tab": "rofi -show window -theme-str 'window {background-color: #111C17; border: 1px solid #34D399; border-radius: 10px; width: 50%;}'",
        "<Primary><Shift>Escape": "xfce4-taskmanager",            # Ctrl + Shift + Esc -> Task Manager
        "<Super>pause": f"python3 '{shell_py}' winver",           # Win + Pause -> About Windows
    }
    for key_combo, cmd in shortcuts.items():
        xfset("xfce4-keyboard-shortcuts", f"/commands/custom/{key_combo}", "string", cmd)

    # XFWM4 Window Management & Windows 11 Aero Snap Shortcuts
    wm_shortcuts = {
        "<Super>d": "show_desktop_key",              # Win + D -> Show Desktop
        "<Super>Up": "maximize_window_key",          # Win + Up -> Maximize
        "<Super>Down": "hide_window_key",            # Win + Down -> Minimize
        "<Super>Left": "tile_left_key",              # Win + Left -> Snap Left Half
        "<Super>Right": "tile_right_key",            # Win + Right -> Snap Right Half
        "<Alt>F4": "close_window_key",               # Alt + F4 -> Close Window
        "<Alt>Tab": "cycle_windows_key",             # Alt + Tab -> Switch Windows
        "<Primary><Super>Right": "right_workspace_key",  # Ctrl + Win + Right -> Next Desktop
        "<Primary><Super>Left": "left_workspace_key",    # Ctrl + Win + Left -> Prev Desktop
        "<Primary><Super>d": "add_workspace_key",        # Ctrl + Win + D -> New Desktop
        "<Primary><Super>F4": "del_workspace_key",       # Ctrl + Win + F4 -> Close Desktop
    }
    for key_combo, action in wm_shortcuts.items():
        xfset("xfce4-keyboard-shortcuts", f"/xfwm4/custom/{key_combo}", "string", action)

    # Start xcape for solo Windows key tap -> <Primary>Escape
    if shutil.which("xcape"):
        sh("pkill -x xcape")
        subprocess.Popen(
            "xcape -e 'Super_L=Control_L|Escape;Super_R=Control_L|Escape'",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )


def main():
    install_dir = os.path.expanduser("~/.local/share/win11-muheeb")
    shell_py = os.path.join(install_dir, "shell", "win11_shell.py")
    pill_py = os.path.join(install_dir, "bin", "win11_panel_pill.py")
    icons_dir = os.path.join(install_dir, "assets", "icons")
    wall_dark = os.path.join(install_dir, "wallpapers", "win11-muheeb-dark.png")

    configure_permanent_persistence(install_dir)

    # 1. Windows 11 Recommended 125% Laptop Scale: 120 DPI, Inter 10.5pt, 28px Cursor
    xfset("xsettings", "/Net/ThemeName", "string", "Win11-Muheeb-Green-Dark")
    xfset("xsettings", "/Net/IconThemeName", "string", "Win11-green-dark")
    xfset("xsettings", "/Gtk/CursorThemeName", "string", "Win11-Cursors-Dark")
    xfset("xsettings", "/Gtk/CursorThemeSize", "int", "30")
    xfset("xsettings", "/Gtk/FontName", "string", "Inter 11")
    xfset("xsettings", "/Gtk/DecorationLayout", "string", "icon:minimize,maximize,close")
    xfset("xsettings", "/Xft/DPI", "int", "122")

    sh("gsettings set org.gnome.desktop.interface gtk-theme 'Win11-Muheeb-Green-Dark'")
    sh("gsettings set org.gnome.desktop.interface icon-theme 'Win11-green-dark'")
    sh("gsettings set org.gnome.desktop.interface cursor-theme 'Win11-Cursors-Dark'")
    sh("gsettings set org.gnome.desktop.interface cursor-size 30")
    sh("gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'")
    sh("gsettings set org.gnome.desktop.interface font-name 'Inter 11'")
    sh("gsettings set org.gnome.desktop.interface text-scaling-factor 1.20")

    xfset("xfwm4", "/general/theme", "string", "Win11-Muheeb-Green-Dark")
    xfset("xfwm4", "/general/button_layout", "string", "O|HMC")
    xfset("xfwm4", "/general/title_alignment", "string", "left")
    xfset("xfwm4", "/general/title_font", "string", "Inter Semi-Bold 10.5")
    xfset("xfwm4", "/general/use_compositing", "bool", "true")
    xfset("xfwm4", "/general/show_popup_shadow", "bool", "false")
    xfset("xfwm4", "/general/show_dock_shadow", "bool", "false")
    xfset("xfwm4", "/general/tile_on_move", "bool", "true")

    # 2. Wallpaper & 125% Windows 11 Desktop Icon Size (58px icons, 10.5pt label)
    for p in subprocess.run(["xfconf-query", "-c", "xfce4-desktop", "-l"], capture_output=True, text=True).stdout.splitlines():
        if p.endswith("/last-image") or p.endswith("/image-path"):
            xfset("xfce4-desktop", p, "string", wall_dark)
        elif p.endswith("/image-style"):
            xfset("xfce4-desktop", p, "int", "5")

    xfset("xfce4-desktop", "/backdrop/screen0/monitoreDP-1/workspace0/last-image", "string", wall_dark)
    xfset("xfce4-desktop", "/backdrop/screen0/monitoreDP-1/workspace0/image-style", "int", "5")
    xfset("xfce4-desktop", "/desktop-icons/icon-size", "int", "58")
    xfset("xfce4-desktop", "/desktop-icons/font-size", "double", "10.5")
    xfset("xfce4-desktop", "/desktop-icons/use-custom-font-size", "bool", "true")

    # 3. Thunar File Explorer (125%+ Spacious Folders & Sidebar)
    xfset("thunar", "/last-location-bar", "string", "ThunarLocationEntry")
    xfset("thunar", "/last-side-pane", "string", "THUNAR_SIDEPANE_TYPE_SHORTCUTS")
    xfset("thunar", "/last-separator-position", "int", "260")
    xfset("thunar", "/last-icon-view-zoom-level", "string", "THUNAR_ZOOM_LEVEL_150_PERCENT")
    xfset("thunar", "/last-statusbar-visible", "bool", "true")
    xfset("thunar", "/last-menubar-visible", "bool", "false")
    xfset("thunar", "/misc-symbolic-icons-in-toolbar", "bool", "true")
    xfset(
        "thunar", "/last-toolbar-items", "string",
        "back:1,forward:1,open-parent:1,reload:1,open-home:1,new-tab:1,location-bar:1,search:1,view-as-icons:1,view-as-detailed-list:1,toggle-split-view:1,menu:1",
    )

    muheeb_dir = os.path.join(install_dir, "Made-by-Muheeb")
    os.makedirs(muheeb_dir, exist_ok=True)
    bm_file = os.path.expanduser("~/.config/gtk-3.0/bookmarks")
    existing_bm = []
    if os.path.isfile(bm_file):
        existing_bm = [
            ln.strip() for ln in open(bm_file, encoding="utf-8").read().splitlines()
            if ln.strip() and "Made-by-Muheeb" not in ln
        ]
    existing_bm.insert(0, "file://" + muheeb_dir.replace(" ", "%20") + " ★ Made by Muheeb")
    with open(bm_file, "w", encoding="utf-8") as f:
        f.write("\n".join(existing_bm) + "\n")

    # 4. Notifications & Complete Windows 11 Shortcut Suite
    xfset("xfce4-notifyd", "/notify-location", "uint", "3")
    configure_all_win11_shortcuts(shell_py)

    # 5. Launch Native Windows 11 Dock Taskbar (replaces xfce4-panel cleanly: zero '⋮⋮' handles, merged running apps!)
    sh("xfce4-panel -q")
    sh("pkill -f win11_taskbar.py")
    taskbar_py = os.path.join(install_dir, "shell", "win11_taskbar.py")
    subprocess.Popen(
        f"nohup python3 '{taskbar_py}' >/dev/null 2>&1 &",
        shell=True,
        start_new_session=True,
    )
    sh("xfdesktop --reload")
    sh("thunar -q")
    print("Configured Permanent 125% Windows 11 Dark Green Desktop with Native Win11 Dock Taskbar (Made by Muheeb).")


if __name__ == "__main__":
    main()
