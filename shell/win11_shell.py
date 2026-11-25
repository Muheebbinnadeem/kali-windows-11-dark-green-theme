#!/usr/bin/env python3
"""
Windows 11 Pro (Dark Green Edition) Complete Shell Suite — Made by Muheeb
Modes:
  - start         : Centered Windows 11 Start Menu (Win / Ctrl+Esc)
  - search        : Customizable Windows 11 Search with Live Taskbar Style Customizer (Win+S)
  - control       : Quick Settings + Full In-Panel Wi-Fi & Bluetooth & Audio Managers (Win+A)
  - notifications : Two-Card Notification Center + Interactive Month Calendar (Win+N)
  - widgets       : Left Windows 11 Widgets Board (Win+W)
  - snip          : Top-Center Windows 11 Snipping Tool Overlay (Win+Shift+S / Print)
  - snip-full     : Instant Windows 11 Fullscreen Screenshot to ~/Pictures/Screenshots + Clipboard (Win+Print)
  - run           : Bottom-Left Windows 11 Run Dialog (Win+R)
  - winx          : Windows 11 Power User Quick Link Menu (Win+X)
  - settings      : Windows 11 Personalization, Wallpaper & Search Settings (Win+I)
  - winver        : About Windows 11 Dialog (Made by Muheeb)
"""
import ast
import calendar
import datetime
import getpass
import json
import operator
import os
import shlex
import signal
import sqlite3
import subprocess
import sys
import time
import urllib.parse

import cairo
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gio, GLib, Gtk, Pango

try:
    import psutil
except ImportError:
    psutil = None

BRAND_AUTHOR = "Made by Muheeb"
BRAND_EDITION = "Windows 11 Pro • Dark Green Edition"
RUNTIME_DIR = os.environ.get("XDG_RUNTIME_DIR", f"/tmp/win11-{os.getuid()}")
os.makedirs(RUNTIME_DIR, exist_ok=True)
STATE_FILE = os.path.join(RUNTIME_DIR, "win11_muheeb_shell.json")
NIGHTLIGHT_STATE = os.path.join(RUNTIME_DIR, "win11_nightlight.on")
SETTINGS_PATH = os.path.expanduser("~/.config/win11-muheeb/settings.json")

SHELL_CSS = b"""
* {
    font-family: "Inter", "Segoe UI", "Noto Sans", sans-serif;
    font-size: 9.5pt;
    outline: none;
}
window.win11-flyout {
    background-color: transparent;
}
.mica-card {
    background-color: rgba(15, 24, 20, 0.97);
    border: 1px solid rgba(52, 211, 153, 0.24);
    border-radius: 10px;
    color: #ECFDF5;
}
.mica-footer {
    background-color: rgba(10, 16, 13, 0.97);
    border-top: 1px solid rgba(52, 211, 153, 0.15);
    border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
}
.search-pill {
    background-color: rgba(25, 40, 33, 0.96);
    border: 1px solid rgba(52, 211, 153, 0.28);
    border-bottom: 2px solid #10B981;
    border-radius: 18px;
    padding: 5px 14px;
    color: #ECFDF5;
    font-size: 10pt;
    caret-color: #34D399;
}
.search-pill:focus {
    background-color: rgba(13, 22, 18, 0.98);
    border-bottom: 2px solid #34D399;
}
.inline-entry {
    background-color: rgba(20, 33, 27, 0.96);
    border: 1px solid rgba(52, 211, 153, 0.28);
    border-bottom: 2px solid #10B981;
    border-radius: 6px;
    padding: 5px 10px;
    color: #ECFDF5;
}
.section-title {
    font-size: 10pt;
    font-weight: 700;
    color: #ECFDF5;
}
.muted-label {
    font-size: 8.8pt;
    color: #9EB3A8;
}
.muheeb-badge {
    background-color: rgba(5, 150, 105, 0.24);
    border: 1px solid rgba(52, 211, 153, 0.42);
    border-radius: 99px;
    padding: 2px 9px;
    color: #34D399;
    font-size: 8.5pt;
    font-weight: 700;
}
.pill-btn {
    background-color: rgba(32, 49, 41, 0.88);
    border: 1px solid rgba(52, 211, 153, 0.18);
    border-radius: 6px;
    padding: 4px 10px;
    color: #D1FAE5;
    font-size: 9pt;
    font-weight: 600;
}
.pill-btn:hover {
    background-color: rgba(16, 185, 129, 0.24);
    border-color: rgba(52, 211, 153, 0.42);
}
.tab-active {
    background-color: #059669;
    border: 1px solid #34D399;
    border-radius: 14px;
    padding: 3px 12px;
    color: #FFFFFF;
    font-size: 9pt;
    font-weight: 700;
}
.tab-inactive {
    background-color: rgba(28, 44, 36, 0.85);
    border: 1px solid rgba(52, 211, 153, 0.16);
    border-radius: 14px;
    padding: 3px 12px;
    color: #CFE3D9;
    font-size: 9pt;
}
.tab-inactive:hover {
    background-color: rgba(52, 211, 153, 0.15);
}
.accent-btn {
    background-color: #059669;
    border: 1px solid #10B981;
    border-radius: 6px;
    padding: 5px 13px;
    color: #FFFFFF;
    font-size: 9.2pt;
    font-weight: 700;
}
.accent-btn:hover {
    background-color: #10B981;
}
.app-tile {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 7px 4px;
    color: #ECFDF5;
}
.app-tile:hover {
    background-color: rgba(52, 211, 153, 0.12);
    border-color: rgba(52, 211, 153, 0.20);
}
.rec-row {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 9px;
    color: #ECFDF5;
}
.rec-row:hover {
    background-color: rgba(52, 211, 153, 0.11);
    border-color: rgba(52, 211, 153, 0.18);
}
.qs-tile {
    background-color: rgba(29, 45, 37, 0.92);
    border: 1px solid rgba(52, 211, 153, 0.18);
    border-radius: 6px;
    min-height: 44px;
    color: #ECFDF5;
    font-weight: 600;
}
.qs-tile:hover {
    background-color: rgba(41, 62, 52, 0.96);
    border-color: rgba(52, 211, 153, 0.35);
}
.qs-tile-active {
    background-color: #059669;
    border: 1px solid #34D399;
    border-radius: 6px;
    min-height: 44px;
    color: #FFFFFF;
    font-weight: 700;
}
.qs-tile-active:hover {
    background-color: #10B981;
}
.qs-split-left {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
    border-right: none;
}
.qs-split-right {
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    min-width: 32px;
    padding: 0 6px;
}
.qs-caption {
    font-size: 8.5pt;
    color: #CBDBD3;
}
.notif-item, .widget-subcard {
    background-color: rgba(24, 38, 31, 0.92);
    border: 1px solid rgba(52, 211, 153, 0.18);
    border-radius: 8px;
    padding: 10px 12px;
}
.cal-day {
    background: transparent;
    border: none;
    border-radius: 17px;
    min-width: 32px;
    min-height: 32px;
    padding: 0;
    color: #E2F1EA;
    font-size: 9pt;
}
.cal-day:hover {
    background-color: rgba(52, 211, 153, 0.16);
}
.cal-today {
    background-color: #059669;
    border: 1px solid #34D399;
    border-radius: 17px;
    min-width: 32px;
    min-height: 32px;
    padding: 0;
    color: #FFFFFF;
    font-weight: 700;
    font-size: 9pt;
}
scale trough {
    background-color: rgba(45, 68, 57, 0.95);
    border-radius: 99px;
    min-height: 4px;
}
scale highlight {
    background-color: #10B981;
    border-radius: 99px;
    min-height: 4px;
}
scale slider {
    background-color: #34D399;
    border: 3px solid #12211A;
    border-radius: 99px;
    min-width: 16px;
    min-height: 16px;
    margin: -6px 0;
}
progressbar trough {
    background-color: rgba(40, 62, 51, 0.9);
    border-radius: 99px;
    min-height: 6px;
}
progressbar progress {
    background-color: #10B981;
    border-radius: 99px;
    min-height: 6px;
}
"""


def load_user_settings():
    defaults = {
        "search_style": "box",  # box | compact | icon | hidden
        "search_label": "Search",
        "search_gleam": True,
        "web_engine": "google",
        "enable_calc": True,
        "enable_files": True,
    }
    try:
        if os.path.isfile(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                defaults.update(json.load(f))
    except Exception:
        pass
    return defaults


def save_user_settings(cfg):
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    # Refresh taskbar search pill immediately!
    spawn_detached("xfce4-panel --plugin-event=genmon-202:refresh:bool:true")


def run_cmd(cmd, timeout=2.5):
    try:
        return subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        ).stdout.strip()
    except Exception:
        return ""


def spawn_detached(cmd):
    try:
        subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass


def safe_eval_math(expr):
    """Safely evaluate simple arithmetic expressions inside Search."""
    allowed = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in allowed:
            return allowed[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in allowed:
            return allowed[type(node.op)](_eval(node.operand))
        raise ValueError("Unsupported")

    cleaned = expr.strip().replace("^", "**")
    if not any(op in cleaned for op in ("+", "-", "*", "/", "%")):
        return None
    tree = ast.parse(cleaned, mode="eval")
    val = _eval(tree.body)
    if isinstance(val, float) and val.is_integer():
        val = int(val)
    elif isinstance(val, float):
        val = round(val, 6)
    return val


def take_snip(kind="region"):
    """Capture Windows 11 screenshot to ~/Pictures/Screenshots AND copy to Clipboard."""
    shots_dir = os.path.expanduser("~/Pictures/Screenshots")
    os.makedirs(shots_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_file = os.path.join(shots_dir, f"Screenshot_{ts}.png")

    if kind == "fullscreen":
        cmd = (
            f"import -window root '{out_file}' && "
            f"xclip -selection clipboard -t image/png -i '{out_file}' && "
            f"notify-send 'Snipping Tool • {BRAND_AUTHOR}' 'Fullscreen saved to Screenshots & copied to clipboard'"
        )
    elif kind == "window":
        cmd = (
            f"xfce4-screenshooter -w -s '{out_file}' && "
            f"[ -f '{out_file}' ] && xclip -selection clipboard -t image/png -i '{out_file}' && "
            f"notify-send 'Snipping Tool • {BRAND_AUTHOR}' 'Window snip saved & copied to clipboard'"
        )
    else:
        cmd = (
            f"xfce4-screenshooter -r -s '{out_file}' && "
            f"[ -f '{out_file}' ] && xclip -selection clipboard -t image/png -i '{out_file}' && "
            f"notify-send 'Snipping Tool • {BRAND_AUTHOR}' 'Snip saved to Screenshots & copied to clipboard'"
        )
    spawn_detached(cmd)


def handle_single_instance(mode):
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            old_pid = int(data.get("pid", 0))
            old_mode = data.get("mode", "")
            if old_pid > 0:
                os.kill(old_pid, 0)
                os.kill(old_pid, signal.SIGTERM)
                if old_mode == mode:
                    try:
                        os.remove(STATE_FILE)
                    except OSError:
                        pass
                    sys.exit(0)
                time.sleep(0.05)
        except Exception:
            pass

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"pid": os.getpid(), "mode": mode}, f)


