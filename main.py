#!/usr/bin/env python3
"""Deliver entry.png for "The World Today", edition news-image-20261122.

The finished image lives next to this file in the repository. All this
program does is copy it into the directory named by the MAKEFUN_OUTPUT_DIR
environment variable, or back into its own folder when that variable is
unset. It uses only the Python standard library so it can run in a bare
python:3.13-slim container.
"""

import os
import shutil
import sys

FILE_NAME = "entry.png"


def image_source():
    # The grader may point MAKEFUN_BOT_DIR at the folder holding the
    # repository files; prefer it when set, else use this file's folder.
    folder = os.environ.get("MAKEFUN_BOT_DIR")
    if not folder:
        folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(folder, FILE_NAME)


def destination_dir():
    target = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if target:
        return target
    return os.path.dirname(os.path.abspath(__file__))


def main():
    src = image_source()
    out_dir = destination_dir()
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, FILE_NAME)
    if os.path.abspath(src) != os.path.abspath(dst):
        shutil.copyfile(src, dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
