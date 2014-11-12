require 'coffee-errors'

path = require 'path'
chai = require 'chai'
{exec} = require 'child_process'

GLOBAL.should = chai.should()

GLOBAL.example = ({crc, string, expected}) ->
  getReferenceValue = (model, value, callback) ->
    return callback null, expected if expected?
    exec "#{__dirname}/pycrc/pycrc.py --model=#{model} --check-string=\"#{value}\"", (err, reference) ->
      callback err, reference?.replace /^0x|\n$/g, ''

  describe "crc for `#{string}`", ->
    it 'should calculate a checksum for text', (done) ->
      getReferenceValue crc.model, string, (err, reference) ->
        return done err if err?
        crc(string).toString(16).should.equal reference
        done()

    it 'should calculate a checksum for multiple data', (done) ->
      middle = string.length / 2
      chunk1 = string.substr 0, middle
      chunk2 = string.substr middle

      v1 = crc chunk1
      v2 = crc chunk2, v1

      getReferenceValue crc.model, string, (err, reference) ->
        return done err if err?
        v2.toString(16).should.equal reference
        done()
