LIST=`cat *.skip*`
REPO_LIST=[]
idx=0
for list in ${LIST[@]}
do
	isExist=0
	for repo in ${REPO_LIST[@]}
	do 
		if [ "$repo" == "$list" ]; then 
			isExist=1
			break
		fi
	done
	if [ $isExist -eq 1 ]; then
		continue
	fi
	REPO_LIST[$idx]=$list
	let idx+=1
done
echo $idx
