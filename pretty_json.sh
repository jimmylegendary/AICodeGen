#!/bin/bash

FILE=$1
if [ ! -e $FILE ]; then
	echo "Please input file"
	exit
fi
LEN=`expr $2 \+ 0`
if [ $LEN -le 0 ]; then
	echo "Please input non-zero len"
	exit
fi

size=0
while read line
do
	echo $line | python -m json.tool
	let size+=1
	if [ $size -ge $LEN ]; then
		break
	fi
done < $FILE
