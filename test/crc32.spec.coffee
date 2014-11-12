require './test_helpers'
crc = require '../src/crc32'

describe 'CRC32', ->
  example
    crc: crc
    string: '1234567890'

  example
    crc: crc
    string: 'Hello, world'
