benchmark = require './benchmark'

global.string = benchmark.getBuffer(1024).toString()

benchmark.add
  minSamples : 100
  name       : 'crc/crc32 1kb'
  fn         : 'var val = crc.crc32(string)'

benchmark.add
  minSamples : 100
  name       : 'buffer-crc32 1kb'
  fn         : 'var val = bufferCRC32(string)'

benchmark.run()

