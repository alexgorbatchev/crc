import crcSuiteFor from './test_helpers';
import crc16 from '../src/crc16';
import createBuffer from '../src/create_buffer';

describe('CRC16', () => {
  crcSuiteFor({ crc: crc16 });

  // https://github.com/alexgorbatchev/node-crc/issues/29
  crcSuiteFor({
    crc: crc16,
    value: createBuffer('AR0AAAGP2KJc/vg/AAAAErgGAK8dAAgLAQAAPpo=', 'base64').slice(0, 27),
  });
});
