import {crcSuiteFor} from './test_helpers';
import crcjam from '../lib/crcjam';

describe('CRCJAM', function() {
  crcSuiteFor({crc: crcjam});
});
