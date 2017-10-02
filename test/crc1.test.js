import {crcSuiteFor} from './test_helpers';
import crc1 from '../lib/crc1';

describe('CRC1', function() {
  crcSuiteFor({
    crc: crc1,
    value: '1234567890',
    expected: 'd'
  });
});
