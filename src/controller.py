import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import time
import os

from gestures import GestureDetector
from filters import OneEuroFilter
from config import (
    CameraConfig,
    FilterConfig,
    MovementConfig,
    GestureConfig,
    HandTrackingConfig,
    PathConfig,
    DisplayConfig
)


class Controller:
    """
    Core controller that reads webcam frames, tracks hands,
    and controls the mouse based on gestures, stabilized.
    
    Optimized for ultra-smooth cursor movement.
    """

    def __init__(self, model_path=None, max_hands=None):
        """
        Initialize the desk controller.
        
        Args:
            model_path: Path to MediaPipe model (uses PathConfig.MODEL_PATH if None)
            max_hands: Max hands to track (uses HandTrackingConfig.MAX_HANDS if None)
        """

        model_path = model_path or PathConfig.MODEL_PATH
        max_hands = max_hands or HandTrackingConfig.MAX_HANDS
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}\n"
                "Please download hand_landmarker.task from:\n"
                "https://developers.google.com/mediapipe/solutions/vision/hand_landmarker"
            )
        
        self.screen_width, self.screen_height = pyautogui.size()

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=HandTrackingConfig.MIN_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=HandTrackingConfig.MIN_PRESENCE_CONFIDENCE,
            min_tracking_confidence=HandTrackingConfig.MIN_TRACKING_CONFIDENCE,
        )

        self.hand_landmarker = vision.HandLandmarker.create_from_options(options)

        self.cap = cv2.VideoCapture(CameraConfig.WEBCAM_INDEX)
        if not self.cap.isOpened():
            raise RuntimeError(
                f"Failed to open webcam at index {CameraConfig.WEBCAM_INDEX}\n"
                "Try changing CameraConfig.WEBCAM_INDEX in config.py (usually 0 or 1)"
            )
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CameraConfig.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CameraConfig.FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, CameraConfig.TARGET_FPS)

        self.frame_width = int(self.cap.get(3))
        self.frame_height = int(self.cap.get(4))

        self.gesture_detector = GestureDetector(
            pinch_threshold=GestureConfig.PINCH_THRESHOLD,
            click_time_threshold=GestureConfig.CLICK_TIME_THRESHOLD,
            drag_distance_threshold=GestureConfig.DRAG_DISTANCE_THRESHOLD
        )

        self.cursor_x = self.screen_width // 2
        self.cursor_y = self.screen_height // 2

        self.prev_fx = None
        self.prev_fy = None

        self.filter_x = OneEuroFilter(
            freq=FilterConfig.FREQ,
            min_cutoff=FilterConfig.MIN_CUTOFF,
            beta=FilterConfig.BETA,
            d_cutoff=FilterConfig.D_CUTOFF
        )
        self.filter_y = OneEuroFilter(
            freq=FilterConfig.FREQ,
            min_cutoff=FilterConfig.MIN_CUTOFF,
            beta=FilterConfig.BETA,
            d_cutoff=FilterConfig.D_CUTOFF
        )

        self.GAIN = MovementConfig.GAIN
        self.DEADZONE = MovementConfig.DEADZONE
        self.MAX_SPEED = MovementConfig.MAX_SPEED
        
        self.velocity_smoothing = MovementConfig.VELOCITY_SMOOTHING
        self.smooth_vx = 0.0
        self.smooth_vy = 0.0
        
        self.last_time = time.time()
        
        print(f"Controller initialized:")
        print(f"  Webcam: Index {CameraConfig.WEBCAM_INDEX}")
        print(f"  Resolution: {self.frame_width}x{self.frame_height}")
        print(f"  Screen: {self.screen_width}x{self.screen_height}")
        print(f"  Filter: min_cutoff={FilterConfig.MIN_CUTOFF}, beta={FilterConfig.BETA}")
        print(f"  Movement: GAIN={MovementConfig.GAIN}, smoothing={MovementConfig.VELOCITY_SMOOTHING}")

    def update_cursor_from_finger(self, raw_x, raw_y):
        """Update cursor position from finger with multi-stage smoothing."""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        # Stage 1: One Euro Filter
        fx = self.filter_x.filter(raw_x, current_time)
        fy = self.filter_y.filter(raw_y, current_time)

        if self.prev_fx is None:
            self.prev_fx = fx
            self.prev_fy = fy
            return self.cursor_x, self.cursor_y

        # Stage 2: Calculate velocity
        dx = fx - self.prev_fx
        dy = fy - self.prev_fy

        # Deadzone
        if abs(dx) < self.DEADZONE and abs(dy) < self.DEADZONE:
            return self.cursor_x, self.cursor_y

        # Convert to screen velocity
        vx = dx * self.GAIN * self.screen_width
        vy = dy * self.GAIN * self.screen_height

        # Stage 3: Velocity smoothing
        self.smooth_vx = self.velocity_smoothing * self.smooth_vx + (1 - self.velocity_smoothing) * vx
        self.smooth_vy = self.velocity_smoothing * self.smooth_vy + (1 - self.velocity_smoothing) * vy

        # Stage 4: Speed limiting
        speed = (self.smooth_vx**2 + self.smooth_vy**2)**0.5
        if speed > self.MAX_SPEED:
            scale = self.MAX_SPEED / speed
            self.smooth_vx *= scale
            self.smooth_vy *= scale

        # Stage 5: Update cursor
        self.cursor_x += self.smooth_vx
        self.cursor_y += self.smooth_vy

        # Clamp to screen - using config margin
        margin = MovementConfig.EDGE_MARGIN
        self.cursor_x = max(margin, min(self.screen_width - margin, self.cursor_x))
        self.cursor_y = max(margin, min(self.screen_height - margin, self.cursor_y))

        self.prev_fx = fx
        self.prev_fy = fy

        return self.cursor_x, self.cursor_y

    def run(self):
        """Main loop with optimized timing"""
        frame_count = 0
        fps_start = time.time()

        while True:
            success, frame = self.cap.read()
            if not success:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            timestamp_ms = int(time.time() * 1000)

            # Detect hands
            result = self.hand_landmarker.detect_for_video(mp_image, timestamp_ms)

            if result.hand_landmarks:
                hand = result.hand_landmarks[0]

                raw_x, raw_y = self.gesture_detector.get_index_position(hand)
                cursor_x, cursor_y = self.update_cursor_from_finger(raw_x, raw_y)

                # Move mouse
                pyautogui.moveTo(int(cursor_x), int(cursor_y), duration=0)

                # Click vs Drag detection
                pinch_state = self.gesture_detector.update_pinch_state(hand, (raw_x, raw_y))

                # Visual feedback - using config settings
                if DisplayConfig.SHOW_GESTURE_TEXT:
                    if pinch_state == "click":
                        cv2.putText(frame, "Click!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        pyautogui.click()
                    elif pinch_state == "drag_start":
                        cv2.putText(frame, "Drag Start", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        pyautogui.mouseDown()
                    elif pinch_state == "dragging":
                        cv2.putText(frame, "Dragging...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 150, 0), 2)
                    elif pinch_state == "drag_end":
                        cv2.putText(frame, "Drag End", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 150, 255), 2)
                        pyautogui.mouseUp()
                else:
                    # Still need to execute actions even if not showing text
                    if pinch_state == "click":
                        pyautogui.click()
                    elif pinch_state == "drag_start":
                        pyautogui.mouseDown()
                    elif pinch_state == "drag_end":
                        pyautogui.mouseUp()

                # Draw landmarks - using config settings
                if DisplayConfig.SHOW_LANDMARKS:
                    for lm in hand:
                        cx, cy = int(lm.x * self.frame_width), int(lm.y * self.frame_height)
                        cv2.circle(
                            frame,
                            (cx, cy),
                            DisplayConfig.LANDMARK_RADIUS,
                            DisplayConfig.LANDMARK_COLOR,
                            -1
                        )

            else:
                self.gesture_detector.reset_pinch()
                pyautogui.mouseUp()
                
                # Reset velocity
                self.smooth_vx = 0.0
                self.smooth_vy = 0.0

            # FPS counter - using config setting
            if DisplayConfig.SHOW_FPS:
                frame_count += 1
                if frame_count % 30 == 0:
                    elapsed = time.time() - fps_start
                    fps = 30 / elapsed if elapsed > 0 else 0
                    fps_start = time.time()
                    cv2.putText(
                        frame,
                        f"FPS: {fps:.1f}",
                        (self.frame_width - 150, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 255),
                        2
                    )

            cv2.imshow(DisplayConfig.WINDOW_NAME, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
        self.hand_landmarker.close()