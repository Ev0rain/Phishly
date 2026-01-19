#!/bin/bash
# Open Phishly WebAdmin in default browser

URL="http://localhost:8006"

# Detect the OS and open with appropriate command
if command -v xdg-open &> /dev/null; then
    xdg-open "$URL"
elif command -v open &> /dev/null; then
    open "$URL"
elif command -v start &> /dev/null; then
    start "$URL"
else
    echo "Could not detect browser opener. Please open $URL manually."
fi
