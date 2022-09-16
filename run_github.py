#!/bin/bash

left=100
while [ $left -gt 10 ]
do
    skip_count=`./check.sh`
    repo_count=`cat output.jsonl | wc -l`
    total=`cat repo.list | wc -l`
    left=`expr $total \- $repo_count`
    left=`expr $left \- $skip_count`
    echo $left
    python github.py
done
