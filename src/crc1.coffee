{Buffer} = require 'buffer'
create = require './create'

module.exports = create (buf, previous) ->
  buf = Buffer buf unless Buffer.isBuffer buf

  crc = ~~previous
  accum = 0
  accum += byte for byte in buf
  crc += accum % 256

  crc % 256
