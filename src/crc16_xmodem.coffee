{Buffer} = require 'buffer'
create = require './create'

module.exports = create 'ccitt', (buf, previous) ->
  buf = Buffer buf unless Buffer.isBuffer buf

  crc = if previous? then ~~previous else 0x0
  count = buf.length
  i = 0
  while count > 0
    code = crc >>> 8 & 0xFF
    code ^= buf[i++] & 0xFF
    code ^= code >>> 4
    crc = crc << 8 & 0xFFFF
    crc ^= code
    code = code << 5 & 0xFFFF
    crc ^= code
    code = code << 7 & 0xFFFF
    crc ^= code
    count--
  crc
