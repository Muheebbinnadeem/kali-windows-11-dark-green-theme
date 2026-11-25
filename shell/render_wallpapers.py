#!/usr/bin/env python3
"""
Render Windows 11 Dark Green 'Made by Muheeb' 1920x1080 Wallpapers.
Color-grades the 3D Bloom sculpture from royal blue into deep cyber/forest Dark Green,
then composites crisp vector Windows 11 Dark Green + 'Made by Muheeb' branding via Cairo.
"""
import colorsys
import os
import cairo
from PIL import Image

ARTIFACT_DIR = "/home/muheeb/.gemini/antigravity/brain/5edef011-1d37-45de-a6eb-870e242fcc6b"
REPO_WALLS = "/home/muheeb/projects/Window Theme Repo/wallpapers"


def grade_to_dark_green(img: Image.Image, dark_mode: bool) -> Image.Image:
    """Smooth continuous channel transform from blue/cyan Bloom to deep Dark Green (zero banding)."""
    rgb = img.convert("RGB").resize((1920, 1080), Image.Resampling.LANCZOS)
    r_ch, g_ch, b_ch = rgb.split()
    r_b = r_ch.tobytes()
    g_b = g_ch.tobytes()
    b_b = b_ch.tobytes()
    out = bytearray(len(r_b) * 3)

    if dark_mode:
        # Map royal-blue (b high, g mid, r low) -> rich dark emerald/forest green (g high, b subtle jade, r obsidian)
        for i in range(len(r_b)):
            rv = r_b[i] / 255.0
            gv = g_b[i] / 255.0
            bv = b_b[i] / 255.0
            lum_green = min(1.0, (0.68 * bv + 0.36 * gv) ** 1.12 * 0.88)
            jade_blue = min(1.0, (0.30 * gv + 0.16 * bv) ** 1.18 * 0.78)
            deep_red = min(1.0, (0.22 * rv + 0.05 * gv) ** 1.15 * 0.65)
            j = i * 3
            out[j] = int(deep_red * 255 + 0.5)
            out[j + 1] = int(lum_green * 255 + 0.5)
            out[j + 2] = int(jade_blue * 255 + 0.5)
    else:
        for i in range(len(r_b)):
            rv = r_b[i] / 255.0
            gv = g_b[i] / 255.0
            bv = b_b[i] / 255.0
            nr = min(1.0, 0.72 * rv + 0.18 * gv)
            ng = min(1.0, 0.25 * gv + 0.75 * bv)
            nb = min(1.0, 0.55 * gv + 0.32 * bv)
            j = i * 3
            out[j] = int(nr * 255 + 0.5)
            out[j + 1] = int(ng * 255 + 0.5)
            out[j + 2] = int(nb * 255 + 0.5)

    return Image.frombytes("RGB", rgb.size, bytes(out))


def rounded_rect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -1.570796, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, 1.570796)
    ctx.arc(x + r, y + h - r, r, 1.570796, 3.141592)
    ctx.arc(x + r, y + r, r, 3.141592, 4.712388)
    ctx.close_path()


def draw_win11_green_logo(ctx, x, y, size):
    gap = size * 0.11
    half = (size - gap) / 2.0
    colors = [
        (0.20, 0.83, 0.60),  # #34D399
        (0.02, 0.59, 0.41),  # #059669
        (0.06, 0.73, 0.51),  # #10B981
        (0.02, 0.37, 0.27),  # #065F46
    ]
    coords = [
        (x, y),
        (x + half + gap, y),
        (x, y + half + gap),
        (x + half + gap, y + half + gap),
    ]
    for (cx, cy), (r, g, b) in zip(coords, colors):
        rounded_rect(ctx, cx, cy, half, half, 1.8)
        ctx.set_source_rgb(r, g, b)
        ctx.fill()


def render_wallpaper(src_jpg, dst_png, is_dark):
    os.makedirs(os.path.dirname(dst_png), exist_ok=True)
    graded = grade_to_dark_green(Image.open(src_jpg), dark_mode=is_dark)
    tmp_png = dst_png + ".tmp.png"
    graded.save(tmp_png, "PNG")

    surface = cairo.ImageSurface.create_from_png(tmp_png)
    os.remove(tmp_png)
    ctx = cairo.Context(surface)

    # 1. Center-bottom Fluent Dark-Green Glass Pill (sits cleanly above 48px taskbar)
    pill_w, pill_h = 346, 42
    pill_x = (1920 - pill_w) / 2.0
    pill_y = 1080 - 48 - pill_h - 26

    rounded_rect(ctx, pill_x, pill_y, pill_w, pill_h, 21)
    if is_dark:
        ctx.set_source_rgba(0.05, 0.12, 0.09, 0.78)
    else:
        ctx.set_source_rgba(0.93, 0.99, 0.96, 0.82)
    ctx.fill_preserve()

    ctx.set_line_width(1.3)
    if is_dark:
        ctx.set_source_rgba(0.20, 0.83, 0.60, 0.45)
    else:
        ctx.set_source_rgba(0.02, 0.47, 0.34, 0.35)
    ctx.stroke()

    draw_win11_green_logo(ctx, pill_x + 18, pill_y + 11, 20)

    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(13.5)
    if is_dark:
        ctx.set_source_rgba(0.93, 0.99, 0.96, 0.96)
    else:
        ctx.set_source_rgba(0.02, 0.25, 0.18, 0.94)
    ctx.move_to(pill_x + 48, pill_y + 26)
    ctx.show_text("Windows 11")

    if is_dark:
        ctx.set_source_rgba(0.20, 0.83, 0.60, 0.98)
    else:
        ctx.set_source_rgba(0.02, 0.47, 0.34, 0.96)
    ctx.move_to(pill_x + 138, pill_y + 26)
    ctx.show_text("•   Made by Muheeb")

    # 2. Bottom-right Windows 11 Edition Watermark above clock/tray
    wm_right = 1920 - 24
    wm_y1 = 1080 - 48 - 34
    wm_y2 = 1080 - 48 - 16

    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(12.5)
    line1 = "Windows 11 Pro (Dark Green)  •  Made by Muheeb"
    ext1 = ctx.text_extents(line1)
    if is_dark:
        ctx.set_source_rgba(0.75, 0.96, 0.87, 0.68)
    else:
        ctx.set_source_rgba(0.02, 0.30, 0.22, 0.65)
    ctx.move_to(wm_right - ext1.width, wm_y1)
    ctx.show_text(line1)

    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(11.0)
    line2 = "Kali GNU/Linux Rolling  •  Build 26100.Muheeb"
    ext2 = ctx.text_extents(line2)
    if is_dark:
        ctx.set_source_rgba(0.75, 0.96, 0.87, 0.46)
    else:
        ctx.set_source_rgba(0.02, 0.30, 0.22, 0.48)
    ctx.move_to(wm_right - ext2.width, wm_y2)
    ctx.show_text(line2)

    surface.write_to_png(dst_png)
    print(f"Rendered Dark-Green Wallpaper: {dst_png}")


if __name__ == "__main__":
    render_wallpaper(
        os.path.join(ARTIFACT_DIR, "win11_bloom_dark_base_v3_1795630297568.jpg"),
        os.path.join(REPO_WALLS, "win11-muheeb-dark.png"),
        True,
    )
    render_wallpaper(
        os.path.join(ARTIFACT_DIR, "win11_bloom_light_base_1795630236743.jpg"),
        os.path.join(REPO_WALLS, "win11-muheeb-light.png"),
        False,
    )
