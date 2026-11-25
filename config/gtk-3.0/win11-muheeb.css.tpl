/* ==========================================================================
   Windows 11 Pro (Dark Green Mica Edition) — Made by Muheeb
   Custom GTK3 Overrides for XFCE4 Taskbar, Thunar Explorer, & Notifications
   ========================================================================== */

/* --- 1. WINDOWS 11 BOTTOM TASKBAR (48px Centered Dark Green Acrylic) --- */
.xfce4-panel.background {
    background-color: rgba(11, 20, 16, 0.95);
    border-top: 1px solid rgba(52, 211, 153, 0.20);
    color: #ECFDF5;
    font-family: "Inter", "Segoe UI", sans-serif;
}

.xfce4-panel button {
    background-color: transparent;
    background-image: none;
    border: 1px solid transparent;
    border-radius: 6px;
    margin: 4px 2px;
    padding: 0 5px;
    box-shadow: none;
    transition: all 120ms ease-in-out;
}

.xfce4-panel button:hover {
    background-color: rgba(52, 211, 153, 0.13);
    border-color: rgba(52, 211, 153, 0.22);
}

.xfce4-panel button:active,
.xfce4-panel button:checked {
    background-color: rgba(16, 185, 129, 0.20);
    border-color: rgba(52, 211, 153, 0.28);
}

/* Windows 11 Tasklist Running & Active App Indicators */
.xfce4-panel .tasklist button {
    min-width: 40px;
    margin: 4px 2px;
    padding: 0 6px;
    border-radius: 6px;
    border-bottom: 2px solid rgba(167, 243, 208, 0.35);
}

.xfce4-panel .tasklist button:checked {
    background-color: rgba(16, 185, 129, 0.22);
    border-bottom: 3px solid #34D399;
}

.xfce4-panel .tasklist button:hover {
    background-color: rgba(52, 211, 153, 0.16);
}

/* Windows 11 Genmon Pills (Search Pill, Control Bar Pill, Clock/Bell Pill, Widgets) */
#genmon-202 box,
#genmon-212 box,
#genmon-213 box,
#genmon-200 box,
#genmon-211 box {
    border-radius: 6px;
    padding: 2px 4px;
    margin: 4px 2px;
    transition: all 120ms ease;
}

/* Rounded Win11 Search Pill right next to Start Button */
#genmon-202 box {
    background-color: rgba(24, 40, 32, 0.92);
    border: 1px solid rgba(52, 211, 153, 0.26);
    border-radius: 18px;
    margin: 7px 4px;
    padding: 0 8px;
}

#genmon-202 box:hover {
    background-color: rgba(32, 54, 43, 0.98);
    border-color: #34D399;
}

/* Quick Settings (Wi-Fi + Vol + Battery) & Clock/Notification Hover Pills */
#genmon-212 box:hover,
#genmon-213 box:hover,
#genmon-200 box:hover,
#genmon-211 box:hover {
    background-color: rgba(52, 211, 153, 0.14);
}

/* Far-right Windows 11 Show Desktop Sliver */
#showdesktop-214 button {
    min-width: 6px;
    padding: 0 2px;
    margin: 4px 0 4px 2px;
    border-left: 1px solid rgba(52, 211, 153, 0.22);
    border-radius: 0;
}

/* System Tray Clean Spacing */
#systray-210 box {
    margin: 4px 2px;
    padding: 0 4px;
}

/* --- 2. THUNAR FILE EXPLORER — EXACT WINDOWS 11 EXPLORER (DARK GREEN) --- */
window.thunar {
    background-color: #0E1713;
    color: #ECFDF5;
}

/* Explorer Command & Navigation Bar */
window.thunar toolbar,
window.thunar #location-toolbar {
    background-color: #13201A;
    border-bottom: 1px solid rgba(52, 211, 153, 0.18);
    padding: 5px 8px;
    min-height: 42px;
}

