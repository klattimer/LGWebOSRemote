#!/bin/bash
SOURCE="$( readlink -f ${BASH_SOURCE[0]} )"
DIR="$( cd "$( dirname "$SOURCE" )" && pwd )"
cd $DIR
source ./venv/bin/activate
python lgtv.py $*
