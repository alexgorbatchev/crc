module.exports = {
  crc1: require('./crc1'),
  crc8: require('./crc8'),
  crc81wire: require('./crc81wire'),
  crc16: require('./crc16'),
  crc16ccitt: require('./crc16ccitt'),
  crc16modbus: require('./crc16modbus'),
  crc16xmodem: require('./crc16xmodem'),
  crc16kermit: require('./crc16kermit'),
  crc24: require('./crc24'),
  crc32: require('./crc32'),
  crc32mpeg: require('./crc32mpeg2'),
  crcjam: require('./crcjam'),
};

module.exports.default = module.exports;
