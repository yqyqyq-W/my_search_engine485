#!/bin/bash

# Stop on errors
set -Eeuo pipefail

# Sanity check command line options
usage() {
  echo "Usage: $0 (create|destroy|reset)"
}

if [ $# -ne 1 ]; then
  usage
  exit 1
fi

# Parse argument.  $1 is the first argument
case $1 in
  "create")
    mkdir -p var/
	sqlite3 var/wikipedia.sqlite3 < sql/wikipedia.sql
    ;;

  "destroy")
    rm -rf var/wikipedia.sqlite3 var
    ;;

  "reset")
    rm -rf var/wikipedia.sqlite3 var
    mkdir -p var/
	sqlite3 var/wikipedia.sqlite3 < sql/wikipedia.sql
    ;;

esac