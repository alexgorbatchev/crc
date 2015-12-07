import {crcSuiteFor} from './test_helpers';

describe('CRC8', function() {
  crcSuiteFor({crc: require('../lib/crc8')});
});
