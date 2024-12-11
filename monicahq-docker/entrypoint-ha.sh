#!/bin/bash

# Default values for environment variables
: "${MYSQL_HOST:=127.0.0.1}"       # MySQL server hostname or IP
: "${MYSQL_PORT:=3306}"            # MySQL server port
: "${HAPROXY_PORT:=3306}"          # Port on which HAProxy will listen
: "${HAPROXY_MAXCONN:=1}"          # Max number of connections to MySQL

# Generate haproxy.cfg
cat <<EOF > /etc/haproxy/haproxy.cfg
global
  stats socket /var/run/api.sock user haproxy group haproxy mode 660 level admin expose-fd listeners
  log stdout format raw local0 info

defaults
  mode http
  timeout client 10s
  timeout connect 5s
  timeout server 10s
  timeout http-request 10s
  log global

frontend stats
  bind *:8404
  stats enable
  stats uri /
  stats refresh 10s

frontend mysql_frontend
    mode tcp
    bind *:${HAPROXY_PORT}
    default_backend mysql_backend

backend mysql_backend
    mode tcp
    server mysql_server ${MYSQL_HOST}:${MYSQL_PORT} maxconn ${HAPROXY_MAXCONN}
EOF

echo "Generated HAProxy configuration:"
cat /etc/haproxy/haproxy.cfg

# run the monica install process
#echo "monica is installing ..."
#exec /usr/local/bin/entrypoint.sh

# Start HAProxy
exec haproxy -f /etc/haproxy/haproxy.cfg
