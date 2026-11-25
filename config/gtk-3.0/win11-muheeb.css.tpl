/* ==========================================================================
   Windows 11 Pro (Dark Green Mica Edition) — Made by Muheeb
   125% Recommended Scale (120 DPI, 56px Centered Taskbar, Aligned Explorer)
   ========================================================================== */

/* --- 1. WINDOWS 11 BOTTOM TASKBAR (56px at 125% Scale, Dead-Center Alignment) --- */
.xfce4-panel.background {
    background-color: rgba(11, 20, 16, 0.96);
    border-top: 1px solid rgba(52, 211, 153, 0.20);
    color: #ECFDF5;
    font-family: "Inter", "Segoe UI", sans-serif;
    font-size: 10.5pt;
}

.xfce4-panel button {
    background-color: transparent;
    background-image: none;
    border: 1px solid transparent;
    border-radius: 6px;
    margin: 5px 3px;
    padding: 0 7px;
    min-width: 44px;
    min-height: 44px;
    box-shadow: none;
    transition: background-color 110ms ease;
}

.xfce4-panel button:hover {
    background-color: rgba(255, 255, 255, 0.08);
    border-color: rgba(52, 211, 153, 0.18);
}

.xfce4-panel button:active,
.xfce4-panel button:checked {
    background-color: rgba(16, 185, 129, 0.20);
    border-color: rgba(52, 211, 153, 0.28);
}

/* Windows 11 Tasklist Running & Active App Indicators (46x44 Slot at 125% Scale) */
.xfce4-panel .tasklist button {
    min-width: 46px;
    min-height: 44px;
    margin: 5px 3px;
    padding: 0 7px;
    border-radius: 6px;
    border-bottom: 2px solid rgba(167, 243, 208, 0.38);
}

.xfce4-panel .tasklist button:checked {
    background-color: rgba(255, 255, 255, 0.09);
    border-bottom: 3px solid #34D399;
}

.xfce4-panel .tasklist button:hover {
    background-color: rgba(255, 255, 255, 0.11);
}

/* Genmon Image Pills (Widgets, Search, Lang, Control Bar, Clock/Bell) */
.xfce4-panel #genmon-200 button,
.xfce4-panel #genmon-202 button,
.xfce4-panel #genmon-211 button,
.xfce4-panel #genmon-212 button,
.xfce4-panel #genmon-213 button {
    padding: 0 5px;
    margin: 5px 2px;
    min-height: 44px;
    min-width: 0;
    border-radius: 6px;
    background: transparent;
    border: 1px solid transparent;
}

/* Left Balance Spacer (Non-interactive) */
.xfce4-panel #genmon-219,
.xfce4-panel #genmon-219 box,
.xfce4-panel #genmon-219 button {
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
    margin: 0;
}

.xfce4-panel #genmon-202 button {
    padding: 0 3px;
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
    border-color: rgba(255, 255, 255, 0.08);
}

/* Hidden Icons Chevron ('^') only in Systray */
#systray-210 box {
    margin: 5px 2px;
    padding: 0 2px;
}

#systray-210 button {
    min-width: 28px;
    min-height: 40px;
    padding: 0 4px;
    margin: 6px 1px;
}

/* Far-right Windows 11 Show Desktop Corner Sliver */
#showdesktop-214 button {
    min-width: 8px;
    padding: 0 2px;
    margin: 8px 0 8px 3px;
    border-left: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 0;
}

#showdesktop-214 button image {
    -gtk-icon-transform: scale(0);
    min-width: 0;
}

/* --- 2. THUNAR FILE EXPLORER — 125% WINDOWS 11 EXPLORER (DARK GREEN) --- */
window.thunar {
    background-color: #0E1713;
    color: #ECFDF5;
    font-size: 10.5pt;
}

window.thunar toolbar,
window.thunar #location-toolbar {
    background-color: #13201A;
    border-bottom: 1px solid rgba(52, 211, 153, 0.18);
    padding: 6px 10px;
    min-height: 48px;
}

window.thunar toolbar button {
    border-radius: 6px;
    min-width: 34px;
    min-height: 34px;
    margin: 0 3px;
    background: transparent;
    border: 1px solid transparent;
    color: #D1FAE5;
}

window.thunar toolbar button:hover {
    background-color: rgba(52, 211, 153, 0.15);
    border-color: rgba(52, 211, 153, 0.25);
}

window.thunar toolbar entry {
    background-color: #1A2B23;
    border: 1px solid rgba(52, 211, 153, 0.24);
    border-bottom: 2px solid #059669;
    border-radius: 6px;
    min-height: 36px;
    padding: 0 14px;
    margin: 0 8px;
    color: #ECFDF5;
    caret-color: #34D399;
}

window.thunar toolbar entry:focus {
    background-color: #0F1A15;
    border-color: rgba(52, 211, 153, 0.45);
    border-bottom: 2px solid #34D399;
}

window.thunar scrolledwindow.sidebar,
window.thunar .sidebar {
    background-color: #101B16;
    border-right: 1px solid rgba(52, 211, 153, 0.15);
}

window.thunar .sidebar treeview.view {
    background-color: transparent;
    color: #E2F1EA;
    padding: 6px 8px;
}

window.thunar .sidebar treeview.view:hover {
    background-color: rgba(52, 211, 153, 0.10);
    border-radius: 6px;
}

window.thunar .sidebar treeview.view:selected {
    background-color: rgba(5, 150, 105, 0.30);
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
    background-color: rgba(16, 185, 129, 0.25);
    border: 1px solid #34D399;
    border-radius: 6px;
    color: #FFFFFF;
}

window.thunar statusbar {
    background-color: #121E18;
    border-top: 1px solid rgba(52, 211, 153, 0.16);
    color: #A7C4B6;
    min-height: 42px;
    padding: 3px 190px 3px 12px;
    background-image: url("__EXPLORER_BADGE__");
    background-repeat: no-repeat;
    background-position: 99% 50%;
}

/* --- 3. WINDOWS 11 TOAST NOTIFICATIONS --- */
#XfceNotifyWindow {
    background-color: rgba(15, 25, 20, 0.97);
    border: 1px solid rgba(52, 211, 153, 0.36);
    border-radius: 10px;
    color: #ECFDF5;
}

#XfceNotifyWindow label#summary {
    font-weight: 700;
    color: #34D399;
}

/* --- 4. DESKTOP ICON LABELS (125% Scale) --- */
XfdesktopIconView.view {
    background: transparent;
    color: #ECFDF5;
    border-radius: 6px;
}

XfdesktopIconView.view:active,
XfdesktopIconView.view:selected {
    background-color: rgba(16, 185, 129, 0.26);
    border: 1px solid rgba(52, 211, 153, 0.52);
    border-radius: 6px;
}

XfdesktopIconView.view .label {
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.94);
}

/* --- 5. CONTEXT MENUS --- */
menu,
.menu,
.context-menu {
    background-color: #14221C;
    border: 1px solid rgba(52, 211, 153, 0.26);
    border-radius: 8px;
    padding: 6px;
    color: #ECFDF5;
}

menuitem {
    border-radius: 5px;
    padding: 7px 12px;
}

menuitem:hover {
    background-color: rgba(16, 185, 129, 0.25);
    color: #FFFFFF;
}
