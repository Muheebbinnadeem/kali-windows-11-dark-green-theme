#!/usr/bin/env python3
"""
Windows 11 Dark Green Fluent Shell Suite — Made by Muheeb
Provides authentic Windows 11 flyouts for XFCE / Kali Linux:
  - start         : Centered Windows 11 Start Menu (Pinned, All Apps, Search, Recommended, Power)
  - search        : Centered Windows 11 Search Flyout
  - control       : Bottom-right Windows 11 Quick Settings / Control Center
  - notifications : Bottom-right two-card Windows 11 Notification Center + Interactive Calendar
  - widgets       : Bottom-left Windows 11 Widgets Board (Live CPU/RAM/Network & Muheeb Edition Card)
  - winver        : Windows 11 'About Windows' (winver) & Theme Info Dialog
"""
import calendar
import datetime
import getpass
import json
import os
import signal
import sqlite3
import subprocess
import sys
import time

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

# Dark Green Fluent Mica CSS
SHELL_CSS = b"""
* {
    font-family: "Inter", "Segoe UI", "Noto Sans", sans-serif;
    outline: none;
}
window.win11-flyout {
    background-color: transparent;
}
.mica-card {
    background-color: rgba(16, 26, 21, 0.96);
    border: 1px solid rgba(52, 211, 153, 0.24);
    border-radius: 12px;
    color: #ECFDF5;
}
.mica-footer {
    background-color: rgba(10, 17, 14, 0.96);
    border-top: 1px solid rgba(52, 211, 153, 0.16);
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
}
.search-pill {
    background-color: rgba(27, 42, 35, 0.95);
    border: 1px solid rgba(52, 211, 153, 0.28);
    border-bottom: 2px solid #10B981;
    border-radius: 20px;
    padding: 6px 14px;
    color: #ECFDF5;
    font-size: 13px;
    caret-color: #34D399;
}
.search-pill:focus {
    background-color: rgba(14, 23, 19, 0.98);
    border-bottom: 2px solid #34D399;
}
.section-title {
    font-size: 13px;
    font-weight: 700;
    color: #ECFDF5;
}
.muted-label {
    font-size: 11.5px;
    color: #9CAEA5;
}
.muheeb-badge {
    background-color: rgba(5, 150, 105, 0.24);
    border: 1px solid rgba(52, 211, 153, 0.42);
    border-radius: 99px;
    padding: 3px 10px;
    color: #34D399;
    font-size: 11px;
    font-weight: 700;
}
.pill-btn {
    background-color: rgba(34, 52, 43, 0.85);
    border: 1px solid rgba(52, 211, 153, 0.18);
    border-radius: 6px;
    padding: 4px 10px;
    color: #D1FAE5;
    font-size: 11.5px;
    font-weight: 600;
}
.pill-btn:hover {
    background-color: rgba(16, 185, 129, 0.24);
    border-color: rgba(52, 211, 153, 0.40);
}
.accent-btn {
    background-color: #059669;
    border: 1px solid #10B981;
    border-radius: 6px;
    padding: 6px 14px;
    color: #FFFFFF;
    font-size: 12px;
    font-weight: 700;
}
.accent-btn:hover {
    background-color: #10B981;
}
.app-tile {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 8px 4px;
    color: #ECFDF5;
}
.app-tile:hover {
    background-color: rgba(52, 211, 153, 0.12);
    border-color: rgba(52, 211, 153, 0.22);
}
.rec-row {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 6px 10px;
    color: #ECFDF5;
}
.rec-row:hover {
    background-color: rgba(52, 211, 153, 0.11);
    border-color: rgba(52, 211, 153, 0.18);
}
.qs-tile {
    background-color: rgba(30, 46, 38, 0.92);
    border: 1px solid rgba(52, 211, 153, 0.18);
    border-radius: 8px;
    min-height: 48px;
    color: #ECFDF5;
    font-size: 15px;
    font-weight: 600;
}
.qs-tile:hover {
    background-color: rgba(42, 64, 53, 0.96);
    border-color: rgba(52, 211, 153, 0.35);
}
.qs-tile-active {
    background-color: #059669;
    border: 1px solid #34D399;
    border-radius: 8px;
    min-height: 48px;
    color: #FFFFFF;
    font-size: 15px;
    font-weight: 700;
}
.qs-tile-active:hover {
    background-color: #10B981;
}
.qs-caption {
    font-size: 11px;
    color: #CBDBD3;
}
.notif-item {
    background-color: rgba(26, 40, 33, 0.90);
    border: 1px solid rgba(52, 211, 153, 0.16);
    border-radius: 8px;
    padding: 10px 12px;
}
.widget-subcard {
    background-color: rgba(24, 38, 31, 0.92);
    border: 1px solid rgba(52, 211, 153, 0.20);
    border-radius: 10px;
    padding: 12px;
}
.cal-day {
    background: transparent;
    border: none;
    border-radius: 18px;
    min-width: 34px;
    min-height: 34px;
    padding: 0;
    color: #E2F1EA;
    font-size: 12px;
}
.cal-day:hover {
    background-color: rgba(52, 211, 153, 0.16);
}
.cal-today {
    background-color: #059669;
    border: 1px solid #34D399;
    border-radius: 18px;
    min-width: 34px;
    min-height: 34px;
    padding: 0;
    color: #FFFFFF;
    font-weight: 700;
    font-size: 12px;
}
scale trough {
    background-color: rgba(45, 68, 57, 0.95);
    border-radius: 99px;
    min-height: 5px;
}
scale highlight {
    background-color: #10B981;
    border-radius: 99px;
    min-height: 5px;
}
scale slider {
    background-color: #34D399;
    border: 3px solid #12211A;
    border-radius: 99px;
    min-width: 18px;
    min-height: 18px;
    margin: -7px 0;
}
progressbar trough {
    background-color: rgba(40, 62, 51, 0.9);
    border-radius: 99px;
    min-height: 7px;
}
progressbar progress {
    background-color: #10B981;
    border-radius: 99px;
    min-height: 7px;
}
"""


