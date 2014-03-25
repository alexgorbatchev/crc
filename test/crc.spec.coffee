require './test_helpers'
crc = require('../src')

describe 'CRC', ->
  it 'should have a shortcut hexdigest', ->
    string = '1234567890'
    expected = '0d'
    crc.crc1(string).should.equal expected
