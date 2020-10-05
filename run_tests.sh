#!/bin/bash
set -e
PORT=8000
HOST=127.0.0.1

###############################################################################
#                                                                             #
#                     UNIT, INTEGRATION & COVERAGE TESTS                      #
#                                                                             #
###############################################################################

# Run tests
echo -e "\033[31;1m*** Running tests ***\033[0m"

# Start HTTP server to serve assets
echo "Starting HTTP server on $HOST:$PORT"
python3 -m http.server $PORT --bind $HOST > /dev/null 2>&1 &
HTTP_SERVER_PID=$!
disown

# Run tests
echo "Running tests"
nosetests --cover-erase --with-coverage --cover-package=rml

# Stop HTTP server
echo "Stopping HTTP server"
kill -9 $HTTP_SERVER_PID > /dev/null 2>&1

###############################################################################
#                                                                             #
#                               STATIC ANALYSIS                               #
#                                                                             #
###############################################################################

# Run static analyzer
echo -e "\033[31;1m*** Running static analyzer ***\033[0m"
mypy rml

###############################################################################
#                                                                             #
#                               PEP8 COMPLIANCE                               #
#                                                                             #
###############################################################################

# Run PEP8 compliance checks
echo -e "\033[31;1m*** Running PEP8 compliance checker ***\033[0m"
pycodestyle --count rml
STATUS=$?
if [ $STATUS -eq 0 ]
then
    echo "Fully PEP8 compliant!"
fi
