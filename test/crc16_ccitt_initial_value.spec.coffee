require './test_helpers'

describe 'CRC16CCITT w/ initial value set to 0x0', ->
  example
    crc: require '../src/crc16_ccitt'
    string: '1234567890'
    expected: 'd321'
    initial: 0x0

