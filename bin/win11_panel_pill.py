#!/usr/bin/env python3
"""
Pixel-Accurate Windows 11 Cairo Taskbar Pills (96-DPI Original Windows 11 Proportions)
Renders crisp monochrome 16px Fluent tray icons (Wi-Fi + Speaker + Battery),
customizable Taskbar Search Box/Pill/Icon, Two-line Clock/Date + monochrome Bell,
and Weather/Widgets pill directly as transparent PNGs for xfce4-genmon-plugin.
"""
import datetime
import json
import math
import os
import subprocess
import sys
import cairo

try:
    import psutil
except ImportError:
    psutil = None

RUNTIME_DIR = os.environ.get("XDG_RUNTIME_DIR", f"/tmp/win11-{os.getuid()}")
PILL_DIR = os.path.join(RUNTIME_DIR, "win11_pills")
os.makedirs(PILL_DIR, exist_ok=True)

SETTINGS_PATH = os.path.expanduser("~/.config/win11-muheeb/settings.json")
SHELL_PY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "shell",
    "win11_shell.py",
)


def load_settings():
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


def run_short(cmd):
    try:
        return subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=1.0
        ).stdout.strip()
    except Exception:
        return ""


def rounded_rect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def emit_img(png_path, click_cmd, tooltip):
    print(f"<img>{png_path}</img>")
    if click_cmd:
        print(f"<click>{click_cmd}</click>")
    print(f"<tool>{tooltip}</tool>")


def draw_wifi_icon(ctx, cx, cy, enabled=True):
    """Exact 16px monochrome Windows 11 Wi-Fi arcs centered around (cx, cy)."""
    ctx.save()
    color = (0.94, 0.98, 0.96, 0.96) if enabled else (0.60, 0.68, 0.64, 0.55)
    ctx.set_source_rgba(*color)
    ctx.set_line_width(1.55)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    by = cy + 5.2
    for radius in (3.6, 6.8, 10.0):
        ctx.new_sub_path()
        ctx.arc(cx, by, radius, -math.pi * 0.76, -math.pi * 0.24)
        ctx.stroke()

    ctx.arc(cx, by + 0.3, 1.35, 0, 2 * math.pi)
    ctx.fill()

    if not enabled:
        ctx.set_source_rgba(0.95, 0.45, 0.45, 0.95)
        ctx.set_line_width(1.6)
        ctx.move_to(cx - 6, cy - 6)
        ctx.line_to(cx + 6, cy + 6)
        ctx.stroke()
    ctx.restore()


def draw_speaker_icon(ctx, cx, cy, muted=False, vol=70):
    """Exact 16px monochrome Windows 11 Speaker Fluent icon."""
    ctx.save()
    ctx.set_source_rgba(0.94, 0.98, 0.96, 0.96)
    ctx.set_line_width(1.5)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    # Speaker body
    x0 = cx - 6.5
    ctx.move_to(x0, cy - 2.3)
    ctx.line_to(x0 + 2.8, cy - 2.3)
    ctx.line_to(x0 + 6.5, cy - 5.6)
    ctx.line_to(x0 + 6.5, cy + 5.6)
    ctx.line_to(x0 + 2.8, cy + 2.3)
    ctx.line_to(x0, cy + 2.3)
    ctx.close_path()
    ctx.stroke()

    if muted or vol == 0:
        ctx.set_source_rgba(0.95, 0.55, 0.55, 0.95)
        ctx.move_to(cx + 2.2, cy - 2.6)
        ctx.line_to(cx + 6.6, cy + 2.6)
        ctx.move_to(cx + 6.6, cy - 2.6)
        ctx.line_to(cx + 2.2, cy + 2.6)
        ctx.stroke()
    else:
        ctx.new_sub_path()
        ctx.arc(cx + 0.2, cy, 3.4, -0.68, 0.68)
        ctx.stroke()
        if vol > 40:
            ctx.new_sub_path()
            ctx.arc(cx + 0.2, cy, 6.2, -0.72, 0.72)
            ctx.stroke()
    ctx.restore()


def draw_battery_icon(ctx, cx, cy, pct=85, plugged=False):
    """Exact 18x10px monochrome Windows 11 Horizontal Battery icon."""
    ctx.save()
    bw, bh = 16.5, 9.5
    bx = cx - bw / 2.0 - 1.0
    by = cy - bh / 2.0

    ctx.set_source_rgba(0.94, 0.98, 0.96, 0.92)
    ctx.set_line_width(1.35)
    rounded_rect(ctx, bx, by, bw, bh, 2.2)
    ctx.stroke()

    # Battery positive terminal nub
    ctx.move_to(bx + bw + 1.4, cy - 2.2)
    ctx.line_to(bx + bw + 1.4, cy + 2.2)
    ctx.set_line_width(1.6)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()

    # Inner proportional charge bar
    fill_w = max(1.8, (bw - 4.0) * max(0.05, min(1.0, pct / 100.0)))
    if plugged:
        ctx.set_source_rgba(0.20, 0.83, 0.60, 0.98)
    elif pct <= 20:
        ctx.set_source_rgba(0.96, 0.42, 0.38, 0.98)
    else:
        ctx.set_source_rgba(0.94, 0.98, 0.96, 0.95)
    rounded_rect(ctx, bx + 2.0, by + 2.0, fill_w, bh - 4.0, 1.0)
    ctx.fill()
    ctx.restore()


