#!/usr/bin/env python3
"""
Native Windows 11 Pro Taskbar Engine — 125% Display Scale Edition (Made by Muheeb)
Built with GTK3 + Wnck 3.0 + Cairo + X11 Non-Focusing Dock Struts.

Key Engineering Guarantees:
  - set_accept_focus(False) & set_focus_on_map(False): clicking taskbar NEVER steals focus
    from active apps or open flyouts — so clicking an open app minimizes/restores cleanly,
    and clicking Start / Search / Quick Settings / Clock toggles open & closed 100% reliably!
  - True 125% Windows 11 Proportions: 56px taskbar height, 28px crisp app icons, 48x44px slots,
    13px crisp tray text, 18px monochrome Fluent tray icons, subtle press-bounce animation.
  - Zero '⋮⋮' handles, flush 0..1920px width, merged Pinned + Running apps, upward '⌃' chevron.
"""
import datetime
import json
import math
import os
import signal
import subprocess
import sys

import cairo
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkX11", "3.0")
gi.require_version("Wnck", "3.0")
from gi.repository import Gdk, GdkPixbuf, GdkX11, GLib, Gtk, Wnck

try:
    import psutil
except ImportError:
    psutil = None

# 125% Windows 11 Taskbar Metrics (45px * 1.25 = 56px, 24px * 1.2 = 28px icons)
BAR_HEIGHT = 56
SLOT_W = 48
SLOT_H = 46
ICON_PX = 28

SETTINGS_PATH = os.path.expanduser("~/.config/win11-muheeb/settings.json")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHELL_PY = os.path.join(REPO_ROOT, "shell", "win11_shell.py")
ICONS_DIR = os.path.join(REPO_ROOT, "assets", "icons")

TASKBAR_CSS = b"""
* {
    font-family: "Inter", "Segoe UI", sans-serif;
    outline: none;
}
window.win11-dock {
    background-color: transparent;
}
menu {
    background-color: #14221C;
    border: 1px solid rgba(52, 211, 153, 0.30);
    border-radius: 8px;
    padding: 6px;
    color: #ECFDF5;
    font-size: 10.5pt;
}
menuitem {
    border-radius: 5px;
    padding: 7px 14px;
}
menuitem:hover {
    background-color: rgba(16, 185, 129, 0.26);
    color: #FFFFFF;
}
"""


def spawn(cmd):
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


def run_short(cmd):
    try:
        return subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=0.9
        ).stdout.strip()
    except Exception:
        return ""


def load_settings():
    defaults = {
        "search_style": "box",
        "search_label": "Search",
        "search_gleam": True,
    }
    try:
        if os.path.isfile(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                defaults.update(json.load(f))
    except Exception:
        pass
    return defaults


def rounded_rect(ctx, x, y, w, h, r):
    if w <= 0 or h <= 0:
        return
    r = min(r, w / 2.0, h / 2.0)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def load_scaled_pixbuf(candidates, size=ICON_PX):
    theme = Gtk.IconTheme.get_default()
    for c in candidates:
        if not c:
            continue
        if os.path.isfile(c):
            try:
                return GdkPixbuf.Pixbuf.new_from_file_at_scale(c, size, size, True)
            except Exception:
                pass
        if theme.has_icon(c):
            try:
                return theme.load_icon(c, size, Gtk.IconLookupFlags.FORCE_SIZE)
            except Exception:
                pass
    try:
        return theme.load_icon("application-x-executable", size, Gtk.IconLookupFlags.FORCE_SIZE)
    except Exception:
        return None


class HoverCanvas(Gtk.EventBox):
    def __init__(self, width, height, tooltip="", on_click=None, on_right_click=None, on_scroll=None):
        super().__init__()
        self.set_visible_window(False)
        self.set_can_focus(False)
        self.set_size_request(width, height)
        self.hovered = False
        self.pressed = False
        self._on_click = on_click
        self._on_right_click = on_right_click
        if tooltip:
            self.set_tooltip_text(tooltip)

        self.area = Gtk.DrawingArea()
        self.area.set_can_focus(False)
        self.area.set_size_request(width, height)
        self.area.connect("draw", self._draw_wrapper)
        self.add(self.area)

        self.add_events(
            Gdk.EventMask.ENTER_NOTIFY_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
            | Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.SCROLL_MASK
        )
        self.connect("enter-notify-event", self._on_enter)
        self.connect("leave-notify-event", self._on_leave)
        self.connect("button-press-event", self._on_btn_press)
        self.connect("button-release-event", self._on_btn_release)
        if on_scroll:
            self.connect("scroll-event", on_scroll)

    def _on_enter(self, *_):
        self.hovered = True
        self.area.queue_draw()
        return False

    def _on_leave(self, *_):
        self.hovered = False
        self.pressed = False
        self.area.queue_draw()
        return False

    def _on_btn_press(self, _, event):
        if event.button == 1:
            self.pressed = True
            self.area.queue_draw()
            return True
        if event.button == 3 and self._on_right_click:
            self._on_right_click(event)
            return True
        return False

    def _on_btn_release(self, widget, event):
        if event.button == 1 and self.pressed:
            self.pressed = False
            self.area.queue_draw()
            alloc = widget.get_allocation()
            if 0 <= event.x <= alloc.width and 0 <= event.y <= alloc.height:
                if self._on_click:
                    self._on_click(event)
            return True
        return False

    def draw_hover_bg(self, ctx, w, h, radius=6.0, active_bg=False):
        if self.pressed:
            rounded_rect(ctx, 1, 1, w - 2, h - 2, radius)
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.05)
            ctx.fill()
        elif self.hovered:
            rounded_rect(ctx, 1, 1, w - 2, h - 2, radius)
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.09)
            ctx.fill_preserve()
            ctx.set_line_width(1.0)
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.08)
            ctx.stroke()
        elif active_bg:
            rounded_rect(ctx, 1, 1, w - 2, h - 2, radius)
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.07)
            ctx.fill_preserve()
            ctx.set_line_width(1.0)
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.05)
            ctx.stroke()

    def _draw_wrapper(self, widget, ctx):
        alloc = widget.get_allocation()
        self.on_draw(ctx, alloc.width, alloc.height)
        return False

    def on_draw(self, ctx, w, h):
        pass


