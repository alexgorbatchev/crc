import {crcSuiteFor} from './test_helpers';
import crc8 from '../lib/es6/crc8';

describe('CRC8', function() {
  crcSuiteFor({crc: crc8});
});