def draw_bell_icon(ctx, cx, cy, dnd=False):
    """Exact 14px monochrome Windows 11 Notification Bell outline."""
    ctx.save()
    ctx.set_source_rgba(0.92, 0.97, 0.94, 0.90 if not dnd else 0.50)
    ctx.set_line_width(1.35)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    ctx.new_sub_path()
    ctx.arc(cx, cy - 1.2, 4.2, math.pi, 2 * math.pi)
    ctx.line_to(cx + 4.2, cy + 2.2)
    ctx.line_to(cx + 5.6, cy + 3.8)
    ctx.line_to(cx - 5.6, cy + 3.8)
    ctx.line_to(cx - 4.2, cy + 2.2)
    ctx.close_path()
    ctx.stroke()

    ctx.new_sub_path()
    ctx.arc(cx, cy + 4.4, 1.5, 0, math.pi)
    ctx.stroke()

    if dnd:
        ctx.set_source_rgba(0.95, 0.55, 0.45, 0.9)
        ctx.move_to(cx - 5, cy - 5)
        ctx.line_to(cx + 5, cy + 5)
        ctx.stroke()
    else:
        # Subtle emerald dot showing active Win11 Notification Center
        ctx.arc(cx + 4.2, cy - 4.0, 2.0, 0, 2 * math.pi)
        ctx.set_source_rgba(0.20, 0.83, 0.60, 0.98)
        ctx.fill()
    ctx.restore()


def render_control_pill():
    w, h = 84, 34
    out = os.path.join(PILL_DIR, "control.png")
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)

    wifi_on = "enabled" in run_short("nmcli radio wifi").lower()
    ssid = run_short("nmcli -t -f active,ssid dev wifi list --rescan no | grep '^yes:' | cut -d: -f2") or ("Wi-Fi" if wifi_on else "Off")
    muted = "yes" in run_short("pactl get-sink-mute @DEFAULT_SINK@").lower()
    vol_out = run_short("pactl get-sink-volume @DEFAULT_SINK@")
    vol = 70
    for t in vol_out.split():
        if t.endswith("%"):
            try:
                vol = int(t[:-1])
                break
            except ValueError:
                pass

    pct, plugged = 100, False
    if psutil and hasattr(psutil, "sensors_battery"):
        b = psutil.sensors_battery()
        if b:
            pct, plugged = int(b.percent), bool(b.power_plugged)

    cy = h / 2.0
    draw_wifi_icon(ctx, 16, cy, enabled=wifi_on)
    draw_speaker_icon(ctx, 41, cy, muted=muted, vol=vol)
    draw_battery_icon(ctx, 67, cy, pct=pct, plugged=plugged)

    surf.write_to_png(out)
    emit_img(
        out,
        f"python3 '{SHELL_PY}' control",
        f"{ssid}  •  Volume: {vol}%  •  Battery: {pct}%\nClick for Quick Settings (Win+A)",
    )


def render_clock_pill():
    w, h = 98, 34
    out = os.path.join(PILL_DIR, "clock.png")
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)

    now = datetime.datetime.now()
    t_str = now.strftime("%I:%M %p").lstrip("0")
    d_str = now.strftime("%m/%d/%Y")
    dnd = run_short("xfconf-query -c xfce4-notifyd -p /do-not-disturb").lower() == "true"

    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(11.2)
    ctx.set_source_rgba(0.95, 0.99, 0.97, 0.96)
    ext1 = ctx.text_extents(t_str)
    right_x = w - 24
    ctx.move_to(right_x - ext1.width, 14.5)
    ctx.show_text(t_str)

    ctx.set_font_size(10.8)
    ctx.set_source_rgba(0.82, 0.90, 0.86, 0.90)
    ext2 = ctx.text_extents(d_str)
    ctx.move_to(right_x - ext2.width, 28.0)
    ctx.show_text(d_str)

    draw_bell_icon(ctx, w - 10, h / 2.0, dnd=dnd)
    surf.write_to_png(out)
    emit_img(
        out,
        f"python3 '{SHELL_PY}' notifications",
        f"{now.strftime('%A, %B %d, %Y')}\nNotifications & Calendar (Win+N) • Made by Muheeb",
    )


