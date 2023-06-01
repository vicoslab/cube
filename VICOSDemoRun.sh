#!/usr/bin/env bash

DEMO_GUI_FOLDER=/home/vicosdemo/vicos_demo_gui-main
DEMO_GUI_VIRTENV=/home/vicosdemo/demo

# activate python virtenv
source $DEMO_GUI_VIRTENV/bin/activate

# start DEMO using ignition
python -m ignition $DEMO_GUI_FOLDER/launch_demo.yaml

# Clean up: stop and then remove any unclosed containers
echo ""
echo "Cleaning up any remaining containers"
docker stop $(docker ps -q) &> /dev/null
docker rm $(docker ps -a -q) &> /dev/null
echo "done"
