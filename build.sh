#!/bin/sh

set -f  # disable glob

DIRNAME=$(basename $(pwd))

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
    "./${DIRNAME}/*"
)

# build ignore options
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

# copy files to subdir
rm -fr "${DIRNAME}"
mkdir "${DIRNAME}"
find . -type f ${OPTIONS} -exec cp --parents "{}" ${DIRNAME} \;

# zip subdir
zip -r "${DIRNAME}.zip" "${DIRNAME}"

# remove subdir
rm -fr "${DIRNAME}"