window.thunar toolbar button {
    border-radius: 6px;
    min-width: 30px;
    min-height: 30px;
    margin: 0 2px;
    background: transparent;
    border: 1px solid transparent;
    color: #D1FAE5;
}

window.thunar toolbar button:hover {
    background-color: rgba(52, 211, 153, 0.14);
    border-color: rgba(52, 211, 153, 0.25);
}

/* Windows 11 Rounded Address / Path Bar with Emerald Focus Line */
window.thunar toolbar entry {
    background-color: #1A2B23;
    border: 1px solid rgba(52, 211, 153, 0.24);
    border-bottom: 2px solid #059669;
    border-radius: 6px;
    min-height: 32px;
    padding: 0 12px;
    margin: 0 6px;
    color: #ECFDF5;
    caret-color: #34D399;
}

window.thunar toolbar entry:focus {
    background-color: #0F1A15;
    border-color: rgba(52, 211, 153, 0.45);
    border-bottom: 2px solid #34D399;
}

/* Explorer Menubar sleek compact bar */
window.thunar menubar {
    background-color: #101B16;
    border-bottom: 1px solid rgba(52, 211, 153, 0.10);
    padding: 2px 6px;
    color: #CFE3D9;
}

/* Explorer Left Navigation Pane */
window.thunar scrolledwindow.sidebar,
window.thunar .sidebar {
    background-color: #101B16;
    border-right: 1px solid rgba(52, 211, 153, 0.16);
}

window.thunar .sidebar treeview.view {
    background-color: transparent;
    color: #E2F1EA;
    padding: 4px 6px;
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

/* Explorer Main Folder View */
window.thunar scrolledwindow.standard-view,
window.thunar .standard-view,
window.thunar exo-icon-view.view,
window.thunar treeview.view {
    background-color: #0D1511;
    color: #ECFDF5;
}

window.thunar exo-icon-view.view:selected,
window.thunar .standard-view *:selected {
    background-color: rgba(16, 185, 129, 0.26);
    border: 1px solid #34D399;
    border-radius: 6px;
    color: #FFFFFF;
}

/* Explorer Statusbar with Built-In 'Windows 11 Pro • Made by Muheeb' Vector Badge */
window.thunar statusbar {
    background-color: #121E18;
    border-top: 1px solid rgba(52, 211, 153, 0.18);
    color: #A7C4B6;
    min-height: 38px;
    padding: 2px 186px 2px 10px;
    background-image: url("__EXPLORER_BADGE__");
    background-repeat: no-repeat;
    background-position: 99% 50%;
}

/* --- 3. WINDOWS 11 TOAST NOTIFICATIONS (xfce4-notifyd) --- */
#XfceNotifyWindow {
    background-color: rgba(15, 25, 20, 0.96);
    border: 1px solid rgba(52, 211, 153, 0.36);
    border-radius: 10px;
    color: #ECFDF5;
}

#XfceNotifyWindow label#summary {
    font-weight: 700;
    color: #34D399;
}

/* --- 4. DESKTOP ICON LABELS (Clean Windows 11 Shadow Text) --- */
XfdesktopIconView.view {
    background: transparent;
    color: #ECFDF5;
    border-radius: 6px;
}

XfdesktopIconView.view:active,
XfdesktopIconView.view:selected {
    background-color: rgba(16, 185, 129, 0.28);
    border: 1px solid rgba(52, 211, 153, 0.55);
    border-radius: 6px;
}

XfdesktopIconView.view .label {
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.92);
}

/* --- 5. GLOBAL MENU & SELECTION POLISH (DARK GREEN) --- */
menu,
.menu,
.context-menu {
    background-color: #14221C;
    border: 1px solid rgba(52, 211, 153, 0.25);
    border-radius: 8px;
    padding: 5px;
    color: #ECFDF5;
}

menuitem {
    border-radius: 5px;
    padding: 6px 10px;
}

menuitem:hover {
    background-color: rgba(16, 185, 129, 0.24);
    color: #FFFFFF;
}
