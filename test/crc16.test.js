import {crcSuiteFor} from './test_helpers';
import crc16 from '../lib/crc16';

describe('CRC16', function() {
  crcSuiteFor({crc: crc16});

  // https://github.com/alexgorbatchev/node-crc/issues/29
  crcSuiteFor({
    crc: crc16,
    value: new Buffer('AR0AAAGP2KJc/vg/AAAAErgGAK8dAAgLAQAAPpo=', 'base64').slice(0, 27)
  });
});