class AppDockSlot(HoverCanvas):
    def __init__(self, wnck_screen, title, pixbuf, launch_cmd=None, windows=None):
        super().__init__(
            SLOT_W,
            SLOT_H,
            tooltip=title,
            on_click=self._handle_left,
            on_right_click=self._handle_right,
        )
        self.wnck_screen = wnck_screen
        self.title = title
        self.pixbuf = pixbuf
        self.launch_cmd = launch_cmd
        self.windows = windows or []
        self.is_focused = False

    def update_state(self, windows, active_win, fallback_pixbuf=None):
        self.windows = windows
        self.is_focused = any(w == active_win for w in windows) if active_win else False
        if not self.pixbuf and fallback_pixbuf:
            self.pixbuf = fallback_pixbuf
        if windows:
            names = [w.get_name() for w in windows if w.get_name()]
            self.set_tooltip_text(names[0] if len(names) == 1 else f"{self.title} ({len(windows)} windows)")
        else:
            self.set_tooltip_text(self.title)
        self.area.queue_draw()

    def _activate_win(self, w, ts):
        ws = w.get_workspace()
        if ws and ws != self.wnck_screen.get_active_workspace():
            ws.activate(ts)
        if w.is_minimized():
            w.unminimize(ts)
        w.activate(ts)

    def _handle_left(self, event):
        ts = event.time or Gdk.CURRENT_TIME
        if not self.windows:
            if self.launch_cmd:
                spawn(self.launch_cmd)
            return

        active_now = self.wnck_screen.get_active_window()
        if len(self.windows) == 1:
            w = self.windows[0]
            if w == active_now and not w.is_minimized():
                w.minimize()
            else:
                self._activate_win(w, ts)
        else:
            idx = -1
            for i, w in enumerate(self.windows):
                if w == active_now and not w.is_minimized():
                    idx = i
                    break
            if idx == -1:
                self._activate_win(self.windows[0], ts)
            else:
                nxt = self.windows[(idx + 1) % len(self.windows)]
                self._activate_win(nxt, ts)

    def _handle_right(self, event):
        menu = Gtk.Menu()
        for w in self.windows:
            title = (w.get_name() or self.title)[:44]
            mi = Gtk.MenuItem(label=f"❐  {title}")
            mi.connect("activate", lambda _, win=w: self._activate_win(win, Gdk.CURRENT_TIME))
            menu.append(mi)

        if self.windows and self.launch_cmd:
            menu.append(Gtk.SeparatorMenuItem())

        if self.launch_cmd:
            ni = Gtk.MenuItem(label=f"➕  New {self.title} window")
            ni.connect("activate", lambda *_: spawn(self.launch_cmd))
            menu.append(ni)

        if self.windows:
            ci = Gtk.MenuItem(label="✕  Close window" if len(self.windows) == 1 else f"✕  Close all ({len(self.windows)})")
            ci.connect("activate", lambda *_: [win.close(Gdk.CURRENT_TIME) for win in list(self.windows)])
            menu.append(ci)

        menu.show_all()
        menu.popup_at_pointer(event)

    def on_draw(self, ctx, w, h):
        if len(self.windows) > 1 and (self.is_focused or self.hovered):
            rounded_rect(ctx, 5, 3, w - 6, h - 6, 6.0)
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.05)
            ctx.fill()

        self.draw_hover_bg(ctx, w - (2 if len(self.windows) > 1 else 0), h, radius=6.0, active_bg=self.is_focused)

        if self.pixbuf:
            bounce_y = 1.5 if self.pressed else 0.0
            ix = (w - self.pixbuf.get_width()) / 2.0
            iy = (h - self.pixbuf.get_height()) / 2.0 - (1.5 if self.windows else 0.0) + bounce_y
            Gdk.cairo_set_source_pixbuf(ctx, self.pixbuf, ix, iy)
            ctx.paint()

        if self.is_focused:
            pw, ph = 18.0, 3.5
            rounded_rect(ctx, (w - pw) / 2.0, h - ph - 1.5, pw, ph, 1.75)
            ctx.set_source_rgba(0.20, 0.83, 0.60, 1.0)
            ctx.fill()
        elif self.windows:
            pw, ph = 7.0, 3.5
            rounded_rect(ctx, (w - pw) / 2.0, h - ph - 1.5, pw, ph, 1.75)
            ctx.set_source_rgba(0.74, 0.84, 0.79, 0.80)
            ctx.fill()


