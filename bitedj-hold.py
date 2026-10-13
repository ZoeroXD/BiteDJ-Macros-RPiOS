#!/usr/bin/env python3
"""BiteDJ On/Off macro for the Pioneer DDJ-FLX4.

Hold both Loop In buttons to start BiteDJ (a Mixxx build).
Hold both Loop Out buttons to stop it.
"""
import subprocess, select, time, re, os

START_HOLD = 3.0
STOP_HOLD = 8.0
MIXXX = os.path.expanduser("~/bitedj/build/mixxx")
MATCH = "^" + MIXXX
PORT = "DDJ-FLX4"
LOOP_IN, LOOP_OUT = 16, 17
CHANNELS = (0, 1)
LOG = os.path.expanduser("~/bitedj-hold.log")
pat = re.compile(r"Note (on|off)\s+(\d+), note (\d+)(?:, velocity (\d+))?")

def log(msg):
    with open(LOG, "a") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")

def running():
    return subprocess.run(["pgrep", "-f", MATCH], capture_output=True).returncode == 0

def start():
    if running():
        log("start skipped: BiteDJ already running")
        return
    if not os.path.exists(MIXXX):
        log("start failed: " + MIXXX + " not found")
        return
    log("starting BiteDJ")
    subprocess.Popen([MIXXX, "--fullScreen"], cwd=os.path.dirname(MIXXX),
                     env=dict(os.environ),
                     stdout=subprocess.DEVNULL, stderr=open(LOG, "a"),
                     start_new_session=True)

def stop():
    log("stopping BiteDJ")
    subprocess.run(["pkill", "-TERM", "-f", MATCH])

ACTIONS = ((LOOP_IN, start, START_HOLD), (LOOP_OUT, stop, STOP_HOLD))

def watch():
    p = subprocess.Popen(["stdbuf", "-oL", "aseqdump", "-p", PORT],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    log("listening on " + PORT)
    held, armed = set(), {}
    while p.poll() is None:
        r, _, _ = select.select([p.stdout], [], [], 0.2)
        if r:
            m = pat.search(p.stdout.readline())
            if m:
                on = m.group(1) == "on" and m.group(4) != "0"
                ch, note = int(m.group(2)), int(m.group(3))
                if note in (LOOP_IN, LOOP_OUT) and ch in CHANNELS:
                    (held.add if on else held.discard)((ch, note))
        now = time.time()
        for note, action, hold in ACTIONS:
            both = all((c, note) in held for c in CHANNELS)
            if not both:
                armed.pop(note, None)
            elif note not in armed:
                armed[note] = now + hold
            elif now >= armed[note]:
                action()
                armed[note] = float("inf")
    log("lost " + PORT + ", retrying")

while True:
    try:
        watch()
    except Exception as e:
        log("error: " + repr(e))
    time.sleep(3)
