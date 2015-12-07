var benchmark = require('benchmark');
var benchmarks = require('beautify-benchmark');
var seedrandom = require('seedrandom');

var getBuffer = function(size) {
  var buffer = new Buffer(size);
  var rng = seedrandom('body ' + size);

  var end = buffer.length - 1;
  for (var i = 0; 0 < end ? i <= end : i >= end; 0 < end ? i++ : i--) {
    buffer[i] = (rng() * 94 + 32) | 0;
  }

  return buffer;
};

global.crc = require('../lib');
global.bufferCRC32 = require('buffer-crc32');

var suite = new benchmark.Suite();

suite.on('start', function(e) {
  return process.stdout.write('Working...\n\n');
});

suite.on('cycle', function(e) {
  return benchmarks.add(e.target);
});

suite.on('complete', function() {
  return benchmarks.log();
});

module.exports = {
  getBuffer: getBuffer,
  add() { return suite.add(...arguments); },
  run() { return suite.run({async: false}); }
};
