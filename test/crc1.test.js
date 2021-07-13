import crcSuiteFor from './test_helpers';
import crc1 from '../lib/es6/crc1';

describe('CRC1', () => {
  crcSuiteFor({
    crc: crc1,
    value: '1234567890',
    expected: 'd',
  });
});