def cleanup_state():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("pid") == os.getpid():
                os.remove(STATE_FILE)
    except Exception:
        pass


def get_primary_geometry():
    display = Gdk.Display.get_default()
    mon = display.get_primary_monitor() or display.get_monitor(0)
    geom = mon.get_geometry()
    return geom.x, geom.y, geom.width, geom.height


def get_all_apps():
    apps = []
    seen = set()
    for app in Gio.AppInfo.get_all():
        if not app.should_show():
            continue
        name = app.get_display_name() or app.get_name()
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        apps.append(app)
    apps.sort(key=lambda a: (a.get_display_name() or "").lower())
    return apps


def find_icon_pixbuf(icon_names, size=28):
    theme = Gtk.IconTheme.get_default()
    if isinstance(icon_names, str):
        icon_names = [icon_names]
    for name in icon_names:
        if not name:
            continue
        if os.path.isfile(name):
            try:
                from gi.repository import GdkPixbuf
                return GdkPixbuf.Pixbuf.new_from_file_at_scale(name, size, size, True)
            except Exception:
                pass
        if theme.has_icon(name):
            try:
                return theme.load_icon(name, size, Gtk.IconLookupFlags.FORCE_SIZE)
            except Exception:
                pass
    try:
        return theme.load_icon("application-x-executable", size, Gtk.IconLookupFlags.FORCE_SIZE)
    except Exception:
        return None


def make_win11_logo_drawing(size=24):
    area = Gtk.DrawingArea()
    area.set_size_request(size, size)

    def on_draw(widget, ctx):
        gap = max(2.0, size * 0.10)
        half = (size - gap) / 2.0
        colors = [
            (0.20, 0.83, 0.60),
            (0.02, 0.59, 0.41),
            (0.06, 0.73, 0.51),
            (0.02, 0.37, 0.27),
        ]
        coords = [(0, 0), (half + gap, 0), (0, half + gap), (half + gap, half + gap)]
        for (x, y), (r, g, b) in zip(coords, colors):
            ctx.new_sub_path()
            rad = 2.0
            ctx.arc(x + half - rad, y + rad, rad, -1.57, 0)
            ctx.arc(x + half - rad, y + half - rad, rad, 0, 1.57)
            ctx.arc(x + rad, y + half - rad, rad, 1.57, 3.14)
            ctx.arc(x + rad, y + rad, rad, 3.14, 4.71)
            ctx.close_path()
            ctx.set_source_rgb(r, g, b)
            ctx.fill()
        return False

    area.connect("draw", on_draw)
    return area


