require './test_helpers'

describe 'CRC1', ->
  example
    crc: require '../src/crc1'
    string: '1234567890'
    expected: 'd'
