#!/bin/bash

# Stop on errors
set -Eeuo pipefail

# Sanity check command line options
usage() {
  echo "Usage: $0 (start|stop|restart)"
}

if [ $# -ne 1 ]; then
  usage
  exit 1
fi

# Parse argument.  $1 is the first argument
case $1 in
  "start")
  export FLASK_DEBUG=True
  export FLASK_APP=search
  export SEARCH_SETTINGS=config.py
  flask run --host 0.0.0.0 --port 8000
    ;;

  "stop")
    pkill -f 'flask run --host 0.0.0.0 --port 8000'
    ;;

  "restart")
    pkill -f 'flask run --host 0.0.0.0 --port 8000'
  export FLASK_DEBUG=True
  export FLASK_APP=search
  export SEARCH_SETTINGS=config.py
  flask run --host 0.0.0.0 --port 8000
    ;;

esac