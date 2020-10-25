#!/bin/bash
set -e

###############################################################################
#                                                                             #
#                     UNIT, INTEGRATION & COVERAGE TESTS                      #
#                                                                             #
###############################################################################

# Run tests
echo -e "\033[31;1m*** Running tests ***\033[0m"

# Run tests
echo "Running tests"
nosetests --cover-erase --with-coverage --cover-package=rml --stop

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
