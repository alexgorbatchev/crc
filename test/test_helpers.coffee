require 'coffee-errors'

path = require 'path'
fs = require 'fs'
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
  getReferenceValueForBuffer = (model, buffer, initial, callback) ->
    return callback null, expected if expected?
    filename = "#{__dirname}/tmp"
    fs.writeFileSync filename, buffer
    initial = initial? and "--xor-in=0x#{initial.toString(16)}" or ''
    exec "#{__dirname}/pycrc/pycrc.py --model=#{model} #{initial} --check-file=\"#{filename}\"", (err, reference) ->
      fs.unlinkSync filename
      callback err, reference?.replace /^0x|\n$/g, ''

  getReferenceValueForString = (model, string, initial, callback) ->
    return callback null, expected if expected?
    initial = initial? and "--xor-in=0x#{initial.toString(16)}" or ''
    exec "#{__dirname}/pycrc/pycrc.py --model=#{model} #{initial} --check-string=\"#{string}\"", (err, reference) ->
      callback err, reference?.replace /^0x|\n$/g, ''

  testStringValue = (string, initial, callback) ->
    getReferenceValueForString crc.model, string, initial, (err, reference) ->
      return done err if err?
      crc(string, initial).toString(16).should.equal reference
      callback()

  testBufferValue = (buffer, initial, callback) ->
    getReferenceValueForBuffer crc.model, buffer, initial, (err, reference) ->
      return done err if err?
      crc(buffer, initial).toString(16).should.equal reference
      callback()

  testStringSplitValue = (value, initial, callback) ->
    middle = value.length / 2
    chunk1 = value.substr 0, middle
    chunk2 = value.substr middle
    v1 = crc chunk1, initial
    v2 = crc chunk2, v1

    getReferenceValueForString crc.model, value, initial, (err, reference) ->
      return callback err if err?
      v2.toString(16).should.equal reference
      callback()

  testBufferSplitValue = (value, initial, callback) ->
    middle = value.length / 2
    chunk1 = value.slice 0, middle
    chunk2 = value.slice middle

    v1 = crc chunk1, initial
    v2 = crc chunk2, v1

    getReferenceValueForBuffer crc.model, value, initial, (err, reference) ->
      return callback err if err?
      v2.toString(16).should.equal reference
      callback()

  if value?
    if Buffer.isBuffer value
      describe "BUFFER: #{value.toString 'base64'}", ->
        it 'should calculate a full checksum', (done) -> testBufferValue value, initial, done
        it 'should calculate a checksum for multiple data', (done) -> testBufferSplitValue value, initial, done
    else
      describe "STRING: #{value}", ->
        it 'should calculate a full checksum', (done) -> testStringValue value, initial, done
        it 'should calculate a checksum for multiple data', (done) -> testStringSplitValue value, initial, done

  else
    VALUES.map (value) ->
      describe "STRING: #{value}", ->
        it 'should calculate a full checksum', (done) -> testStringValue value, initial, done
        it 'should calculate a full checksum with initial 0x0', (done) -> testStringValue value, 0, done
        it 'should calculate a checksum for multiple data', (done) -> testStringSplitValue value, initial, done
        it 'should calculate a checksum for multiple data with initial 0x0', (done) -> testStringSplitValue value, 0, done
