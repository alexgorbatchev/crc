require './test_helpers'

describe 'CRC1', ->
  crcSuiteFor
    crc: require '../src/crc1'
    value: '1234567890'
    expected: 'd'