def run_cmd(cmd, timeout=2.0):
    try:
        res = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return res.stdout.strip()
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


def handle_single_instance(mode):
    """Toggle off if same mode is open; replace if another mode is open."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            old_pid = int(data.get("pid", 0))
            old_mode = data.get("mode", "")
            if old_pid > 0:
                os.kill(old_pid, 0)  # check alive
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


def find_icon_pixbuf(icon_names, size=32):
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


def make_win11_logo_drawing(size=28):
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
            rad = 2.2
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
        else:  # dialog center
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
        GLib.timeout_add(80, self._check_focus_and_close)
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


class StartMenuFlyout(BaseFlyout):
    def __init__(self, repo_root, focus_search=False):
        super().__init__(640, 670, align="center")
        self.repo_root = repo_root
        self.all_apps = get_all_apps()

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        card.get_style_context().add_class("mica-card")
        self.add(card)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        body.set_margin_top(22)
        body.set_margin_start(26)
        body.set_margin_end(26)
        body.set_margin_bottom(14)
        card.pack_start(body, True, True, 0)

        # Search Bar
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("🔍   Search for apps, settings, and documents")
        self.search_entry.get_style_context().add_class("search-pill")
        self.search_entry.connect("changed", self.on_search_changed)
        self.search_entry.connect("activate", self.on_search_activate)
        body.pack_start(self.search_entry, False, False, 0)

        # Stack for Pinned vs All Apps vs Search Results
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(160)
        body.pack_start(self.stack, True, True, 0)

        self.stack.add_named(self._build_home_page(), "home")
        self.stack.add_named(self._build_all_apps_page(), "all")
        self.stack.add_named(self._build_search_page(), "search")

        # Power Strip (inline reveal so focus never leaves flyout)
        self.power_revealer = Gtk.Revealer()
        self.power_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        pbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        pbox.set_margin_start(26)
        pbox.set_margin_end(26)
        pbox.set_margin_bottom(8)
        pbox.set_halign(Gtk.Align.END)
        for lbl, cmd in [
            ("🔒 Lock", "xflock4"),
            ("🚪 Sign out", "xfce4-session-logout --logout"),
            ("🔄 Restart", "xfce4-session-logout --reboot"),
            ("⏻ Shut down", "xfce4-session-logout --halt"),
        ]:
            b = Gtk.Button(label=lbl)
            b.get_style_context().add_class("pill-btn")
            b.connect("clicked", lambda _, c=cmd: (spawn_detached(c), self.close_flyout()))
            pbox.pack_start(b, False, False, 0)
        self.power_revealer.add(pbox)
        card.pack_start(self.power_revealer, False, False, 0)

        # Bottom Mica Footer
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        footer.get_style_context().add_class("mica-footer")
        footer.set_size_request(-1, 60)
        footer.set_margin_top(2)

        f_inner = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        f_inner.set_margin_start(26)
        f_inner.set_margin_end(26)
        f_inner.set_valign(Gtk.Align.CENTER)
        footer.pack_start(f_inner, True, True, 0)

        user = getpass.getuser().capitalize()
        avatar = make_win11_logo_drawing(24)
        f_inner.pack_start(avatar, False, False, 0)

        u_lbl = Gtk.Label(label=user)
        u_lbl.get_style_context().add_class("section-title")
        f_inner.pack_start(u_lbl, False, False, 0)

        badge = Gtk.Label(label=f"★ {BRAND_AUTHOR}")
        badge.get_style_context().add_class("muheeb-badge")
        f_inner.pack_start(badge, False, False, 4)

        spacer = Gtk.Box()
        f_inner.pack_start(spacer, True, True, 0)

        for tip, txt, cmd in [
            ("File Explorer", "📁", "thunar"),
            ("About Win11 (Muheeb)", "ℹ️", f"python3 '{os.path.abspath(__file__)}' winver"),
            ("System Settings", "⚙️", "xfce4-settings-manager"),
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

        if focus_search:
            GLib.idle_add(self.search_entry.grab_focus)
        else:
            GLib.idle_add(pwr_btn.grab_focus)

    def _build_home_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        # Pinned Header
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        lbl = Gtk.Label(label="Pinned")
        lbl.get_style_context().add_class("section-title")
        hdr.pack_start(lbl, False, False, 4)

        all_btn = Gtk.Button(label="All apps  ›")
        all_btn.get_style_context().add_class("pill-btn")
        all_btn.connect("clicked", lambda *_: self.stack.set_visible_child_name("all"))
        hdr.pack_end(all_btn, False, False, 0)
        box.pack_start(hdr, False, False, 0)

        # Pinned Grid (6 cols x 3 rows)
        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_spacing(6)
        grid.set_column_spacing(6)

        icons_dir = os.path.join(self.repo_root, "assets", "icons")
        pinned_specs = [
            ("File Explorer", [os.path.join(icons_dir, "win11-explorer.svg"), "system-file-manager"], "thunar"),
            ("Terminal", [os.path.join(icons_dir, "win11-terminal.svg"), "utilities-terminal"], "qterminal || xfce4-terminal || x-terminal-emulator"),
            ("Brave / Web", ["brave-browser", "firefox-esr", "firefox", "web-browser"], "brave-browser || firefox || x-www-browser"),
            ("VS Code", ["code", "com.visualstudio.code", "accessories-text-editor"], "code || mousepad"),
            ("Settings", [os.path.join(icons_dir, "win11-settings.svg"), "preferences-system"], "xfce4-settings-manager"),
            ("About Win11", [os.path.join(icons_dir, "win11-start.svg")], f"python3 '{os.path.abspath(__file__)}' winver"),
            ("Control Bar", ["preferences-system-network", "network-wireless"], f"python3 '{os.path.abspath(__file__)}' control"),
            ("Notifications", ["preferences-system-notifications", "bell"], f"python3 '{os.path.abspath(__file__)}' notifications"),
            ("Widgets", [os.path.join(icons_dir, "win11-widgets.svg")], f"python3 '{os.path.abspath(__file__)}' widgets"),
            ("Task Manager", ["utilities-system-monitor", "org.xfce.taskmanager"], "xfce4-taskmanager"),
            ("Screenshot", ["applets-screenshooter", "org.xfce.screenshooter"], "xfce4-screenshooter"),
            ("Text Editor", ["org.xfce.mousepad", "accessories-text-editor"], "mousepad"),
            ("Downloads", ["folder-download", "folder-downloads"], f"thunar '{os.path.expanduser('~/Downloads')}'"),
            ("Documents", ["folder-documents"], f"thunar '{os.path.expanduser('~/Documents')}'"),
            ("Pictures", ["folder-pictures"], f"thunar '{os.path.expanduser('~/Pictures')}'"),
            ("Projects", ["folder-development", "folder"], f"thunar '{os.path.expanduser('~/projects')}'"),
            ("App Finder", ["org.xfce.appfinder", "system-search"], "xfce4-appfinder"),
            ("Kali Tweaks", ["kali-menu", "security-high"], "kali-tweaks || qterminal -e kali-tweaks"),
        ]

        for idx, (title, ic_list, cmd) in enumerate(pinned_specs):
            btn = Gtk.Button()
            btn.get_style_context().add_class("app-tile")
            vb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            vb.set_halign(Gtk.Align.CENTER)
            pb = find_icon_pixbuf(ic_list, 32)
            if pb:
                vb.pack_start(Gtk.Image.new_from_pixbuf(pb), False, False, 0)
            tl = Gtk.Label(label=title)
            tl.set_max_width_chars(12)
            tl.set_ellipsize(Pango.EllipsizeMode.END)
            tl.set_markup(f"<span size='9200'>{GLib.markup_escape_text(title)}</span>")
            vb.pack_start(tl, False, False, 0)
            btn.add(vb)
            btn.connect("clicked", lambda _, c=cmd: (spawn_detached(c), self.close_flyout()))
            grid.attach(btn, idx % 6, idx // 6, 1, 1)

        box.pack_start(grid, False, False, 0)

        # Recommended Header
        rhdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        rhdr.set_margin_top(6)
        rlbl = Gtk.Label(label="Recommended")
        rlbl.get_style_context().add_class("section-title")
        rhdr.pack_start(rlbl, False, False, 4)

        sub_tag = Gtk.Label(label=f"{BRAND_EDITION} • {BRAND_AUTHOR}")
        sub_tag.get_style_context().add_class("muted-label")
        rhdr.pack_end(sub_tag, False, False, 4)
        box.pack_start(rhdr, False, False, 0)

        rgrid = Gtk.Grid()
        rgrid.set_column_homogeneous(True)
        rgrid.set_column_spacing(12)
        rgrid.set_row_spacing(4)

        rec_items = [
            (
                "Windows 11 Dark Green Theme",
                f"{BRAND_AUTHOR} • System Edition",
                os.path.join(icons_dir, "win11-start.svg"),
                f"python3 '{os.path.abspath(__file__)}' winver",
            ),
            (
                "File Explorer — Quick Access",
                f"Pinned • {BRAND_AUTHOR}",
                os.path.join(icons_dir, "win11-explorer.svg"),
                "thunar",
            ),
            (
                "Window Theme Repository",
                "Open local Git repo folder",
                "folder-green",
                f"thunar '{self.repo_root}'",
            ),
            (
                "Kali Terminal (Win11 Styled)",
                "Command Prompt / ZSH",
                os.path.join(icons_dir, "win11-terminal.svg"),
                "qterminal || xfce4-terminal",
            ),
        ]

        for i, (rtitle, rsub, ricon, rcmd) in enumerate(rec_items):
            rbtn = Gtk.Button()
            rbtn.get_style_context().add_class("rec-row")
            hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            pb = find_icon_pixbuf([ricon, "folder"], 28)
            if pb:
                hb.pack_start(Gtk.Image.new_from_pixbuf(pb), False, False, 0)
            tvb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
            t1 = Gtk.Label(xalign=0)
            t1.set_markup(f"<span size='9500' weight='600'>{GLib.markup_escape_text(rtitle)}</span>")
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
        lbl = Gtk.Label(label="Best match & installed apps", xalign=0)
        lbl.get_style_context().add_class("section-title")
        box.pack_start(lbl, False, False, 0)

        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.search_results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        sc.add(self.search_results_box)
        box.pack_start(sc, True, True, 0)
        return box

    def _make_app_row(self, app):
        btn = Gtk.Button()
        btn.get_style_context().add_class("rec-row")
        hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        gicon = app.get_icon()
        img = Gtk.Image.new_from_gicon(gicon, Gtk.IconSize.LARGE_TOOLBAR) if gicon else Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)
        img.set_pixel_size(26)
        hb.pack_start(img, False, False, 0)

        vb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        nl = Gtk.Label(label=app.get_display_name(), xalign=0)
        vb.pack_start(nl, False, False, 0)
        desc = app.get_description()
        if desc:
            dl = Gtk.Label(label=desc, xalign=0)
            dl.set_max_width_chars(56)
            dl.set_ellipsize(Pango.EllipsizeMode.END)
            dl.get_style_context().add_class("muted-label")
            vb.pack_start(dl, False, False, 0)
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
        matches = [
            a
            for a in self.all_apps
            if q in (a.get_display_name() or "").lower()
            or q in (a.get_description() or "").lower()
            or q in (a.get_executable() or "").lower()
        ][:25]
        for app in matches:
            self.search_results_box.pack_start(self._make_app_row(app), False, False, 0)
        self.search_results_box.show_all()
        self.stack.set_visible_child_name("search")

    def on_search_activate(self, entry):
        children = self.search_results_box.get_children()
        if children:
            children[0].clicked()


class ControlCenterFlyout(BaseFlyout):
    """Windows 11 Quick Settings / Control Bar (Bottom-Right)."""

    def __init__(self):
        super().__init__(368, 456, align="right")

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        card.get_style_context().add_class("mica-card")
        self.add(card)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        body.set_margin_top(20)
        body.set_margin_start(20)
        body.set_margin_end(20)
        body.set_margin_bottom(16)
        card.pack_start(body, True, True, 0)

        # Header
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hl = Gtk.Label(label="Quick Settings")
        hl.get_style_context().add_class("section-title")
        hdr.pack_start(hl, False, False, 0)
        mb = Gtk.Label(label=BRAND_AUTHOR)
        mb.get_style_context().add_class("muheeb-badge")
        hdr.pack_end(mb, False, False, 0)
        body.pack_start(hdr, False, False, 0)

        # 3x2 Toggle Grid
        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_column_spacing(10)
        grid.set_row_spacing(12)

        wifi_on = "enabled" in run_cmd("nmcli radio wifi").lower()
        ssid = run_cmd("nmcli -t -f active,ssid dev wifi list --rescan no | grep '^yes:' | cut -d: -f2") or ("Wi-Fi" if wifi_on else "Off")
        dnd_on = run_cmd("xfconf-query -c xfce4-notifyd -p /do-not-disturb").lower() == "true"
        pwr_prof = run_cmd("powerprofilesctl get")
        saver_on = pwr_prof == "power-saver"
        nl_on = os.path.exists(NIGHTLIGHT_STATE)

        toggles = [
            ("📶", ssid[:12], wifi_on, self._toggle_wifi),
            ("ᛒ", "Bluetooth", True, self._toggle_bt),
            ("✈️", "Airplane mode", not wifi_on, self._toggle_airplane),
            ("🍃", "Energy saver", saver_on, self._toggle_saver),
            ("🌙", "Night light", nl_on, self._toggle_nightlight),
            ("🔕", "Do Not Disturb", dnd_on, self._toggle_dnd),
        ]

        for idx, (icon_txt, cap_txt, active, handler) in enumerate(toggles):
            cell = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            btn = Gtk.Button(label=icon_txt)
            btn.get_style_context().add_class("qs-tile-active" if active else "qs-tile")
            cap = Gtk.Label(label=cap_txt)
            cap.get_style_context().add_class("qs-caption")
            btn._active_state = active
            btn._caption = cap
            btn.connect("clicked", handler)
            cell.pack_start(btn, False, False, 0)
            cell.pack_start(cap, False, False, 0)
            grid.attach(cell, idx % 3, idx // 3, 1, 1)

        body.pack_start(grid, False, False, 0)

        # Brightness Slider
        b_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        b_lbl = Gtk.Label(label="☀️")
        b_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 25, 100, 1)
        b_scale.set_draw_value(False)
        b_scale.set_value(self._get_brightness())
        b_val = Gtk.Label(label=f"{int(b_scale.get_value())}%")
        b_val.get_style_context().add_class("muted-label")
        b_scale.connect("value-changed", self._on_brightness_changed, b_val)
        b_row.pack_start(b_lbl, False, False, 0)
        b_row.pack_start(b_scale, True, True, 0)
        b_row.pack_start(b_val, False, False, 0)
        body.pack_start(b_row, False, False, 4)

        # Volume Slider
        v_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        cur_vol = self._get_volume()
        v_btn = Gtk.Button(label="🔊")
        v_btn.get_style_context().add_class("pill-btn")
        v_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        v_scale.set_draw_value(False)
        v_scale.set_value(cur_vol)
        v_val = Gtk.Label(label=f"{cur_vol}%")
        v_val.get_style_context().add_class("muted-label")
        v_btn.connect("clicked", lambda *_: run_cmd("pactl set-sink-mute @DEFAULT_SINK@ toggle"))
        v_scale.connect("value-changed", self._on_volume_changed, v_val)
        v_row.pack_start(v_btn, False, False, 0)
        v_row.pack_start(v_scale, True, True, 0)
        v_row.pack_start(v_val, False, False, 0)
        body.pack_start(v_row, False, False, 0)

        # Footer Bar
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        footer.get_style_context().add_class("mica-footer")
        footer.set_size_request(-1, 52)
        f_in = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        f_in.set_margin_start(18)
        f_in.set_margin_end(18)
        f_in.set_valign(Gtk.Align.CENTER)
        footer.pack_start(f_in, True, True, 0)

        bat_str = self._get_battery_text()
        bat_lbl = Gtk.Label(label=bat_str)
        bat_lbl.get_style_context().add_class("muted-label")
        f_in.pack_start(bat_lbl, False, False, 0)

        f_in.pack_start(Gtk.Box(), True, True, 0)

        snd_btn = Gtk.Button(label="🎛️ Mixer")
        snd_btn.get_style_context().add_class("pill-btn")
        snd_btn.connect("clicked", lambda *_: (spawn_detached("pavucontrol || xfce4-settings-manager"), self.close_flyout()))
        f_in.pack_start(snd_btn, False, False, 0)

        set_btn = Gtk.Button(label="⚙️")
        set_btn.get_style_context().add_class("pill-btn")
        set_btn.connect("clicked", lambda *_: (spawn_detached("xfce4-settings-manager"), self.close_flyout()))
        f_in.pack_start(set_btn, False, False, 0)

        card.pack_end(footer, False, False, 0)

    def _flip_btn(self, btn, new_state):
        btn._active_state = new_state
        ctx = btn.get_style_context()
        ctx.remove_class("qs-tile")
        ctx.remove_class("qs-tile-active")
        ctx.add_class("qs-tile-active" if new_state else "qs-tile")

    def _toggle_wifi(self, btn):
        nxt = not btn._active_state
        run_cmd(f"nmcli radio wifi {'on' if nxt else 'off'}")
        btn._caption.set_text("Wi-Fi On" if nxt else "Wi-Fi Off")
        self._flip_btn(btn, nxt)

    def _toggle_bt(self, btn):
        nxt = not btn._active_state
        spawn_detached("blueman-manager")
        self._flip_btn(btn, nxt)

    def _toggle_airplane(self, btn):
        nxt = not btn._active_state
        run_cmd(f"nmcli radio all {'off' if nxt else 'on'}")
        self._flip_btn(btn, nxt)

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
        run_cmd(
            f"xfconf-query -c xfce4-notifyd -p /do-not-disturb -n -t bool -s {'true' if nxt else 'false'}"
        )
        self._flip_btn(btn, nxt)

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
                plug = "⚡" if b.power_plugged else "🔋"
                return f"{plug} {int(b.percent)}%"
        return "🔋 AC Power"


class NotificationCalendarFlyout(BaseFlyout):
    """Authentic two-card Windows 11 Notification Center (top) + Calendar (bottom)."""

    def __init__(self):
        super().__init__(368, 646, align="right")
        today = datetime.date.today()
        self.shown_year = today.year
        self.shown_month = today.month
        self.focus_mins = 30

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(outer)

        # --- TOP CARD: NOTIFICATIONS ---
        ncard = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        ncard.get_style_context().add_class("mica-card")
        ncard.set_size_request(-1, 252)

        n_in = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        n_in.set_margin_top(16)
        n_in.set_margin_bottom(14)
        n_in.set_margin_start(18)
        n_in.set_margin_end(18)
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
        self.notif_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self._populate_notifications()
        sc.add(self.notif_list)
        n_in.pack_start(sc, True, True, 0)

        outer.pack_start(ncard, True, True, 0)

        # --- BOTTOM CARD: CALENDAR & FOCUS ---
        ccard = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        ccard.get_style_context().add_class("mica-card")
        ccard.set_size_request(-1, 382)

        c_in = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        c_in.set_margin_top(16)
        c_in.set_margin_start(18)
        c_in.set_margin_end(18)
        c_in.set_margin_bottom(12)
        ccard.pack_start(c_in, True, True, 0)

        # Date Banner
        dhdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        dlbl = Gtk.Label(label=today.strftime("%A, %B %d"), xalign=0)
        dlbl.get_style_context().add_class("section-title")
        dhdr.pack_start(dlbl, False, False, 0)
        mb = Gtk.Label(label=BRAND_AUTHOR)
        mb.get_style_context().add_class("muheeb-badge")
        dhdr.pack_end(mb, False, False, 0)
        c_in.pack_start(dhdr, False, False, 0)

        # Month Switcher
        mhdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.month_lbl = Gtk.Label(xalign=0)
        self.month_lbl.get_style_context().add_class("muted-label")
        mhdr.pack_start(self.month_lbl, True, True, 0)

        prev_b = Gtk.Button(label="▲")
        prev_b.get_style_context().add_class("pill-btn")
        prev_b.connect("clicked", lambda *_: self._shift_month(-1))
        next_b = Gtk.Button(label="▼")
        next_b.get_style_context().add_class("pill-btn")
        next_b.connect("clicked", lambda *_: self._shift_month(1))
        mhdr.pack_start(prev_b, False, False, 0)
        mhdr.pack_start(next_b, False, False, 0)
        c_in.pack_start(mhdr, False, False, 0)

        self.cal_grid = Gtk.Grid()
        self.cal_grid.set_column_homogeneous(True)
        self.cal_grid.set_row_spacing(3)
        self.cal_grid.set_column_spacing(2)
        c_in.pack_start(self.cal_grid, True, True, 0)
        self._render_calendar()

        # Focus Session Footer
        ffoot = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        ffoot.get_style_context().add_class("mica-footer")
        ffoot.set_size_request(-1, 50)
        fin = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        fin.set_margin_start(18)
        fin.set_margin_end(18)
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

        fbtn = Gtk.Button(label="▶  Focus")
        fbtn.get_style_context().add_class("accent-btn")
        fbtn.connect("clicked", self._start_focus)
        fin.pack_start(fbtn, False, False, 0)

        ccard.pack_end(ffoot, False, False, 0)
        outer.pack_start(ccard, False, False, 0)

    def _populate_notifications(self):
        items = [
            (
                "Windows 11 Shell • Made by Muheeb",
                "Dark Green Edition active",
                "Taskbar, Explorer Nav Bar, Control Bar & Notification Center ready.",
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
                    rows = cur.execute(
                        f"SELECT {app_col}, {sum_col}, {body_col} FROM {t} ORDER BY rowid DESC LIMIT 6"
                    ).fetchall()
                    for a, s, b in rows:
                        if s:
                            items.append((a or "System", s, b or ""))
                con.close()
            except Exception:
                pass

        for app_name, summary, body in items:
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
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
        empty.set_margin_top(60)
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
        cal = calendar.Calendar(firstweekday=6)  # Sunday first like Win11
        for col, dname in enumerate(["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]):
            dl = Gtk.Label(label=dname)
            dl.get_style_context().add_class("muted-label")
            self.cal_grid.attach(dl, col, 0, 1, 1)

        today = datetime.date.today()
        weeks = cal.monthdayscalendar(self.shown_year, self.shown_month)
        for r_idx, week in enumerate(weeks, start=1):
            for c_idx, day in enumerate(week):
                if day == 0:
                    self.cal_grid.attach(Gtk.Label(label=""), c_idx, r_idx, 1, 1)
                else:
                    b = Gtk.Button(label=str(day))
                    is_today = (
                        day == today.day
                        and self.shown_month == today.month
                        and self.shown_year == today.year
                    )
                    b.get_style_context().add_class("cal-today" if is_today else "cal-day")
                    self.cal_grid.attach(b, c_idx, r_idx, 1, 1)
        self.cal_grid.show_all()

    def _adj_focus(self, delta):
        self.focus_mins = max(15, min(180, self.focus_mins + delta))
        self.focus_lbl.set_text(f"{self.focus_mins} mins")

    def _start_focus(self, *_):
        run_cmd("xfconf-query -c xfce4-notifyd -p /do-not-disturb -n -t bool -s true")
        spawn_detached(
            f"notify-send 'Focus Session ({self.focus_mins}m)' 'Do Not Disturb enabled • {BRAND_AUTHOR}'"
        )
        self.close_flyout()


class WidgetsFlyout(BaseFlyout):
    """Windows 11 Left Widgets Board."""

    def __init__(self):
        super().__init__(480, 640, align="left")
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        card.get_style_context().add_class("mica-card")
        self.add(card)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        body.set_margin_top(20)
        body.set_margin_bottom(20)
        body.set_margin_start(22)
        body.set_margin_end(22)
        card.pack_start(body, True, True, 0)

        # Top Clock & Badge
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        now = datetime.datetime.now().strftime("%I:%M %p")
        tl = Gtk.Label(xalign=0)
        tl.set_markup(f"<span size='15000' weight='700'>{now}</span>")
        hdr.pack_start(tl, False, False, 0)
        mb = Gtk.Label(label=f"★ {BRAND_AUTHOR}")
        mb.get_style_context().add_class("muheeb-badge")
        hdr.pack_end(mb, False, False, 0)
        body.pack_start(hdr, False, False, 0)

        # Signature Hero Card
        hero = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        hero.get_style_context().add_class("widget-subcard")
        hero.pack_start(make_win11_logo_drawing(40), False, False, 4)
        hvb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        h1 = Gtk.Label(xalign=0)
        h1.set_markup(f"<span size='12000' weight='700' color='#34D399'>{BRAND_EDITION}</span>")
        h2 = Gtk.Label(label=f"Custom Kali Linux Desktop • {BRAND_AUTHOR}", xalign=0)
        h2.get_style_context().add_class("muted-label")
        hvb.pack_start(h1, False, False, 0)
        hvb.pack_start(h2, False, False, 0)
        hero.pack_start(hvb, True, True, 0)
        body.pack_start(hero, False, False, 0)

        # System Resource Card
        scard = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        scard.get_style_context().add_class("widget-subcard")
        st = Gtk.Label(label="System Performance (Live)", xalign=0)
        st.get_style_context().add_class("section-title")
        scard.pack_start(st, False, False, 0)

        cpu_p = psutil.cpu_percent(interval=0.05) if psutil else 18.0
        mem_p = psutil.virtual_memory().percent if psutil else 42.0
        dsk_p = psutil.disk_usage("/").percent if psutil else 35.0
        for name, pct in [("CPU Load", cpu_p), ("Memory (RAM)", mem_p), ("Disk (/)", dsk_p)]:
            r = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
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

        # Network & Host Card
        ncard = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        ncard.get_style_context().add_class("widget-subcard")
        nt = Gtk.Label(label="Kali Network & Environment", xalign=0)
        nt.get_style_context().add_class("section-title")
        ncard.pack_start(nt, False, False, 0)
        ip = run_cmd("hostname -I | awk '{print $1}'") or "127.0.0.1"
        kern = run_cmd("uname -r")
        for k, v in [("Local IP", ip), ("Kernel", kern), ("Builder", BRAND_AUTHOR)]:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            kl = Gtk.Label(label=k, xalign=0)
            kl.get_style_context().add_class("muted-label")
            vl = Gtk.Label(label=v, xalign=1)
            row.pack_start(kl, True, True, 0)
            row.pack_end(vl, False, False, 0)
            ncard.pack_start(row, False, False, 0)
        body.pack_start(ncard, False, False, 0)

        # Quick Explorer Shortcuts
        qbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for lbl, path in [
            ("📁 Home", os.path.expanduser("~")),
            ("⬇️ Downloads", os.path.expanduser("~/Downloads")),
            ("💻 Projects", os.path.expanduser("~/projects")),
        ]:
            b = Gtk.Button(label=lbl)
            b.get_style_context().add_class("pill-btn")
            b.connect("clicked", lambda _, p=path: (spawn_detached(f"thunar '{p}'"), self.close_flyout()))
            qbox.pack_start(b, True, True, 0)
        body.pack_end(qbox, False, False, 0)


class WinverDialog(BaseFlyout):
    """Authentic Windows 11 'winver' About Dialog — Made by Muheeb."""

    def __init__(self, repo_root):
        super().__init__(480, 390, align="dialog", close_on_blur=False)
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        card.get_style_context().add_class("mica-card")
        self.add(card)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        body.set_margin_top(24)
        body.set_margin_bottom(20)
        body.set_margin_start(28)
        body.set_margin_end(28)
        card.pack_start(body, True, True, 0)

        # Header Logo
        lh = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        lh.set_halign(Gtk.Align.CENTER)
        lh.pack_start(make_win11_logo_drawing(42), False, False, 0)
        lt = Gtk.Label()
        lt.set_markup("<span size='22000' weight='700' color='#ECFDF5'>Windows 11</span>")
        lh.pack_start(lt, False, False, 0)
        body.pack_start(lh, False, False, 4)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        body.pack_start(sep, False, False, 4)

        info = Gtk.Label(xalign=0)
        info.set_line_wrap(True)
        info.set_markup(
            f"<span weight='700' size='11500' color='#34D399'>{BRAND_EDITION}</span>\n"
            f"Version 24H2 (OS Build 26100.Muheeb • Kali GNU/Linux Rolling)\n\n"
            f"Crafted &amp; Engineered by: <b>{BRAND_AUTHOR}</b>\n"
            "Includes Windows 11 Centered Taskbar, Fluent Explorer Navigation Bar,\n"
            "Quick Settings Control Bar, Notification Center &amp; Dark Green Mica UI."
        )
        body.pack_start(info, True, True, 0)

        brow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        exp_b = Gtk.Button(label="📁 Open Explorer")
        exp_b.get_style_context().add_class("pill-btn")
        exp_b.connect("clicked", lambda *_: (spawn_detached("thunar"), self.close_flyout()))
        brow.pack_start(exp_b, False, False, 0)

        brow.pack_start(Gtk.Box(), True, True, 0)

        ok_b = Gtk.Button(label="OK")
        ok_b.set_size_request(96, 34)
        ok_b.get_style_context().add_class("accent-btn")
        ok_b.connect("clicked", lambda *_: self.close_flyout())
        brow.pack_end(ok_b, False, False, 0)
        body.pack_end(brow, False, False, 0)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "start"
    handle_single_instance(mode)

    provider = Gtk.CssProvider()
    provider.load_from_data(SHELL_CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if mode == "start":
        win = StartMenuFlyout(repo_root, focus_search=False)
    elif mode == "search":
        win = StartMenuFlyout(repo_root, focus_search=True)
    elif mode == "control":
        win = ControlCenterFlyout()
    elif mode == "notifications":
        win = NotificationCalendarFlyout()
    elif mode == "widgets":
        win = WidgetsFlyout()
    elif mode == "winver":
        win = WinverDialog(repo_root)
    else:
        win = StartMenuFlyout(repo_root)

    signal.signal(signal.SIGTERM, lambda *_: (cleanup_state(), Gtk.main_quit()))
    win.show_flyout()
    Gtk.main()


if __name__ == "__main__":
    main()
