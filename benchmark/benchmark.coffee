benchmark = require 'benchmark'
benchmarks = require 'beautify-benchmark'
seedrandom = require 'seedrandom'

getBuffer = (size) ->
  buffer = new Buffer size
  rng = seedrandom 'body ' + size

  for i in [0..buffer.length - 1]
    buffer[i] = (rng() * 94 + 32) | 0

  buffer

global.crc = require '../src'
global.bufferCRC32 = require 'buffer-crc32'
global.string100 = getBuffer(100).toString()
global.string1kb = getBuffer(1024).toString()

suite = new benchmark.Suite

suite.on 'start', (e) ->
  process.stdout.write 'Working...\n\n'

suite.on 'cycle', (e) ->
  benchmarks.add e.target

suite.on 'complete', ->
  benchmarks.log()

module.exports =
  getBuffer: getBuffer
  add: -> suite.add arguments...
  run: -> suite.run async: false
