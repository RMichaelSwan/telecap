#!/usr/bin/env python3

"""
    TODO: Refactor to proper class structure

    Useful references:

    https://stackoverflow.com/a/53902189/5715374
    Useful, though the loopback is unnecessary: https://stackoverflow.com/a/56612274/5715374
"""

import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

def main():

    p = pyaudio.PyAudio()

    # ind = 6
    # devices = [p.get_device_info_by_index(i) for i in range(p.get_device_count())]

    # host_info = p.get_host_api_info_by_index(0)    
    # device_count = host_info.get('deviceCount')
    # devices = []
    # # iterate between devices:
    # for i in range(0, device_count):
    #     device = p.get_device_info_by_host_api_device_index(0, i)
    #     devices.append(device['name'])

    # for item in devices:
    #     print(item)
    # print(p.get_host_api_count())
    # print(f"device count: {device_count}")
    # print(devices[ind])

    stream = p.open(format=FORMAT,
                    channels=2,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

if __name__ == "__main__":
    main()