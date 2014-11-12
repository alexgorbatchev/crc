require './test_helpers'

describe 'CRC16Modbus', ->
  crcSuiteFor crc: require '../src/crc16_modbus'
