import subprocess
import time
import pygame

BLUETOOTH_MAC = "XX:XX:XX:XX:XX:XX"  # Replace with your device's MAC address
WAV_FILE = "example.wav"  # Path to the audio file

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(result.stderr)
    return result.stdout.strip()

def pair_and_connect(mac):
    print("[*] Starting bluetoothctl...")
    cmds = f"""
    power on
    agent on
    default-agent
    pair {mac}
    trust {mac}
    connect {mac}
    exit
    """
    subprocess.run(['bluetoothctl'], input=cmds.encode())

def set_default_sink():
    print("[*] Setting default audio sink...")
    sinks = run_cmd("pactl list short sinks")
    for line in sinks.splitlines():
        if "bluez" in line:
            sink_name = line.split()[1]
            run_cmd(f"pactl set-default-sink {sink_name}")
            print(f"[+] Set default sink to {sink_name}")
            return True
    print("[!] No Bluetooth sink found.")
    return False

def play_audio(file):
    print(f"[*] Playing audio: {file}")
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def main():
    pair_and_connect(BLUETOOTH_MAC)
    time.sleep(3)  # wait for connection to settle
    if set_default_sink():
        play_audio(WAV_FILE)
    else:
        print("[-] Could not play audio. Bluetooth device not set as default.")

if __name__ == "__main__":
    main()
