#!/usr/bin/python3

import os
import shlex
import sys

SOUNDS_DIR="/var/lib/asterisk/sounds"
SOUND_EXTENSIONS=set(["ulaw", "gsm", "pcm"])
ALWAYS_ESCAPE_PREFIXES=set(["silence", "digits", "letters",
                            "phonetics", "nodenames", "rpt"])


def get_sounds():
    paths=[]
    for dirpath, _dirnames, filenames in os.walk(SOUNDS_DIR):
        for name in filenames:
            path = os.path.join(dirpath, name)
            _, ext = os.path.splitext(path)
            if not ext:
                continue
            if not ext[1:] in SOUND_EXTENSIONS:
                continue
            paths.append(path)
    return paths


def gen_sox_input_args(paths):
    args = []
    for path in paths:
        _, ext = os.path.splitext(path)
        if ext == ".ulaw":
            args.extend(["-t", "raw", "-e", "u-law", "-c", "1", "-r",  "8000"])
        args.append(path)
    return args

def build_sound_dict(argv0):
    paths = get_sounds()
    sounds = dict()
    for path in sorted(paths):
        root, _ = os.path.splitext(path)
        key = os.path.basename(root)
        prefix = os.path.basename(os.path.dirname(path))
        if prefix in ALWAYS_ESCAPE_PREFIXES:
            key = os.path.join(prefix, key)
        if key in sounds:
            print(f"{argv0}: duplicated key {key}: {sounds[key]} vs {path}",
                  file=sys.stderr)
            key = os.path.join(prefix, key)
        sounds[key] = path
    return sounds


def main(argv):
    argv0 = argv[0]
    args = argv[1:]
    if not args:
        print(f"{argv0}: nothing to do", file=sys.stderr)
        return 1

    sounds = build_sound_dict(argv0)
    try:
        paths = []
        for sound in args:
            if len(sound) == 1:
                if sound.isdigit():
                    sound = os.path.join("digits", sound)
                elif sound.isalpha():
                    sound = os.path.join("letters", sound.lower())
                    paths.append(sounds[sound])
            paths.append(sounds[sound])
    except KeyError as e:
        print(f"{argv0}: unrecongized input: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"{argv0}: error: {e}", file=sys.stderr)
        return 1

    sox_input = " ".join(map(shlex.quote, gen_sox_input_args(paths)))
    print(f"sox {sox_input} -t raw -e u-law -r 8000 -c 1 -")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
