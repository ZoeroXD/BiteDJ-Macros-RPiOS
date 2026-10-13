#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
mkdir -p ~/bin ~/.config/systemd/user
[ -f ~/bin/bitedj-hold.py ] && cp ~/bin/bitedj-hold.py ~/bin/bitedj-hold.py.bak
install -m 755 bitedj-hold.py ~/bin/bitedj-hold.py
install -m 755 bite-mode ~/bin/bite-mode
install -m 755 bitedj-toggle ~/bin/bitedj-toggle
install -m 644 systemd/bitedj-hold.service ~/.config/systemd/user/bitedj-hold.service

# At login, trim the desktop extras (panel, desktop icons) whenever the Bite Launcher is up
AUTOSTART=~/.config/labwc/autostart
if [ -f "$AUTOSTART" ] && ! grep -q "bite-mode boot" "$AUTOSTART"; then
  echo '$HOME/bin/bite-mode boot &   # bitedj-hold: trim desktop extras in launcher mode' >> "$AUTOSTART"
fi

# Ctrl+Alt+B toggles BiteDJ (labwc keybind), then reload labwc so it works right away
python3 add-keybind.py
[ -n "${WAYLAND_DISPLAY:-}" ] || export WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/$(id -u)
labwc --reconfigure 2>/dev/null || echo "Log out and back in (or reboot) to enable Ctrl+Alt+B"

# Start the user service at boot, even before anyone logs in
sudo loginctl enable-linger "$USER"

systemctl --user daemon-reload
systemctl --user enable bitedj-hold.service
systemctl --user restart bitedj-hold.service

echo
echo "Linger:  $(loginctl show-user "$USER" -p Linger --value)"
echo "Enabled: $(systemctl --user is-enabled bitedj-hold.service)"
echo "Active:  $(systemctl --user is-active bitedj-hold.service)"
echo "Mode:    $(~/bin/bite-mode status 2>/dev/null)"
echo "Log:     ~/bitedj-hold.log"