class BaseFlyout(Gtk.Window):
    def __init__(self, width, height, align="center", close_on_blur=True):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.get_style_context().add_class("win11-flyout")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.set_app_paintable(True)
        self.set_size_request(width, height)
        self.set_default_size(width, height)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        mx, my, mw, mh = get_primary_geometry()
        panel_h = 48
        gap = 12
        if align == "center":
            x = mx + (mw - width) // 2
            y = my + mh - panel_h - height - gap
        elif align == "right":
            x = mx + mw - width - gap
            y = my + mh - panel_h - height - gap
        elif align == "left":
            x = mx + gap
            y = my + mh - panel_h - height - gap
        elif align == "top-center":
            x = mx + (mw - width) // 2
            y = my + 22
        else:
            x = mx + (mw - width) // 2
            y = my + (mh - height) // 2

        self.target_pos = (x, y)
        self.move(x, y)
        self._created_at = time.monotonic()

        self.connect("draw", self._on_transparent_draw)
        self.connect("key-press-event", self._on_key)
        self.connect("destroy", lambda *_: (cleanup_state(), Gtk.main_quit()))
        if close_on_blur:
            self.connect("focus-out-event", self._on_focus_out)

    def _on_transparent_draw(self, widget, ctx):
        ctx.set_source_rgba(0, 0, 0, 0)
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)
        return False

    def _on_key(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close_flyout()
            return True
        return False

    def _on_focus_out(self, widget, event):
        if time.monotonic() - self._created_at < 0.35:
            return False
        GLib.timeout_add(90, self._check_focus_and_close)
        return False

    def _check_focus_and_close(self):
        if not self.is_active():
            self.close_flyout()
        return False

    def close_flyout(self):
        cleanup_state()
        self.destroy()

    def show_flyout(self):
        self.show_all()
        self.move(*self.target_pos)
        self.present_with_time(Gdk.CURRENT_TIME)


# ==============================================================================
#  1. WINDOWS 11 START MENU (Win / Ctrl+Esc)
# ==============================================================================
class StartMenuFlyout(BaseFlyout):
    def __init__(self, repo_root):
        super().__init__(620, 640, align="center")
        self.repo_root = repo_root
        self.all_apps = get_all_apps()

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        card.get_style_context().add_class("mica-card")
        self.add(card)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        body.set_margin_top(20)
        body.set_margin_start(24)
        body.set_margin_end(24)
        body.set_margin_bottom(12)
        card.pack_start(body, True, True, 0)

        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search for apps, settings, and documents")
        self.search_entry.get_style_context().add_class("search-pill")
        self.search_entry.connect("changed", self.on_search_changed)
        self.search_entry.connect("activate", self.on_search_activate)
        body.pack_start(self.search_entry, False, False, 0)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(150)
        body.pack_start(self.stack, True, True, 0)

        self.stack.add_named(self._build_home_page(), "home")
        self.stack.add_named(self._build_all_apps_page(), "all")
        self.stack.add_named(self._build_search_page(), "search")

        self.power_revealer = Gtk.Revealer()
        self.power_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        pbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        pbox.set_margin_start(24)
        pbox.set_margin_end(24)
        pbox.set_margin_bottom(8)
        pbox.set_halign(Gtk.Align.END)
        for lbl, cmd in [
            ("Lock (Win+L)", "xflock4"),
            ("Sign out", "xfce4-session-logout --logout"),
            ("Restart", "xfce4-session-logout --reboot"),
            ("Shut down", "xfce4-session-logout --halt"),
        ]:
            b = Gtk.Button(label=lbl)
            b.get_style_context().add_class("pill-btn")
            b.connect("clicked", lambda _, c=cmd: (spawn_detached(c), self.close_flyout()))
            pbox.pack_start(b, False, False, 0)
        self.power_revealer.add(pbox)
        card.pack_start(self.power_revealer, False, False, 0)

        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        footer.get_style_context().add_class("mica-footer")
        footer.set_size_request(-1, 56)

        f_inner = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        f_inner.set_margin_start(24)
        f_inner.set_margin_end(24)
        f_inner.set_valign(Gtk.Align.CENTER)
        footer.pack_start(f_inner, True, True, 0)

        f_inner.pack_start(make_win11_logo_drawing(22), False, False, 0)
        u_lbl = Gtk.Label(label=getpass.getuser().capitalize())
        u_lbl.get_style_context().add_class("section-title")
        f_inner.pack_start(u_lbl, False, False, 0)

        badge = Gtk.Label(label=f"★ {BRAND_AUTHOR}")
        badge.get_style_context().add_class("muheeb-badge")
        f_inner.pack_start(badge, False, False, 4)

        f_inner.pack_start(Gtk.Box(), True, True, 0)

        for tip, txt, cmd in [
            ("File Explorer (Win+E)", "Explorer", "thunar"),
            ("Win11 Settings (Win+I)", "Settings", f"python3 '{os.path.abspath(__file__)}' settings"),
            ("Snipping Tool (Win+Shift+S)", "Snip", f"python3 '{os.path.abspath(__file__)}' snip"),
        ]:
            ib = Gtk.Button(label=txt)
            ib.set_tooltip_text(tip)
            ib.get_style_context().add_class("pill-btn")
            ib.connect("clicked", lambda _, c=cmd: (spawn_detached(c), self.close_flyout()))
            f_inner.pack_start(ib, False, False, 0)

        pwr_btn = Gtk.Button(label="⏻")
        pwr_btn.set_tooltip_text("Power options")
        pwr_btn.get_style_context().add_class("accent-btn")
        pwr_btn.connect(
            "clicked",
            lambda *_: self.power_revealer.set_reveal_child(
                not self.power_revealer.get_reveal_child()
            ),
        )
        f_inner.pack_start(pwr_btn, False, False, 0)
        card.pack_end(footer, False, False, 0)

        GLib.idle_add(pwr_btn.grab_focus)

    def _build_home_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        lbl = Gtk.Label(label="Pinned")
        lbl.get_style_context().add_class("section-title")
        hdr.pack_start(lbl, False, False, 4)

        all_btn = Gtk.Button(label="All apps  ›")
        all_btn.get_style_context().add_class("pill-btn")
        all_btn.connect("clicked", lambda *_: self.stack.set_visible_child_name("all"))
        hdr.pack_end(all_btn, False, False, 0)
        box.pack_start(hdr, False, False, 0)

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_spacing(4)
        grid.set_column_spacing(4)

        icons_dir = os.path.join(self.repo_root, "assets", "icons")
        me = os.path.abspath(__file__)
        pinned_specs = [
            ("File Explorer", [os.path.join(icons_dir, "win11-explorer.svg"), "system-file-manager"], "thunar"),
            ("Terminal", [os.path.join(icons_dir, "win11-terminal.svg"), "utilities-terminal"], "qterminal || xfce4-terminal"),
            ("Browser", ["brave-browser", "firefox-esr", "web-browser"], "brave-browser || firefox"),
            ("VS Code", ["code", "accessories-text-editor"], "code || mousepad"),
            ("Settings", [os.path.join(icons_dir, "win11-settings.svg")], f"python3 '{me}' settings"),
            ("Wi-Fi & BT", ["preferences-system-network"], f"python3 '{me}' control"),
            ("Snipping Tool", ["applets-screenshooter"], f"python3 '{me}' snip"),
            ("Search Setup", [os.path.join(icons_dir, "win11-search.svg")], f"python3 '{me}' search"),
            ("Widgets", [os.path.join(icons_dir, "win11-widgets.svg")], f"python3 '{me}' widgets"),
            ("Task Manager", ["utilities-system-monitor"], "xfce4-taskmanager"),
            ("Run (Win+R)", ["system-run"], f"python3 '{me}' run"),
            ("About Win11", [os.path.join(icons_dir, "win11-start.svg")], f"python3 '{me}' winver"),
            ("Downloads", ["folder-download"], f"thunar '{os.path.expanduser('~/Downloads')}'"),
            ("Documents", ["folder-documents"], f"thunar '{os.path.expanduser('~/Documents')}'"),
            ("Pictures", ["folder-pictures"], f"thunar '{os.path.expanduser('~/Pictures')}'"),
            ("Screenshots", ["folder-pictures"], f"thunar '{os.path.expanduser('~/Pictures/Screenshots')}'"),
            ("Text Editor", ["org.xfce.mousepad", "accessories-text-editor"], "mousepad"),
            ("Kali Tweaks", ["kali-menu", "security-high"], "kali-tweaks || qterminal -e kali-tweaks"),
        ]

        for idx, (title, ic_list, cmd) in enumerate(pinned_specs):
            btn = Gtk.Button()
            btn.get_style_context().add_class("app-tile")
            vb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            vb.set_halign(Gtk.Align.CENTER)
            pb = find_icon_pixbuf(ic_list, 28)
            if pb:
                vb.pack_start(Gtk.Image.new_from_pixbuf(pb), False, False, 0)
            tl = Gtk.Label(label=title)
            tl.set_max_width_chars(12)
            tl.set_ellipsize(Pango.EllipsizeMode.END)
            tl.set_markup(f"<span size='8800'>{GLib.markup_escape_text(title)}</span>")
            vb.pack_start(tl, False, False, 0)
            btn.add(vb)
            btn.connect("clicked", lambda _, c=cmd: (spawn_detached(c), self.close_flyout()))
            grid.attach(btn, idx % 6, idx // 6, 1, 1)

        box.pack_start(grid, False, False, 0)

        rhdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        rhdr.set_margin_top(4)
        rlbl = Gtk.Label(label="Recommended")
        rlbl.get_style_context().add_class("section-title")
        rhdr.pack_start(rlbl, False, False, 4)
        sub_tag = Gtk.Label(label=f"{BRAND_EDITION} • {BRAND_AUTHOR}")
        sub_tag.get_style_context().add_class("muted-label")
        rhdr.pack_end(sub_tag, False, False, 4)
        box.pack_start(rhdr, False, False, 0)

        rgrid = Gtk.Grid()
        rgrid.set_column_homogeneous(True)
        rgrid.set_column_spacing(10)
        rgrid.set_row_spacing(4)
        rec_items = [
            ("Personalize Search & Theme", f"Win+I • {BRAND_AUTHOR}", os.path.join(icons_dir, "win11-settings.svg"), f"python3 '{me}' settings"),
            ("Wi-Fi & Bluetooth Quick Bar", "Win+A • Manage networks", "network-wireless", f"python3 '{me}' control"),
            ("Snipping Tool (Screenshot)", "Win+Shift+S or Print", "applets-screenshooter", f"python3 '{me}' snip"),
            ("About Windows 11 (winver)", BRAND_AUTHOR, os.path.join(icons_dir, "win11-start.svg"), f"python3 '{me}' winver"),
        ]
        for i, (rtitle, rsub, ricon, rcmd) in enumerate(rec_items):
            rbtn = Gtk.Button()
            rbtn.get_style_context().add_class("rec-row")
            hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            pb = find_icon_pixbuf([ricon, "folder"], 24)
            if pb:
                hb.pack_start(Gtk.Image.new_from_pixbuf(pb), False, False, 0)
            tvb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
            t1 = Gtk.Label(xalign=0)
            t1.set_markup(f"<span size='9200' weight='600'>{GLib.markup_escape_text(rtitle)}</span>")
            t2 = Gtk.Label(label=rsub, xalign=0)
            t2.get_style_context().add_class("muted-label")
            tvb.pack_start(t1, False, False, 0)
            tvb.pack_start(t2, False, False, 0)
            hb.pack_start(tvb, True, True, 0)
            rbtn.add(hb)
            rbtn.connect("clicked", lambda _, c=rcmd: (spawn_detached(c), self.close_flyout()))
            rgrid.attach(rbtn, i % 2, i // 2, 1, 1)
        box.pack_start(rgrid, False, False, 0)
        return box

    def _build_all_apps_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        lbl = Gtk.Label(label="All apps")
        lbl.get_style_context().add_class("section-title")
        hdr.pack_start(lbl, False, False, 4)
        back_btn = Gtk.Button(label="‹  Back")
        back_btn.get_style_context().add_class("pill-btn")
        back_btn.connect("clicked", lambda *_: self.stack.set_visible_child_name("home"))
        hdr.pack_end(back_btn, False, False, 0)
        box.pack_start(hdr, False, False, 0)

        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        for app in self.all_apps:
            vbox.pack_start(self._make_app_row(app), False, False, 0)
        sc.add(vbox)
        box.pack_start(sc, True, True, 0)
        return box

    def _build_search_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.search_results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        sc.add(self.search_results_box)
        box.pack_start(sc, True, True, 0)
        return box

    def _make_app_row(self, app):
        btn = Gtk.Button()
        btn.get_style_context().add_class("rec-row")
        hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        gicon = app.get_icon()
        img = Gtk.Image.new_from_gicon(gicon, Gtk.IconSize.LARGE_TOOLBAR) if gicon else Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)
        img.set_pixel_size(24)
        hb.pack_start(img, False, False, 0)
        vb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vb.pack_start(Gtk.Label(label=app.get_display_name(), xalign=0), False, False, 0)
        hb.pack_start(vb, True, True, 0)
        btn.add(hb)
        btn.connect("clicked", lambda _, a=app: (a.launch([], None), self.close_flyout()))
        return btn

    def on_search_changed(self, entry):
        q = entry.get_text().strip().lower()
        if not q:
            self.stack.set_visible_child_name("home")
            return
        for ch in self.search_results_box.get_children():
            self.search_results_box.remove(ch)
        for app in [
            a for a in self.all_apps
            if q in (a.get_display_name() or "").lower() or q in (a.get_executable() or "").lower()
        ][:22]:
            self.search_results_box.pack_start(self._make_app_row(app), False, False, 0)
        self.search_results_box.show_all()
        self.stack.set_visible_child_name("search")

    def on_search_activate(self, entry):
        ch = self.search_results_box.get_children()
        if ch:
            ch[0].clicked()


# ==============================================================================
#  2. CUSTOMIZABLE WINDOWS 11 SEARCH FLYOUT (Win+S)
# ==============================================================================
class CustomizableSearchFlyout(BaseFlyout):
    def __init__(self):
        super().__init__(660, 610, align="center")
        self.cfg = load_user_settings()
        self.all_apps = get_all_apps()
        self.active_tab = "all"

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.get_style_context().add_class("mica-card")
        self.add(card)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        body.set_margin_top(18)
        body.set_margin_bottom(16)
        body.set_margin_start(22)
        body.set_margin_end(22)
        card.pack_start(body, True, True, 0)

        # Top Search Bar + Customize Button
        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text(f"{self.cfg.get('search_label', 'Search')} apps, files, math (e.g. 24*15), or web...")
        self.entry.get_style_context().add_class("search-pill")
        self.entry.connect("changed", self._refresh_results)
        self.entry.connect("activate", self._activate_first)
        top_row.pack_start(self.entry, True, True, 0)

        cust_btn = Gtk.Button(label="⚙️ Customize Search")
        cust_btn.get_style_context().add_class("pill-btn")
        cust_btn.connect("clicked", lambda *_: self._switch_tab("customize"))
        top_row.pack_end(cust_btn, False, False, 0)
        body.pack_start(top_row, False, False, 0)

        # Category Filter Tabs
        tab_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.tab_buttons = {}
        for tid, tlabel in [("all", "All"), ("apps", "Apps"), ("files", "Files"), ("web", "Web"), ("customize", "Search Settings")]:
            tb = Gtk.Button(label=tlabel)
            tb.get_style_context().add_class("tab-active" if tid == "all" else "tab-inactive")
            tb.connect("clicked", lambda _, t=tid: self._switch_tab(t))
            self.tab_buttons[tid] = tb
            tab_row.pack_start(tb, False, False, 0)

        mb = Gtk.Label(label=BRAND_AUTHOR)
        mb.get_style_context().add_class("muheeb-badge")
        tab_row.pack_end(mb, False, False, 0)
        body.pack_start(tab_row, False, False, 0)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        body.pack_start(self.stack, True, True, 0)

        # Results Page (Left list + Right preview card)
        res_pane = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.results_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        sc.add(self.results_list)
        res_pane.pack_start(sc, True, True, 0)

        self.preview_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.preview_box.get_style_context().add_class("widget-subcard")
        self.preview_box.set_size_request(220, -1)
        res_pane.pack_end(self.preview_box, False, False, 0)
        self.stack.add_named(res_pane, "results")

        # Customize Search Page
        self.stack.add_named(self._build_customize_page(), "customize")

        self._refresh_results()
        GLib.idle_add(self.entry.grab_focus)

    def _switch_tab(self, tid):
        self.active_tab = tid
        for k, b in self.tab_buttons.items():
            ctx = b.get_style_context()
            ctx.remove_class("tab-active")
            ctx.remove_class("tab-inactive")
            ctx.add_class("tab-active" if k == tid else "tab-inactive")
        if tid == "customize":
            self.stack.set_visible_child_name("customize")
        else:
            self.stack.set_visible_child_name("results")
            self._refresh_results()

    def _build_customize_page(self):
        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        # 1. Taskbar Search Style
        c1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        c1.get_style_context().add_class("widget-subcard")
        t1 = Gtk.Label(label="Taskbar Search Bar Appearance (Live Update)", xalign=0)
        t1.get_style_context().add_class("section-title")
        c1.pack_start(t1, False, False, 0)

        srow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for sid, slbl in [
            ("box", "Full Search Box"),
            ("compact", "Compact Pill"),
            ("icon", "Icon Only"),
            ("hidden", "Hidden"),
        ]:
            b = Gtk.Button(label=slbl)
            b.get_style_context().add_class(
                "accent-btn" if self.cfg.get("search_style") == sid else "pill-btn"
            )
            b.connect("clicked", self._set_search_style, sid, srow)
            b._sid = sid
            srow.pack_start(b, True, True, 0)
        c1.pack_start(srow, False, False, 0)

        # Custom Search Box Label
        lrow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        lrow.pack_start(Gtk.Label(label="Custom Search Text:", xalign=0), False, False, 0)
        lbl_entry = Gtk.Entry()
        lbl_entry.set_text(self.cfg.get("search_label", "Search"))
        lbl_entry.get_style_context().add_class("inline-entry")
        apply_lbl = Gtk.Button(label="Apply Text")
        apply_lbl.get_style_context().add_class("accent-btn")
        apply_lbl.connect("clicked", lambda *_: self._update_label(lbl_entry.get_text()))
        lrow.pack_start(lbl_entry, True, True, 0)
        lrow.pack_start(apply_lbl, False, False, 0)
        c1.pack_start(lrow, False, False, 0)
        box.pack_start(c1, False, False, 0)

        # 2. Web Search Engine
        c2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        c2.get_style_context().add_class("widget-subcard")
        t2 = Gtk.Label(label="Default Web Search Engine", xalign=0)
        t2.get_style_context().add_class("section-title")
        c2.pack_start(t2, False, False, 0)

        erow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for eid, elbl in [("google", "Google"), ("duckduckgo", "DuckDuckGo"), ("brave", "Brave Search"), ("bing", "Bing")]:
            eb = Gtk.Button(label=elbl)
            eb.get_style_context().add_class(
                "accent-btn" if self.cfg.get("web_engine") == eid else "pill-btn"
            )
            eb._eid = eid
            eb.connect("clicked", self._set_engine, eid, erow)
            erow.pack_start(eb, True, True, 0)
        c2.pack_start(erow, False, False, 0)
        box.pack_start(c2, False, False, 0)

        # 3. Feature Toggles
        c3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        c3.get_style_context().add_class("widget-subcard")
        t3 = Gtk.Label(label="Search Capabilities", xalign=0)
        t3.get_style_context().add_class("section-title")
        c3.pack_start(t3, False, False, 0)

        for key, desc in [
            ("search_gleam", "Show Dark-Green Search Highlight Emblem inside Taskbar Search Box"),
            ("enable_calc", "Enable Instant Math Calculator in Search"),
            ("enable_files", "Search Personal Files & Folders in Home Directory"),
        ]:
            chk = Gtk.CheckButton(label=desc)
            chk.set_active(bool(self.cfg.get(key, True)))
            chk.connect("toggled", self._toggle_opt, key)
            c3.pack_start(chk, False, False, 0)
        box.pack_start(c3, False, False, 0)

        sc.add(box)
        return sc

    def _set_search_style(self, btn, sid, container):
        self.cfg["search_style"] = sid
        save_user_settings(self.cfg)
        for ch in container.get_children():
            ctx = ch.get_style_context()
            ctx.remove_class("accent-btn")
            ctx.remove_class("pill-btn")
            ctx.add_class("accent-btn" if getattr(ch, "_sid", "") == sid else "pill-btn")

    def _update_label(self, txt):
        self.cfg["search_label"] = txt.strip() or "Search"
        save_user_settings(self.cfg)
        self.entry.set_placeholder_text(f"{self.cfg['search_label']} apps, files, math, or web...")

    def _set_engine(self, btn, eid, container):
        self.cfg["web_engine"] = eid
        save_user_settings(self.cfg)
        for ch in container.get_children():
            ctx = ch.get_style_context()
            ctx.remove_class("accent-btn")
            ctx.remove_class("pill-btn")
            ctx.add_class("accent-btn" if getattr(ch, "_eid", "") == eid else "pill-btn")

    def _toggle_opt(self, chk, key):
        self.cfg[key] = chk.get_active()
        save_user_settings(self.cfg)

    def _set_preview(self, title, subtitle, action_lbl, action_cb, icon_widget=None):
        for ch in self.preview_box.get_children():
            self.preview_box.remove(ch)
        if icon_widget:
            icon_widget.set_margin_top(12)
            self.preview_box.pack_start(icon_widget, False, False, 0)
        tl = Gtk.Label(label=title)
        tl.set_line_wrap(True)
        tl.set_justify(Gtk.Justification.CENTER)
        tl.get_style_context().add_class("section-title")
        self.preview_box.pack_start(tl, False, False, 0)

        sl = Gtk.Label(label=subtitle)
        sl.set_line_wrap(True)
        sl.set_justify(Gtk.Justification.CENTER)
        sl.get_style_context().add_class("muted-label")
        self.preview_box.pack_start(sl, False, False, 0)

        ab = Gtk.Button(label=action_lbl)
        ab.get_style_context().add_class("accent-btn")
        ab.connect("clicked", lambda *_: action_cb())
        self.preview_box.pack_start(ab, False, False, 8)

        self.preview_box.pack_end(Gtk.Label(label=BRAND_AUTHOR), False, False, 0)
        self.preview_box.show_all()

    def _refresh_results(self, *_):
        if self.active_tab == "customize":
            return
        for ch in self.results_list.get_children():
            self.results_list.remove(ch)

        q = self.entry.get_text().strip()
        ql = q.lower()

        # 1. Instant Math Calculator
        if q and self.cfg.get("enable_calc", True) and self.active_tab in ("all",):
            try:
                ans = safe_eval_math(q)
                if ans is not None:
                    cbtn = Gtk.Button(label=f"🧮  {q} = {ans}   (Click to copy)")
                    cbtn.get_style_context().add_class("accent-btn")
                    cbtn.connect(
                        "clicked",
                        lambda *_, a=str(ans): (
                            spawn_detached(f"printf %s {shlex.quote(a)} | xclip -selection clipboard"),
                            self.close_flyout(),
                        ),
                    )
                    self.results_list.pack_start(cbtn, False, False, 2)
            except Exception:
                pass

        # 2. Apps
        if self.active_tab in ("all", "apps"):
            apps = (
                [
                    a for a in self.all_apps
                    if ql in (a.get_display_name() or "").lower()
                    or ql in (a.get_description() or "").lower()
                    or ql in (a.get_executable() or "").lower()
                ][:14]
                if q
                else self.all_apps[:12]
            )
            first_shown = False
            for app in apps:
                btn = Gtk.Button()
                btn.get_style_context().add_class("rec-row")
                hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                gicon = app.get_icon()
                img = Gtk.Image.new_from_gicon(gicon, Gtk.IconSize.LARGE_TOOLBAR) if gicon else Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)
                img.set_pixel_size(24)
                hb.pack_start(img, False, False, 0)
                hb.pack_start(Gtk.Label(label=app.get_display_name(), xalign=0), True, True, 0)
                btn.add(hb)
                btn.connect("clicked", lambda _, a=app: (a.launch([], None), self.close_flyout()))
                btn.connect(
                    "enter-notify-event",
                    lambda _, __, a=app: self._preview_app(a),
                )
                self.results_list.pack_start(btn, False, False, 0)
                if not first_shown:
                    self._preview_app(app)
                    first_shown = True

        # 3. Files in Home
        if q and self.cfg.get("enable_files", True) and self.active_tab in ("all", "files"):
            home = os.path.expanduser("~")
            found = []
            for root_d, dirs, files in os.walk(home):
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__")]
                for nm in dirs + files:
                    if not nm.startswith(".") and ql in nm.lower():
                        found.append(os.path.join(root_d, nm))
                        if len(found) >= 8:
                            break
                if len(found) >= 8:
                    break
            for fpath in found:
                fbtn = Gtk.Button(label=f"📄  {os.path.basename(fpath)}   ({fpath.replace(home, '~')})")
                fbtn.get_style_context().add_class("rec-row")
                fbtn.connect("clicked", lambda _, p=fpath: (spawn_detached(f"xdg-open {shlex.quote(p)}"), self.close_flyout()))
                self.results_list.pack_start(fbtn, False, False, 0)

        # 4. Web Search
        if q and self.active_tab in ("all", "web"):
            engines = {
                "google": "https://www.google.com/search?q=",
                "duckduckgo": "https://duckduckgo.com/?q=",
                "brave": "https://search.brave.com/search?q=",
                "bing": "https://www.bing.com/search?q=",
            }
            eng = self.cfg.get("web_engine", "google")
            url = engines.get(eng, engines["google"]) + urllib.parse.quote_plus(q)
            wbtn = Gtk.Button(label=f"🌐  Search {eng.capitalize()} for \"{q}\"")
            wbtn.get_style_context().add_class("pill-btn")
            wbtn.connect("clicked", lambda *_, u=url: (spawn_detached(f"xdg-open {shlex.quote(u)}"), self.close_flyout()))
            self.results_list.pack_start(wbtn, False, False, 4)

        self.results_list.show_all()

    def _preview_app(self, app):
        gicon = app.get_icon()
        img = Gtk.Image.new_from_gicon(gicon, Gtk.IconSize.DIALOG) if gicon else Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.DIALOG)
        img.set_pixel_size(48)
        self._set_preview(
            app.get_display_name() or "Application",
            app.get_description() or "Installed Kali Application",
            "Open",
            lambda: (app.launch([], None), self.close_flyout()),
            img,
        )

    def _activate_first(self, *_):
        ch = self.results_list.get_children()
        if ch:
            ch[0].clicked()


