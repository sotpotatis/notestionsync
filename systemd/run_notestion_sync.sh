#!/bin/bash
#run_notestion_sync.sh
#Runs the Google Drive to Notion syncing script.
SCRIPT_LOCATION_DIR="$HOME/Documents/notestionsync"
echo "Moving into directory..."
cd $SCRIPT_LOCATION_DIR || exit 1
echo "Running script..."
python main.py