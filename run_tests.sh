#!/bin/bash

# Start HTTP server to serve assets
python3 -m http.server 8000 --bind 127.0.0.1 > /dev/null 2>&1 &
HTTP_SERVER_PID=$!

# Run tests
nosetests --with-coverage --cover-package=rml

# Clean up
kill -9 $HTTP_SERVER_PID
