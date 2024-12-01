#!/bin/bash

trap ctrl_c INT

function ctrl_c() {
    echo "Exiting..."
    kill $server_pid
    wait $server_pid
    exit 0
}

if [[ $1 == "--test" ]]; then
    while true; do
        echo "Starting Hypercorn server in test environment..."
        python main.py --bind 0.0.0.0:8000 --log-level debug --reload --access-log - &
        server_pid=$!
        wait $server_pid

        echo "Hypercorn server crashed in test environment. Restarting in 3 seconds..."
        sleep 3
    done
else
    # Print the value of the WORKERS environment variable
    echo "WORKERS: ${WORKERS:-1}"
    python main.py --workers ${WORKERS:-1} --bind 0.0.0.0:8000 &
    server_pid=$!
    wait $server_pid
fi
