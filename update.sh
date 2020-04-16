#!/bin/bash
source /home/ecp/.bashrc

if [ "$1" == "" ]; then
  source activate py2
  supervisorctl update
fi

while [ "$1" != "" ]; do
  case $1 in
  "source")
    source activate $2
    if [ "$3" != "" ]; then
      supervisorctl -c $3 update
    else
      supervisorctl update
    fi
    ;;
  "conda")
    conda activate $2
    if [ "$3" != "" ]; then
      supervisorctl -c $3 update
    else
      supervisorctl update
    fi
    ;;
  *)
    # conda activate $2
    if [ "$1" != "" ]; then
      supervisorctl -c $1 update
    else
      supervisorctl update
    fi
    ;;
  esac
  shift
done
