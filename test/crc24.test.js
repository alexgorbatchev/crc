import {crcSuiteFor} from './test_helpers';

describe('CRC24', function() {
  crcSuiteFor({crc: require('../lib/crc24')});
});
