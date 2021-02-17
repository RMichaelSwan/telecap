# telecap
Capture individual audio and video from each video call/Zoom participant in real-time

## Current limitations

* Relies on GTK 3.0 being installed on system (**likely only works on Linux/Ubuntu**)
* Has to activate desired window in order to get a handle on its pixels.
* Getting a handle on correct window may be adversely affected by system CPU load (may get a handle on incorrect window and thus require increased sleep time). Unable to programmatically wait for desired window to be active and get handle.
