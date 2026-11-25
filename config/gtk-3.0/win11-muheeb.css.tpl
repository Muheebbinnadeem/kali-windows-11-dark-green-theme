/* ==========================================================================
   Windows 11 Pro (Dark Green Mica Edition) — Made by Muheeb
   Original 96-DPI Windows 11 Sizing for Taskbar, Explorer & Notifications
   ========================================================================== */

/* --- 1. WINDOWS 11 BOTTOM TASKBAR (Exact 48px Height, 24px App Icons, 16px Tray) --- */
.xfce4-panel.background {
    background-color: rgba(11, 20, 16, 0.96);
    border-top: 1px solid rgba(52, 211, 153, 0.18);
    color: #ECFDF5;
    font-family: "Inter", "Segoe UI", sans-serif;
    font-size: 9.5pt;
}

.xfce4-panel button {
    background-color: transparent;
    background-image: none;
    border: 1px solid transparent;
    border-radius: 5px;
    margin: 4px 2px;
    padding: 0 5px;
    min-height: 38px;
    box-shadow: none;
    transition: background-color 110ms ease;
}

.xfce4-panel button:hover {
    background-color: rgba(255, 255, 255, 0.07);
    border-color: rgba(52, 211, 153, 0.16);
}

.xfce4-panel button:active,
.xfce4-panel button:checked {
    background-color: rgba(16, 185, 129, 0.18);
    border-color: rgba(52, 211, 153, 0.24);
}

/* Windows 11 Tasklist Running & Active App Indicators (40x40 Exact Win11 Slot) */
.xfce4-panel .tasklist button {
    min-width: 40px;
    min-height: 38px;
    margin: 4px 2px;
    padding: 0 6px;
    border-radius: 5px;
    border-bottom: 2px solid rgba(167, 243, 208, 0.35);
}

.xfce4-panel .tasklist button:checked {
    background-color: rgba(255, 255, 255, 0.08);
    border-bottom: 3px solid #34D399;
}

.xfce4-panel .tasklist button:hover {
    background-color: rgba(255, 255, 255, 0.10);
}

/* Genmon Image Buttons (Widgets, Search, Lang, Control Bar, Clock/Bell) */
.xfce4-panel #genmon-200 button,
.xfce4-panel #genmon-202 button,
.xfce4-panel #genmon-211 button,
.xfce4-panel #genmon-212 button,
.xfce4-panel #genmon-213 button {
    padding: 0 4px;
    margin: 4px 1px;
    border-radius: 5px;
    background: transparent;
    border: 1px solid transparent;
}

/* Search Pill Button uses its own Cairo pill border */
.xfce4-panel #genmon-202 button {
    padding: 0 2px;
}

.xfce4-panel #genmon-202 button:hover {
    background-color: transparent;
    border-color: transparent;
}

.xfce4-panel #genmon-200 button:hover,
.xfce4-panel #genmon-211 button:hover,
.xfce4-panel #genmon-212 button:hover,
.xfce4-panel #genmon-213 button:hover {
    background-color: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.06);
}

/* Hidden Icons Chevron ('^') only in Systray — 16px clean slot */
#systray-210 box {
    margin: 4px 1px;
    padding: 0 2px;
}

#systray-210 button {
    min-width: 24px;
    padding: 0 3px;
    margin: 6px 1px;
}

/* Far-right Windows 11 Show Desktop Corner Sliver (6px wide) */
#showdesktop-214 button {
    min-width: 6px;
    padding: 0 2px;
    margin: 6px 0 6px 2px;
    border-left: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 0;
}

#showdesktop-214 button image {
    -gtk-icon-transform: scale(0);
    min-width: 0;
}

/* --- 2. THUNAR FILE EXPLORER — EXACT WINDOWS 11 EXPLORER (DARK GREEN) --- */
window.thunar {
    background-color: #0E1713;
    color: #ECFDF5;
    font-size: 9.5pt;
}

