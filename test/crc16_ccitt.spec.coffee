require './test_helpers'

describe 'CRC16CCITT', ->
  example
    crc: require '../src/crc16_ccitt'
    string: '1234567890'
