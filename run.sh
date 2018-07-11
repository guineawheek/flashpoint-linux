#!/bin/sh
set -eux

source ./config
trap 'trap - SIGTERM && kill 0' SIGINT SIGTERM EXIT
# launch apache
apache/bin/httpd -DFOREGROUND -e info &

cd pyflashpoint
# launch the redirector
python3 -m pyflashpoint.redirector &

# launch the UI server
export FLASHPOINT
export FLASHPOINT_MODE
export FLASK_APP="pyflashpoint.flask"
python3 -m flask run 
