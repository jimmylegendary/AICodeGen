#!/bin/bash

ORIG_FILE="mydata.jsonl"
if [ ! $1="" ]; then
	ORIG_FILE=$1
fi
DEV_RATIO=10
ORIG_SIZE=`cat $ORIG_FILE | wc -l`
#DEV_SIZE=`expr $ORIG_SIZE \/ $DEV_RATIO`
DEV_SIZE=187500
DEV_FILE="devdata.jsonl"
head -n $DEV_SIZE $ORIG_FILE > $DEV_FILE
data_size=`cat $DEV_FILE | wc -l`
train_data_size=`expr $data_size \* 8`
train_data_size=`expr $train_data_size \/ 10`
valid_data_size=`expr $data_size \/ 10`
test_data_size=`expr $data_size \- $train_data_size`
test_data_size=`expr $test_data_size \- $valid_data_size`

DATA_DIR="/data/team14/falcon/data/Code_Refinement/jimmy_dev"
if [ ! -d $DATA_DIR ]; then
	mkdir $DATA_DIR
fi
TRAIN_FILE="$DATA_DIR/ref-train.jsonl"
VALID_FILE="$DATA_DIR/ref-valid.jsonl"
TEST_FILE="$DATA_DIR/ref-test.jsonl"
sum=$train_data_size
cat $DEV_FILE | head -n $sum > $TRAIN_FILE
sum=`expr $sum \+ $valid_data_size`
cat $DEV_FILE | head -n $sum | tail -n $valid_data_size > $VALID_FILE
cat $DEV_FILE | tail -n $test_data_size > $TEST_FILE

rm $DEV_FILE
