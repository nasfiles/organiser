#!/bin/bash

echo "Updating your server tools..."


cd /usr/share/organiser;
git pull > /dev/null 2>&1;

echo "Scripts updated"

# add execution rights
chmod +x *.py
cp *.py /usr/local/bin

exit 0