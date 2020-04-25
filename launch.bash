#!/bin/bash
while true; do
  git fetch --all
  git reset --hard origin/master
  bash update.bash
  pip3 install -r requirements.txt
  python3 server.py
  echo "Restarting in 3 seconds... Abort with Control C."
  sleep 3
done
