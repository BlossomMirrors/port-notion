#!/bin/bash
XDG_CONFIG_HOME=${XDG_CONFIG_HOME:-~/.config}

if [[ -f $XDG_CONFIG_HOME/notion-flags.conf ]]; then
    NOTION_USER_FLAGS="$(grep -v '^#' $XDG_CONFIG_HOME/notion-flags.conf)"
fi

exec /app/lib/notion/electron \
    --no-sandbox \
    /app/lib/notion/resources/app.asar \
    $NOTION_USER_FLAGS "$@"
