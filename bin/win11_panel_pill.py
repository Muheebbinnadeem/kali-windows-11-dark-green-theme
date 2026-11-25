#!/usr/bin/env python3
"""
Pixel-Accurate Windows 11 Cairo Taskbar Pills — 125% Recommended Display Scale (56px Taskbar)
Mathematical font-extents vertical centering + left/right balance spacer so center taskbar icons
sit at exact 960px screen center on 1920x1080.
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

PILL_H = 42  # Uniform vertical height inside 56px taskbar for 100% consistent alignment


def load_settings():
    defaults = {
        "search_style": "box",
        "search_label": "Search",
        "search_gleam": True,
        "web_engine": "google",
        "enable_calc": True,
        "enable_files": True,
        "scale_pct": 125,
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


def draw_two_lines(ctx, line1, line2, x_anchor, align="left", size1=13.0, size2=11.8,
                   col1=(0.95, 0.99, 0.97, 0.97), col2=(0.78, 0.89, 0.84, 0.92), bold1=True):
    """Draw two vertically centered text lines inside PILL_H with mathematical precision."""
    gap = 3.5
    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold1 else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size1)
    ascent1, descent1, _, _, _ = ctx.font_extents()
    ext1 = ctx.text_extents(line1)

    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size2)
    ascent2, descent2, _, _, _ = ctx.font_extents()
    ext2 = ctx.text_extents(line2)

    h1 = ascent1
    h2 = ascent2
    total_h = h1 + gap + h2
    top_y = (PILL_H - total_h) / 2.0

    # Line 1
    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold1 else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size1)
    ctx.set_source_rgba(*col1)
    if align == "right":
        x1 = x_anchor - ext1.width
    elif align == "center":
        x1 = x_anchor - ext1.width / 2.0
    else:
        x1 = x_anchor
    ctx.move_to(x1, top_y + ascent1)
    ctx.show_text(line1)

    # Line 2
    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size2)
    ctx.set_source_rgba(*col2)
    if align == "right":
        x2 = x_anchor - ext2.width
    elif align == "center":
        x2 = x_anchor - ext2.width / 2.0
    else:
        x2 = x_anchor
    ctx.move_to(x2, top_y + h1 + gap + ascent2)
    ctx.show_text(line2)


def emit_img(png_path, click_cmd, tooltip):
    print(f"<img>{png_path}</img>")
    if click_cmd:
        print(f"<click>{click_cmd}</click>")
    print(f"<tool>{tooltip}</tool>")


def draw_wifi_icon(ctx, cx, cy, enabled=True):
    ctx.save()
    color = (0.95, 0.99, 0.97, 0.97) if enabled else (0.60, 0.68, 0.64, 0.55)
    ctx.set_source_rgba(*color)
    ctx.set_line_width(1.85)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    by = cy + 6.4
    for radius in (4.4, 8.2, 12.0):
        ctx.new_sub_path()
        ctx.arc(cx, by, radius, -math.pi * 0.76, -math.pi * 0.24)
        ctx.stroke()

    ctx.arc(cx, by + 0.3, 1.65, 0, 2 * math.pi)
    ctx.fill()

    if not enabled:
        ctx.set_source_rgba(0.96, 0.45, 0.45, 0.95)
        ctx.set_line_width(1.8)
        ctx.move_to(cx - 7, cy - 7)
        ctx.line_to(cx + 7, cy + 7)
        ctx.stroke()
    ctx.restore()


def draw_speaker_icon(ctx, cx, cy, muted=False, vol=70):
    ctx.save()
    ctx.set_source_rgba(0.95, 0.99, 0.97, 0.97)
    ctx.set_line_width(1.75)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    x0 = cx - 7.8
    ctx.move_to(x0, cy - 2.8)
    ctx.line_to(x0 + 3.4, cy - 2.8)
    ctx.line_to(x0 + 7.8, cy - 6.8)
    ctx.line_to(x0 + 7.8, cy + 6.8)
    ctx.line_to(x0 + 3.4, cy + 2.8)
    ctx.line_to(x0, cy + 2.8)
    ctx.close_path()
    ctx.stroke()

    if muted or vol == 0:
        ctx.set_source_rgba(0.96, 0.52, 0.52, 0.96)
        ctx.move_to(cx + 2.6, cy - 3.2)
        ctx.line_to(cx + 7.8, cy + 3.2)
        ctx.move_to(cx + 7.8, cy - 3.2)
        ctx.line_to(cx + 2.6, cy + 3.2)
        ctx.stroke()
    else:
        ctx.new_sub_path()
        ctx.arc(cx + 0.3, cy, 4.1, -0.68, 0.68)
        ctx.stroke()
        if vol > 35:
            ctx.new_sub_path()
            ctx.arc(cx + 0.3, cy, 7.4, -0.72, 0.72)
            ctx.stroke()
    ctx.restore()


def draw_battery_icon(ctx, cx, cy, pct=85, plugged=False):
    ctx.save()
    bw, bh = 20.5, 11.5
    bx = cx - bw / 2.0 - 1.2
    by = cy - bh / 2.0

    ctx.set_source_rgba(0.95, 0.99, 0.97, 0.94)
    ctx.set_line_width(1.55)
    rounded_rect(ctx, bx, by, bw, bh, 2.6)
    ctx.stroke()

    ctx.move_to(bx + bw + 1.8, cy - 2.6)
    ctx.line_to(bx + bw + 1.8, cy + 2.6)
    ctx.set_line_width(1.9)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()

    fill_w = max(2.2, (bw - 4.6) * max(0.06, min(1.0, pct / 100.0)))
    if plugged:
        ctx.set_source_rgba(0.20, 0.83, 0.60, 0.98)
    elif pct <= 20:
        ctx.set_source_rgba(0.96, 0.42, 0.38, 0.98)
    else:
        ctx.set_source_rgba(0.95, 0.99, 0.97, 0.96)
    rounded_rect(ctx, bx + 2.3, by + 2.3, fill_w, bh - 4.6, 1.2)
    ctx.fill()
    ctx.restore()


def draw_bell_icon(ctx, cx, cy, dnd=False):
    ctx.save()
    ctx.set_source_rgba(0.94, 0.98, 0.96, 0.94 if not dnd else 0.50)
    ctx.set_line_width(1.6)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    ctx.new_sub_path()
    ctx.arc(cx, cy - 1.5, 5.0, math.pi, 2 * math.pi)
    ctx.line_to(cx + 5.0, cy + 2.8)
    ctx.line_to(cx + 6.8, cy + 4.6)
    ctx.line_to(cx - 6.8, cy + 4.6)
    ctx.line_to(cx - 5.0, cy + 2.8)
    ctx.close_path()
    ctx.stroke()

    ctx.new_sub_path()
    ctx.arc(cx, cy + 5.2, 1.8, 0, math.pi)
    ctx.stroke()

    if dnd:
        ctx.set_source_rgba(0.96, 0.52, 0.45, 0.92)
        ctx.move_to(cx - 6, cy - 6)
        ctx.line_to(cx + 6, cy + 6)
        ctx.stroke()
    else:
        ctx.arc(cx + 5.0, cy - 4.8, 2.4, 0, 2 * math.pi)
        ctx.set_source_rgba(0.20, 0.83, 0.60, 0.98)
        ctx.fill()
    ctx.restore()


def render_control_pill():
    w, h = 106, PILL_H
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
    draw_wifi_icon(ctx, 20, cy, enabled=wifi_on)
    draw_speaker_icon(ctx, 52, cy, muted=muted, vol=vol)
    draw_battery_icon(ctx, 85, cy, pct=pct, plugged=plugged)

    surf.write_to_png(out)
    emit_img(
        out,
        f"python3 '{SHELL_PY}' control",
        f"{ssid}  •  Volume: {vol}%  •  Battery: {pct}%\nQuick Settings: Wi-Fi & Bluetooth (Win+A)",
    )


def render_clock_pill():
    w, h = 122, PILL_H
    out = os.path.join(PILL_DIR, "clock.png")
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)

    now = datetime.datetime.now()
    t_str = now.strftime("%I:%M %p").lstrip("0")
    d_str = now.strftime("%m/%d/%Y")
    dnd = run_short("xfconf-query -c xfce4-notifyd -p /do-not-disturb").lower() == "true"

    draw_two_lines(
        ctx, t_str, d_str,
        x_anchor=w - 30, align="right",
        size1=13.0, size2=12.0, bold1=False,
    )
    draw_bell_icon(ctx, w - 12, h / 2.0, dnd=dnd)

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
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, PILL_H)
        surf.write_to_png(out)
        emit_img(out, "", "Search hidden (Press Win+S to search)")
        return

    if style == "icon":
        w, h = 42, PILL_H
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(surf)
        ctx.set_source_rgba(0.94, 0.99, 0.96, 0.96)
        ctx.set_line_width(2.0)
        ctx.arc(19.0, 19.0, 7.2, 0, 2 * math.pi)
        ctx.stroke()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(24.5, 24.5)
        ctx.line_to(30.5, 30.5)
        ctx.stroke()
        surf.write_to_png(out)
        emit_img(out, f"python3 '{SHELL_PY}' search", "Search (Win+S)")
        return

    w = 232 if style == "box" else 124
    h = PILL_H
    box_h = 36
    by = (h - box_h) / 2.0
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)

    rounded_rect(ctx, 1.5, by, w - 3, box_h, box_h / 2.0)
    ctx.set_source_rgba(0.13, 0.22, 0.18, 0.96)
    ctx.fill_preserve()
    ctx.set_line_width(1.2)
    ctx.set_source_rgba(0.20, 0.83, 0.60, 0.34)
    ctx.stroke()

    cy = h / 2.0
    ctx.set_source_rgba(0.92, 0.98, 0.95, 0.94)
    ctx.set_line_width(1.8)
    ctx.arc(21.0, cy - 1.2, 5.8, 0, 2 * math.pi)
    ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(25.4, cy + 3.2)
    ctx.line_to(29.8, cy + 7.6)
    ctx.stroke()

    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(13.8)
    ascent, descent, _, _, _ = ctx.font_extents()
    ctx.set_source_rgba(0.80, 0.89, 0.84, 0.94)
    ctx.move_to(40, (h - ascent - descent) / 2.0 + ascent)
    ctx.show_text(label[:16])

    if style == "box" and gleam:
        gx, gy = w - 23, cy
        ctx.arc(gx, gy, 9.2, 0, 2 * math.pi)
        ctx.set_source_rgba(0.02, 0.59, 0.41, 0.35)
        ctx.fill()
        ctx.arc(gx - 2.0, gy - 1.2, 3.3, 0, 2 * math.pi)
        ctx.set_source_rgba(0.20, 0.83, 0.60, 0.95)
        ctx.fill()
        ctx.arc(gx + 3.0, gy + 2.2, 2.2, 0, 2 * math.pi)
        ctx.set_source_rgba(0.70, 0.97, 0.85, 0.92)
        ctx.fill()

    surf.write_to_png(out)
    emit_img(out, f"python3 '{SHELL_PY}' search", f"{label} (Win+S) • Click ⚙️ inside Search to customize")


def render_widgets_pill():
    w, h = 148, PILL_H
    out = os.path.join(PILL_DIR, "widgets.png")
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)

    cy = h / 2.0
    ctx.arc(17, cy - 3.5, 6.4, 0, 2 * math.pi)
    ctx.set_source_rgba(0.98, 0.82, 0.24, 0.97)
    ctx.fill()

    rounded_rect(ctx, 13, cy - 1.5, 20, 10.5, 5.2)
    ctx.set_source_rgba(0.90, 0.97, 0.94, 0.97)
    ctx.fill()
    ctx.arc(20, cy - 1.5, 5.6, 0, 2 * math.pi)
    ctx.fill()

    draw_two_lines(
        ctx, "24°C", "Muheeb",
        x_anchor=41, align="left",
        size1=13.2, size2=12.0,
        col1=(0.95, 0.99, 0.97, 0.97),
        col2=(0.20, 0.83, 0.60, 0.98),
        bold1=True,
    )

    surf.write_to_png(out)
    emit_img(out, f"python3 '{SHELL_PY}' widgets", "Widgets Board (Win+W) • Made by Muheeb")


def render_lang_pill():
    w, h = 44, PILL_H
    out = os.path.join(PILL_DIR, "lang.png")
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)

    draw_two_lines(
        ctx, "ENG", "US",
        x_anchor=w / 2.0, align="center",
        size1=12.0, size2=11.5, bold1=False,
    )
    surf.write_to_png(out)
    emit_img(out, f"python3 '{SHELL_PY}' settings", "Display Scale (125%) & Search Settings (Win+I)")


def render_balance_spacer():
    """Invisible spacer on left side so Center Taskbar Icons sit at exact 960px screen center."""
    w, h = 48, PILL_H
    out = os.path.join(PILL_DIR, "spacer.png")
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    surf.write_to_png(out)
    print(f"<img>{out}</img>")


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
    elif kind == "spacer":
        render_balance_spacer()


if __name__ == "__main__":
    main()
