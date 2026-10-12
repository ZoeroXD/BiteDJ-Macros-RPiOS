#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
mkdir -p ~/bin ~/.config/systemd/user
[ -f ~/bin/bitedj-hold.py ] && cp ~/bin/bitedj-hold.py ~/bin/bitedj-hold.py.bak
install -m 755 bitedj-hold.py ~/bin/bitedj-hold.py
install -m 644 systemd/bitedj-hold.service ~/.config/systemd/user/bitedj-hold.service
systemctl --user daemon-reload
systemctl --user enable bitedj-hold.service
systemctl --user restart bitedj-hold.service
echo "Installed. Log: ~/bitedj-hold.log"
