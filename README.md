# BiteDJ Macros for Raspberry Pi OS

Start and stop BiteDJ (a Mixxx build) on a Raspberry Pi with the Pioneer DDJ-FLX4 controller, no mouse or touchscreen needed, or toggle it with Ctrl+Alt+B on a keyboard.

| Action | Gesture |
|---|---|
| Start BiteDJ (full screen) | Hold **both Loop In** buttons for 3 seconds |
| Stop BiteDJ | Hold **both Loop Out** buttons for 8 seconds |
| Toggle BiteDJ from a keyboard | Press **Ctrl+Alt+B** |

A small Python script listens to the FLX4 MIDI port with `aseqdump` and runs as a systemd user service, so it is always ready after boot and reconnects automatically if the controller is unplugged.

## Requirements

- Raspberry Pi OS (desktop) with a Pioneer DDJ-FLX4 connected by USB
- `alsa-utils` (provides `aseqdump`): `sudo apt install alsa-utils`
- BiteDJ / Mixxx built at `~/bitedj/build/mixxx` (edit `MIXXX` in the script if yours is elsewhere)

## Install Steps - Run this Script 

```bash
git clone https://github.com/ZoeroXD/BiteDJ-Macros-RPiOS.git
cd BiteDJ-Macros-RPiOS
./install.sh
```

This copies the scripts to `~/bin`, adds the Ctrl+Alt+B shortcut, installs the user service, and starts it. An existing script is backed up to `~/bin/bitedj-hold.py.bak`.

## Ctrl+Alt+B keyboard shortcut

`install.sh` adds a labwc keybind to `~/.config/labwc/rc.xml` (backup saved as `rc.xml.bak`) that runs `~/bin/bitedj-toggle`:

- BiteDJ not running: starts `/home/xdj/bitedj/build/mixxx --fullScreen`
- BiteDJ running: closes it with `pkill mixxx`

labwc catches the shortcut before any app, so it works on the Pi desktop, over the Bite Launcher, and inside BiteDJ. The installer reloads labwc (`labwc --reconfigure`) so it works right away. Running the installer again does not add a second copy.

## bite-mode helper for the Bite Launcher

`install.sh` also installs `~/bin/bite-mode`. There is no FLX4 button for it; the [Bite Launcher](https://github.com/ZoeroXD/BiteDJ-Launcher) uses it when you pick **Switch to Pi Desktop** in its tray panel (tap the clock), press **Ctrl+Alt+D**, or double-click the **Bite Launcher** desktop icon to come back.

| Switching to | What happens |
|---|---|
| **Pi desktop** | BiteDJ closes (it gets 15 seconds to save and quit), the Bite Launcher and its black backdrop close, and the taskbar (`wf-panel-pi`) and desktop (`pcmanfm-pi`) come back |
| **Bite Launcher** | The taskbar and desktop are stopped, the black backdrop starts, and the Bite Launcher opens |

The choice is remembered across reboots through `~/.config/bite-launcher/autostart-off`: when that file exists, the launcher doesn't start at login.

Why the desktop needs stopping: Raspberry Pi OS starts labwc in merge mode (`labwc -m`), so the taskbar and desktop still run behind the full-screen Bite Launcher and use RAM and CPU. They are wrapped in `lwrespawn`, which restarts them a second after they close, so `bite-mode` stops the `lwrespawn` loop first. `install.sh` adds `bite-mode boot` to `~/.config/labwc/autostart`, so they are stopped right after login whenever the Bite Launcher is up.

Over SSH:

```bash
~/bin/bite-mode status     # launcher | desktop
~/bin/bite-mode desktop    # force the Pi desktop
~/bin/bite-mode launcher   # force the Bite Launcher
```

## Always running

The service is set up to run all the time:

- **Starts at boot:** `install.sh` runs `sudo loginctl enable-linger $USER`, so the user service starts when the Pi boots, not only after you log in.
- **Restarts on crash:** `Restart=always` with `RestartSec=3` brings it back 3 seconds after any exit.
- **Never gives up:** `StartLimitIntervalSec=0` stops systemd from disabling it after repeated restarts.
- **Survives unplugging:** the script reconnects to the FLX4 every 3 seconds when the controller is missing.

Check all of it at once:

```bash
loginctl show-user "$USER" -p Linger          # Linger=yes
systemctl --user is-enabled bitedj-hold.service   # enabled
systemctl --user is-active bitedj-hold.service    # active
```

BiteDJ itself only opens on screen once the desktop is up, so use desktop autologin (`sudo raspi-config` > System Options > Boot / Auto Login > Desktop Autologin) for a fully hands-free rig.

## Configure

Edit the top of `~/bin/bitedj-hold.py`, then run `systemctl --user restart bitedj-hold.service`.

| Setting | Default | Meaning |
|---|---|---|
| `START_HOLD` | `3.0` | Seconds to hold both Loop In buttons |
| `STOP_HOLD` | `8.0` | Seconds to hold both Loop Out buttons |
| `MIXXX` | `~/bitedj/build/mixxx` | Path to the BiteDJ binary |
| `PORT` | `DDJ-FLX4` | MIDI port name (check with `aseqdump -l`) |
| `LOOP_IN`, `LOOP_OUT` | `16`, `17` | MIDI note numbers of the buttons |
| `CHANNELS` | `(0, 1)` | MIDI channels of deck 1 and deck 2 |

`bite-mode` settings go in `/etc/djrig.conf` (all optional):

| Setting | Default | Meaning |
|---|---|---|
| `BITE_MODE_DESKTOP` | `"pcmanfm-pi wf-panel-pi"` | Desktop programs stopped in launcher mode and restarted in desktop mode |
| `BITE_MODE_EXTRA_STOP` | (empty) | More programs to stop in launcher mode, for example `"squeekboard"`. These are not restarted |
| `BITE_MODE_CLOSE_BITEDJ` | `1` | `0` = leave BiteDJ open when switching to the desktop |

Only the BiteDJ binary at `MIXXX` is matched, so a separately installed stock Mixxx is never blocked or closed.

## Troubleshooting

```bash
systemctl --user status bitedj-hold.service --no-pager
tail -n 20 ~/bitedj-hold.log
lsusb | grep -i -E "pioneer|alphatheta|ddj"
aseqdump -l
```

To confirm the button notes, stop the service and watch the presses:

```bash
systemctl --user stop bitedj-hold.service
aseqdump -p DDJ-FLX4   # Loop In: "note 16", Loop Out: "note 17"
systemctl --user start bitedj-hold.service
```

If the notes differ on your unit, update `LOOP_IN` and `LOOP_OUT`. Mode switches are logged to `~/bitedj-hold.log` as `bite-mode: switching to ...`.

## Uninstall

```bash
systemctl --user disable --now bitedj-hold.service
rm ~/.config/systemd/user/bitedj-hold.service ~/bin/bitedj-hold.py ~/bin/bite-mode ~/bin/bitedj-toggle
sed -i '/bitedj-toggle/d' ~/.config/labwc/rc.xml && labwc --reconfigure
sed -i '/bite-mode boot/d' ~/.config/labwc/autostart
systemctl --user daemon-reload
```

## License

MIT
