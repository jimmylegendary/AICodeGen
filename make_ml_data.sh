#!/bin/bash

ORIG_FILE="mydata.jsonl"
if [ ! $1="" ]; then
	ORIG_FILE=$1
fi
data_size=`cat mydata.jsonl | wc -l`
train_data_size=`expr $data_size \* 8`
train_data_size=`expr $train_data_size \/ 10`
valid_data_size=`expr $data_size \/ 10`
test_data_size=`expr $data_size \- $train_data_size`
test_data_size=`expr $test_data_size \- $valid_data_size`

FILE_PATH="/data/team14/falcon/data/Code_Refinement/jimmy"
TRAIN_FILE="$FILE_PATH/ref-train.jsonl"
VALID_FILE="$FILE_PATH/ref-valid.jsonl"
TEST_FILE="$FILE_PATH/ref-test.jsonl"
sum=$train_data_size
cat $ORIG_FILE | head -n $sum > $TRAIN_FILE
sum=`expr $sum \+ $valid_data_size`
cat $ORIG_FILE | head -n $sum | tail -n $valid_data_size > $VALID_FILE
cat $ORIG_FILE | tail -n $test_data_size > $TEST_FILE
