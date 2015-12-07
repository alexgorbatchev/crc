require './test_helpers'

describe 'CRC16KERMIT', ->
  crcSuiteFor crc: require '../src/crc16_kermit'
