/* eslint-disable import/no-extraneous-dependencies */
const benchmark = require('benchmark');
const benchmarks = require('beautify-benchmark');
const seedrandom = require('seedrandom');

const getBuffer = (size) => {
  const buffer = Buffer.alloc(size);
  const rng = seedrandom(`body ${size}`);

  for (let i = 0; i < buffer.length - 1; i++) {
    buffer[i] = (rng() * 94 + 32) | 0;
  }

  return buffer;
};

global.crc = require('../../lib');
global.bufferCRC32 = require('buffer-crc32');

const suite = new benchmark.Suite();
suite.on('start', () => process.stdout.write('Working...\n\n'));
suite.on('cycle', (e) => benchmarks.add(e.target));
suite.on('complete', () => benchmarks.log());

module.exports = {
  getBuffer,
  add() {
    return suite.add(...arguments);
  },
  run() {
    return suite.run({ async: false });
  },
};
