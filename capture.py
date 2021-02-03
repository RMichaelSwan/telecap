#!/usr/bin/env python3

"""
    A script to capture the screen from specific Gtk windows using Wnck.
    Assuming the window is acquired correctly, it does not have to be on top once
    session is started (minimization may cause a problem though).
    Wnck API Reference: https://lazka.github.io/pgi-docs/Wnck-3.0/classes/Screen.html
    Gdk API Reference: https://lazka.github.io/pgi-docs/Gdk-3.0/classes/Screen.html

    TODO: Process in OpenCV to get separate squares for each box in the window
    TODO: Allow user to select desired window to record
"""

import time
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Wnck', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, Wnck

Gtk.init([])  # necessary only if not using a Gtk.main() loop
screen = Wnck.Screen.get_default()
screen.force_update()  # recommended per Wnck documentation

# loop all windows
found_win = False
for i, window in enumerate(screen.get_windows()):
    name = window.get_name()
    if (name == "Zoom Meeting"):
        # Activate desired window  and wait for it to come up since there seems 
        # to be no way to tell Gdk which window to use directly.
        found_win = True
        window.activate(0)
        time.sleep(0.1)
        break
    # print(i, name)

if (not found_win):
    "Unable to find, activate, and record desired window."

screen = Gdk.Screen.get_default()
window = screen.get_active_window()
pb = Gdk.pixbuf_get_from_window(window, *window.get_geometry())
pb.savev("{}.png".format(0), "png", (), ())

# --FPS Test--
# TODO: move this test to a proper test case
i = 1
frames = 100
start = time.time()
while (i <= frames):
  pb = Gdk.pixbuf_get_from_window(window, *window.get_geometry())
#   pb.savev("{}.png".format(i), "png", (), ())
  i += 1
print("--- achieved %s fps ---" % (frames / (time.time() - start)))
# --End Test--

# clean up Wnck (saves resources, check documentation)
window = None
screen = None
Wnck.shutdown()


# --capture all windows--
# screen = Gdk.Screen.get_default()
# for i, window in enumerate(screen.get_window_stack()):
    # print(i, window.list_properties())
    # print(window.get_state())
    # if (window.get_state() == Gdk.WindowState.FOCUSED):
    # pb = Gdk.pixbuf_get_from_window(window, *window.get_geometry())
    # pb.savev("{}.png".format(i), "png", (), ())




#X11 attempt (had issues with screen capture, names work though)
# import Xlib.display

# screen = Xlib.display.Display().screen()
# root_win = screen.root

# savew = None
# window_names = []
# for window in root_win.query_tree()._data['children']:
#     window_name = window.get_wm_name()
#     window_names.append(window_name)

# print(window_names)