class WidgetsButton(HoverCanvas):
    def __init__(self):
        super().__init__(
            144,
            SLOT_H,
            tooltip="Widgets Board (Win+W) • Made by Muheeb",
            on_click=lambda *_: spawn(f"python3 '{SHELL_PY}' widgets"),
        )

    def on_draw(self, ctx, w, h):
        self.draw_hover_bg(ctx, w, h, radius=6.0)
        cy = h / 2.0

        ctx.arc(18, cy - 3.5, 6.4, 0, 2 * math.pi)
        ctx.set_source_rgba(0.99, 0.80, 0.20, 0.98)
        ctx.fill()

        rounded_rect(ctx, 14.0, cy - 1.2, 20.0, 10.2, 5.1)
        ctx.set_source_rgba(0.93, 0.98, 0.95, 0.98)
        ctx.fill()
        ctx.arc(21.0, cy - 1.2, 5.5, 0, 2 * math.pi)
        ctx.fill()

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(13.2)
        ctx.set_source_rgba(0.95, 0.99, 0.97, 0.97)
        ctx.move_to(42, cy - 2.0)
        ctx.show_text("24°C")

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(12.0)
        ctx.set_source_rgba(0.20, 0.83, 0.60, 0.96)
        ctx.move_to(42, cy + 12.5)
        ctx.show_text("Muheeb")


class SearchPillWidget(HoverCanvas):
    def __init__(self):
        self.cfg = load_settings()
        self._last_mtime = 0
        w = self._calc_width()
        super().__init__(
            w,
            SLOT_H,
            tooltip="Search (Win+S) • Customize inside Search",
            on_click=lambda *_: spawn(f"python3 '{SHELL_PY}' search"),
        )
        self._sync_visibility()

    def _calc_width(self):
        st = self.cfg.get("search_style", "box")
        if st == "box":
            return 212
        if st == "compact":
            return 114
        if st == "icon":
            return SLOT_W
        return 0

    def _sync_visibility(self):
        w = self._calc_width()
        if w == 0:
            self.hide()
        else:
            self.set_size_request(w, SLOT_H)
            self.area.set_size_request(w, SLOT_H)
            self.show_all()

    def poll_config(self):
        try:
            st = os.stat(SETTINGS_PATH).st_mtime if os.path.isfile(SETTINGS_PATH) else 0
            if st != self._last_mtime:
                self._last_mtime = st
                self.cfg = load_settings()
                self._sync_visibility()
                self.area.queue_draw()
        except Exception:
            pass
        return True

    def on_draw(self, ctx, w, h):
        style = self.cfg.get("search_style", "box")
        label = self.cfg.get("search_label", "Search") or "Search"
        cy = h / 2.0

        if style == "icon":
            self.draw_hover_bg(ctx, w, h, radius=6.0)
            ctx.set_source_rgba(0.94, 0.99, 0.96, 0.95)
            ctx.set_line_width(1.9)
            ctx.arc(w / 2.0 - 1.8, cy - 1.8, 7.2, 0, 2 * math.pi)
            ctx.stroke()
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(w / 2.0 + 3.5, cy + 3.5)
            ctx.line_to(w / 2.0 + 8.8, cy + 8.8)
            ctx.stroke()
            return

        bh = 37.0
        by = (h - bh) / 2.0
        rounded_rect(ctx, 2.0, by, w - 4.0, bh, bh / 2.0)
        if self.hovered:
            ctx.set_source_rgba(0.17, 0.27, 0.22, 0.98)
        else:
            ctx.set_source_rgba(0.14, 0.22, 0.18, 0.96)
        ctx.fill_preserve()

        ctx.set_line_width(1.1)
        if self.hovered:
            ctx.set_source_rgba(0.20, 0.83, 0.60, 0.58)
        else:
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.14)
        ctx.stroke()

        ctx.set_source_rgba(0.92, 0.98, 0.95, 0.94)
        ctx.set_line_width(1.75)
        ctx.arc(21.0, cy - 1.2, 5.8, 0, 2 * math.pi)
        ctx.stroke()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(25.3, cy + 3.1)
        ctx.line_to(29.8, cy + 7.6)
        ctx.stroke()

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(13.6)
        ascent, descent, _, _, _ = ctx.font_extents()
        ctx.set_source_rgba(0.80, 0.88, 0.84, 0.94)
        ctx.move_to(39.0, (h - ascent - descent) / 2.0 + ascent)
        ctx.show_text(label[:15])

        if style == "box" and self.cfg.get("search_gleam", True):
            gx = w - 22.0
            ctx.arc(gx, cy, 8.8, 0, 2 * math.pi)
            ctx.set_source_rgba(0.06, 0.73, 0.51, 0.26)
            ctx.fill()
            ctx.arc(gx - 1.8, cy - 1.2, 3.0, 0, 2 * math.pi)
            ctx.set_source_rgba(0.20, 0.83, 0.60, 0.96)
            ctx.fill()
            ctx.arc(gx + 2.6, cy + 1.8, 2.0, 0, 2 * math.pi)
            ctx.set_source_rgba(0.75, 0.98, 0.88, 0.94)
            ctx.fill()


