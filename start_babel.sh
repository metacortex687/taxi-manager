#!/usr/bin/env bash

echo "Starting Babel watcher..."
cd /home/taxi-manager/taxi_manager/react_frontend || exit 1
nohup npx babel react_src --out-dir static/react_frontend/js --extensions .js,.jsx --watch --copy-files > babel.log 2>&1 &
echo "Done"