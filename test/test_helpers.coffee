require 'coffee-errors'

path = require 'path'
chai = require 'chai'
{exec} = require 'child_process'

GLOBAL.should = chai.should()

VALUES = [
  "1234567890"
  "cwd String Current working directory of the child process"
  "env Object Environment key-value pairs"
  "encoding String (Default: 'utf8')"
  "timeout Number (Default: 0)"
  "maxBuffer Number (Default: 200*1024)"
  "killSignal String (Default: 'SIGTERM')"
]

GLOBAL.crcSuiteFor = ({crc, value, expected}) ->
  getReferenceValue = (model, value, callback) ->
    return callback null, expected if expected?
    exec "#{__dirname}/pycrc/pycrc.py --model=#{model} --check-string=\"#{value}\"", (err, reference) ->
      callback err, reference?.replace /^0x|\n$/g, ''

  testValue = (value, callback) ->
    getReferenceValue crc.model, value, (err, reference) ->
      return done err if err?
      crc(value).toString(16).should.equal reference
      callback()

  testSplitValue = (value, callback) ->
    middle = value.length / 2
    chunk1 = value.substr 0, middle
    chunk2 = value.substr middle

    v1 = crc chunk1
    v2 = crc chunk2, v1

    getReferenceValue crc.model, value, (err, reference) ->
      return done err if err?
      v2.toString(16).should.equal reference
      callback()

  if value? and expected?
    describe "STRING: #{value}", ->
      it 'should calculate a full checksum', (done) -> testValue value, done
      it 'should calculate a checksum for multiple data', (done) -> testSplitValue value, done

  else
    VALUES.map (value) ->
      describe "STRING: #{value}", ->
        it 'should calculate a full checksum', (done) -> testValue value, done
        it 'should calculate a checksum for multiple data', (done) -> testSplitValue value, done
