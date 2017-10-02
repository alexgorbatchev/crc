import {crcSuiteFor} from './test_helpers';
import crc16_kermit from '../lib/crc16_kermit';

describe('CRC16KERMIT', function() {
  crcSuiteFor({crc: crc16_kermit});
});
