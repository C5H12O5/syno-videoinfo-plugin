#!/bin/sh

BASEDIR=$(dirname $0)
ARGV=""
PORT=5125

escape()
{
	local ARG=$(echo -E "$@" | sed "s/'/'\\\\''/g")
	echo \'$ARG\'
}

i=1
while [ $i -le $# ]; do
	eval ARG=\$\(escape \${$i}\)
	ARGV="$ARGV $ARG"
	i=`expr $i + 1`
done

if ! netstat -tuln | grep ":$PORT" >/dev/null; then
	nohup /usr/bin/env python3 "$BASEDIR"/configserver/serve.py > /dev/null 2>&1 &
fi

eval "/usr/bin/env python3 $BASEDIR/main.py $ARGV"