# ==============================================================================
#  3. QUICK SETTINGS / CONTROL BAR WITH IN-PANEL WI-FI & BLUETOOTH MANAGERS (Win+A)
# ==============================================================================
class ControlCenterFlyout(BaseFlyout):
    def __init__(self):
        super().__init__(380, 480, align="right")

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        card.get_style_context().add_class("mica-card")
        self.add(card)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(160)
        card.pack_start(self.stack, True, True, 0)

        self.stack.add_named(self._build_main_qs(), "main")
        self.wifi_page = self._build_wifi_manager_page()
        self.bt_page = self._build_bt_manager_page()
        self.audio_page = self._build_audio_page()
        self.stack.add_named(self.wifi_page, "wifi")
        self.stack.add_named(self.bt_page, "bluetooth")
        self.stack.add_named(self.audio_page, "audio")

        # Footer Bar
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        footer.get_style_context().add_class("mica-footer")
        footer.set_size_request(-1, 48)
        fin = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        fin.set_margin_start(16)
        fin.set_margin_end(16)
        fin.set_valign(Gtk.Align.CENTER)
        footer.pack_start(fin, True, True, 0)

        bat_lbl = Gtk.Label(label=self._get_battery_text())
        bat_lbl.get_style_context().add_class("muted-label")
        fin.pack_start(bat_lbl, False, False, 0)

        mb = Gtk.Label(label=BRAND_AUTHOR)
        mb.get_style_context().add_class("muheeb-badge")
        fin.pack_start(mb, False, False, 4)

        fin.pack_start(Gtk.Box(), True, True, 0)

        set_btn = Gtk.Button(label="⚙️ Settings")
        set_btn.get_style_context().add_class("pill-btn")
        set_btn.connect(
            "clicked",
            lambda *_: (
                spawn_detached(f"python3 '{os.path.abspath(__file__)}' settings"),
                self.close_flyout(),
            ),
        )
        fin.pack_start(set_btn, False, False, 0)
        card.pack_end(footer, False, False, 0)

    def _build_main_qs(self):
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        body.set_margin_top(18)
        body.set_margin_start(18)
        body.set_margin_end(18)
        body.set_margin_bottom(12)

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_column_spacing(10)
        grid.set_row_spacing(12)

        wifi_on = "enabled" in run_cmd("nmcli radio wifi").lower()
        ssid = run_cmd("nmcli -t -f active,ssid dev wifi list --rescan no | grep '^yes:' | cut -d: -f2") or ("Available" if wifi_on else "Off")
        bt_blocked = "yes" in run_cmd("rfkill list bluetooth | grep -i 'Soft blocked'").lower()
        bt_on = not bt_blocked
        dnd_on = run_cmd("xfconf-query -c xfce4-notifyd -p /do-not-disturb").lower() == "true"
        saver_on = run_cmd("powerprofilesctl get") == "power-saver"
        nl_on = os.path.exists(NIGHTLIGHT_STATE)

        # Tile 0: Split Wi-Fi Button (Toggle + '>' Manage Networks)
        grid.attach(
            self._make_split_tile("Wi-Fi", ssid[:13], wifi_on, self._toggle_wifi, lambda *_: self._open_wifi_page()),
            0, 0, 1, 1,
        )
        # Tile 1: Split Bluetooth Button (Toggle + '>' Manage Devices)
        grid.attach(
            self._make_split_tile("Bluetooth", "On" if bt_on else "Off", bt_on, self._toggle_bt, lambda *_: self._open_bt_page()),
            1, 0, 1, 1,
        )
        # Tiles 2..5
        simple_tiles = [
            ("Airplane", not wifi_on, self._toggle_airplane),
            ("Battery saver", saver_on, self._toggle_saver),
            ("Night light", nl_on, self._toggle_nightlight),
            ("Focus / DND", dnd_on, self._toggle_dnd),
        ]
        for idx, (cap_txt, active, handler) in enumerate(simple_tiles, start=2):
            cell = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            btn = Gtk.Button(label=cap_txt.split()[0])
            btn.get_style_context().add_class("qs-tile-active" if active else "qs-tile")
            cap = Gtk.Label(label=cap_txt)
            cap.get_style_context().add_class("qs-caption")
            btn._active_state = active
            btn.connect("clicked", handler)
            cell.pack_start(btn, False, False, 0)
            cell.pack_start(cap, False, False, 0)
            grid.attach(cell, idx % 3, idx // 3, 1, 1)

        body.pack_start(grid, False, False, 0)

        # Brightness Slider
        b_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        b_row.pack_start(Gtk.Label(label="☀️"), False, False, 0)
        b_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 25, 100, 1)
        b_scale.set_draw_value(False)
        b_scale.set_value(self._get_brightness())
        b_val = Gtk.Label(label=f"{int(b_scale.get_value())}%")
        b_val.get_style_context().add_class("muted-label")
        b_scale.connect("value-changed", self._on_brightness_changed, b_val)
        b_row.pack_start(b_scale, True, True, 0)
        b_row.pack_start(b_val, False, False, 0)
        body.pack_start(b_row, False, False, 4)

        # Volume Slider + '>' Output Device Switcher
        v_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        cur_vol = self._get_volume()
        v_btn = Gtk.Button(label="🔊")
        v_btn.get_style_context().add_class("pill-btn")
        v_btn.set_tooltip_text("Mute / Unmute")
        v_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        v_scale.set_draw_value(False)
        v_scale.set_value(cur_vol)
        v_val = Gtk.Label(label=f"{cur_vol}%")
        v_val.get_style_context().add_class("muted-label")
        v_out_btn = Gtk.Button(label="›")
        v_out_btn.set_tooltip_text("Select sound output device")
        v_out_btn.get_style_context().add_class("pill-btn")
        v_out_btn.connect("clicked", lambda *_: self._open_audio_page())
        v_btn.connect("clicked", lambda *_: (run_cmd("pactl set-sink-mute @DEFAULT_SINK@ toggle"), self._refresh_panel_control()))
        v_scale.connect("value-changed", self._on_volume_changed, v_val)
        v_row.pack_start(v_btn, False, False, 0)
        v_row.pack_start(v_scale, True, True, 0)
        v_row.pack_start(v_val, False, False, 0)
        v_row.pack_start(v_out_btn, False, False, 0)
        body.pack_start(v_row, False, False, 0)

        # Quick Wi-Fi & Bluetooth Direct Shortcut Bar
        hint_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        w_manage = Gtk.Button(label="📶 Manage Wi-Fi Networks ›")
        w_manage.get_style_context().add_class("pill-btn")
        w_manage.connect("clicked", lambda *_: self._open_wifi_page())
        b_manage = Gtk.Button(label="ᛒ Bluetooth ›")
        b_manage.get_style_context().add_class("pill-btn")
        b_manage.connect("clicked", lambda *_: self._open_bt_page())
        hint_row.pack_start(w_manage, True, True, 0)
        hint_row.pack_start(b_manage, False, False, 0)
        body.pack_end(hint_row, False, False, 0)
        return body

    def _make_split_tile(self, title, sub, active, toggle_cb, arrow_cb):
        cell = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        left_b = Gtk.Button(label=title)
        right_b = Gtk.Button(label="›")
        cls = "qs-tile-active" if active else "qs-tile"
        left_b.get_style_context().add_class(cls)
        left_b.get_style_context().add_class("qs-split-left")
        right_b.get_style_context().add_class(cls)
        right_b.get_style_context().add_class("qs-split-right")

        cap = Gtk.Label(label=sub)
        cap.get_style_context().add_class("qs-caption")
        left_b._active_state = active
        left_b._partner = right_b
        left_b._caption = cap
        left_b.connect("clicked", toggle_cb)
        right_b.connect("clicked", arrow_cb)

        hb.pack_start(left_b, True, True, 0)
        hb.pack_start(right_b, False, False, 0)
        cell.pack_start(hb, False, False, 0)
        cell.pack_start(cap, False, False, 0)
        return cell

    # --- IN-PANEL WI-FI MANAGER ---
    def _build_wifi_manager_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        page.set_margin_top(16)
        page.set_margin_start(16)
        page.set_margin_end(16)
        page.set_margin_bottom(10)

        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        back = Gtk.Button(label="‹  Back")
        back.get_style_context().add_class("pill-btn")
        back.connect("clicked", lambda *_: self.stack.set_visible_child_name("main"))
        hdr.pack_start(back, False, False, 0)

        tl = Gtk.Label(label="Wi-Fi Networks")
        tl.get_style_context().add_class("section-title")
        hdr.pack_start(tl, True, True, 0)

        scan_b = Gtk.Button(label="⟳ Scan")
        scan_b.get_style_context().add_class("pill-btn")
        scan_b.connect("clicked", lambda *_: self._populate_wifi_list(rescan=True))
        hdr.pack_end(scan_b, False, False, 0)
        page.pack_start(hdr, False, False, 0)

        self.wifi_status_lbl = Gtk.Label(label="Select a network to connect or disconnect", xalign=0)
        self.wifi_status_lbl.get_style_context().add_class("muted-label")
        page.pack_start(self.wifi_status_lbl, False, False, 0)

        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.wifi_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        sc.add(self.wifi_list_box)
        page.pack_start(sc, True, True, 0)
        return page

    def _open_wifi_page(self):
        self.stack.set_visible_child_name("wifi")
        GLib.idle_add(self._populate_wifi_list, False)

    def _populate_wifi_list(self, rescan=False):
        for ch in self.wifi_list_box.get_children():
            self.wifi_list_box.remove(ch)

        flag = "yes" if rescan else "no"
        out = run_cmd(f"nmcli -t -f IN-USE,SSID,SIGNAL,SECURITY dev wifi list --rescan {flag}", timeout=5.0)
        seen = set()
        for line in out.splitlines():
            parts = line.split(":")
            if len(parts) < 4:
                continue
            in_use = parts[0].strip() == "*"
            ssid = parts[1].strip()
            sig = parts[2].strip()
            sec = parts[3].strip() or "Open"
            if not ssid or ssid in seen:
                continue
            seen.add(ssid)

            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            card.get_style_context().add_class("notif-item")

            top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            nl = Gtk.Label(xalign=0)
            status_tag = "  •  Connected" if in_use else ""
            nl.set_markup(
                f"<span weight='700'>{GLib.markup_escape_text(ssid)}</span>\n"
                f"<span size='8500' color='#9EB3A8'>Signal {sig}%  •  {GLib.markup_escape_text(sec)}{status_tag}</span>"
            )
            top.pack_start(nl, True, True, 0)

            if in_use:
                dbtn = Gtk.Button(label="Disconnect")
                dbtn.get_style_context().add_class("pill-btn")
                dbtn.connect("clicked", self._disconnect_wifi, ssid)
                top.pack_end(dbtn, False, False, 0)
                card.pack_start(top, False, False, 0)
            else:
                rev = Gtk.Revealer()
                rev_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                pw_entry = Gtk.Entry()
                pw_entry.set_visibility(False)
                pw_entry.set_placeholder_text("Password (leave empty if saved)")
                pw_entry.get_style_context().add_class("inline-entry")
                go_btn = Gtk.Button(label="Connect")
                go_btn.get_style_context().add_class("accent-btn")
                go_btn.connect("clicked", self._connect_wifi, ssid, pw_entry)
                rev_box.pack_start(pw_entry, True, True, 0)
                rev_box.pack_start(go_btn, False, False, 0)
                rev.add(rev_box)

                cbtn = Gtk.Button(label="Connect")
                cbtn.get_style_context().add_class("accent-btn")
                cbtn.connect(
                    "clicked",
                    lambda _, r=rev, pe=pw_entry: (
                        r.set_reveal_child(not r.get_reveal_child()),
                        pe.grab_focus(),
                    ),
                )
                top.pack_end(cbtn, False, False, 0)
                card.pack_start(top, False, False, 0)
                card.pack_start(rev, False, False, 0)

            self.wifi_list_box.pack_start(card, False, False, 0)

        if not seen:
            self.wifi_list_box.pack_start(
                Gtk.Label(label="Wi-Fi is turned off or no networks found."), True, True, 20
            )
        self.wifi_list_box.show_all()
        return False

    def _connect_wifi(self, _, ssid, pw_entry):
        pw = pw_entry.get_text().strip()
        self.wifi_status_lbl.set_text(f"Connecting to {ssid}...")
        while Gtk.events_pending():
            Gtk.main_iteration()
        if pw:
            cmd = f"nmcli dev wifi connect {shlex.quote(ssid)} password {shlex.quote(pw)}"
        else:
            cmd = f"nmcli con up {shlex.quote(ssid)} || nmcli dev wifi connect {shlex.quote(ssid)}"
        out = run_cmd(cmd, timeout=10.0)
        if "successfully" in out.lower():
            self.wifi_status_lbl.set_text(f"Connected to {ssid}!")
        else:
            self.wifi_status_lbl.set_text(out[:58] or f"Connection attempt sent for {ssid}")
        self._refresh_panel_control()
        self._populate_wifi_list(False)

    def _disconnect_wifi(self, _, ssid):
        run_cmd(f"nmcli con down {shlex.quote(ssid)}", timeout=4.0)
        self.wifi_status_lbl.set_text(f"Disconnected from {ssid}")
        self._refresh_panel_control()
        self._populate_wifi_list(False)

    # --- IN-PANEL BLUETOOTH MANAGER ---
    def _build_bt_manager_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        page.set_margin_top(16)
        page.set_margin_start(16)
        page.set_margin_end(16)
        page.set_margin_bottom(10)

        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        back = Gtk.Button(label="‹  Back")
        back.get_style_context().add_class("pill-btn")
        back.connect("clicked", lambda *_: self.stack.set_visible_child_name("main"))
        hdr.pack_start(back, False, False, 0)

        tl = Gtk.Label(label="Bluetooth Devices")
        tl.get_style_context().add_class("section-title")
        hdr.pack_start(tl, True, True, 0)

        scan_b = Gtk.Button(label="⟳ Pair / Scan")
        scan_b.get_style_context().add_class("pill-btn")
        scan_b.connect("clicked", self._scan_bt)
        hdr.pack_end(scan_b, False, False, 0)
        page.pack_start(hdr, False, False, 0)

        self.bt_status_lbl = Gtk.Label(label="Manage paired & nearby Bluetooth devices", xalign=0)
        self.bt_status_lbl.get_style_context().add_class("muted-label")
        page.pack_start(self.bt_status_lbl, False, False, 0)

        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.bt_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        sc.add(self.bt_list_box)
        page.pack_start(sc, True, True, 0)
        return page

    def _open_bt_page(self):
        self.stack.set_visible_child_name("bluetooth")
        GLib.idle_add(self._populate_bt_list)

    def _scan_bt(self, *_):
        self.bt_status_lbl.set_text("Scanning nearby Bluetooth devices (4s)...")
        spawn_detached("bluetoothctl --timeout 4 scan on")
        GLib.timeout_add(2500, self._populate_bt_list)

    def _populate_bt_list(self):
        for ch in self.bt_list_box.get_children():
            self.bt_list_box.remove(ch)
        out = run_cmd("bluetoothctl devices")
        count = 0
        for line in out.splitlines():
            if not line.startswith("Device "):
                continue
            parts = line.split(" ", 2)
            if len(parts) < 3:
                continue
            mac, name = parts[1], parts[2]
            info = run_cmd(f"bluetoothctl info {shlex.quote(mac)}")
            connected = "connected: yes" in info.lower()
            count += 1

            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            row.get_style_context().add_class("notif-item")
            lbl = Gtk.Label(xalign=0)
            lbl.set_markup(
                f"<span weight='700'>{GLib.markup_escape_text(name)}</span>\n"
                f"<span size='8500' color='#9EB3A8'>{mac}  •  {'Connected' if connected else 'Paired / Available'}</span>"
            )
            row.pack_start(lbl, True, True, 0)

            act = Gtk.Button(label="Disconnect" if connected else "Connect")
            act.get_style_context().add_class("pill-btn" if connected else "accent-btn")
            act.connect("clicked", self._toggle_bt_device, mac, connected)
            row.pack_end(act, False, False, 0)
            self.bt_list_box.pack_start(row, False, False, 0)

        if count == 0:
            self.bt_list_box.pack_start(
                Gtk.Label(label="No Bluetooth devices listed yet.\nClick '⟳ Pair / Scan' to discover nearby devices."),
                True, True, 20,
            )
        self.bt_list_box.show_all()
        return False

    def _toggle_bt_device(self, _, mac, was_connected):
        verb = "disconnect" if was_connected else "connect"
        self.bt_status_lbl.set_text(f"Running bluetoothctl {verb} {mac}...")
        run_cmd(f"bluetoothctl {verb} {shlex.quote(mac)}", timeout=5.0)
        self._populate_bt_list()

    # --- IN-PANEL AUDIO OUTPUT PAGE ---
    def _build_audio_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        page.set_margin_top(16)
        page.set_margin_start(16)
        page.set_margin_end(16)

        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        back = Gtk.Button(label="‹  Back")
        back.get_style_context().add_class("pill-btn")
        back.connect("clicked", lambda *_: self.stack.set_visible_child_name("main"))
        hdr.pack_start(back, False, False, 0)
        tl = Gtk.Label(label="Sound Output")
        tl.get_style_context().add_class("section-title")
        hdr.pack_start(tl, True, True, 0)
        page.pack_start(hdr, False, False, 0)

        self.audio_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        page.pack_start(self.audio_list, True, True, 0)
        return page

    def _open_audio_page(self):
        for ch in self.audio_list.get_children():
            self.audio_list.remove(ch)
        cur_sink = run_cmd("pactl get-default-sink")
        for ln in run_cmd("pactl list short sinks").splitlines():
            cols = ln.split("\t")
            if len(cols) >= 2:
                sname = cols[1]
                b = Gtk.Button(label=f"{'✓  ' if sname == cur_sink else ''}{sname}")
                b.get_style_context().add_class("accent-btn" if sname == cur_sink else "pill-btn")
                b.connect("clicked", lambda _, s=sname: (run_cmd(f"pactl set-default-sink {shlex.quote(s)}"), self._open_audio_page()))
                self.audio_list.pack_start(b, False, False, 0)
        self.audio_list.show_all()
        self.stack.set_visible_child_name("audio")

    # --- TOGGLE HELPERS ---
    def _refresh_panel_control(self):
        spawn_detached("xfce4-panel --plugin-event=genmon-212:refresh:bool:true")

    def _flip_btn(self, btn, new_state):
        btn._active_state = new_state
        targets = [btn] + ([btn._partner] if hasattr(btn, "_partner") else [])
        for t in targets:
            ctx = t.get_style_context()
            ctx.remove_class("qs-tile")
            ctx.remove_class("qs-tile-active")
            ctx.add_class("qs-tile-active" if new_state else "qs-tile")

    def _toggle_wifi(self, btn):
        nxt = not btn._active_state
        run_cmd(f"nmcli radio wifi {'on' if nxt else 'off'}")
        btn._caption.set_text("On" if nxt else "Off")
        self._flip_btn(btn, nxt)
        self._refresh_panel_control()

    def _toggle_bt(self, btn):
        nxt = not btn._active_state
        run_cmd(f"rfkill {'unblock' if nxt else 'block'} bluetooth")
        run_cmd(f"bluetoothctl power {'on' if nxt else 'off'}")
        btn._caption.set_text("On" if nxt else "Off")
        self._flip_btn(btn, nxt)

    def _toggle_airplane(self, btn):
        nxt = not btn._active_state
        run_cmd(f"nmcli radio all {'off' if nxt else 'on'}")
        self._flip_btn(btn, nxt)
        self._refresh_panel_control()

    def _toggle_saver(self, btn):
        nxt = not btn._active_state
        run_cmd(f"powerprofilesctl set {'power-saver' if nxt else 'balanced'}")
        self._flip_btn(btn, nxt)

    def _toggle_nightlight(self, btn):
        nxt = not btn._active_state
        out = run_cmd("xrandr --current | awk '/ connected/{print $1; exit}'") or "eDP-1"
        if nxt:
            run_cmd(f"xrandr --output {out} --gamma 1.0:0.86:0.72")
            open(NIGHTLIGHT_STATE, "w").close()
        else:
            run_cmd(f"xrandr --output {out} --gamma 1.0:1.0:1.0")
            if os.path.exists(NIGHTLIGHT_STATE):
                os.remove(NIGHTLIGHT_STATE)
        self._flip_btn(btn, nxt)

    def _toggle_dnd(self, btn):
        nxt = not btn._active_state
        run_cmd(f"xfconf-query -c xfce4-notifyd -p /do-not-disturb -n -t bool -s {'true' if nxt else 'false'}")
        self._flip_btn(btn, nxt)
        spawn_detached("xfce4-panel --plugin-event=genmon-213:refresh:bool:true")

    def _get_volume(self):
        out = run_cmd("pactl get-sink-volume @DEFAULT_SINK@")
        for tok in out.split():
            if tok.endswith("%"):
                try:
                    return max(0, min(100, int(tok[:-1])))
                except ValueError:
                    pass
        return 70

    def _on_volume_changed(self, scale, label):
        val = int(scale.get_value())
        label.set_text(f"{val}%")
        spawn_detached(f"pactl set-sink-volume @DEFAULT_SINK@ {val}%")

    def _get_brightness(self):
        try:
            bl_root = "/sys/class/backlight"
            if os.path.isdir(bl_root):
                devs = os.listdir(bl_root)
                if devs:
                    d = os.path.join(bl_root, devs[0])
                    cur = int(open(os.path.join(d, "brightness")).read().strip())
                    mx = int(open(os.path.join(d, "max_brightness")).read().strip())
                    if mx > 0:
                        return max(25, min(100, round(cur * 100 / mx)))
        except Exception:
            pass
        return 100

    def _on_brightness_changed(self, scale, label):
        val = int(scale.get_value())
        label.set_text(f"{val}%")
        out = run_cmd("xrandr --current | awk '/ connected/{print $1; exit}'") or "eDP-1"
        spawn_detached(f"xrandr --output {out} --brightness {val / 100.0:.2f}")

    def _get_battery_text(self):
        if psutil and hasattr(psutil, "sensors_battery"):
            b = psutil.sensors_battery()
            if b:
                return f"{'⚡' if b.power_plugged else '🔋'} {int(b.percent)}%"
        return "AC Power"


