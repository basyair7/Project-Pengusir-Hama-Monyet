#!/bin/bash
cd /home/pi/Desktop/Project-Pengusir-Hama-Monyet
source ./venv/bin/activate
python main.py 2>&1 | while IFS= read -r line; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') $line"
done >> /home/pi/Desktop/log.txt
