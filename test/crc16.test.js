import {crcSuiteFor} from './test_helpers';
var crc = require('../src/crc16');

describe('CRC16', function() {
  crcSuiteFor({crc});

  // https://github.com/alexgorbatchev/node-crc/issues/29
  crcSuiteFor({
    crc: crc,
    value: new Buffer('AR0AAAGP2KJc/vg/AAAAErgGAK8dAAgLAQAAPpo=', 'base64').slice(0, 27)
  });
});
