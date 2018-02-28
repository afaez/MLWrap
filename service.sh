#!/bin/bash

echo 'Checking dependencies...'
{
  pip install flask
  pip install flask-api
  pip install jsonpickle
  pip install numpy
  pip install scipy
  pip install gunicorn
} &> /dev/null # Hides output

echo 'Checking python version...'
# Need to check if version is above 3.6:
# Run python one-liner that returns 0 if the python version is supported
python -c 'import sys; import platform; version = platform.python_version(); sys.exit((0 if (int(version[0]) >= 3 and int(version[2])>=6) else 1))'
if [ $? -ne 0  ]; then # if the return code is not equal 0, exit.
  echo "ERROR: Only python version 3.6 and above are supported."
  exit 1
fi

echo 'Creating system envirement variable...'

# Create system envirement:
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export MLWRAP_PATH="$DIR"

echo 'Running service... '
if [ "$1" = "" ]; then # No port was specified.
  set -- "5000"
fi
# Run service using gunicorn:
cd "src"
gunicorn --bind 0.0.0.0:$1 server --log-level info