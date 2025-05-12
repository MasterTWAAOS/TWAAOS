#!/bin/bash

# A more reliable script for running Cypress tests in Docker
echo "Waiting 15 seconds for all services to be ready..."
sleep 15

echo "Starting Cypress tests..."
cypress run "$@"
