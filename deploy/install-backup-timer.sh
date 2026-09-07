#!/usr/bin/env sh
# Install the Oracle pilot's daily database-backup systemd timer.
# Run from the repository root with: sudo ./deploy/install-backup-timer.sh
set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo "Run this installer with sudo." >&2
    exit 1
fi

install -m 0644 deploy/systemd/msfea-chatbot-backup.service \
    /etc/systemd/system/msfea-chatbot-backup.service
install -m 0644 deploy/systemd/msfea-chatbot-backup.timer \
    /etc/systemd/system/msfea-chatbot-backup.timer

systemctl daemon-reload
systemctl enable --now msfea-chatbot-backup.timer

echo "Daily backup timer installed."
systemctl list-timers msfea-chatbot-backup.timer --no-pager