def render_search_pill():
    cfg = load_settings()
    style = cfg.get("search_style", "box")
    label = cfg.get("search_label", "Search") or "Search"
    gleam = cfg.get("search_gleam", True)
    out = os.path.join(PILL_DIR, "search.png")

    if style == "hidden":
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 32)
        surf.write_to_png(out)
        emit_img(out, "", "Search hidden (Press Win+S to search)")
        return

    if style == "icon":
        w, h = 34, 34
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(surf)
        ctx.set_source_rgba(0.93, 0.98, 0.95, 0.95)
        ctx.set_line_width(1.7)
        ctx.arc(15.5, 15.5, 6.2, 0, 2 * math.pi)
        ctx.stroke()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(20.2, 20.2)
        ctx.line_to(25.0, 25.0)
        ctx.stroke()
        surf.write_to_png(out)
        emit_img(out, f"python3 '{SHELL_PY}' search", "Search (Win+S) • Customize inside Search")
        return

    w = 192 if style == "box" else 104
    h = 32
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)

    # Authentic Win11 Search Pill Surface
    rounded_rect(ctx, 1, 1, w - 2, h - 2, 15)
    ctx.set_source_rgba(0.13, 0.21, 0.17, 0.95)
    ctx.fill_preserve()
    ctx.set_line_width(1.0)
    ctx.set_source_rgba(0.20, 0.83, 0.60, 0.30)
    ctx.stroke()

    # Crisp thin magnifying glass
    ctx.set_source_rgba(0.90, 0.97, 0.94, 0.92)
    ctx.set_line_width(1.55)
    ctx.arc(17.5, 15.2, 5.0, 0, 2 * math.pi)
    ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(21.3, 19.0)
    ctx.line_to(25.0, 22.7)
    ctx.stroke()

    # Search label
    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(11.8)
    ctx.set_source_rgba(0.78, 0.87, 0.82, 0.92)
    ctx.move_to(33, 20.0)
    ctx.show_text(label[:16])

    # Optional Win11 Search Highlight Dark-Green Sparkle on right of full box
    if style == "box" and gleam:
        gx, gy = w - 20, h / 2.0
        ctx.arc(gx, gy, 7.5, 0, 2 * math.pi)
        ctx.set_source_rgba(0.02, 0.59, 0.41, 0.35)
        ctx.fill()
        ctx.arc(gx - 1.5, gy - 1.0, 2.8, 0, 2 * math.pi)
        ctx.set_source_rgba(0.20, 0.83, 0.60, 0.92)
        ctx.fill()
        ctx.arc(gx + 2.5, gy + 1.8, 1.8, 0, 2 * math.pi)
        ctx.set_source_rgba(0.65, 0.95, 0.82, 0.90)
        ctx.fill()

    surf.write_to_png(out)
    emit_img(
        out,
        f"python3 '{SHELL_PY}' search",
        f"{label} (Win+S) • Click ⚙️ inside Search to customize",
    )


def render_widgets_pill():
    w, h = 118, 34
    out = os.path.join(PILL_DIR, "widgets.png")
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)

    # Crisp Sun + Cloud vector icon (left)
    ctx.arc(14, 14, 5.2, 0, 2 * math.pi)
    ctx.set_source_rgba(0.98, 0.82, 0.24, 0.96)
    ctx.fill()

    rounded_rect(ctx, 11, 15.5, 16, 8.5, 4.2)
    ctx.set_source_rgba(0.88, 0.96, 0.92, 0.96)
    ctx.fill()
    ctx.arc(16.5, 15.5, 4.5, 0, 2 * math.pi)
    ctx.fill()

    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(11.0)
    ctx.set_source_rgba(0.94, 0.99, 0.96, 0.96)
    ctx.move_to(33, 14.5)
    ctx.show_text("24°C")

    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(10.2)
    ctx.set_source_rgba(0.20, 0.83, 0.60, 0.95)
    ctx.move_to(33, 27.2)
    ctx.show_text("Muheeb")

    surf.write_to_png(out)
    emit_img(out, f"python3 '{SHELL_PY}' widgets", "Widgets Board (Win+W) • Made by Muheeb")


def render_lang_pill():
    w, h = 34, 34
    out = os.path.join(PILL_DIR, "lang.png")
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)

    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(10.2)
    ctx.set_source_rgba(0.93, 0.98, 0.95, 0.92)
    for txt, y in (("ENG", 14.5), ("US", 27.0)):
        ext = ctx.text_extents(txt)
        ctx.move_to((w - ext.width) / 2.0, y)
        ctx.show_text(txt)

    surf.write_to_png(out)
    emit_img(out, f"python3 '{SHELL_PY}' settings", "Keyboard & Theme Settings (Win+I) • Made by Muheeb")


def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else "clock"
    if kind == "control":
        render_control_pill()
    elif kind == "clock":
        render_clock_pill()
    elif kind == "search":
        render_search_pill()
    elif kind == "widgets":
        render_widgets_pill()
    elif kind == "lang":
        render_lang_pill()


if __name__ == "__main__":
    main()
