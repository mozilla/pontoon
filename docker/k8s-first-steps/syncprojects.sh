#!/bin/bash

# a recommended value for SYNC_INTERVAL is 30 --> 30 minutes

if [ ! -z "$SYNC_INTERVAL" ]; then
    syncInterval=$SYNC_INTERVAL
    echo "syncInterval=$SYNC_INTERVAL"
    echo "SYNC_INTERVAL=$SYNC_INTERVAL for syncing projects" >> /app/run_webApp.log
    if((syncInterval > 5)); then
        echo "doing startup delay of 60 seconds..."
        sleep 60
        echo "running loop"
        while true
        do
           echo "calling sync_projects for user pontoon"
           python /app/manage.py sync_projects > /app/lastSync.log
           # multiply by 60 to have minutes in the env var
           sleep $((syncInterval*60))
        done
    fi
fi
echo "SYNC_INTERVAL is not defined or <5, doing nothing."
echo "SYNC_INTERVAL is not defined or <5, doing nothing." >> /app/run_webApp.log
