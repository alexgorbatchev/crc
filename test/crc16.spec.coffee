require './test_helpers'

describe 'CRC16', ->
  example
    crc: require('../src/crc16').CRC16
    string: '1234567890'
    expected: 'c57a'
