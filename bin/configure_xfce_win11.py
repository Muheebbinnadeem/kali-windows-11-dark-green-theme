#!/usr/bin/env python3
"""
Configure Kali Linux XFCE 4.20 to look & behave like an exact Windows 11 Dark Green Desktop
('Made by Muheeb' Edition):
  - 48px Bottom Taskbar with Left Widgets, Centered Start/Search/TaskView/Apps/Tasklist,
    and Right Tray + Unified Quick Settings Control Bar + Two-Line Clock/Date/Notifications + Show Desktop
  - Thunar File Explorer configured with Windows 11 Navigation/Address Bar + 'Made by Muheeb' Quick Access & Context Menu
  - XFWM4 Windows 11 Dark Green Titlebars (Left-aligned title, crisp square Win11 caption buttons)
  - Windows Key (Super_L) bound to Windows 11 Start Menu, Super+A to Control Bar, Super+N to Notification Center, Super+W to Widgets
  - Desktop Wallpaper & Icons sized to authentic Windows 11 proportions
"""
import os
import shutil
import subprocess
import sys


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
    full = os.path.join(ldir, dfile)
    with open(full, "w", encoding="utf-8") as f:
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
            "xfconf-query",
            "-c",
            "xfce4-panel",
            "-p",
            f"/plugins/plugin-{plugin_id}/items",
            "-n",
            "-a",
            "-t",
            "string",
            "-s",
            dfile,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def create_genmon(plugin_id, cmd, period_ms=3000):
    xfreset("xfce4-panel", f"/plugins/plugin-{plugin_id}")
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}", "string", "genmon")
    rc_dir = os.path.expanduser("~/.config/xfce4/panel")
    os.makedirs(rc_dir, exist_ok=True)
    rc_path = os.path.join(rc_dir, f"genmon-{plugin_id}.rc")
    with open(rc_path, "w", encoding="utf-8") as f:
        f.write(
            f"Command={cmd}\n"
            f"UseLabel=0\n"
            f"Text=(win11)\n"
            f"UpdatePeriod={period_ms}\n"
            f"Font=Inter 9\n"
        )
    # Also set xfconf properties used by newer xfce4-genmon-plugin (>= 4.18)
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}/command", "string", cmd)
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}/use-label", "bool", "false")
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}/update-period", "int", str(period_ms))
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}/enable-single-row", "bool", "false")
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}/font", "string", "Inter 9")


def create_separator(plugin_id, expand=True):
    xfreset("xfce4-panel", f"/plugins/plugin-{plugin_id}")
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}", "string", "separator")
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}/expand", "bool", "true" if expand else "false")
    xfset("xfce4-panel", f"/plugins/plugin-{plugin_id}/style", "int", "0")  # transparent


