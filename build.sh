#!/bin/sh

set -f  # disable glob

DIRPATH=$(pwd)
DIRNAME=$(basename ${DIRPATH})

IGNORE_FILES=(
    "build.sh"
    ".gitignore"
    "requirements.txt"
    "*.pyc"
    "${DIRNAME}.zip"
)
IGNORE_PATHS=(
    "./.git/*"
    "./.idea/*"
    "./venv/*"
    "./tests/*"
    "*/__pycache__/*"
)

# build ignore options
OPTIONS=()
for IGNORE_FILE in ${IGNORE_FILES[*]}
do
    OPTIONS+=("-not -name ${IGNORE_FILE}")
done
for IGNORE_PATH in ${IGNORE_PATHS[*]}
do
    OPTIONS+=("-not -path ${IGNORE_PATH}")
done
OPTIONS=${OPTIONS[*]}

# copy files to subdir
TEMPDIR=$(mktemp -d)
mkdir "${TEMPDIR}/${DIRNAME}"
find . -type f ${OPTIONS} -exec cp --parents "{}" "${TEMPDIR}/${DIRNAME}" \;

# zip subdir
cd "${TEMPDIR}"
zip -r "${DIRPATH}/${DIRNAME}.zip" "${DIRNAME}"

# remove temp dir
rm -fr "${TEMPDIR}"
