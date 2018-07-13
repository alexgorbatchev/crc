import {crcSuiteFor} from './test_helpers';
import crcjam from '../lib/es6/crcjam';

describe('CRCJAM', function() {
  crcSuiteFor({crc: crcjam});
});
