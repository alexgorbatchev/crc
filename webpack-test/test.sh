#!/bin/bash -e

cd webpack-test

if [ ! -d node_modules ]; then
  npm install
  ln -s $(cd .. && pwd) node_modules/crc
fi

$(npm bin)/webpack --mode=production

if [[ "$(node output.js)" != "222957957 222957957" ]]; then
  echo "👎 Webpack bundle didn't produce expected output!"
  exit 1
fi

echo "👍 Webpack bundle ok!"