def main():
    install_dir = os.path.expanduser("~/.local/share/win11-muheeb")
    shell_py = os.path.join(install_dir, "shell", "win11_shell.py")
    pill_py = os.path.join(install_dir, "bin", "win11_panel_pill.py")
    icons_dir = os.path.join(install_dir, "assets", "icons")
    wall_dark = os.path.join(install_dir, "wallpapers", "win11-muheeb-dark.png")

    # 1. GTK, Icons, Cursors, Fonts & XFWM4 Window Manager (Exact Win11 Proportions)
    xfset("xsettings", "/Net/ThemeName", "string", "Win11-Muheeb-Green-Dark")
    xfset("xsettings", "/Net/IconThemeName", "string", "Win11-green-dark")
    xfset("xsettings", "/Gtk/CursorThemeName", "string", "Win11-Cursors-Dark")
    xfset("xsettings", "/Gtk/CursorThemeSize", "int", "24")
    xfset("xsettings", "/Gtk/FontName", "string", "Inter 10")
    xfset("xsettings", "/Gtk/DecorationLayout", "string", "icon:minimize,maximize,close")
    xfset("xsettings", "/Xft/DPI", "int", "98")

    sh("gsettings set org.gnome.desktop.interface gtk-theme 'Win11-Muheeb-Green-Dark'")
    sh("gsettings set org.gnome.desktop.interface icon-theme 'Win11-green-dark'")
    sh("gsettings set org.gnome.desktop.interface cursor-theme 'Win11-Cursors-Dark'")
    sh("gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'")
    sh("gsettings set org.gnome.desktop.interface font-name 'Inter 10'")

    xfset("xfwm4", "/general/theme", "string", "Win11-Muheeb-Green-Dark")
    xfset("xfwm4", "/general/button_layout", "string", "O|HMC")
    xfset("xfwm4", "/general/title_alignment", "string", "left")
    xfset("xfwm4", "/general/title_font", "string", "Inter Semi-Bold 9.5")
    xfset("xfwm4", "/general/use_compositing", "bool", "true")
    xfset("xfwm4", "/general/show_popup_shadow", "bool", "false")
    xfset("xfwm4", "/general/show_dock_shadow", "bool", "false")
    xfset("xfwm4", "/general/frame_border_top", "int", "0")

    # 2. Desktop Wallpaper (apply to ALL monitors & workspaces) + Win11 Desktop Icon Sizing
    props = subprocess.run(
        ["xfconf-query", "-c", "xfce4-desktop", "-l"],
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    for p in props:
        if p.endswith("/last-image") or p.endswith("/image-path"):
            xfset("xfce4-desktop", p, "string", wall_dark)
        elif p.endswith("/image-style"):
            xfset("xfce4-desktop", p, "int", "5")  # Zoomed/Fill

    # Ensure standard monitor paths exist too
    xfset("xfce4-desktop", "/backdrop/screen0/monitoreDP-1/workspace0/last-image", "string", wall_dark)
    xfset("xfce4-desktop", "/backdrop/screen0/monitoreDP-1/workspace0/image-style", "int", "5")
    xfset("xfce4-desktop", "/desktop-icons/icon-size", "int", "48")
    xfset("xfce4-desktop", "/desktop-icons/font-size", "double", "9.5")
    xfset("xfce4-desktop", "/desktop-icons/use-custom-font-size", "bool", "true")
    xfset("xfce4-desktop", "/desktop-icons/file-icons/show-home", "bool", "true")
    xfset("xfce4-desktop", "/desktop-icons/file-icons/show-trash", "bool", "true")
    xfset("xfce4-desktop", "/desktop-icons/file-icons/show-filesystem", "bool", "true")

    # Create Desktop shortcut for 'Windows 11 — Made by Muheeb'
    desk_dir = os.path.expanduser("~/Desktop")
    if os.path.isdir(desk_dir):
        about_dt = os.path.join(desk_dir, "Win11-Made-by-Muheeb.desktop")
        with open(about_dt, "w", encoding="utf-8") as f:
            f.write(
                f"[Desktop Entry]\n"
                f"Version=1.0\n"
                f"Type=Application\n"
                f"Name=Win11 • Made by Muheeb\n"
                f"Comment=Windows 11 Dark Green Theme Info & Settings\n"
                f"Exec=python3 '{shell_py}' winver\n"
                f"Icon={os.path.join(icons_dir, 'win11-start.svg')}\n"
                f"Terminal=false\n"
            )
        os.chmod(about_dt, 0o755)
        sh(f"gio set '{about_dt}' metadata::trusted true")

    # 3. Thunar File Explorer — Exact Windows 11 Toolbar, Address Bar & 'Made by Muheeb' Places
    xfset("thunar", "/last-location-bar", "string", "ThunarLocationEntry")
    xfset("thunar", "/last-side-pane", "string", "THUNAR_SIDEPANE_TYPE_SHORTCUTS")
    xfset("thunar", "/last-separator-position", "int", "225")
    xfset("thunar", "/last-statusbar-visible", "bool", "true")
    xfset("thunar", "/last-menubar-visible", "bool", "false")
    xfset("thunar", "/misc-symbolic-icons-in-toolbar", "bool", "true")
    xfset(
        "thunar",
        "/last-toolbar-items",
        "string",
        "back:1,forward:1,open-parent:1,reload:1,open-home:1,new-tab:1,location-bar:1,search:1,view-as-icons:1,view-as-detailed-list:1,toggle-split-view:1,menu:1",
    )

    # Create 'Made by Muheeb' showcase folder & bookmark in Explorer Quick Access
    muheeb_dir = os.path.join(install_dir, "Made-by-Muheeb")
    os.makedirs(muheeb_dir, exist_ok=True)
    with open(os.path.join(muheeb_dir, "README - Made by Muheeb.txt"), "w", encoding="utf-8") as f:
        f.write(
            "========================================================\n"
            "  Windows 11 Pro (Dark Green Edition) — Made by Muheeb\n"
            "========================================================\n"
            "Custom Kali Linux Desktop Experience featuring:\n"
            "  • Centered 48px Windows 11 Dark Green Acrylic Taskbar\n"
            "  • Authentic Windows 11 Start Menu, Search & Widgets\n"
            "  • Quick Settings Control Bar (Wi-Fi, Sound, Brightness)\n"
            "  • Two-Card Notification Center & Interactive Calendar\n"
            "  • Windows 11 File Explorer Toolbar & Navigation Bar\n"
        )

    bm_file = os.path.expanduser("~/.config/gtk-3.0/bookmarks")
    os.makedirs(os.path.dirname(bm_file), exist_ok=True)
    existing_bm = []
    if os.path.isfile(bm_file):
        existing_bm = [
            ln.strip()
            for ln in open(bm_file, encoding="utf-8").read().splitlines()
            if ln.strip() and "Made-by-Muheeb" not in ln
        ]
    muheeb_uri = "file://" + muheeb_dir.replace(" ", "%20") + " ★ Made by Muheeb"
    existing_bm.insert(0, muheeb_uri)
    with open(bm_file, "w", encoding="utf-8") as f:
        f.write("\n".join(existing_bm) + "\n")

    # 4. Notifications (Bottom-Right like Windows 11 Toast Notifications)
    xfset("xfce4-notifyd", "/notify-location", "uint", "3")  # 3 = Bottom right
    xfset("xfce4-notifyd", "/theme", "string", "Default")
    xfset("xfce4-notifyd", "/initial-opacity", "double", "0.96")

    # 5. Windows 11 Keyboard Shortcuts (Super = Start, Super+A = Control Bar, Super+N = Notifications, Super+W = Widgets, Super+E = Explorer)
    xfset("xfce4-keyboard-shortcuts", "/commands/custom/Super_L", "string", f"python3 '{shell_py}' start")
    xfset("xfce4-keyboard-shortcuts", "/commands/custom/<Super>s", "string", f"python3 '{shell_py}' search")
    xfset("xfce4-keyboard-shortcuts", "/commands/custom/<Super>a", "string", f"python3 '{shell_py}' control")
    xfset("xfce4-keyboard-shortcuts", "/commands/custom/<Super>n", "string", f"python3 '{shell_py}' notifications")
    xfset("xfce4-keyboard-shortcuts", "/commands/custom/<Super>w", "string", f"python3 '{shell_py}' widgets")
    xfset("xfce4-keyboard-shortcuts", "/commands/custom/<Super>e", "string", "thunar")

    # 6. Exact Windows 11 Bottom Taskbar (xfce4-panel: 48px, Full Width, Always Visible, Centered Icons!)
    sh("xfce4-panel -q")

    # Left: [200: Widgets] [201: Expanding Separator]
    # Center: [202_start: Start] [202: Search Pill] [203: Task View] [204: Explorer] [205: Terminal] [206: Browser] [207: Code] [208: Settings] [209: Win11 Tasklist]
    # Right: [215: Expanding Separator] [210: Systray] [211: ENG/US] [212: Unified Control Bar Pill] [213: Two-Line Clock+Date+Bell Pill] [214: Show Desktop Sliver]

    create_genmon(200, f"python3 '{pill_py}' widgets", 5000)
    create_separator(201, expand=True)

    create_launcher(
        220,
        "Start",
        "Windows 11 Start Menu • Made by Muheeb",
        f"python3 '{shell_py}' start",
        os.path.join(icons_dir, "win11-start.svg"),
    )
    create_genmon(202, f"python3 '{pill_py}' search", 60000)
    create_launcher(
        203,
        "Task View",
        "Windows 11 Task View",
        "rofi -show window -theme-str 'window {background-color: #111C17; border: 1px solid #34D399; border-radius: 12px; width: 52%;}'",
        os.path.join(icons_dir, "win11-taskview.svg"),
    )
    create_launcher(
        204,
        "File Explorer",
        "File Explorer • Made by Muheeb",
        "thunar",
        os.path.join(icons_dir, "win11-explorer.svg"),
    )
    create_launcher(
        205,
        "Windows Terminal",
        "Kali Terminal",
        "sh -c 'qterminal || xfce4-terminal || x-terminal-emulator'",
        os.path.join(icons_dir, "win11-terminal.svg"),
    )
    browser_cmd = "brave-browser" if shutil.which("brave-browser") else "firefox"
    browser_icon = "brave-browser" if shutil.which("brave-browser") else "firefox-esr"
    create_launcher(206, "Web Browser", "Browser", browser_cmd, browser_icon)
    editor_cmd = "code" if shutil.which("code") else "mousepad"
    editor_icon = "code" if shutil.which("code") else "org.xfce.mousepad"
    create_launcher(207, "VS Code", "Code Editor", editor_cmd, editor_icon)
    create_launcher(
        208,
        "Settings",
        "Windows 11 Info & Settings • Made by Muheeb",
        f"python3 '{shell_py}' winver",
        os.path.join(icons_dir, "win11-settings.svg"),
    )

    # Plugin 209: Icon-only Windows 11 Tasklist
    xfreset("xfce4-panel", "/plugins/plugin-209")
    xfset("xfce4-panel", "/plugins/plugin-209", "string", "tasklist")
    xfset("xfce4-panel", "/plugins/plugin-209/show-labels", "bool", "false")
    xfset("xfce4-panel", "/plugins/plugin-209/flat-buttons", "bool", "true")
    xfset("xfce4-panel", "/plugins/plugin-209/show-handle", "bool", "false")
    xfset("xfce4-panel", "/plugins/plugin-209/grouping", "int", "1")
    xfset("xfce4-panel", "/plugins/plugin-209/middle-click", "int", "1")

    create_separator(215, expand=True)

    # Plugin 210: System Tray
    xfreset("xfce4-panel", "/plugins/plugin-210")
    xfset("xfce4-panel", "/plugins/plugin-210", "string", "systray")
    xfset("xfce4-panel", "/plugins/plugin-210/size-max", "int", "20")
    xfset("xfce4-panel", "/plugins/plugin-210/square-icons", "bool", "true")
    xfset("xfce4-panel", "/plugins/plugin-210/symbolic-icons", "bool", "true")

    # Plugin 211: Language Indicator (ENG / US)
    create_genmon(211, f"python3 '{pill_py}' lang", 60000)

    # Plugin 212: Unified Control Bar Button (Wi-Fi + Volume + Battery -> Quick Settings Flyout)
    create_genmon(212, f"python3 '{pill_py}' control", 3000)

    # Plugin 213: Two-line Clock + Date + Notification Bell -> Notification Center & Calendar Flyout
    create_genmon(213, f"python3 '{pill_py}' clock", 10000)

    # Plugin 214: Far-right Show Desktop sliver
    xfreset("xfce4-panel", "/plugins/plugin-214")
    xfset("xfce4-panel", "/plugins/plugin-214", "string", "showdesktop")

    # Panel 1 Geometry: Full-width bottom taskbar, 48px height, locked, no autohide!
    plugin_order = [200, 201, 220, 202, 203, 204, 205, 206, 207, 208, 209, 215, 210, 211, 212, 213, 214]
    subprocess.run(
        ["xfconf-query", "-c", "xfce4-panel", "-p", "/panels", "-n", "-a", "-t", "int", "-s", "1"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    xfset("xfce4-panel", "/panels/dark-mode", "bool", "true")
    xfset("xfce4-panel", "/panels/panel-1/position", "string", "p=8;x=960;y=1056")
    xfset("xfce4-panel", "/panels/panel-1/length", "double", "100")
    xfset("xfce4-panel", "/panels/panel-1/length-adjust", "bool", "true")
    xfset("xfce4-panel", "/panels/panel-1/mode", "int", "0")
    xfset("xfce4-panel", "/panels/panel-1/nrows", "int", "1")
    xfset("xfce4-panel", "/panels/panel-1/size", "int", "48")
    xfset("xfce4-panel", "/panels/panel-1/icon-size", "int", "24")
    xfset("xfce4-panel", "/panels/panel-1/autohide-behavior", "int", "0")
    xfset("xfce4-panel", "/panels/panel-1/position-locked", "bool", "true")
    xfset("xfce4-panel", "/panels/panel-1/background-style", "int", "0")
    xfset("xfce4-panel", "/panels/panel-1/enter-opacity", "int", "100")
    xfset("xfce4-panel", "/panels/panel-1/leave-opacity", "int", "100")

    xfreset("xfce4-panel", "/panels/panel-1/plugin-ids")
    cmd = ["xfconf-query", "-c", "xfce4-panel", "-p", "/panels/panel-1/plugin-ids", "-n", "-a"]
    for pid in plugin_order:
        cmd.extend(["-t", "int", "-s", str(pid)])
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Restart panel & reload Thunar/xfdesktop cleanly
    subprocess.Popen(
        "xfce4-panel -r >/dev/null 2>&1 || xfce4-panel >/dev/null 2>&1 &",
        shell=True,
        start_new_session=True,
    )
    sh("xfdesktop --reload")
    sh("thunar -q")
    print("Configured XFCE Windows 11 Dark Green Desktop (Made by Muheeb).")


if __name__ == "__main__":
    main()
