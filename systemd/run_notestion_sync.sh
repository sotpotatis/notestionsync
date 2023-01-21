#!/bin/bash
#run_notestion_sync.sh
#Runs the Google Drive to Notion syncing script.
SCRIPT_LOCATION_DIR="$HOME/notestionsync"
echo "Moving into directory..."
cd $SCRIPT_LOCATION_DIR || exit 1
echo "Running script..."
python3 main.py