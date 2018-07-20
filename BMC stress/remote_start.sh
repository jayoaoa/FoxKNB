#!/bin/sh


if [ $# -ne 1 ]
then
echo "$0 <oobip>";
exit -1;
fi


cycle=1;
task=10;

oobip=$1;
U=admin;
P=admin;

echo $oobip;
echo $P;
echo $U;


./bmc_remote_test.sh $oobip $U $P > $oobip.result

for((i=0; i<$task;i++))
do
{
	for((j=0;j<$cycle;j++))
	do
		echo "loop_count: $j" >> yace$i.$oobip;
		./bmc_remote_test.sh $oobip $U $P >> yace$i.$oobip;
	done
} &
done
