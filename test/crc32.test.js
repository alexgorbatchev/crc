import {crcSuiteFor} from './test_helpers';

describe('CRC32', function() {
  crcSuiteFor({crc: require('../lib/crc32')});
});
