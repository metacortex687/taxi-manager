#!/usr/bin/env bash

echo "Starting Vite watcher..."
cd /home/taxi-manager/taxi_manager/react_frontend || exit 1
npm run dev -- --host 0.0.0.0
