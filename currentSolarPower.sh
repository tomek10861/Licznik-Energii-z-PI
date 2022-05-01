#!/bin/bash
#Skrypt testowany z falownikiem Sofar i modułem wifi
#Ades ip falownika
IPPV=192.168.1.2
UserPV=admin
PasswordPV=hasłoDoFalownika

data=($(curl -s -u $UserPV:$PasswordPV "http://$IPPV/status.html" | grep 'var webdata_' | awk {'print $4'} | sed 's/;//'| tr -d '"' ))
[ -z "$data" ] && exit 1
[[ -z "${data[5]}" ]] && data=($(curl -s -u $UserPV:$PasswordPV "http://$IPPV/status.html" | grep 'var webdata_' | awk {'print $4'} | sed 's/;//'| tr -d '"' ))


if [[ "$1" == "actual" ]]
then
	echo ${data[5]}| tr -d '\r'
elif [[ "$1" == "today" ]]
then
	echo ${data[6]} | tr -d '\r'
fi
