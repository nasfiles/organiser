#!/bin/bash

echo "Updating your server tools..."


cd /usr/share/organiser;
git pull > /dev/null 2>&1;

echo "Scripts updated"

# add execution rights
cp *.py /usr/local/bin
chmod +x /usr/local/bin/*.py

exit 0