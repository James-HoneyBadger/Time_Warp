"""
Advanced Audio System
Enhanced audio engine with 3D spatial audio, effects, and multi-format support.
"""

import math
import os
from datetime import datetime

# Optional pygame import for audio functionality
PYGAME_AVAILABLE = False
pygame = None
try:
    import pygame

    PYGAME_AVAILABLE = True
except ImportError:
    # pygame not available - will use simulation mode
    pass


class AudioClip:
    """Represents an audio file with metadata and playback properties"""

    def __init__(self, name, file_path, loop=False, volume=1.0):
        self.name = name
        self.file_path = file_path
        self.loop = loop
        self.volume = max(0.0, min(1.0, volume))
        self.duration = 0.0
        self.channels = 1
        self.sample_rate = 44100
        self.is_loaded = False
        self.effects = []

    def add_effect(self, effect_type, **params):
        """Add audio effect to the clip"""
        self.effects.append({"type": effect_type, "params": params})

    def remove_effect(self, effect_type):
        """Remove audio effect from the clip"""
        self.effects = [e for e in self.effects if e["type"] != effect_type]

    def get_info(self):
        """Get audio clip information"""
        return {
            "name": self.name,
            "file_path": self.file_path,
            "loop": self.loop,
            "volume": self.volume,
            "duration": self.duration,
            "channels": self.channels,
            "sample_rate": self.sample_rate,
            "effects": len(self.effects),
            "is_loaded": self.is_loaded,
        }


class SpatialAudio:
    """3D spatial audio positioning system"""

    def __init__(self):
        # Import Vector2D locally to avoid circular imports
        try:
            from games.engine import Vector2D

            self.listener_position = Vector2D(0, 0)
        except ImportError:
            # Simple fallback position class
            class Position:
                def __init__(self, x, y):
                    self.x, self.y = x, y

            self.listener_position = Position(0, 0)

        self.listener_orientation = 0.0  # degrees
        self.max_distance = 1000.0
        self.rolloff_factor = 1.0

    def set_listener_position(self, x, y, orientation=0):
        """Set the audio listener's position and orientation"""
        try:
            from games.engine import Vector2D

            self.listener_position = Vector2D(x, y)
        except ImportError:

            class Position:
                def __init__(self, x, y):
                    self.x, self.y = x, y

            self.listener_position = Position(x, y)

        self.listener_orientation = orientation

    def calculate_volume_and_pan(self, source_position, base_volume=1.0):
        """Calculate volume and stereo pan based on spatial positioning"""
        # Calculate distance
        dx = source_position.x - self.listener_position.x
        dy = source_position.y - self.listener_position.y
        distance = math.sqrt(dx * dx + dy * dy)

        # Distance attenuation
        if distance > self.max_distance:
            volume = 0.0
        else:
            volume = base_volume * (
                1.0 - (distance / self.max_distance) ** self.rolloff_factor
            )

        # Stereo panning based on relative position
        if distance > 0:
            angle = math.atan2(dy, dx) - math.radians(self.listener_orientation)
            pan = math.sin(angle) * 0.5  # -0.5 (left) to 0.5 (right)
        else:
            pan = 0.0

        return max(0.0, min(1.0, volume)), max(-1.0, min(1.0, pan))


