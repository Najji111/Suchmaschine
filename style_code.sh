#!/bin/bash

# welcome
printf "Checkstyle python...\n"

res=$(sed -i -e "s/^\s\s*$//g" \
			-e "s/\s\s*$//g" \
			-E -e "s/(^[[:space:]]*[^[:space:]]+[[:space:]])[[:space:]]+([^[:space:]]+)/\1\2/g" $1)

printf "$res\n"