class ChevronTrayButton(HoverCanvas):
    def __init__(self):
        super().__init__(
            32,
            SLOT_H,
            tooltip="Show quick system tools",
            on_click=self._open_menu,
        )

    def _open_menu(self, event):
        menu = Gtk.Menu()
        for lbl, cmd in [
            ("📶  Wi-Fi & Bluetooth (Win+A)", f"python3 '{SHELL_PY}' control"),
            ("✂️  Snipping Tool (Win+Shift+S)", f"python3 '{SHELL_PY}' snip"),
            ("⚡  Power User Menu (Win+X)", f"python3 '{SHELL_PY}' winx"),
            ("📊  Task Manager (Ctrl+Shift+Esc)", "xfce4-taskmanager"),
            ("📋  Clipboard History (Win+V)", "xfce4-popup-clipman"),
            ("⚙️  Win11 Settings (Win+I)", f"python3 '{SHELL_PY}' settings"),
            ("ℹ️  About Windows 11 (Made by Muheeb)", f"python3 '{SHELL_PY}' winver"),
        ]:
            mi = Gtk.MenuItem(label=lbl)
            mi.connect("activate", lambda _, c=cmd: spawn(c))
            menu.append(mi)
        menu.show_all()
        menu.popup_at_pointer(event)

    def on_draw(self, ctx, w, h):
        self.draw_hover_bg(ctx, w, h, radius=6.0)
        cx, cy = w / 2.0, h / 2.0
        ctx.set_source_rgba(0.93, 0.98, 0.95, 0.92)
        ctx.set_line_width(1.75)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.move_to(cx - 5.2, cy + 2.4)
        ctx.line_to(cx, cy - 2.8)
        ctx.line_to(cx + 5.2, cy + 2.4)
        ctx.stroke()


class LangTrayButton(HoverCanvas):
    def __init__(self):
        super().__init__(
            44,
            SLOT_H,
            tooltip="English (United States)\nClick for Display Scale & Search Settings (Win+I)",
            on_click=lambda *_: spawn(f"python3 '{SHELL_PY}' settings"),
        )

    def on_draw(self, ctx, w, h):
        self.draw_hover_bg(ctx, w, h, radius=6.0)
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(12.2)
        ctx.set_source_rgba(0.94, 0.98, 0.96, 0.95)
        for txt, dy in (("ENG", -2.5), ("US", 12.2)):
            ext = ctx.text_extents(txt)
            ctx.move_to((w - ext.width) / 2.0, h / 2.0 + dy)
            ctx.show_text(txt)


