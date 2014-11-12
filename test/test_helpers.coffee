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

GLOBAL.crcSuiteFor = ({crc, value, expected, initial}) ->
  getReferenceValue = (model, value, initial, callback) ->
    return callback null, expected if expected?
    initial = initial? and "--xor-in=0x#{initial.toString(16)}" or ''
    exec "#{__dirname}/pycrc/pycrc.py --model=#{model} #{initial} --check-string=\"#{value}\"", (err, reference) ->
      callback err, reference?.replace /^0x|\n$/g, ''

  testValue = (value, initial, callback) ->
    getReferenceValue crc.model, value, initial, (err, reference) ->
      return done err if err?
      crc(value, initial).toString(16).should.equal reference
      callback()

  testSplitValue = (value, initial, callback) ->
    middle = value.length / 2
    chunk1 = value.substr 0, middle
    chunk2 = value.substr middle

    v1 = crc chunk1, initial
    v2 = crc chunk2, v1

    getReferenceValue crc.model, value, initial, (err, reference) ->
      return done err if err?
      v2.toString(16).should.equal reference
      callback()

  if value? and expected?
    describe "STRING: #{value}", ->
      it 'should calculate a full checksum', (done) -> testValue value, initial, done
      it 'should calculate a checksum for multiple data', (done) -> testSplitValue value, initial, done

  else
    VALUES.map (value) ->
      describe "STRING: #{value}", ->
        it 'should calculate a full checksum', (done) -> testValue value, initial, done
        it 'should calculate a full checksum with initial 0x0', (done) -> testValue value, 0, done
        it 'should calculate a checksum for multiple data', (done) -> testSplitValue value, initial, done
        it 'should calculate a checksum for multiple data with initial 0x0', (done) -> testSplitValue value, 0, done
