#!/bin/bash
if [[ ! -d web ]]
then
  git clone https://github.com/CleanEarthIO/web.git
fi
cd web
git fetch --all
git reset --hard origin/master
npm install
npm run build
cd ..