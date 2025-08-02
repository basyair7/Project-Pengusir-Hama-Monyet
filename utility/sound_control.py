# utils/sound_control.py

SOUND_FILE = "sound.txt"

def is_sound_enabled():
    """Check if sound is enabled by reading from a file."""
    try:
        with open(SOUND_FILE, 'r') as file:
            return file.read().strip().lower() == "on"
    
    except FileNotFoundError:
        print(f"Warning: {SOUND_FILE} not found. Defaulting to sound enabled.")
        return True  # Default to sound enabled if file does not exist
    
    except Exception as e:
        print(f"Error reading {SOUND_FILE}: {e}")
        return True  # Default to sound enabled on error
    
def set_sound_enabled(enabled: bool):
    with open(SOUND_FILE, 'w') as file:
        file.write("on" if enabled else "off")