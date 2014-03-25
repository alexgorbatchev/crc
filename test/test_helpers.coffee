require 'coffee-errors'


path = require 'path'
chai = require 'chai'

GLOBAL.should = chai.should()

GLOBAL.example = ({crc, string, expected}) ->
  crc = new crc()

  it "should define block_length of 1", ->
    crc.block_length().should.equal 1

  # it "should pack to an empty String by default", ->
    # crc.pack(0).should.be.empty

  it 'should calculate a checksum for text', ->
    crc.hexdigest(string).should.equal expected

  it 'should calculate a checksum for multiple data', ->
    middle = string.length / 2

    chunk1 = string.substr 0, middle
    chunk2 = string.substr middle

    crc.update chunk1
    crc.update chunk2
    crc.hexdigest().should.equal expected

  it 'should provide direct access to the checksum value', ->
    crc.update string
    crc.checksum().should.equal parseInt expected, 16
