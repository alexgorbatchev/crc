#!/bin/bash -e

cd webpack-test

[ ! -d node_modules ] && npm install
$(npm bin)/webpack --mode=production

if [[ "$(node output.js)" != "222957957" ]]; then
  echo "👎 Webpack bundle didn't produce expected output!"
  exit 1
fi

echo "👍 Webpack bundle ok!"
