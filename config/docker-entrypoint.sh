#!/bin/bash

echo "Checking display connectivity..."
if ! timeout 2 xdpyinfo >/dev/null 2>&1; then
    echo "WARNING: Cannot connect to X display. Using virtual framebuffer."
    Xvfb :1 -screen 0 1280x720x24 -ac &
    export DISPLAY=:1
fi

# Convert Windows paths if needed (for models or other paths passed as arguments)
args=()
for arg in "$@"; do
    # If arg contains a Windows path character (C:\ or similar), convert it
    if [[ "$arg" == *":"* && "$arg" != "--"* ]]; then
        # Remove drive letter, replace backslashes, and add /mnt/c style path
        drive=$(echo "$arg" | cut -d: -f1 | tr "[:upper:]" "[:lower:]")
        path=$(echo "$arg" | cut -d: -f2- | tr "\\\\" "/")
        arg="/mnt/$drive$path"
    fi
    args+=("$arg")
done

echo "Display setup complete. Running command: ${args[@]}"
exec "${args[@]}" 