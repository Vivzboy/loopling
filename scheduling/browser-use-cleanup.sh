#!/bin/bash
# browser-use-cleanup.sh — sweep leaked browser-use temp Chrome profiles.
# browser-use copies the Chrome profile to a temp dir per session; if a session crashes
# or never calls `close`, these pile up (can reach multiple GB and slow the Mac badly).
# Deletes ones older than 30 min. Safe to run on a schedule (e.g. launchd every 2 hours).

find /private/var/folders -maxdepth 4 -type d -name "browser-use-user-data-dir-*" \
  -mmin +30 -exec rm -rf {} + 2>/dev/null
echo "[$(date '+%Y-%m-%d %H:%M:%S')] browser-use temp cleanup done"