window.thunar toolbar,
window.thunar #location-toolbar {
    background-color: #13201A;
    border-bottom: 1px solid rgba(52, 211, 153, 0.16);
    padding: 4px 8px;
    min-height: 40px;
}

window.thunar toolbar button {
    border-radius: 5px;
    min-width: 28px;
    min-height: 28px;
    margin: 0 2px;
    background: transparent;
    border: 1px solid transparent;
    color: #D1FAE5;
}

window.thunar toolbar button:hover {
    background-color: rgba(52, 211, 153, 0.14);
    border-color: rgba(52, 211, 153, 0.22);
}

window.thunar toolbar entry {
    background-color: #1A2B23;
    border: 1px solid rgba(52, 211, 153, 0.22);
    border-bottom: 2px solid #059669;
    border-radius: 5px;
    min-height: 30px;
    padding: 0 10px;
    margin: 0 6px;
    color: #ECFDF5;
    caret-color: #34D399;
}

window.thunar toolbar entry:focus {
    background-color: #0F1A15;
    border-color: rgba(52, 211, 153, 0.42);
    border-bottom: 2px solid #34D399;
}

window.thunar scrolledwindow.sidebar,
window.thunar .sidebar {
    background-color: #101B16;
    border-right: 1px solid rgba(52, 211, 153, 0.14);
}

window.thunar .sidebar treeview.view {
    background-color: transparent;
    color: #E2F1EA;
    padding: 4px 6px;
}

window.thunar .sidebar treeview.view:hover {
    background-color: rgba(52, 211, 153, 0.10);
    border-radius: 5px;
}

window.thunar .sidebar treeview.view:selected {
    background-color: rgba(5, 150, 105, 0.28);
    color: #FFFFFF;
    border-left: 3px solid #34D399;
}

window.thunar scrolledwindow.standard-view,
window.thunar .standard-view,
window.thunar exo-icon-view.view,
window.thunar treeview.view {
    background-color: #0D1511;
    color: #ECFDF5;
}

window.thunar exo-icon-view.view:selected,
window.thunar .standard-view *:selected {
    background-color: rgba(16, 185, 129, 0.24);
    border: 1px solid #34D399;
    border-radius: 5px;
    color: #FFFFFF;
}

/* Explorer Statusbar with Right-Aligned 'Windows 11 Pro • Made by Muheeb' Badge */
window.thunar statusbar {
    background-color: #121E18;
    border-top: 1px solid rgba(52, 211, 153, 0.16);
    color: #A7C4B6;
    min-height: 38px;
    padding: 2px 186px 2px 10px;
    background-image: url("__EXPLORER_BADGE__");
    background-repeat: no-repeat;
    background-position: 99% 50%;
}

/* --- 3. WINDOWS 11 TOAST NOTIFICATIONS --- */
#XfceNotifyWindow {
    background-color: rgba(15, 25, 20, 0.96);
    border: 1px solid rgba(52, 211, 153, 0.34);
    border-radius: 8px;
    color: #ECFDF5;
}

#XfceNotifyWindow label#summary {
    font-weight: 700;
    color: #34D399;
}

/* --- 4. DESKTOP ICON LABELS (Original Win11 9pt Crisp Labels) --- */
XfdesktopIconView.view {
    background: transparent;
    color: #ECFDF5;
    border-radius: 4px;
}

XfdesktopIconView.view:active,
XfdesktopIconView.view:selected {
    background-color: rgba(16, 185, 129, 0.25);
    border: 1px solid rgba(52, 211, 153, 0.50);
    border-radius: 4px;
}

XfdesktopIconView.view .label {
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.94);
}

/* --- 5. CONTEXT MENUS --- */
menu,
.menu,
.context-menu {
    background-color: #14221C;
    border: 1px solid rgba(52, 211, 153, 0.24);
    border-radius: 8px;
    padding: 4px;
    color: #ECFDF5;
}

menuitem {
    border-radius: 4px;
    padding: 5px 10px;
}

menuitem:hover {
    background-color: rgba(16, 185, 129, 0.24);
    color: #FFFFFF;
}
