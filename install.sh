#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
mkdir -p ~/bin ~/.config/systemd/user
[ -f ~/bin/bitedj-hold.py ] && cp ~/bin/bitedj-hold.py ~/bin/bitedj-hold.py.bak
install -m 755 bitedj-hold.py ~/bin/bitedj-hold.py
install -m 644 systemd/bitedj-hold.service ~/.config/systemd/user/bitedj-hold.service

# Start the user service at boot, even before anyone logs in
sudo loginctl enable-linger "$USER"

systemctl --user daemon-reload
systemctl --user enable bitedj-hold.service
systemctl --user restart bitedj-hold.service

echo
echo "Linger:  $(loginctl show-user "$USER" -p Linger --value)"
echo "Enabled: $(systemctl --user is-enabled bitedj-hold.service)"
echo "Active:  $(systemctl --user is-active bitedj-hold.service)"
echo "Log:     ~/bitedj-hold.log"
