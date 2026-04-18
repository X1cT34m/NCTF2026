#!/bin/bash

echo $GZCTF_FLAG > /flag
unset GZCTF_FLAG

chown node:node /flag
chmod 000 /flag

su - node -c 'nohup opencode web >/tmp/opencode-web.log 2>&1 &'
su - node -c 'export PLAYWRIGHT_BROWSERS_PATH=/ms-playwright; cd /app/ && node bot.js'
