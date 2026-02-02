#!/usr/bin/env python3
"""
Hand Gesture Mouse Controller
Main entry point for the application.
"""

from controller import Controller


def main():
    """Initialize and run the hand gesture controller."""
    print("=" * 50)
    print("Hand Gesture Mouse Controller")
    print("=" * 50)
    print("\nControls:")
    print("  - Move your INDEX FINGER to control cursor")
    print("  - PINCH (thumb + middle) for click/drag:")
    print("    • Quick pinch = Click")
    print("    • Pinch + hold = Drag")
    print("\n" + "=" * 50)
    print("Starting controller...\n")

    # ============================================
    # OPTIONAL: Uncomment ONE preset to use it
    # ============================================
    # Presets.ultra_smooth()  
    # Presets.balanced()     
    # Presets.responsive() 
    
    try:
        controller = Controller()
        controller.run()
    except KeyboardInterrupt:
        print("\n\nController stopped by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        print("Make sure:")
        print("  1. Webcam is connected")
        print("  2. hand_landmarker.task is in models/ directory")
        print("  3. All dependencies are installed (pip install -r requirements.txt)")
        raise


if __name__ == "__main__":
    main()