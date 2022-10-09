#!/bin/sh

echo "Rosae generate the html"
rosaenlg  -l en_US /templates/drone_dji.pug -o /templates/generated/


echo "Convert html to markdown"
html-to-markdown /templates/generated/drone_dji.html -o /templates/generated/

echo "Done"
