#!/bin/sh
set -eux

source ./config
trap 'trap - SIGTERM && kill 0' SIGINT SIGTERM EXIT
# launch apache
apache/bin/httpd -DFOREGROUND -e info &

# launch the redirector
python3 -m pyflashpoint.redirector &

# launch the UI server
BASE=$(cd $(dirname "$0") && pwd)
export WINEPREFIX="${BASE}/wine"
export FLASHPOINT
export FLASHPOINT_MODE
export FLASK_APP="pyflashpoint.uiserver"
python3 -m flask run 

# it's faster in the future to use gunicorn instead
# but that needs gunicorn and python-eventlet
# gunicorn -k eventlet -b 127.0.0.1:500 pyflashpoint.uiserver:app
