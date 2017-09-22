import {crcSuiteFor} from './test_helpers';

describe('CRCJAM', function() {
  crcSuiteFor({crc: require('../lib/crcjam')});
});
