# BiteDJ On/Off Macro with FLX4

Start and stop BiteDJ (a Mixxx build), and switch between the Bite Launcher and the regular Raspberry Pi desktop, using only the Pioneer DDJ-FLX4 controller. No keyboard, mouse, or touchscreen needed.

| Action | Gesture |
|---|---|
| Start BiteDJ (full screen) | Hold **both Loop In** buttons for 3 seconds |
| Stop BiteDJ | Hold **both Loop Out** buttons for 8 seconds |
| Switch Bite Launcher ⇄ Pi desktop | Hold **both 4 BEAT/EXIT** buttons for 8 seconds |

A small Python script listens to the FLX4 MIDI port with `aseqdump` and runs as a systemd user service, so it is always ready after boot and reconnects automatically if the controller is unplugged.

## Requirements

- Raspberry Pi OS (desktop) with a Pioneer DDJ-FLX4 connected by USB
- `alsa-utils` (provides `aseqdump`): `sudo apt install alsa-utils`
- BiteDJ / Mixxx built at `~/bitedj/build/mixxx` (edit `MIXXX` in the script if yours is elsewhere)

## Install Steps - Run this Script 

```bash
git clone https://github.com/ZoeroXD/BiteDJ-On-Off-Macro-with-FLX4.git
cd BiteDJ-On-Off-Macro-with-FLX4
./install.sh
```

This copies the script to `~/bin/bitedj-hold.py`, installs the user service, and starts it. An existing script is backed up to `~/bin/bitedj-hold.py.bak`.

## Switch between Bite Launcher and the Pi desktop

Hold **both 4 BEAT/EXIT** buttons (deck 1 and deck 2) together for 8 seconds. Letting go of either one early cancels it. The switch runs `~/bin/bite-mode toggle`:

| You are in | After the 8-second hold |
|---|---|
| **Bite Launcher** (running, with or without BiteDJ on top) | BiteDJ closes (it gets 15 seconds to save and quit), the Bite Launcher and its black backdrop close, and the Pi desktop comes back: taskbar (`wf-panel-pi`) and desktop icons/wallpaper (`pcmanfm-pi`) |
| **Pi desktop** (Bite Launcher not running) | The taskbar and desktop are stopped, the black backdrop starts, and the Bite Launcher opens |

The switch is remembered across reboots. Switching to the Pi desktop turns the Bite Launcher's autostart off, and switching back turns it on again, so the Pi boots into whichever mode you used last. This is the same as **Ctrl+Alt+D** in the Bite Launcher, and as double-clicking its **Bite Launcher** desktop shortcut. All three share one marker file, `~/.config/bite-launcher/autostart-off`: when it exists, the launcher doesn't start at login.

Why the desktop needs stopping: Raspberry Pi OS starts labwc in merge mode (`labwc -m`), so the system autostart (taskbar, desktop) still runs behind the full-screen Bite Launcher and uses RAM and CPU. Those programs are wrapped in `lwrespawn`, which restarts them a second after they close, so `bite-mode` stops the `lwrespawn` loop first and then the program. `pcmanfm-pi` is a wrapper script, so the `pcmanfm --desktop` (or wallpaper `swaybg`) process it starts is stopped as well. `install.sh` also adds `bite-mode boot` to `~/.config/labwc/autostart`, so the taskbar and desktop are stopped right after login whenever the Bite Launcher is up.

Pressing 4 BEAT/EXIT inside BiteDJ also starts a 4-beat loop on each deck before the 8 seconds are up. That is harmless when you are leaving BiteDJ anyway.

The Bite Launcher has its own ways in and out as well: **Switch to Pi Desktop** in its tray panel (tap the clock), **Ctrl+Alt+D**, and the **Bite Launcher** desktop icon to come back.

You can also run it over SSH:

```bash
~/bin/bite-mode status     # launcher | desktop
~/bin/bite-mode desktop    # force the Pi desktop
~/bin/bite-mode launcher   # force the Bite Launcher
```

This needs the [Bite Launcher](https://github.com/ZoeroXD/BiteDJ-Launcher) installed at `/usr/local/bin/bitedj-launcher` (`/opt/bitedj-launcher/bitedj_launcher.py`).

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
| `MODE_HOLD` | `8.0` | Seconds to hold both 4 BEAT/EXIT buttons |
| `MIXXX` | `~/bitedj/build/mixxx` | Path to the BiteDJ binary |
| `PORT` | `DDJ-FLX4` | MIDI port name (check with `aseqdump -l`) |
| `LOOP_IN`, `LOOP_OUT` | `16`, `17` | MIDI note numbers of the buttons |
| `BEAT4_EXIT` | `77` (0x4D) | MIDI note number of 4 BEAT/EXIT |
| `CHANNELS` | `(0, 1)` | MIDI channels of deck 1 and deck 2 |

Mode-switch settings go in `/etc/djrig.conf` (all optional):

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
aseqdump -p DDJ-FLX4   # Loop In: "note 16", 4 BEAT/EXIT: "note 77"
systemctl --user start bitedj-hold.service
```

If the notes differ on your unit, update `LOOP_IN`, `LOOP_OUT` or `BEAT4_EXIT`. Mode switches are logged to `~/bitedj-hold.log` as `bite-mode: switching to ...`.

## Uninstall

```bash
systemctl --user disable --now bitedj-hold.service
rm ~/.config/systemd/user/bitedj-hold.service ~/bin/bitedj-hold.py ~/bin/bite-mode
sed -i '/bite-mode boot/d' ~/.config/labwc/autostart
systemctl --user daemon-reload
```

## License

MIT
