#!/usr/bin/env bash
set -e

docker run --rm ubuntu bash -lc '
echo "Inside container:"
whoami
uname -a
cat /etc/os-release | head -n 5
'
