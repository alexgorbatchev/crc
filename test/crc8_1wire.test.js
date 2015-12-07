import {crcSuiteFor} from './test_helpers';

describe('CRC8 1 Wire', function() {
  crcSuiteFor({crc: require('../lib/crc8_1wire')});
});
