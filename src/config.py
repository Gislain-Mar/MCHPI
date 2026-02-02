"""
Configuration file for Hand Gesture Mouse Controller.
"""


class CameraConfig:
    """Webcam and video capture settings."""
    
    WEBCAM_INDEX = 1
    FRAME_WIDTH = 1280
    FRAME_HEIGHT = 720
    TARGET_FPS = 60


class FilterConfig:
    """One Euro Filter smoothing parameters.
    
    See docs/ONE_EURO_FILTER_CHEATSHEET.md for detailed explanations.
    """
    
    FREQ = 60  # Expected frame rate (Hz)
    
    # Smoothing strength when hand is still
    # Lower = smoother but more lag, Higher = more responsive
    MIN_CUTOFF = 1.0
    
    # How much filter adapts to velocity
    # Keep this LOW (0.005-0.02) for stability
    BETA = 0.01
    
    # Derivative (velocity) smoothing
    # Usually keep at 1.0
    D_CUTOFF = 1.0


class MovementConfig:
    """Cursor movement and sensitivity parameters."""
    
    # Movement amplification (how fast cursor moves)
    # Lower = slower/smoother, Higher = faster/jerkier
    GAIN = 3.0
    
    # Ignore movements smaller than this (normalized coordinates)
    # Prevents micro-jitter when hand is still
    DEADZONE = 0.0015
    
    # Maximum cursor speed (pixels per frame)
    # Prevents sudden jumps from tracking glitches
    MAX_SPEED = 35
    
    # Velocity smoothing coefficient (0.0-1.0)
    # Higher = smoother but more inertia
    VELOCITY_SMOOTHING = 0.5
    
    # Screen edge margin (pixels)
    # Prevents cursor from getting stuck at edges
    EDGE_MARGIN = 5


class GestureConfig:
    """Gesture detection thresholds."""
    
    # Distance threshold for pinch detection (normalized)
    # Lower = easier to trigger, Higher = requires tighter pinch
    PINCH_THRESHOLD = 0.05
    
    # Maximum time for a pinch to be considered a click (seconds)
    # Longer pinches become drags
    CLICK_TIME_THRESHOLD = 0.2
    
    # Minimum movement to trigger drag instead of click (normalized)
    # Prevents accidental drags from hand shake
    DRAG_DISTANCE_THRESHOLD = 0.01


class HandTrackingConfig:
    """MediaPipe hand tracking confidence thresholds.
    
    Higher values = more stable but may lose tracking more easily.
    Lower values = tracks better but more false positives.
    """
    
    # Confidence for initial hand detection
    MIN_DETECTION_CONFIDENCE = 0.7
    
    # Confidence that hand is present in frame
    MIN_PRESENCE_CONFIDENCE = 0.7
    
    # Confidence for tracking hand between frames
    MIN_TRACKING_CONFIDENCE = 0.7
    
    # Maximum number of hands to track (1 recommended)
    MAX_HANDS = 1


class PathConfig:
    """File paths for models and resources."""
    
    # Path to MediaPipe hand landmark model
    MODEL_PATH = "models/hand_landmarker.task"


class DisplayConfig:
    """UI and visualization settings."""
    
    # Window name for video feed
    WINDOW_NAME = "MediaPipe Hand-Computer Interface"
    
    # Show hand landmarks on video feed
    SHOW_LANDMARKS = True
    
    # Show gesture state text
    SHOW_GESTURE_TEXT = True
    
    # Show FPS counter (for debugging)
    SHOW_FPS = False
    
    # Landmark circle size
    LANDMARK_RADIUS = 5
    
    LANDMARK_COLOR = (0, 255, 0)


# Preset configurations for different use cases
class Presets:
    """Pre-configured parameter sets for different scenarios."""
    
    @staticmethod
    def ultra_smooth():
        """Maximum smoothness, slight lag acceptable."""
        FilterConfig.MIN_CUTOFF = 0.5
        FilterConfig.BETA = 0.005
        MovementConfig.GAIN = 3.0
        MovementConfig.VELOCITY_SMOOTHING = 0.6
    
    @staticmethod
    def balanced():
        """Balanced smoothness and responsiveness (default)."""
        FilterConfig.MIN_CUTOFF = 1.0
        FilterConfig.BETA = 0.01
        MovementConfig.GAIN = 3.0
        MovementConfig.VELOCITY_SMOOTHING = 0.5
    
    @staticmethod
    def responsive():
        """Prioritize speed, accept slight jitter."""
        FilterConfig.MIN_CUTOFF = 1.5
        FilterConfig.BETA = 0.02
        MovementConfig.GAIN = 4.0
        MovementConfig.VELOCITY_SMOOTHING = 0.3