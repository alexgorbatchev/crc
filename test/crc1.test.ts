import crcSuiteFor from './test_helpers';
import crc1 from '../src/crc1';

describe('CRC1', () => {
  crcSuiteFor({
    crc: crc1,
    value: '1234567890',
    expected: 'd',
  });
});
