#!/bin/bash -e

cd webpack-test

if [ ! -d node_modules ]; then
  npm install
fi

$(npm bin)/webpack --mode=production

if [[ "$(node output/with-buffer.js)" != "222957957 222957957" ]]; then
  echo "👎 Webpack bundle didn't produce expected output (with-buffer.js)!"
  exit 1
fi

if [[ "$(node output/with-array.js)" != "222957957" ]]; then
  echo "👎 Webpack bundle didn't produce expected output (with-array.js)!"
  exit 1
fi

echo "👍 Webpack bundle ok!"
