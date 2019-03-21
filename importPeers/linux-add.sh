#!/bin/bash

IPV4=1
IPV6=0
COUNT=5
GEOIP=1
DRY=0

for i in "$@"
do
case $i in
    -g=*|--geoip=*)
    GEOIP="${i#*=}"
    shift
    ;;
    -4=*|--ipv4=*)
    IPV4="${i#*=}"
    shift
    ;;
    -6=*|--ipv6=*)
    IPV6="${i#*=}"
    shift
    ;;
    -c=*|--count=*)
    COUNT="${i#*=}"
    shift
    ;;
    *)
	echo "
	linux-add.sh - Script to automate adding nodes
	contact passenger:tekst.xyz Matrix

	-g|--geoip=1|0 Sort nodes by closest location
	-c|--count=5   Number of nodes to add
	-4|--ipv4=1|0  Return ipv4 enabled nodes
	-6|--ipv6=1|0  Return ipv6 enabled nodes
	"
	exit 1;
    ;;
esac
done


URL="https://api.yggdrasil.icu/public-peers/?max_results=$COUNT&output=raw"

if [ $GEOIP -eq 1 ]; then
	URL="$URL&geo_nearby"
fi

if [ $IPV4 -eq 1 ]; then
	URL="$URL&give_ipv4"
fi

if [ $IPV6 -eq 1 ]; then
	URL="$URL&give_ipv6"
fi

tmpfile=$(mktemp /tmp/yggdrasil-addpeer.XXXXXX)
wget $URL -q -O $tmpfile

if [ $? -ne 0 ];then
	echo "Unable to retrieve $URL"
	exit 1
fi

for node in $(cat $tmpfile);do
	node=${node//[^a-zA-Z0-9:/.]/}
	node=$(echo $node | tr -d '\r\n')
	yggdrasilctl addPeer uri=$node
done;

rm $tmpfile

