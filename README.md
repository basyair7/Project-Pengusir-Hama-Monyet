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
2. **Install library python**:
- if running on RPi:
```sh
python3 -m pip install -r lib_rpi
```
- if running on PC:
```sh
python -m pip install -r lib_pc
```
3. **Running program**:
```sh
python main.py
```