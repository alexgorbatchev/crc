import {crcSuiteFor} from './test_helpers';

describe('CRC16KERMIT', function() {
  crcSuiteFor({crc: require('../lib/crc16_kermit')});
});
