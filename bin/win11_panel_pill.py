#!/usr/bin/env python3
"""
Windows 11 XFCE4-Panel Genmon Widget Outputs (Dark Green Edition — Made by Muheeb)
Usage:
  win11_panel_pill.py widgets
  win11_panel_pill.py search
  win11_panel_pill.py control
  win11_panel_pill.py clock
  win11_panel_pill.py brand
"""
import datetime
import os
import subprocess
import sys

try:
    import psutil
except ImportError:
    psutil = None

SHELL_PY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "shell",
    "win11_shell.py",
)


def run_short(cmd):
    try:
        return subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=1.2
        ).stdout.strip()
    except Exception:
        return ""


def emit(txt, click_cmd, tooltip):
    print(f"<txt>{txt}</txt>")
    if click_cmd:
        print(f"<txtclick>{click_cmd}</txtclick>")
    print(f"<tool>{tooltip}</tool>")


def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else "clock"

    if kind == "widgets":
        cpu = int(psutil.cpu_percent(interval=0.05)) if psutil else 14
        txt = (
            "<span font='Inter 8.5' foreground='#34D399' weight='700'>  🌤️ 24°C</span>\n"
            f"<span font='Inter 7.5' foreground='#B7CEC3'>  Muheeb • {cpu}%  </span>"
        )
        emit(txt, f"python3 '{SHELL_PY}' widgets", "Widgets Board • Made by Muheeb")

    elif kind == "search":
        txt = (
            "<span font='Inter 9.5' foreground='#34D399'>  🔍 </span>"
            "<span font='Inter 9' foreground='#CFE3D9'>Search          </span>"
        )
        emit(txt, f"python3 '{SHELL_PY}' search", "Search Windows 11 • Made by Muheeb")

    elif kind == "control":
        wifi = "📶" if "enabled" in run_short("nmcli radio wifi").lower() else "✈️"
        muted = "yes" in run_short("pactl get-sink-mute @DEFAULT_SINK@").lower()
        vol_icon = "🔇" if muted else "🔊"
        bat_txt = "🔋"
        if psutil and hasattr(psutil, "sensors_battery"):
            b = psutil.sensors_battery()
            if b:
                bat_txt = f"{'⚡' if b.power_plugged else '🔋'} {int(b.percent)}%"
        txt = (
            f"<span font='Inter 9.5' foreground='#ECFDF5'>  {wifi}   {vol_icon}   {bat_txt}  </span>"
        )
        emit(
            txt,
            f"python3 '{SHELL_PY}' control",
            "Quick Settings (Wi-Fi, Sound, Brightness) • Made by Muheeb",
        )

    elif kind == "clock":
        now = datetime.datetime.now()
        t_str = now.strftime("%I:%M %p").lstrip("0")
        d_str = now.strftime("%m/%d/%Y")
        dnd = run_short("xfconf-query -c xfce4-notifyd -p /do-not-disturb").lower() == "true"
        bell = "🔕" if dnd else "🔔"
        txt = (
            f"<span font='Inter 8.5' foreground='#ECFDF5' weight='600'>  {t_str}  {bell} </span>\n"
            f"<span font='Inter 8' foreground='#B7CEC3'>  {d_str}     </span>"
        )
        emit(
            txt,
            f"python3 '{SHELL_PY}' notifications",
            "Notifications & Calendar • Made by Muheeb",
        )

    elif kind == "lang":
        txt = (
            "<span font='Inter 7.5' foreground='#ECFDF5' weight='600'> ENG </span>\n"
            "<span font='Inter 7.5' foreground='#9CAEA5'> US  </span>"
        )
        emit(txt, f"python3 '{SHELL_PY}' winver", "Windows 11 Dark Green • Made by Muheeb")


if __name__ == "__main__":
    main()