class QuickSettingsPill(HoverCanvas):
    def __init__(self):
        super().__init__(
            102,
            SLOT_H,
            tooltip="Quick Settings (Win+A)",
            on_click=lambda *_: spawn(f"python3 '{SHELL_PY}' control"),
            on_scroll=self._on_wheel,
        )
        self.wifi_on = True
        self.muted = False
        self.vol = 70
        self.pct = 85
        self.plugged = False
        self.refresh_status()

    def _on_wheel(self, _, event):
        if event.direction == Gdk.ScrollDirection.UP:
            spawn("pactl set-sink-volume @DEFAULT_SINK@ +4%")
            self.vol = min(100, self.vol + 4)
            self.area.queue_draw()
        elif event.direction == Gdk.ScrollDirection.DOWN:
            spawn("pactl set-sink-volume @DEFAULT_SINK@ -4%")
            self.vol = max(0, self.vol - 4)
            self.area.queue_draw()
        return True

    def refresh_status(self):
        self.wifi_on = "enabled" in run_short("nmcli radio wifi").lower()
        ssid = run_short("nmcli -t -f active,ssid dev wifi list --rescan no | grep '^yes:' | cut -d: -f2") or ("Wi-Fi" if self.wifi_on else "Off")
        self.muted = "yes" in run_short("pactl get-sink-mute @DEFAULT_SINK@").lower()
        vol_out = run_short("pactl get-sink-volume @DEFAULT_SINK@")
        for t in vol_out.split():
            if t.endswith("%"):
                try:
                    self.vol = int(t[:-1])
                    break
                except ValueError:
                    pass
        if psutil and hasattr(psutil, "sensors_battery"):
            b = psutil.sensors_battery()
            if b:
                self.pct, self.plugged = int(b.percent), bool(b.power_plugged)
        self.set_tooltip_text(f"{ssid}  •  Sound: {self.vol}%  •  Battery: {self.pct}%\nScroll to adjust volume • Click for Quick Settings (Win+A)")
        self.area.queue_draw()
        return True

    def on_draw(self, ctx, w, h):
        self.draw_hover_bg(ctx, w, h, radius=6.0)
        cy = h / 2.0

        # 1. Wi-Fi (x=19)
        ctx.save()
        ctx.set_source_rgba(0.95, 0.99, 0.97, 0.96 if self.wifi_on else 0.42)
        ctx.set_line_width(1.75)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        by = cy + 5.8
        for r in (4.0, 7.6, 11.2):
            ctx.new_sub_path()
            ctx.arc(19.0, by, r, -math.pi * 0.76, -math.pi * 0.24)
            ctx.stroke()
        ctx.arc(19.0, by + 0.2, 1.55, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()

        # 2. Speaker (x=49)
        ctx.save()
        ctx.set_source_rgba(0.95, 0.99, 0.97, 0.96)
        ctx.set_line_width(1.65)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        sx = 42.0
        ctx.move_to(sx, cy - 2.6)
        ctx.line_to(sx + 3.0, cy - 2.6)
        ctx.line_to(sx + 7.2, cy - 6.2)
        ctx.line_to(sx + 7.2, cy + 6.2)
        ctx.line_to(sx + 3.0, cy + 2.6)
        ctx.line_to(sx, cy + 2.6)
        ctx.close_path()
        ctx.stroke()
        if self.muted or self.vol == 0:
            ctx.move_to(sx + 9.5, cy - 2.8)
            ctx.line_to(sx + 14.0, cy + 2.8)
            ctx.move_to(sx + 14.0, cy - 2.8)
            ctx.line_to(sx + 9.5, cy + 2.8)
            ctx.stroke()
        else:
            ctx.new_sub_path()
            ctx.arc(sx + 7.4, cy, 3.8, -0.68, 0.68)
            ctx.stroke()
            if self.vol > 35:
                ctx.new_sub_path()
                ctx.arc(sx + 7.4, cy, 6.8, -0.72, 0.72)
                ctx.stroke()
        ctx.restore()

        # 3. Battery (x=79)
        ctx.save()
        bw, bh = 20.0, 11.0
        bx = 70.0
        btop = cy - bh / 2.0
        ctx.set_source_rgba(0.95, 0.99, 0.97, 0.94)
        ctx.set_line_width(1.5)
        rounded_rect(ctx, bx, btop, bw, bh, 2.5)
        ctx.stroke()

        ctx.move_to(bx + bw + 1.8, cy - 2.4)
        ctx.line_to(bx + bw + 1.8, cy + 2.4)
        ctx.set_line_width(1.8)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()

        fw = max(2.2, (bw - 4.4) * max(0.08, min(1.0, self.pct / 100.0)))
        if self.plugged:
            ctx.set_source_rgba(0.20, 0.83, 0.60, 0.98)
        else:
            ctx.set_source_rgba(0.95, 0.99, 0.97, 0.96)
        rounded_rect(ctx, bx + 2.2, btop + 2.2, fw, bh - 4.4, 1.1)
        ctx.fill()
        ctx.restore()


class ClockBellPill(HoverCanvas):
    def __init__(self):
        super().__init__(
            122,
            SLOT_H,
            tooltip="Notifications & Calendar (Win+N) • Made by Muheeb",
            on_click=lambda *_: spawn(f"python3 '{SHELL_PY}' notifications"),
        )
        self.dnd = False

    def refresh_clock(self):
        self.dnd = run_short("xfconf-query -c xfce4-notifyd -p /do-not-disturb").lower() == "true"
        now = datetime.datetime.now()
        self.set_tooltip_text(f"{now.strftime('%A, %B %d, %Y')}\nNotifications & Calendar (Win+N) • Made by Muheeb")
        self.area.queue_draw()
        return True

    def on_draw(self, ctx, w, h):
        self.draw_hover_bg(ctx, w, h, radius=6.0)
        now = datetime.datetime.now()
        t_str = now.strftime("%I:%M %p").lstrip("0")
        d_str = now.strftime("%m/%d/%Y")

        right_x = w - 28.0
        cy = h / 2.0

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(13.0)
        ctx.set_source_rgba(0.95, 0.99, 0.97, 0.97)
        ext1 = ctx.text_extents(t_str)
        ctx.move_to(right_x - ext1.width, cy - 2.5)
        ctx.show_text(t_str)

        ctx.set_font_size(12.2)
        ctx.set_source_rgba(0.82, 0.90, 0.86, 0.92)
        ext2 = ctx.text_extents(d_str)
        ctx.move_to(right_x - ext2.width, cy + 12.5)
        ctx.show_text(d_str)

        bx = w - 13.0
        ctx.set_source_rgba(0.94, 0.98, 0.96, 0.94 if not self.dnd else 0.45)
        ctx.set_line_width(1.55)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.new_sub_path()
        ctx.arc(bx, cy - 1.5, 4.7, math.pi, 2 * math.pi)
        ctx.line_to(bx + 4.7, cy + 2.6)
        ctx.line_to(bx + 6.3, cy + 4.3)
        ctx.line_to(bx - 6.3, cy + 4.3)
        ctx.line_to(bx - 4.7, cy + 2.6)
        ctx.close_path()
        ctx.stroke()
        ctx.new_sub_path()
        ctx.arc(bx, cy + 5.0, 1.7, 0, math.pi)
        ctx.stroke()


class ShowDesktopSliver(HoverCanvas):
    def __init__(self, wnck_screen):
        self.wnck_screen = wnck_screen
        super().__init__(
            8,
            BAR_HEIGHT,
            tooltip="Show desktop (Win+D)",
            on_click=self._toggle_desktop,
        )

    def _toggle_desktop(self, *_):
        cur = self.wnck_screen.get_showing_desktop()
        self.wnck_screen.toggle_showing_desktop(not cur)

    def on_draw(self, ctx, w, h):
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.24 if self.hovered else 0.14)
        ctx.set_line_width(1.0)
        ctx.move_to(1.5, 11)
        ctx.line_to(1.5, h - 11)
        ctx.stroke()
        if self.hovered:
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.09)
            ctx.rectangle(2, 0, w - 2, h)
            ctx.fill()