class AudioEngine:
    """Advanced audio engine with 3D spatial audio, effects, and multi-format support"""

    def __init__(self):
        self.clips = {}  # name -> AudioClip
        self.playing_sounds = {}  # instance_id -> playback info
        self.background_music = None
        self.master_volume = 1.0
        self.sound_volume = 1.0
        self.music_volume = 1.0
        self.spatial_audio = SpatialAudio()
        self.sound_library = {}  # Built-in sound effects
        self.instance_counter = 0

        # Audio format support
        self.supported_formats = [".wav", ".ogg", ".mp3", ".m4a", ".flac"]

        # Initialize pygame mixer if available
        self.mixer_available = False
        if PYGAME_AVAILABLE and pygame:
            try:
                pygame.mixer.pre_init(
                    frequency=44100, size=-16, channels=2, buffer=1024
                )
                pygame.mixer.init()
                self.mixer_available = True
                self.pygame = pygame
                print("🔊 Audio: Pygame mixer initialized")
            except Exception as e:
                print(f"🔊 Audio: Mixer initialization failed: {e}")
        else:
            print("🔊 Audio: Pygame not available - audio simulation mode")

    def load_clip(self, name, file_path, loop=False, volume=1.0):
        """Load an audio clip"""
        if not os.path.exists(file_path):
            print(f"🔊 Audio: File not found: {file_path}")
            return False

        clip = AudioClip(name, file_path, loop, volume)

        # Try to load actual audio file info if pygame is available
        if self.mixer_available:
            try:
                sound = self.pygame.mixer.Sound(file_path)
                clip.is_loaded = True
                print(f"🔊 Audio: Loaded '{name}' from {file_path}")
            except Exception as e:
                print(f"🔊 Audio: Failed to load {file_path}: {e}")
                return False
        else:
            # Simulation mode
            clip.is_loaded = True
            print(f"🔊 Audio: [SIM] Loaded '{name}' from {file_path}")

        self.clips[name] = clip
        return True

    def play_clip(self, name, position=None, volume=None):
        """Play an audio clip"""
        if name not in self.clips:
            print(f"🔊 Audio: Clip '{name}' not found")
            return None

        clip = self.clips[name]
        play_volume = volume if volume is not None else clip.volume

        # Apply spatial audio if position is provided
        if position:
            spatial_volume, pan = self.spatial_audio.calculate_volume_and_pan(
                position, play_volume
            )
            play_volume = spatial_volume

        # Apply volume settings
        final_volume = play_volume * self.sound_volume * self.master_volume

        if self.mixer_available and clip.is_loaded:
            try:
                sound = self.pygame.mixer.Sound(clip.file_path)
                sound.set_volume(final_volume)

                if clip.loop:
                    channel = sound.play(-1)  # Loop infinitely
                else:
                    channel = sound.play()

                if channel:
                    self.instance_counter += 1
                    instance_id = self.instance_counter
                    self.playing_sounds[instance_id] = {
                        "clip": clip,
                        "channel": channel,
                        "position": position,
                        "start_time": datetime.now(),
                    }
                    return instance_id

            except Exception as e:
                print(f"🔊 Audio: Playback failed: {e}")
        else:
            # Simulation mode
            self.instance_counter += 1
            instance_id = self.instance_counter
            self.playing_sounds[instance_id] = {
                "clip": clip,
                "channel": None,
                "position": position,
                "start_time": datetime.now(),
            }
            print(f"🔊 Audio: [SIM] Playing '{name}' at volume {final_volume:.2f}")
            return instance_id

        return None

    def stop_clip(self, instance_id):
        """Stop a playing audio clip instance"""
        if instance_id in self.playing_sounds:
            playback_info = self.playing_sounds[instance_id]

            if self.mixer_available and playback_info["channel"]:
                try:
                    playback_info["channel"].stop()
                except Exception:
                    pass

            del self.playing_sounds[instance_id]
            print(f"🔊 Audio: Stopped audio instance {instance_id}")
            return True

        return False

    def stop_all_clips(self):
        """Stop all playing audio clips"""
        for instance_id in list(self.playing_sounds.keys()):
            self.stop_clip(instance_id)

        if self.mixer_available:
            try:
                self.pygame.mixer.stop()
            except Exception:
                pass

        print("🔊 Audio: All clips stopped")

    def play_music(self, file_path, loop=True, volume=None):
        """Play background music"""
        music_volume = volume if volume is not None else 1.0
        final_volume = music_volume * self.music_volume * self.master_volume

        if self.mixer_available:
            try:
                self.pygame.mixer.music.load(file_path)
                self.pygame.mixer.music.set_volume(final_volume)

                if loop:
                    self.pygame.mixer.music.play(-1)  # Loop infinitely
                else:
                    self.pygame.mixer.music.play()

                self.background_music = {
                    "file_path": file_path,
                    "loop": loop,
                    "volume": music_volume,
                }
                print(f"🔊 Audio: Playing music: {os.path.basename(file_path)}")
                return True

            except Exception as e:
                print(f"🔊 Audio: Music playback failed: {e}")
        else:
            # Simulation mode
            self.background_music = {
                "file_path": file_path,
                "loop": loop,
                "volume": music_volume,
            }
            print(f"🔊 Audio: [SIM] Playing music: {os.path.basename(file_path)}")
            return True

        return False

    def stop_music(self):
        """Stop background music"""
        if self.mixer_available:
            try:
                self.pygame.mixer.music.stop()
            except Exception:
                pass

        self.background_music = None
        print("🔊 Audio: Music stopped")

    def set_master_volume(self, volume):
        """Set master volume (0.0 to 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        self.update_all_volumes()

    def set_sound_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sound_volume = max(0.0, min(1.0, volume))

    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.mixer_available and self.background_music:
            try:
                final_volume = self.music_volume * self.master_volume
                self.pygame.mixer.music.set_volume(final_volume)
            except Exception:
                pass

    def update_all_volumes(self):
        """Update volumes for all currently playing sounds"""
        # Update music volume
        if self.mixer_available and self.background_music:
            try:
                final_volume = self.music_volume * self.master_volume
                self.pygame.mixer.music.set_volume(final_volume)
            except Exception:
                pass

    def get_audio_info(self):
        """Get current audio system information"""
        return {
            "mixer_available": self.mixer_available,
            "clips_loaded": len(self.clips),
            "sounds_playing": len(self.playing_sounds),
            "background_music": self.background_music is not None,
            "master_volume": self.master_volume,
            "sound_volume": self.sound_volume,
            "music_volume": self.music_volume,
            "supported_formats": self.supported_formats,
        }

    def create_sound_library(self):
        """Create built-in procedural sound effects"""
        # This would generate simple sound effects programmatically
        # For now, just create placeholders
        self.sound_library = {
            "beep": {"frequency": 440, "duration": 0.1},
            "click": {"frequency": 800, "duration": 0.05},
            "error": {"frequency": 200, "duration": 0.3},
            "success": {"frequency": 600, "duration": 0.2},
        }
        print("🔊 Audio: Built-in sound library created")

    def play_builtin_sound(self, sound_name):
        """Play a built-in procedural sound"""
        if sound_name in self.sound_library:
            sound_params = self.sound_library[sound_name]
            # In a real implementation, this would generate the sound
            print(f"🔊 Audio: [SIM] Playing built-in sound '{sound_name}'")
            return True
        return False
