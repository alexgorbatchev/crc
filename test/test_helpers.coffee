require 'coffee-errors'

path = require 'path'
chai = require 'chai'

GLOBAL.should = chai.should()

GLOBAL.example = ({crc, string, expected}) ->
  describe "crc for `#{string}`", ->
    it 'should calculate a checksum for text', ->
      crc(string).toString(16).should.equal expected

    it 'should calculate a checksum for multiple data', ->
      middle = string.length / 2
      chunk1 = string.substr 0, middle
      chunk2 = string.substr middle

      v1 = crc chunk1
      v2 = crc chunk2, v1

      v2.toString(16).should.equal expected
