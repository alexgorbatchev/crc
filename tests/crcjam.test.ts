import crcSuiteFor from './test_helpers';
import crcjam from './.build/crcjam';

describe('CRCJAM', () => {
  crcSuiteFor({ crc: crcjam });
});
