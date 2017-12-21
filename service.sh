#!/bin/bash
echo 'Installing dependencies:'
pip install flask
pip install jsonpickle
pip install sklearn
pip install numpy
pip install scipy

# Need to check if version is above 3.6:
# Run python one-liner that returns 0 if the python version is supported
python -c 'import sys; import platform; version = platform.python_version(); sys.exit((0 if (int(version[0]) >= 3 and int(version[2])>=6) else 1))'

if [ $? -ne 0  ]; then # if the return code is not equal 0, exit.
  echo "ERROR: Only python version 3.6 and above are supported."
  exit 1
fi

# Create system envirement:
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export MLWRAP_PATH="$DIR"
echo $MLWRAP_PATH

# Run service:
python src/server.py