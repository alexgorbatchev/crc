require './test_helpers'

describe 'CRC16CCITT', ->
  crcSuiteFor crc: require '../src/crc16_ccitt'
