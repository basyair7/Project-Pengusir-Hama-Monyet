# MicroBox - Pengusir Hama Monyet

## Version Program
- 1.0.0 - Alpha release

## Equipment specifications
- Raspi 3B/3B+ or Mini PC (Arduino Needed)
- PIR Sensor
- Speaker/TOA
- Amplifier

## How to run it
1. **Update your package list (if using RPi)**: Run the following command to update your package list:
```sh
sudo apt update
```
3. **Install CODEX FFMPEG**:
- if running on windows:
```
1. Download on https://www.gyan.dev/ffmpeg/builds/
2. add path to Environment variables
```
- if running on RPi:
```
sudo apt-get install ffmpeg -y
```
3. **Install library python**:
- if running on RPi:
```sh
python3 -m pip install -r lib_rpi
```
- if running on PC:
```sh
python -m pip install -r lib_pc
```
4. **Running program**:
```sh
python main.py
```