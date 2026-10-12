# BiteDJ On/Off Macro with FLX4

Start and stop BiteDJ (a Mixxx build) on a Raspberry Pi using only the Pioneer DDJ-FLX4 controller. No keyboard, mouse, or touchscreen needed.

| Action | Gesture |
|---|---|
| Start BiteDJ (full screen) | Hold **both Loop In** buttons for 3 seconds |
| Stop BiteDJ | Hold **both Loop Out** buttons for 8 seconds |

A small Python script listens to the FLX4 MIDI port with `aseqdump` and runs as a systemd user service, so it is always ready after boot and reconnects automatically if the controller is unplugged.

## Requirements

- Raspberry Pi OS (desktop) with a Pioneer DDJ-FLX4 connected by USB
- `alsa-utils` (provides `aseqdump`): `sudo apt install alsa-utils`
- BiteDJ / Mixxx built at `~/bitedj/build/mixxx` (edit `MIXXX` in the script if yours is elsewhere)

## Install

```bash
git clone https://github.com/ZoeroXD/BiteDJ-On-Off-Macro-with-FLX4.git
cd BiteDJ-On-Off-Macro-with-FLX4
./install.sh
```

This copies the script to `~/bin/bitedj-hold.py`, installs the user service, and starts it. An existing script is backed up to `~/bin/bitedj-hold.py.bak`.

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
aseqdump -p DDJ-FLX4   # press Loop In: expect "Note on 0, note 16"
systemctl --user start bitedj-hold.service
```

If the Loop In / Loop Out notes differ on your unit, update `LOOP_IN` and `LOOP_OUT`.

## Uninstall

```bash
systemctl --user disable --now bitedj-hold.service
rm ~/.config/systemd/user/bitedj-hold.service ~/bin/bitedj-hold.py
systemctl --user daemon-reload
```

## License

MIT
