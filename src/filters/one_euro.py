import math

class OneEuroFilter:
    """
    One Euro Filter with derivative smoothing for ultra-smooth cursor control.
    """
    
    def __init__(self, freq=60, min_cutoff=1.0, beta=0.007, d_cutoff=1.0):
        """
        Args:
            freq: Expected update frequency (Hz)
            min_cutoff: Minimum cutoff frequency for position (lower = smoother but more lag)
            beta: Speed coefficient (how much to increase cutoff with velocity)
            d_cutoff: Cutoff frequency for derivative (velocity smoothing)
        """
        self.freq = freq
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        
        self.prev_x = None
        self.prev_dx = 0.0
        self.prev_time = None
    
    def alpha(self, cutoff):
        """Calculate smoothing factor from cutoff frequency."""
        tau = 1.0 / (2 * math.pi * cutoff)
        te = 1.0 / self.freq
        return 1.0 / (1.0 + tau / te)
    
    def filter(self, x, timestamp=None):
        """
        Filter a new value.
        
        Args:
            x: Raw input value
            timestamp: Optional timestamp (for variable frame rate)
        
        Returns:
            Filtered value
        """

        if self.prev_x is None:
            self.prev_x = x
            self.prev_time = timestamp
            return x
        
        # Calculate time delta (for variable frame rates)
        if timestamp is not None and self.prev_time is not None:
            te = timestamp - self.prev_time
            if te > 0:
                self.freq = 1.0 / te
            self.prev_time = timestamp
        
        # --- Step 1: Smooth the derivative (velocity) ---
        dx = (x - self.prev_x) * self.freq  # velocity
        
        # Apply low-pass filter to derivative
        a_d = self.alpha(self.d_cutoff)
        dx_smooth = a_d * dx + (1 - a_d) * self.prev_dx
        
        # --- Step 2: Adaptive cutoff based on smoothed velocity ---
        cutoff = self.min_cutoff + self.beta * abs(dx_smooth)
        
        # --- Step 3: Smooth the position ---
        a = self.alpha(cutoff)
        result = a * x + (1 - a) * self.prev_x
        
        # Update state
        self.prev_x = result
        self.prev_dx = dx_smooth
        
        return result
    
    def reset(self):
        """Reset filter state."""
        self.prev_x = None
        self.prev_dx = 0.0
        self.prev_time = None