# ==============================================================================
#  4. TWO-CARD NOTIFICATION CENTER & CALENDAR (Win+N)
# ==============================================================================
class NotificationCalendarFlyout(BaseFlyout):
    def __init__(self):
        super().__init__(364, 636, align="right")
        today = datetime.date.today()
        self.shown_year = today.year
        self.shown_month = today.month
        self.focus_mins = 30

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(outer)

        ncard = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        ncard.get_style_context().add_class("mica-card")
        ncard.set_size_request(-1, 246)
        n_in = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        n_in.set_margin_top(14)
        n_in.set_margin_bottom(12)
        n_in.set_margin_start(16)
        n_in.set_margin_end(16)
        ncard.pack_start(n_in, True, True, 0)

        nhdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        ntitle = Gtk.Label(label="Notifications")
        ntitle.get_style_context().add_class("section-title")
        nhdr.pack_start(ntitle, False, False, 0)
        clr_btn = Gtk.Button(label="Clear all")
        clr_btn.get_style_context().add_class("pill-btn")
        clr_btn.connect("clicked", self._clear_notifications)
        nhdr.pack_end(clr_btn, False, False, 0)
        n_in.pack_start(nhdr, False, False, 0)

        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.notif_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self._populate_notifications()
        sc.add(self.notif_list)
        n_in.pack_start(sc, True, True, 0)
        outer.pack_start(ncard, True, True, 0)

        ccard = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        ccard.get_style_context().add_class("mica-card")
        ccard.set_size_request(-1, 378)
        c_in = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        c_in.set_margin_top(14)
        c_in.set_margin_start(16)
        c_in.set_margin_end(16)
        c_in.set_margin_bottom(10)
        ccard.pack_start(c_in, True, True, 0)

        dhdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        dlbl = Gtk.Label(label=today.strftime("%A, %B %d"), xalign=0)
        dlbl.get_style_context().add_class("section-title")
        dhdr.pack_start(dlbl, False, False, 0)
        mb = Gtk.Label(label=BRAND_AUTHOR)
        mb.get_style_context().add_class("muheeb-badge")
        dhdr.pack_end(mb, False, False, 0)
        c_in.pack_start(dhdr, False, False, 0)

        mhdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.month_lbl = Gtk.Label(xalign=0)
        mhdr.pack_start(self.month_lbl, True, True, 0)
        for sym, dlt in [("▲", -1), ("▼", 1)]:
            b = Gtk.Button(label=sym)
            b.get_style_context().add_class("pill-btn")
            b.connect("clicked", lambda _, d=dlt: self._shift_month(d))
            mhdr.pack_start(b, False, False, 0)
        c_in.pack_start(mhdr, False, False, 0)

        self.cal_grid = Gtk.Grid()
        self.cal_grid.set_column_homogeneous(True)
        self.cal_grid.set_row_spacing(2)
        self.cal_grid.set_column_spacing(2)
        c_in.pack_start(self.cal_grid, True, True, 0)
        self._render_calendar()

        ffoot = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        ffoot.get_style_context().add_class("mica-footer")
        ffoot.set_size_request(-1, 46)
        fin = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        fin.set_margin_start(16)
        fin.set_margin_end(16)
        fin.set_valign(Gtk.Align.CENTER)
        ffoot.pack_start(fin, True, True, 0)

        minus_b = Gtk.Button(label="−")
        minus_b.get_style_context().add_class("pill-btn")
        self.focus_lbl = Gtk.Label(label="30 mins")
        self.focus_lbl.get_style_context().add_class("section-title")
        plus_b = Gtk.Button(label="+")
        plus_b.get_style_context().add_class("pill-btn")
        minus_b.connect("clicked", lambda *_: self._adj_focus(-15))
        plus_b.connect("clicked", lambda *_: self._adj_focus(15))
        fin.pack_start(minus_b, False, False, 0)
        fin.pack_start(self.focus_lbl, False, False, 4)
        fin.pack_start(plus_b, False, False, 0)
        fin.pack_start(Gtk.Box(), True, True, 0)

        fbtn = Gtk.Button(label="▶ Focus")
        fbtn.get_style_context().add_class("accent-btn")
        fbtn.connect("clicked", self._start_focus)
        fin.pack_start(fbtn, False, False, 0)
        ccard.pack_end(ffoot, False, False, 0)
        outer.pack_start(ccard, False, False, 0)

    def _populate_notifications(self):
        items = [
            (
                f"Windows 11 Shell • {BRAND_AUTHOR}",
                "Dark Green Edition Ready",
                "Press Win+A for Wi-Fi/BT Quick Settings, Win+Shift+S for Snipping Tool.",
            )
        ]
        db_path = os.path.expanduser("~/.cache/xfce4/notifyd/log.sqlite")
        if os.path.isfile(db_path):
            try:
                con = sqlite3.connect(db_path)
                cur = con.cursor()
                tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
                if tables:
                    t = tables[0]
                    cols = [r[1] for r in cur.execute(f"PRAGMA table_info({t})")]
                    app_col = "app_name" if "app_name" in cols else cols[0]
                    sum_col = "summary" if "summary" in cols else cols[min(1, len(cols) - 1)]
                    body_col = "body" if "body" in cols else sum_col
                    for a, s, b in cur.execute(f"SELECT {app_col}, {sum_col}, {body_col} FROM {t} ORDER BY rowid DESC LIMIT 6"):
                        if s:
                            items.append((a or "System", s, b or ""))
                con.close()
            except Exception:
                pass
        for app_name, summary, body in items:
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            card.get_style_context().add_class("notif-item")
            al = Gtk.Label(label=str(app_name), xalign=0)
            al.get_style_context().add_class("muted-label")
            sl = Gtk.Label(xalign=0)
            sl.set_line_wrap(True)
            sl.set_max_width_chars(38)
            sl.set_markup(f"<span weight='700'>{GLib.markup_escape_text(str(summary))}</span>")
            card.pack_start(al, False, False, 0)
            card.pack_start(sl, False, False, 0)
            if body:
                bl = Gtk.Label(label=str(body), xalign=0)
                bl.set_line_wrap(True)
                bl.set_max_width_chars(40)
                bl.get_style_context().add_class("muted-label")
                card.pack_start(bl, False, False, 0)
            self.notif_list.pack_start(card, False, False, 0)

    def _clear_notifications(self, *_):
        for ch in self.notif_list.get_children():
            self.notif_list.remove(ch)
        empty = Gtk.Label(label=f"No new notifications\n{BRAND_AUTHOR}")
        empty.set_justify(Gtk.Justification.CENTER)
        empty.get_style_context().add_class("muted-label")
        empty.set_margin_top(45)
        self.notif_list.pack_start(empty, True, True, 0)
        self.notif_list.show_all()

    def _shift_month(self, delta):
        m = self.shown_month + delta
        y = self.shown_year
        if m < 1:
            m, y = 12, y - 1
        elif m > 12:
            m, y = 1, y + 1
        self.shown_month, self.shown_year = m, y
        self._render_calendar()

    def _render_calendar(self):
        for ch in self.cal_grid.get_children():
            self.cal_grid.remove(ch)
        self.month_lbl.set_markup(
            f"<span weight='700' color='#ECFDF5'>{calendar.month_name[self.shown_month]} {self.shown_year}</span>"
        )
        cal = calendar.Calendar(firstweekday=6)
        for col, dname in enumerate(["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]):
            dl = Gtk.Label(label=dname)
            dl.get_style_context().add_class("muted-label")
            self.cal_grid.attach(dl, col, 0, 1, 1)

        today = datetime.date.today()
        for r_idx, week in enumerate(cal.monthdayscalendar(self.shown_year, self.shown_month), start=1):
            for c_idx, day in enumerate(week):
                if day == 0:
                    self.cal_grid.attach(Gtk.Label(label=""), c_idx, r_idx, 1, 1)
                else:
                    b = Gtk.Button(label=str(day))
                    is_today = (day == today.day and self.shown_month == today.month and self.shown_year == today.year)
                    b.get_style_context().add_class("cal-today" if is_today else "cal-day")
                    self.cal_grid.attach(b, c_idx, r_idx, 1, 1)
        self.cal_grid.show_all()

    def _adj_focus(self, delta):
        self.focus_mins = max(15, min(180, self.focus_mins + delta))
        self.focus_lbl.set_text(f"{self.focus_mins} mins")

    def _start_focus(self, *_):
        run_cmd("xfconf-query -c xfce4-notifyd -p /do-not-disturb -n -t bool -s true")
        spawn_detached(f"notify-send 'Focus ({self.focus_mins}m)' 'Do Not Disturb enabled • {BRAND_AUTHOR}'")
        self.close_flyout()


# ==============================================================================
#  5. WINDOWS 11 SNIPPING TOOL BAR (Win+Shift+S / Print)
# ==============================================================================
class SnippingToolOverlay(BaseFlyout):
    def __init__(self):
        super().__init__(440, 56, align="top-center")
        card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        card.get_style_context().add_class("mica-card")
        self.add(card)

        inner = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        inner.set_margin_start(10)
        inner.set_margin_end(10)
        inner.set_valign(Gtk.Align.CENTER)
        card.pack_start(inner, True, True, 0)

        for lbl, mode in [
            ("⬚ Region Snip", "region"),
            ("❐ Window", "window"),
            ("🖥️ Fullscreen", "fullscreen"),
        ]:
            b = Gtk.Button(label=lbl)
            b.get_style_context().add_class("accent-btn" if mode == "region" else "pill-btn")
            b.connect("clicked", self._trigger_snip, mode)
            inner.pack_start(b, False, False, 0)

        fbtn = Gtk.Button(label="📂")
        fbtn.set_tooltip_text("Open Screenshots folder")
        fbtn.get_style_context().add_class("pill-btn")
        fbtn.connect(
            "clicked",
            lambda *_: (
                os.makedirs(os.path.expanduser("~/Pictures/Screenshots"), exist_ok=True),
                spawn_detached(f"thunar '{os.path.expanduser('~/Pictures/Screenshots')}'"),
                self.close_flyout(),
            ),
        )
        inner.pack_start(fbtn, False, False, 0)

        xbtn = Gtk.Button(label="✕")
        xbtn.get_style_context().add_class("pill-btn")
        xbtn.connect("clicked", lambda *_: self.close_flyout())
        inner.pack_end(xbtn, False, False, 0)

    def _trigger_snip(self, _, mode):
        self.hide()
        while Gtk.events_pending():
            Gtk.main_iteration()
        time.sleep(0.15)
        take_snip(mode)
        self.close_flyout()


# ==============================================================================
#  6. WINDOWS 11 RUN DIALOG (Win+R) & POWER USER MENU (Win+X)
# ==============================================================================
class RunDialog(BaseFlyout):
    def __init__(self):
        super().__init__(410, 200, align="left")
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        card.get_style_context().add_class("mica-card")
        self.add(card)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        body.set_margin_top(16)
        body.set_margin_bottom(14)
        body.set_margin_start(18)
        body.set_margin_end(18)
        card.pack_start(body, True, True, 0)

        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hdr.pack_start(make_win11_logo_drawing(22), False, False, 0)
        tl = Gtk.Label(label="Run", xalign=0)
        tl.get_style_context().add_class("section-title")
        hdr.pack_start(tl, True, True, 0)
        mb = Gtk.Label(label=BRAND_AUTHOR)
        mb.get_style_context().add_class("muheeb-badge")
        hdr.pack_end(mb, False, False, 0)
        body.pack_start(hdr, False, False, 0)

        sub = Gtk.Label(label="Type the name of a program, folder, or Windows alias (cmd, wt, explorer, calc, winver):", xalign=0)
        sub.set_line_wrap(True)
        sub.get_style_context().add_class("muted-label")
        body.pack_start(sub, False, False, 0)

        self.entry = Gtk.Entry()
        self.entry.get_style_context().add_class("inline-entry")
        self.entry.connect("activate", self._exec)
        body.pack_start(self.entry, False, False, 0)

        brow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        brow.set_halign(Gtk.Align.END)
        ok = Gtk.Button(label="OK")
        ok.get_style_context().add_class("accent-btn")
        ok.connect("clicked", self._exec)
        cn = Gtk.Button(label="Cancel")
        cn.get_style_context().add_class("pill-btn")
        cn.connect("clicked", lambda *_: self.close_flyout())
        brow.pack_start(ok, False, False, 0)
        brow.pack_start(cn, False, False, 0)
        body.pack_end(brow, False, False, 0)
        GLib.idle_add(self.entry.grab_focus)

    def _exec(self, *_):
        raw = self.entry.get_text().strip()
        if not raw:
            return
        me = os.path.abspath(__file__)
        aliases = {
            "explorer": "thunar",
            "cmd": "qterminal || xfce4-terminal",
            "wt": "qterminal || xfce4-terminal",
            "powershell": "qterminal || xfce4-terminal",
            "notepad": "mousepad",
            "taskmgr": "xfce4-taskmanager",
            "winver": f"python3 '{me}' winver",
            "control": f"python3 '{me}' settings",
            "ms-settings:": f"python3 '{me}' settings",
            "ncpa.cpl": f"python3 '{me}' control",
        }
        spawn_detached(aliases.get(raw.lower(), raw))
        self.close_flyout()


class WinXMenu(BaseFlyout):
    def __init__(self):
        super().__init__(250, 420, align="left")
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        card.get_style_context().add_class("mica-card")
        self.add(card)

        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        inner.set_margin_top(10)
        inner.set_margin_bottom(10)
        inner.set_margin_start(10)
        inner.set_margin_end(10)
        card.pack_start(inner, True, True, 0)

        me = os.path.abspath(__file__)
        items = [
            ("Installed Apps", "xfce4-appfinder"),
            ("Wi-Fi & Bluetooth (Win+A)", f"python3 '{me}' control"),
            ("Power & Battery", "xfce4-power-manager-settings"),
            ("System About (winver)", f"python3 '{me}' winver"),
            ("Terminal", "qterminal || xfce4-terminal"),
            ("Terminal (Admin)", "pkexec qterminal || qterminal"),
            ("Task Manager (Ctrl+Shift+Esc)", "xfce4-taskmanager"),
            ("Personalize & Search (Win+I)", f"python3 '{me}' settings"),
            ("File Explorer (Win+E)", "thunar"),
            ("Search (Win+S)", f"python3 '{me}' search"),
            ("Snipping Tool (Win+Shift+S)", f"python3 '{me}' snip"),
            ("Run (Win+R)", f"python3 '{me}' run"),
            ("Lock Screen (Win+L)", "xflock4"),
        ]
        for lbl, cmd in items:
            b = Gtk.Button(label=lbl)
            b.get_style_context().add_class("rec-row")
            b.get_child().set_xalign(0)
            b.connect("clicked", lambda _, c=cmd: (spawn_detached(c), self.close_flyout()))
            inner.pack_start(b, False, False, 0)


# ==============================================================================
#  7. WIDGETS BOARD (Win+W), SETTINGS (Win+I) & WINVER
# ==============================================================================
class WidgetsFlyout(BaseFlyout):
    def __init__(self):
        super().__init__(460, 610, align="left")
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.get_style_context().add_class("mica-card")
        self.add(card)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        body.set_margin_top(18)
        body.set_margin_bottom(18)
        body.set_margin_start(20)
        body.set_margin_end(20)
        card.pack_start(body, True, True, 0)

        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        tl = Gtk.Label(xalign=0)
        tl.set_markup(f"<span size='13500' weight='700'>{datetime.datetime.now().strftime('%I:%M %p')}</span>")
        hdr.pack_start(tl, False, False, 0)
        mb = Gtk.Label(label=f"★ {BRAND_AUTHOR}")
        mb.get_style_context().add_class("muheeb-badge")
        hdr.pack_end(mb, False, False, 0)
        body.pack_start(hdr, False, False, 0)

        hero = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        hero.get_style_context().add_class("widget-subcard")
        hero.pack_start(make_win11_logo_drawing(36), False, False, 4)
        hvb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        h1 = Gtk.Label(xalign=0)
        h1.set_markup(f"<span size='11000' weight='700' color='#34D399'>{BRAND_EDITION}</span>")
        h2 = Gtk.Label(label=f"Kali Linux Desktop • {BRAND_AUTHOR}", xalign=0)
        h2.get_style_context().add_class("muted-label")
        hvb.pack_start(h1, False, False, 0)
        hvb.pack_start(h2, False, False, 0)
        hero.pack_start(hvb, True, True, 0)
        body.pack_start(hero, False, False, 0)

        scard = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scard.get_style_context().add_class("widget-subcard")
        st = Gtk.Label(label="System Performance", xalign=0)
        st.get_style_context().add_class("section-title")
        scard.pack_start(st, False, False, 0)

        cpu_p = psutil.cpu_percent(interval=0.05) if psutil else 16.0
        mem_p = psutil.virtual_memory().percent if psutil else 42.0
        dsk_p = psutil.disk_usage("/").percent if psutil else 35.0
        for name, pct in [("CPU Load", cpu_p), ("Memory (RAM)", mem_p), ("Disk (/)", dsk_p)]:
            r = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            rh = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            rh.pack_start(Gtk.Label(label=name, xalign=0), True, True, 0)
            pl = Gtk.Label(label=f"{pct:.0f}%")
            pl.get_style_context().add_class("muted-label")
            rh.pack_end(pl, False, False, 0)
            pb = Gtk.ProgressBar()
            pb.set_fraction(min(1.0, max(0.0, pct / 100.0)))
            r.pack_start(rh, False, False, 0)
            r.pack_start(pb, False, False, 0)
            scard.pack_start(r, False, False, 0)
        body.pack_start(scard, False, False, 0)

        ncard = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        ncard.get_style_context().add_class("widget-subcard")
        nt = Gtk.Label(label="Windows 11 Active Shortcuts", xalign=0)
        nt.get_style_context().add_class("section-title")
        ncard.pack_start(nt, False, False, 0)
        for k, v in [
            ("Win / Ctrl+Esc", "Start Menu"),
            ("Win + A", "Wi-Fi, Bluetooth & Quick Settings"),
            ("Win + S", "Customizable Search"),
            ("Win + Shift + S / Print", "Snipping Tool Screenshot"),
            ("Win + E / R / X / I / D / L", "Explorer / Run / Power / Settings / Desktop / Lock"),
        ]:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            kl = Gtk.Label(label=k, xalign=0)
            kl.get_style_context().add_class("muted-label")
            row.pack_start(kl, True, True, 0)
            row.pack_end(Gtk.Label(label=v, xalign=1), False, False, 0)
            ncard.pack_start(row, False, False, 0)
        body.pack_start(ncard, False, False, 0)


class SettingsDialog(BaseFlyout):
    """Windows 11 Settings (Win+I): Wallpaper, Taskbar Search Style, Wi-Fi/BT & System."""

    def __init__(self, repo_root):
        super().__init__(560, 440, align="dialog", close_on_blur=False)
        self.repo_root = repo_root
        self.cfg = load_user_settings()

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.get_style_context().add_class("mica-card")
        self.add(card)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        body.set_margin_top(20)
        body.set_margin_bottom(18)
        body.set_margin_start(24)
        body.set_margin_end(24)
        card.pack_start(body, True, True, 0)

        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hdr.pack_start(make_win11_logo_drawing(28), False, False, 0)
        tl = Gtk.Label(label="Windows 11 Settings & Personalization", xalign=0)
        tl.get_style_context().add_class("section-title")
        hdr.pack_start(tl, True, True, 0)
        mb = Gtk.Label(label=BRAND_AUTHOR)
        mb.get_style_context().add_class("muheeb-badge")
        hdr.pack_end(mb, False, False, 0)
        body.pack_start(hdr, False, False, 0)

        # Wallpaper Switcher
        wcard = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        wcard.get_style_context().add_class("widget-subcard")
        wt = Gtk.Label(label="Desktop Wallpaper (Made by Muheeb)", xalign=0)
        wt.get_style_context().add_class("section-title")
        wcard.pack_start(wt, False, False, 0)
        wrow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for lbl, fname in [("🌲 Dark Green Bloom (Default)", "win11-muheeb-dark.png"), ("🌿 Light Emerald Bloom", "win11-muheeb-light.png")]:
            wb = Gtk.Button(label=lbl)
            wb.get_style_context().add_class("pill-btn")
            wb.connect("clicked", self._set_wallpaper, fname)
            wrow.pack_start(wb, True, True, 0)
        wcard.pack_start(wrow, False, False, 0)
        body.pack_start(wcard, False, False, 0)

        # Taskbar Search Bar Customization
        scard = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scard.get_style_context().add_class("widget-subcard")
        st = Gtk.Label(label="Taskbar Search Bar Style", xalign=0)
        st.get_style_context().add_class("section-title")
        scard.pack_start(st, False, False, 0)
        srow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for sid, slbl in [("box", "Search Box"), ("compact", "Compact Pill"), ("icon", "Icon Only"), ("hidden", "Hidden")]:
            sb = Gtk.Button(label=slbl)
            sb.get_style_context().add_class("accent-btn" if self.cfg.get("search_style") == sid else "pill-btn")
            sb.connect("clicked", lambda _, s=sid: self._apply_search_style(s))
            srow.pack_start(sb, True, True, 0)
        scard.pack_start(srow, False, False, 0)
        body.pack_start(scard, False, False, 0)

        # Quick System Controls
        qrow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        me = os.path.abspath(__file__)
        for lbl, cmd in [
            ("📶 Wi-Fi & Bluetooth", f"python3 '{me}' control"),
            ("🔍 Search Settings", f"python3 '{me}' search"),
            ("🖥️ XFCE Settings", "xfce4-settings-manager"),
        ]:
            b = Gtk.Button(label=lbl)
            b.get_style_context().add_class("pill-btn")
            b.connect("clicked", lambda _, c=cmd: (spawn_detached(c), self.close_flyout()))
            qrow.pack_start(b, True, True, 0)
        body.pack_start(qrow, False, False, 0)

        close_b = Gtk.Button(label="Close")
        close_b.set_halign(Gtk.Align.END)
        close_b.get_style_context().add_class("accent-btn")
        close_b.connect("clicked", lambda *_: self.close_flyout())
        body.pack_end(close_b, False, False, 0)

    def _set_wallpaper(self, _, fname):
        wpath = os.path.join(self.repo_root, "wallpapers", fname)
        for prop in run_cmd("xfconf-query -c xfce4-desktop -l").splitlines():
            if prop.endswith("/last-image") or prop.endswith("/image-path"):
                run_cmd(f"xfconf-query -c xfce4-desktop -p '{prop}' -n -t string -s '{wpath}'")

    def _apply_search_style(self, sid):
        self.cfg["search_style"] = sid
        save_user_settings(self.cfg)


class WinverDialog(BaseFlyout):
    def __init__(self, repo_root):
        super().__init__(460, 360, align="dialog", close_on_blur=False)
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.get_style_context().add_class("mica-card")
        self.add(card)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        body.set_margin_top(22)
        body.set_margin_bottom(18)
        body.set_margin_start(26)
        body.set_margin_end(26)
        card.pack_start(body, True, True, 0)

        lh = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        lh.set_halign(Gtk.Align.CENTER)
        lh.pack_start(make_win11_logo_drawing(38), False, False, 0)
        lt = Gtk.Label()
        lt.set_markup("<span size='20000' weight='700' color='#ECFDF5'>Windows 11</span>")
        lh.pack_start(lt, False, False, 0)
        body.pack_start(lh, False, False, 4)

        body.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 4)

        info = Gtk.Label(xalign=0)
        info.set_line_wrap(True)
        info.set_markup(
            f"<span weight='700' size='11000' color='#34D399'>{BRAND_EDITION}</span>\n"
            f"Version 24H2 (OS Build 26100.Muheeb • Kali GNU/Linux Rolling)\n\n"
            f"Designed &amp; Engineered by: <b>{BRAND_AUTHOR}</b>\n"
            "Original 96-DPI Windows 11 Proportions • In-Panel Wi-Fi &amp; Bluetooth •\n"
            "Customizable Search Bar • Snipping Tool (Win+Shift+S) • Full Win11 Shortcuts."
        )
        body.pack_start(info, True, True, 0)

        ok_b = Gtk.Button(label="OK")
        ok_b.set_size_request(92, 32)
        ok_b.set_halign(Gtk.Align.END)
        ok_b.get_style_context().add_class("accent-btn")
        ok_b.connect("clicked", lambda *_: self.close_flyout())
        body.pack_end(ok_b, False, False, 0)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "start"
    if mode == "snip-full":
        take_snip("fullscreen")
        return

    handle_single_instance(mode)

    provider = Gtk.CssProvider()
    provider.load_from_data(SHELL_CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if mode == "start":
        win = StartMenuFlyout(repo_root)
    elif mode == "search":
        win = CustomizableSearchFlyout()
    elif mode == "control":
        win = ControlCenterFlyout()
    elif mode == "notifications":
        win = NotificationCalendarFlyout()
    elif mode == "widgets":
        win = WidgetsFlyout()
    elif mode == "snip":
        win = SnippingToolOverlay()
    elif mode == "run":
        win = RunDialog()
    elif mode == "winx":
        win = WinXMenu()
    elif mode == "settings":
        win = SettingsDialog(repo_root)
    elif mode == "winver":
        win = WinverDialog(repo_root)
    else:
        win = StartMenuFlyout(repo_root)

    signal.signal(signal.SIGTERM, lambda *_: (cleanup_state(), Gtk.main_quit()))
    win.show_flyout()
    Gtk.main()


if __name__ == "__main__":
    main()
