import wave
import wave
import struct
import math
import random
import os

os.makedirs('sounds', exist_ok=True)

framerate = 44100

def synth_goblin(path):
    """Dramatic goblin death: layered squeal, guttural underlayer and short yelps."""
    duration = 0.65
    nframes = int(framerate * duration)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        for i in range(nframes):
            t = i / framerate
            # envelope: quick attack then slower decay
            if t < 0.02:
                env = t / 0.02
            else:
                env = max(0.0, (1.0 - (t / duration)) ** 2.4)

            # Squeal: fast pitch-modulated carrier that shifts downward
            base_freq = 1200 + 800 * (1 - t / duration)
            vibrato = 1.0 + 0.006 * math.sin(2 * math.pi * 14 * t)
            squeal = math.sin(2 * math.pi * base_freq * vibrato * t)

            # Guttural growl - low band-limited noise modulated by slow oscillator
            growl = (random.uniform(-1, 1) * (1.0 - t / duration) * 0.8) * math.sin(2 * math.pi * 90 * t)

            # Little yelps: short random high-frequency bursts at early times
            yelp = 0.0
            if t < 0.4 and random.random() < 0.003:
                freq = 1600 + random.uniform(-300, 300)
                yelp = 0.9 * math.sin(2 * math.pi * freq * t) * math.exp(-20 * (t % 0.04))

            sample = (0.75 * squeal + 0.6 * growl + 0.6 * yelp) * env
            val = int(max(-32767, min(32767, sample * 16000)))
            wf.writeframes(struct.pack('<h', val))

    print('Wrote', path)


def synth_skeleton(path):
    """Skeleton death: rattle/clacks followed by heavy bone-thud."""
    duration = 0.85
    nframes = int(framerate * duration)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        for i in range(nframes):
            t = i / framerate
            # Rattle: bandpassed noise bursts that decay
            rattle = 0.0
            if t < 0.5:
                gate = math.exp(-6 * t)
                # many tiny clicking components
                for k in range(4):
                    rattle += (random.uniform(-1, 1) * 0.15) * gate

            # multiple clacks: short decaying sinusoids
            clacks = 0.0
            if t < 0.35:
                for f_c, decay in ((1200, 30), (1800, 18), (2600, 22)):
                    clacks += 0.12 * math.sin(2 * math.pi * f_c * t) * math.exp(-decay * t)

            # Bone-thud: delayed low, damped sine (starts a bit after impact)
            thud = 0.0
            if t > 0.14:
                td = t - 0.14
                thud += 1.2 * math.sin(2 * math.pi * 90 * td) * math.exp(-3.0 * td)

            sample = (0.95 * rattle + 0.9 * clacks + 1.0 * thud) * 0.9
            val = int(max(-32767, min(32767, sample * 15000)))
            wf.writeframes(struct.pack('<h', val))

    print('Wrote', path)


if __name__ == '__main__':
    synth_goblin('sounds/goblin_death.wav')
    synth_skeleton('sounds/skeleton_death.wav')
