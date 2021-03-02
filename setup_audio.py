#!/usr/bin/env python3

    """
    Sets up your PC to capture audio played to speakers. Refer to README.MD for full instructions.
    """

import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

def main():

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=2,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    input("""
Stream opened. You should see it in the Recording tab of pavucontrol. 
Select the from device for this recorder (likely a Monitor of your default speaker). 
If you are currently playing anything to that device, the bar below it should be moving. 
When done, press Enter to continue...""")
    print("Setup done!")

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    main()