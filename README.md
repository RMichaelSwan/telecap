# telecap
Capture individual video streams from each video call/Zoom participant in real-time. Audio is a single stream. 

## Assumptions

* You are using a tool similar to Zoom in gallery mode and the window is currently open.
* You are using PulseAudio

## Current limitations

* Ubuntu/GTK envrionments only: **no crossplatform support.**
* Relies on GTK 3.0 being installed on system (**likely only works on Linux/Ubuntu**)
* Has to activate desired window in order to get a handle on its pixels.
* Getting a handle on correct window may be adversely affected by system CPU load (may get a handle on incorrect window and thus require increased sleep time). Unable to programmatically wait for desired window to be active and get handle.
* Resizing your video window during capture will likely cause instability/crashes/missing participants
* Large video window sizes (e.g. full screen) may cause instability/crashes

# Audio Setup

Audio setup in Linux is not clean. You either need to know too much (i.e. [create a virtual loopback device through Alsa](https://unix.stackexchange.com/a/310200)) or you have to run a manual config step (**our approach**).

1. Install pavucontrol if not already installed: `sudo apt-get install pavucontrol`
2. Open pavucontrol, and navigate to the recording tab.
![pavucontrol][./pavucontrol-example.png]
3. Run audio setup and follow instructions: `python3 setup_audio.py`
