import {crcSuiteFor} from './test_helpers';
import crc32 from '../lib/es6/crc32';

describe('CRC32', function() {
  crcSuiteFor({crc: crc32});
});
