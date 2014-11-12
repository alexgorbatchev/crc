require './test_helpers'

describe 'CRC8 1 Wire', ->
  crcSuiteFor crc: require '../src/crc8_1wire'
