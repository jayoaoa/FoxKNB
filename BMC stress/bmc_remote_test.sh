#!/bin/sh


#notes:
#	used to check BMC basic function 
#

version="1.3";

if [ $# -ne 3 ]; 
then 
	echo "version: $version"; 
	echo "Copyright (c) 2015 Alibaba. All Rights Reserved.";
	echo "Usage:";
	echo "    $0 <ip> <user> <password>";
	exit -1; 
fi

IP=$1; 
U=$2; 
P=$3;

IPMI="ipmitool -I lanplus -H $IP -U $U -P $P ";

echo "-----------------------------------------------------------------------start";
date "+%Y-%m-%d %H:%M:%S";

echo -n "check BMC version: "; 
$IPMI mc info | grep 'Firmware Revision' | awk -F\: '{print $2}';

$IPMI fru print 0;

echo;
echo "----------------------get BMC info----------------------";
CMD="$IPMI mc info";
echo "==>$CMD"; $CMD;
CMD="$IPMI mc guid";
echo "==>$CMD"; $CMD;
CMD="$IPMI mc selftest";
echo "==>$CMD"; $CMD;


echo;
echo "----------------------get LAN info----------------------";
CMD="$IPMI lan print 1";
echo "==>$CMD"; $CMD;

echo;
echo "----------------------get chassis info----------------------";
CMD="$IPMI chassis status";
echo "==>$CMD"; $CMD;
CMD="$IPMI chassis power status";
echo "==>$CMD"; $CMD;
CMD="$IPMI chassis identify";
echo "==>$CMD"; $CMD;
CMD="$IPMI chassis policy list";
echo "==>$CMD"; $CMD;
CMD="$IPMI chassis restart_cause";
echo "==>$CMD"; $CMD;
CMD="$IPMI chassis selftest";
echo "==>$CMD"; $CMD;



echo;
echo "----------------------get SDR information----------------------";
CMD="$IPMI sdr elist";
echo "==>$CMD"; $CMD;
CMD="$IPMI sdr dump sdr.dat";
echo "==>$CMD"; $CMD;



echo "ME information";
echo -n "ME - node power: ";
$IPMI -t 0x2c -b 0 raw 0x2E 0xC8 0x57 0x01 0x00 0x1 0x0 0x0 |/usr/bin/xargs|awk '{print strtonum("0x"$5$4)}';

echo -n "ME - CPU power: ";
$IPMI -b 0 -t 0x2c raw 0x2e 0xc8 0x57 0x01 0x00 0x01 0x1 0x0 |/usr/bin/xargs|awk '{print strtonum("0x"$5$4)}';

echo -n "ME - DIMM power: ";
$IPMI -b 0 -t 0x2c raw 0x2e 0xc8 0x57 0x01 0x00 0x01 0x2 0x0 |/usr/bin/xargs|awk '{print strtonum("0x"$5$4)}';

echo -n "ME - CPU/DIMM Temp";
$IPMI -t 0x2c -b 0 raw 0x2e 0x4b 0x57 0x01 0x00 0x03 0xff 0xff 0xff 0xff 0x00 0x00 0x00 0x00;


echo;
echo "----------------------get sensor threshold----------------------";
CMD="$IPMI sensor list";
echo "==>$CMD"; $CMD;

echo;
echo "----------------------get FRU information----------------------";
CMD="$IPMI fru print 0";
echo "==>$CMD"; $CMD;
CMD="$IPMI fru read 0 fru.dat";
echo "==>$CMD"; $CMD;


echo;
echo "----------------------get SEL information----------------------";
CMD="$IPMI sel info";
echo "==>$CMD"; $CMD;
CMD="$IPMI sel time get";
echo "==>$CMD"; $CMD;
CMD="$IPMI sel writeraw sel.dat";
echo "==>$CMD"; $CMD;

echo;
echo "----------------------get SOL information----------------------";
CMD="$IPMI sol info 1";
echo "==>$CMD"; $CMD;
userid=`$IPMI user list 1 | grep admin | awk '{print $1}'`;
CMD="$IPMI sol  payload status 1 $userid";
echo "==>$CMD"; $CMD;


echo;
echo "----------------------get user info----------------------";
CMD="$IPMI user list 1";
echo "==>$CMD"; $CMD;


echo;
echo "----------------------get channel info----------------------";
CMD="$IPMI channel info 1";
echo "==>$CMD"; $CMD;
CMD="$IPMI channel getaccess 1 $userid";
echo "==>$CMD"; $CMD;
CMD="$IPMI channel getciphers ipmi 1";
echo "==>$CMD"; $CMD;
CMD="$IPMI channel getciphers sol 1";
echo "==>$CMD"; $CMD;

CMD="$IPMI channel info 0";
echo "==>$CMD"; $CMD;


date "+%Y-%m-%d %H:%M:%S";
echo "-----------------------------------------------------------------------end";



