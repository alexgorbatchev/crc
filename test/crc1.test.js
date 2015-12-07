import {crcSuiteFor} from './test_helpers';

describe('CRC1', function() {
  crcSuiteFor({
    crc: require('../lib/crc1'),
    value: '1234567890',
    expected: 'd'
  });
});
