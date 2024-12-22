#!/bin/bash

# Check if screen is already running
if screen -list | grep -q "turbodl"; then
    echo "Bot is already running in a screen session."
    exit 1
fi

# Change to the script directory
cd "$(dirname "$0")"

# Start a new screen session
screen -dmS turbodl bash -c '
    source venv/bin/activate
    python bot.py
    exec $SHELL
'

echo "Bot started in screen session 'turbodl'"
echo "To attach to the session, use: screen -r turbodl"
