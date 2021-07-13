const benchmark = require('./benchmark');

global.string = benchmark.getBuffer(100 * 1024).toString();

benchmark.add({
  minSamples: 100,
  name: 'crc/crc32 100kb',
  fn: 'var val = crc.crc32.signed(string)',
});

benchmark.add({
  minSamples: 100,
  name: 'buffer-crc32 100kb',
  fn: 'var val = bufferCRC32(string)',
});

benchmark.run();
