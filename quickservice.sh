
echo 'Running service... '
if [ "$1" = "" ]; then # No port was specified.
  set -- "5000"
fi
# Run service using gunicorn:
cd "src"
gunicorn --bind 0.0.0.0:$1 server --access-logfile ../log.txt --log-level debug