class Win11Taskbar(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.get_style_context().add_class("win11-dock")
        self.set_title("Win11-Taskbar-Muheeb")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        # CRITICAL: Never steal X11 input focus when taskbar buttons are clicked!
        self.set_accept_focus(False)
        self.set_focus_on_map(False)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.stick()
        self.set_keep_above(True)
        self.set_app_paintable(True)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        self.wnck = Wnck.Screen.get_default()
        self.wnck.force_update()

        self.connect("draw", self._on_draw_bg)
        self.connect("realize", self._on_realize)
        screen.connect("size-changed", lambda *_: self._reposition_and_strut())

        root_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.add(root_box)

        # 1. LEFT: Widgets Pill
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        left_box.set_margin_start(10)
        left_box.set_valign(Gtk.Align.CENTER)
        left_box.pack_start(WidgetsButton(), False, False, 0)
        root_box.pack_start(left_box, False, False, 0)

        # 2. DEAD-CENTER: Start + Search + Task View + Merged Pinned/Running Apps
        self.center_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.center_box.set_valign(Gtk.Align.CENTER)
        root_box.set_center_widget(self.center_box)

        start_pb = load_scaled_pixbuf([os.path.join(ICONS_DIR, "win11-start.svg")], ICON_PX)
        self.start_btn = HoverCanvas(
            SLOT_W,
            SLOT_H,
            tooltip="Start (Win) • Right-click for Power Menu (Win+X)",
            on_click=lambda *_: spawn(f"python3 '{SHELL_PY}' start"),
            on_right_click=lambda *_: spawn(f"python3 '{SHELL_PY}' winx"),
        )
        self.start_btn.on_draw = lambda ctx, w, h: (
            self.start_btn.draw_hover_bg(ctx, w, h, radius=6.0),
            Gdk.cairo_set_source_pixbuf(
                ctx, start_pb,
                (w - ICON_PX) / 2.0,
                (h - ICON_PX) / 2.0 + (1.5 if self.start_btn.pressed else 0.0),
            ) if start_pb else None,
            ctx.paint() if start_pb else None,
        )
        self.center_box.pack_start(self.start_btn, False, False, 0)

        self.search_widget = SearchPillWidget()
        self.center_box.pack_start(self.search_widget, False, False, 0)

        tv_pb = load_scaled_pixbuf([os.path.join(ICONS_DIR, "win11-taskview.svg")], ICON_PX)
        tv_btn = HoverCanvas(
            SLOT_W,
            SLOT_H,
            tooltip="Task View (Win+Tab)",
            on_click=lambda *_: spawn("rofi -show window -theme-str 'window {background-color: #111C17; border: 1px solid #34D399; border-radius: 10px; width: 50%;}'"),
        )
        tv_btn.on_draw = lambda ctx, w, h: (
            tv_btn.draw_hover_bg(ctx, w, h, radius=6.0),
            Gdk.cairo_set_source_pixbuf(
                ctx, tv_pb,
                (w - ICON_PX) / 2.0,
                (h - ICON_PX) / 2.0 + (1.5 if tv_btn.pressed else 0.0),
            ) if tv_pb else None,
            ctx.paint() if tv_pb else None,
        )
        self.center_box.pack_start(tv_btn, False, False, 0)

        self.pinned_defs = [
            {
                "id": "explorer",
                "title": "File Explorer",
                "match": ("thunar", "org.xfce.thunar", "nautilus"),
                "icons": [os.path.join(ICONS_DIR, "win11-explorer.svg"), "system-file-manager"],
                "cmd": "thunar",
            },
            {
                "id": "terminal",
                "title": "Windows Terminal",
                "match": ("qterminal", "xfce4-terminal", "kitty", "alacritty", "gnome-terminal"),
                "icons": [os.path.join(ICONS_DIR, "win11-terminal.svg"), "utilities-terminal"],
                "cmd": "qterminal || xfce4-terminal || x-terminal-emulator",
            },
            {
                "id": "browser",
                "title": "Brave Browser",
                "match": ("brave-browser", "brave", "firefox", "firefox-esr", "chromium"),
                "icons": ["brave-browser", "firefox-esr", "web-browser"],
                "cmd": "brave-browser || firefox || x-www-browser",
            },
            {
                "id": "vscode",
                "title": "Visual Studio Code",
                "match": ("com.microsoft.vscode", "code", "vscodium", "antigravity"),
                "icons": [os.path.join(ICONS_DIR, "win11-vscode.svg"), "com.visualstudio.code"],
                "cmd": "code",
            },
            {
                "id": "settings",
                "title": "Settings",
                "match": ("xfce4-settings-manager",),
                "icons": [os.path.join(ICONS_DIR, "win11-settings.svg"), "preferences-system"],
                "cmd": f"python3 '{SHELL_PY}' settings",
            },
        ]

        self.pinned_slots = {}
        for pdef in self.pinned_defs:
            pb = load_scaled_pixbuf(pdef["icons"], ICON_PX)
            slot = AppDockSlot(self.wnck, pdef["title"], pb, launch_cmd=pdef["cmd"])
            self.pinned_slots[pdef["id"]] = slot
            self.center_box.pack_start(slot, False, False, 0)

        self.dynamic_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.center_box.pack_start(self.dynamic_box, False, False, 0)
        self.dynamic_slots = {}

        # 3. FAR-RIGHT: '⌃' Chevron + ENG/US + Quick Settings + Clock/Bell + Show Desktop
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        right_box.set_valign(Gtk.Align.CENTER)

        right_box.pack_start(ChevronTrayButton(), False, False, 0)
        right_box.pack_start(LangTrayButton(), False, False, 0)
        self.qs_pill = QuickSettingsPill()
        right_box.pack_start(self.qs_pill, False, False, 0)
        self.clock_pill = ClockBellPill()
        right_box.pack_start(self.clock_pill, False, False, 0)

        root_box.pack_end(ShowDesktopSliver(self.wnck), False, False, 0)
        root_box.pack_end(right_box, False, False, 0)

        self.wnck.connect("window-opened", lambda *_: self.sync_windows())
        self.wnck.connect("window-closed", lambda *_: self.sync_windows())
        self.wnck.connect("active-window-changed", lambda *_: self.sync_windows())

        GLib.timeout_add(1000, self.search_widget.poll_config)
        GLib.timeout_add(4000, self.qs_pill.refresh_status)
        GLib.timeout_add(5000, self.clock_pill.refresh_clock)

        self._reposition_and_strut()
        self.sync_windows()

    def _get_geom(self):
        display = Gdk.Display.get_default()
        mon = display.get_primary_monitor() or display.get_monitor(0)
        g = mon.get_geometry()
        return g.x, g.y, g.width, g.height

    def _reposition_and_strut(self):
        mx, my, mw, mh = self._get_geom()
        self.set_size_request(mw, BAR_HEIGHT)
        self.resize(mw, BAR_HEIGHT)
        self.move(mx, my + mh - BAR_HEIGHT)
        if self.get_realized():
            self._apply_x11_strut(mx, mw, mh)

    def _on_realize(self, *_):
        mx, my, mw, mh = self._get_geom()
        self.move(mx, my + mh - BAR_HEIGHT)
        self._apply_x11_strut(mx, mw, mh)

    def _apply_x11_strut(self, mx, mw, mh):
        try:
            gdk_win = self.get_window()
            if isinstance(gdk_win, GdkX11.X11Window):
                xid = gdk_win.get_xid()
                end_x = mx + mw - 1
                subprocess.run(
                    [
                        "xprop", "-id", str(xid),
                        "-f", "_NET_WM_STRUT_PARTIAL", "32c",
                        "-set", "_NET_WM_STRUT_PARTIAL",
                        f"0, 0, 0, {BAR_HEIGHT}, 0, 0, 0, 0, 0, 0, {mx}, {end_x}",
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                subprocess.run(
                    [
                        "xprop", "-id", str(xid),
                        "-f", "_NET_WM_STRUT", "32c",
                        "-set", "_NET_WM_STRUT",
                        f"0, 0, 0, {BAR_HEIGHT}",
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except Exception:
            pass

    def _on_draw_bg(self, widget, ctx):
        alloc = widget.get_allocation()
        w, h = alloc.width, alloc.height
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        ctx.set_source_rgba(0.055, 0.095, 0.075, 0.96)
        ctx.rectangle(0, 0, w, h)
        ctx.fill()

        ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.set_source_rgba(0.35, 0.85, 0.65, 0.22)
        ctx.set_line_width(1.0)
        ctx.move_to(0, 0.5)
        ctx.line_to(w, 0.5)
        ctx.stroke()
        return False

    def sync_windows(self):
        active_win = self.wnck.get_active_window()
        pinned_buckets = {p["id"]: [] for p in self.pinned_defs}
        unpinned_groups = {}

        for w in self.wnck.get_windows():
            if w.is_skip_tasklist() or w.is_skip_pager():
                continue
            wtype = w.get_window_type()
            if wtype in (Wnck.WindowType.DESKTOP, Wnck.WindowType.DOCK, Wnck.WindowType.SPLASHSCREEN):
                continue
            if w.get_name() == "Win11-Taskbar-Muheeb":
                continue

            cg = (w.get_class_group_name() or "").lower()
            ci = (w.get_class_instance_name() or "").lower()
            matched_id = None
            for pdef in self.pinned_defs:
                if any(m in cg or m in ci for m in pdef["match"]):
                    matched_id = pdef["id"]
                    break

            if matched_id:
                pinned_buckets[matched_id].append(w)
            else:
                key = cg or ci or f"win-{w.get_xid()}"
                unpinned_groups.setdefault(key, []).append(w)

        for pdef in self.pinned_defs:
            pid = pdef["id"]
            self.pinned_slots[pid].update_state(pinned_buckets[pid], active_win)

        for key in list(self.dynamic_slots.keys()):
            if key not in unpinned_groups:
                slot = self.dynamic_slots.pop(key)
                self.dynamic_box.remove(slot)

        for key, wins in unpinned_groups.items():
            w0 = wins[0]
            raw_pb = w0.get_icon()
            scaled_pb = (
                raw_pb.scale_simple(ICON_PX, ICON_PX, GdkPixbuf.InterpType.BILINEAR)
                if raw_pb
                else load_scaled_pixbuf(["application-x-executable"], ICON_PX)
            )
            if key not in self.dynamic_slots:
                title = w0.get_class_group_name() or w0.get_name() or "App"
                slot = AppDockSlot(self.wnck, title, scaled_pb, windows=wins)
                self.dynamic_slots[key] = slot
                self.dynamic_box.pack_start(slot, False, False, 0)
                slot.show_all()
            self.dynamic_slots[key].update_state(wins, active_win, scaled_pb)


def main():
    pid_file = os.path.join(
        os.environ.get("XDG_RUNTIME_DIR", f"/tmp/win11-{os.getuid()}"),
        "win11_taskbar.pid",
    )
    if os.path.exists(pid_file):
        try:
            old = int(open(pid_file).read().strip())
            if old != os.getpid():
                os.kill(old, signal.SIGTERM)
        except Exception:
            pass
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    provider = Gtk.CssProvider()
    provider.load_from_data(TASKBAR_CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    bar = Win11Taskbar()
    signal.signal(signal.SIGTERM, lambda *_: Gtk.main_quit())
    bar.show_all()
    bar.search_widget._sync_visibility()
    Gtk.main()


if __name__ == "__main__":
    main()
