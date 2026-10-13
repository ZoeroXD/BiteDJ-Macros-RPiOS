#!/usr/bin/env python3
"""Add (or refresh) the Ctrl+Alt+B keybind in ~/.config/labwc/rc.xml."""
import os, re, shutil
path = os.path.expanduser("~/.config/labwc/rc.xml")
cmd = os.path.expanduser("~/bin/bitedj-toggle")
bind = ('<keybind key="C-A-b"><!-- bitedj-toggle -->'
        '<action name="Execute" command="%s"/></keybind>' % cmd)
os.makedirs(os.path.dirname(path), exist_ok=True)
if not os.path.exists(path):
    xml = '<?xml version="1.0"?>\n<openbox_config xmlns="http://openbox.org/3.4/rc">\n</openbox_config>\n'
else:
    xml = open(path).read()
    shutil.copy(path, path + ".bak")
# drop an older copy of our bind
xml = re.sub(r'\s*<keybind key="C-A-b"><!-- bitedj-toggle -->.*?</keybind>', "", xml, flags=re.S)
if re.search(r"<keyboard\s*/>", xml):
    xml = re.sub(r"<keyboard\s*/>", "<keyboard>\n    %s\n  </keyboard>" % bind, xml, count=1)
elif "<keyboard" in xml:
    xml = re.sub(r"(<keyboard[^>]*>)", r"\1\n    " + bind.replace("\\", "\\\\"), xml, count=1)
else:
    root = re.search(r"</(openbox_config|labwc_config)>", xml)
    if not root:
        raise SystemExit("rc.xml has no <openbox_config> or <labwc_config> root, not changed")
    xml = xml[:root.start()] + "  <keyboard>\n    %s\n  </keyboard>\n" % bind + xml[root.start():]
open(path, "w").write(xml)
print("Ctrl+Alt+B ->", cmd, "in", path)
