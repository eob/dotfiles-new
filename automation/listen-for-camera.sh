#!/usr/bin/env bash

# Exit on error
set -euo pipefail

ELGATO_LIGHT_HOST="${ELGATO_LIGHT_HOST:-192.168.0.199}"

toggle_desk_light() {
    local on=$1
    local url="http://${ELGATO_LIGHT_HOST}:9123/elgato/lights"
    local on_value=0

    if [[ "$on" == "true" ]]; then
        on_value=1
    fi

    local data=$(cat <<EOF
{
    "Lights": [{
        "Temperature": 344,
        "Brightness": 20,
        "On": ${on_value}
    }],
    "NumberOfLights": 1
}
EOF
)

    echo "Toggling desk light: on=$on"
    curl -X PUT "$url" \
        -H "Content-Type: application/json" \
        -d "$data" \
        --silent --show-error
    echo ""
}

main() {
    echo "Starting camera monitor..."
    echo "Watching for camera state changes..."

    log stream --predicate 'subsystem contains "com.apple.UVCExtension" and composedMessage contains "Post PowerLog"' | \
    while IFS= read -r line; do
        if echo "$line" | grep -qE '^\s*"VDCAssistant_Power_State"\s*=\s*(Off|On);\s*$'; then
            if echo "$line" | grep -qE '^\s*"VDCAssistant_Power_State"\s*=\s*On;\s*$'; then
                toggle_desk_light true
            else
                toggle_desk_light false
            fi
        fi
    done
}

main
