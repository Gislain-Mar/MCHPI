import time


class GestureDetector:
    """
    Detects gestures from hand landmarks.
    Currently supports:
    - Quick pinch → click
    - Pinch + hold → drag
    - Index finger position → cursor movement
    """

    # Landmarks
    THUMB_TIP = 4
    INDEX_TIP = 8
    MIDDLE_TIP = 12

    def __init__(self, pinch_threshold=0.05, click_time_threshold=0.2, drag_distance_threshold=0.01):
        """
        Args:
            pinch_threshold: Distance threshold for pinch detection
            click_time_threshold: Max time (seconds) for a pinch to be considered a click
            drag_distance_threshold: Min movement (normalized) to be considered a drag
        """
        self.pinch_threshold = pinch_threshold
        self.click_time_threshold = click_time_threshold
        self.drag_distance_threshold = drag_distance_threshold
        
        self.pinch_active = False
        self.pinch_start_time = None
        self.pinch_start_pos = None 
        self.is_dragging = False
        
    def detect_pinch(self, hand_landmarks):
        """Return True if thumb and middle finger are pinched (raw, single-frame)"""
        thumb_tip = hand_landmarks[self.THUMB_TIP]
        middle_tip = hand_landmarks[self.MIDDLE_TIP]
        distance = ((thumb_tip.x - middle_tip.x) ** 2 + (thumb_tip.y - middle_tip.y) ** 2) ** 0.5
        return distance < self.pinch_threshold

    def update_pinch_state(self, hand_landmarks, current_finger_pos):
        """
        Call once per frame. Returns a state string:
            "click"   - quick pinch and release (like a mouse click)
            "drag_start" - pinch held long enough or moved far enough to start dragging
            "dragging" - currently dragging
            "drag_end" - drag ended (release after dragging)
            None      - no pinch activity
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            current_finger_pos: (x, y) tuple of current finger position (normalized)
        """
        currently_pinched = self.detect_pinch(hand_landmarks)
        current_time = time.time()
        
        # --- Pinch just started ---
        if currently_pinched and not self.pinch_active:
            self.pinch_active = True
            self.pinch_start_time = current_time
            self.pinch_start_pos = current_finger_pos
            self.is_dragging = False
            return None  # Don't trigger anything yet, wait to see if it's click or drag
        
        # --- Pinch is ongoing ---
        elif currently_pinched and self.pinch_active:
            pinch_duration = current_time - self.pinch_start_time
            
            # Calculate distance moved since pinch started
            if self.pinch_start_pos:
                dx = current_finger_pos[0] - self.pinch_start_pos[0]
                dy = current_finger_pos[1] - self.pinch_start_pos[1]
                distance_moved = (dx**2 + dy**2)**0.5
            else:
                distance_moved = 0
            
            # Determine if this should be a drag
            should_drag = (
                pinch_duration > self.click_time_threshold or 
                distance_moved > self.drag_distance_threshold
            )
            
            if should_drag and not self.is_dragging:
                # Transition to dragging
                self.is_dragging = True
                return "drag_start"
            elif self.is_dragging:
                return "dragging"
            else:
                # Still in the "maybe click, maybe drag" phase
                return None
        
        # --- Pinch just released ---
        elif not currently_pinched and self.pinch_active:
            was_dragging = self.is_dragging
            
            # Reset state
            self.pinch_active = False
            self.pinch_start_time = None
            self.pinch_start_pos = None
            self.is_dragging = False
            
            # Determine what kind of release this was
            if was_dragging:
                return "drag_end"
            else:
                # It was a quick pinch - treat as click
                return "click"
        
        return None

    def reset_pinch(self):
        """Call this when the hand disappears so we don't get stuck in 'hold'."""
        self.pinch_active = False
        self.pinch_start_time = None
        self.pinch_start_pos = None
        self.is_dragging = False

    def get_index_position(self, hand_landmarks):
        """Return the normalized x,y of the index finger tip"""
        index_tip = hand_landmarks[self.INDEX_TIP]
        return index_tip.x, index_tip.y