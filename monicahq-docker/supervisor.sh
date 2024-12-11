#!/bin/sh

echo "Checking running processes"
ps -ef

echo "Starting supervisord"
supervisord -c /etc/supervisor/conf.d/monica-and-haproxy.conf
#supervisord
echo "Done"
