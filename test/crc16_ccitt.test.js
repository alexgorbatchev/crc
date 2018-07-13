import {crcSuiteFor} from './test_helpers';
import crc16_ccitt from '../lib/crc16_ccitt';

describe('CRC16CCITT', function() {
  crcSuiteFor({crc: crc16_ccitt});
});
