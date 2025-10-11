"""
Audio utilities for Time_Warp
Handles sound mixing and playback functionality.
"""

import sys
import subprocess
import os


def _has_exe(name):
    """Check if an executable is available in PATH"""
    try:
        subprocess.run(
            [name, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True
    except (FileNotFoundError, subprocess.SubprocessError):
        return False


class Mixer:
    """Simple audio mixer for sound effects and music playback"""

    def __init__(self):
        self.registry = {}  # name -> path
        self.has_play = _has_exe("play")
        self.has_aplay = _has_exe("aplay")

    def snd(self, name, path, vol=0.8):
        """Register a sound file with a name"""
        self.registry[name] = path

    def play_snd(self, name):
        """Play a registered sound by name"""
        path = self.registry.get(name)
        if not path:
            return

        if self.has_play:
            subprocess.run(["play", "-q", path], shell=False)
        elif self.has_aplay and path.lower().endswith(".wav"):
            subprocess.run(["aplay", "-q", path], shell=False)
        else:
            # Fallback to system bell
            sys.stdout.write("\a")
            sys.stdout.flush()
