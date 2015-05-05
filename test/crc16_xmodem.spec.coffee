require './test_helpers'

describe 'CRC16XModem', ->
  crcSuiteFor crc: require '../src/crc16_xmodem'
