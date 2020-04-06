#!/bin/sh

FILENAME="plugin.video.dokustreams.de.zip"

set -f  # disable glob

IGNORE_FILES=(
    'build.sh'
    '.gitignore'
    'requirements.txt'
    '*.pyc'
)
IGNORE_PATHS=(
    './.git/*'
    './.idea/*'
    './venv/*'
    './tests/*'
    '*/__pycache__/*'
)

OPTIONS=()
for IGNORE_FILE in ${IGNORE_FILES[*]}
do
    OPTIONS+=("-not -name ${IGNORE_FILE}")
done
for IGNORE_PATH in ${IGNORE_PATHS[*]}
do
    OPTIONS+=("-not -path $IGNORE_PATH")
done
OPTIONS=${OPTIONS[*]}

find . -type f ${OPTIONS} -print | zip "$FILENAME" -@
