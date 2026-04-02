#!/bin/sh

echo "Starting app"

if [ -z "$DB_HOST" ]; then
  echo "ERROR: DB_HOST is missing"
  exit 1
fi

echo "DB_HOST=$DB_HOST"
echo "App started successfully"
sleep 300
