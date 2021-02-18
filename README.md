# telecap
Capture individual video streams from each video call/Zoom participant in real-time. Audio is a single stream. 

## Assumptions

* You are using a tool similar to Zoom in gallery mode and the window is currently open.
* Each user's video is rectangular and has an aspect ratio ~= 1.77 (H/W) -- note that aspect ration is a changeable argument in the ParticipantDetector class.

## Current limitations

* Ubuntu/GTK envrionments only: **no crossplatform support.**
* Relies on GTK 3.0 being installed on system (**likely only works on Linux/Ubuntu**)
* Has to activate desired window in order to get a handle on its pixels.
* Getting a handle on correct window may be adversely affected by system CPU load (may get a handle on incorrect window and thus require increased sleep time). Unable to programmatically wait for desired window to be active and get handle.
