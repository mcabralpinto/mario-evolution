#!/bin/bash
cd /server
# Wait 5 seconds to ensure the display is fully ready
sleep 3
# Loop through ports 4242 to 4252
for port in {4242..4251}; do
    java ch.idsia.scenarios.MainRun -ag ServerAgent:$port -server on &
    sleep 1
done
wait 
