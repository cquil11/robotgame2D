import wave
import struct
import random
import os
import math

# Create sounds directory if needed
os.makedirs('sounds', exist_ok=True)

fname = os.path.join('sounds', 'explosion.wav')
framerate = 44100
duration = 0.45  # seconds
nframes = int(framerate * duration)
amp = 16000  # amplitude for 16-bit

with wave.open(fname, 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(framerate)

    for i in range(nframes):
        t = i / framerate
        # Exponential-ish envelope for a punchy burst
        env = max(0.0, (1.0 - (t / duration)) ** 2)
        # White noise combined with a lower-frequency roar component
        noise = random.uniform(-1.0, 1.0)
        roar = 0.5 * math.sin(2 * math.pi * 120 * t) * (1.0 - t / duration)
        sample = amp * env * (0.8 * noise + 0.2 * roar)
        # Clamp to 16-bit
        val = int(max(-32767, min(32767, sample)))
        wf.writeframes(struct.pack('<h', val))

print(f'Wrote explosion sample: {fname}')
