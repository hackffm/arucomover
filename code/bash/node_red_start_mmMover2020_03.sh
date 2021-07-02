#!/bin/bash

cd ~/nodered/node_modules/node-red
node red --settings ~/git/arucomover/code/nodered/arucomover.js --flowFile ~/git/arucomover/code/nodered/flows_arucomover.json
