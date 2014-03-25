require './test_helpers'

describe 'CRC32', ->
  example
    crc: require('../src').CRC32
    string: '1234567890'
    expected: '261daee5'
