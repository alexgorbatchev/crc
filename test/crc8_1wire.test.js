import {crcSuiteFor} from './test_helpers';
import crc8_1wire from '../lib/crc8_1wire';

describe('CRC8 1 Wire', function() {
  crcSuiteFor({crc: crc8_1wire});
});
