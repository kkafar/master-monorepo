#!/bin/bash

# https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash
# OPTIND=1
# opt_str="i:"
#
# input_files=""
#
# while getopts "${opt_str}" opt
# do
#   case "${opt}" in
#     i)
#       input_files=${OPTARG}
#       ;;
#   esac
# done
#
# shift $((OPTIND-1))
#
# ${input_files:?"Input files must be set"}
#
#
# echo "${input_files}"

list="one two three four"

array=(
  "one" "two" "$list"
)

for item in "${array[@]}"; do
  echo $item
done
