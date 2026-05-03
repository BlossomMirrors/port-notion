#!/bin/bash
set -e
INDEX="$1"

# Fix tray icon and right-click menu
sed -i 's|this.tray.on("click",(()=>{this.onClick()}))|this.tray.setContextMenu(this.trayMenu),this.tray.on("click",(()=>{this.onClick()}))|g' "$INDEX"
sed -i 's|getIcon(){[^}]*}|getIcon(){return require("path").resolve(__dirname, "trayIcon.png");}|g' "$INDEX"

# Fake Windows user-agent to fix spellchecker and other issues
sed -i 's|e.setUserAgent(`${e.getUserAgent()} WantsServiceWorker`),|e.setUserAgent(`${e.getUserAgent().replace("Linux", "Windows")} WantsServiceWorker`),|g' "$INDEX"

# Fully disable auto-updates
sed -i 's|if("darwin"===process.platform){const e=l.systemPreferences?.getUserDefault(C,"boolean"),t=M.Store.getState().app.preferences?.isAutoUpdaterDisabled,r=M.Store.getState().app.preferences?.isAutoUpdaterOSSupportBypass,n=(0,y.isOsUnsupportedForAutoUpdates)();return Boolean(e\|\|t\|\|!r&&n)}return!1|return!0|g' "$INDEX"

# Fix URL opening / single instance lock on Linux
sed -i 's|handleOpenUrl);else if("win32"===process.platform)|handleOpenUrl);else if("linux"===process.platform)|g' "$INDEX"
sed -i 's|async function(){(0,E.setupCrashReporter)(),|o.app.requestSingleInstanceLock() ? async function(){(0,E.setupCrashReporter)(),|g' "$INDEX"
sed -i 's|setupCleanup)()}()}()|setupCleanup)()}()}() : o.app.quit();|g' "$INDEX"

# Use Linux tray menu style (Windows variant)
sed -i 's|r="win32"===process.platform?function(e,t)|r="linux"===process.platform?function(e,t)|g' "$INDEX"
