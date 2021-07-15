import crcSuiteFor from './test_helpers';
import crcjam from '../src/crcjam';

describe('CRCJAM', () => {
  crcSuiteFor({ crc: crcjam });
});
