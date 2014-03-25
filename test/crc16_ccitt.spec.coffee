require './test_helpers'

describe 'CRC16CCITT', ->
  example
    crc: require('../src/crc16_ccitt').CRC16CCITT
    string: '1234567890'
    expected: '3218'
