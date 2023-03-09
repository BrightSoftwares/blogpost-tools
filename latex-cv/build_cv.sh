#!/bin/bash

echo Generating the CVs from folder ${INPUT_SRC_FOLDER}
cd ${INPUT_SRC_FOLDER}

echo Here is the content of the file
ls -lah

echo Generating the CV now
pdflatex main.tex
