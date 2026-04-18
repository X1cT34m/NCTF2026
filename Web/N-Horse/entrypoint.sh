#!/bin/sh

echo "$GZCTF_FLAG" > /flag

unset GZCTF_FLAG

python /app/app.py