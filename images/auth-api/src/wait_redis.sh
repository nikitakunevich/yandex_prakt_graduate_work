#!/bin/sh

cmd="$@"

while [ "$(redis-cli -h $REDIS_HOST -p $REDIS_PORT ping)" != "PONG" ]
do
  >&2 echo "Redis is unavailable - sleeping"
  sleep 2;
done

exec $cmd
