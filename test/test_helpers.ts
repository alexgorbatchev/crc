import fs from 'fs';
import chai from 'chai';
import { exec } from 'child_process';
import { CRCModule } from '../src/types';

const TEST_VALUES = [
  '1234567890',
  'cwd String Current working directory of the child process',
  'env Object Environment key-value pairs',
  "encoding String (Default: 'utf8')",
  'timeout Number (Default: 0)',
  'maxBuffer Number (Default: 200*1024)',
  "killSignal String (Default: 'SIGTERM')",
];

chai.should();

type Callback = (err?: Error | null, result?: string | number) => void;

function getReferenceValueForBuffer(
  model: string,
  buffer: Buffer,
  initial: number | undefined,
  expected: string | undefined,
  callback: Callback
) {
  if (expected) {
    callback(null, expected);
  } else {
    const initialArg = typeof initial !== 'undefined' ? `--xor-in=0x${initial.toString(16)}` : '';
    const filename = `${__dirname}/tmp`;
    const cmd = `pycrc.py --model=${model} ${initialArg} --check-file="${filename}"`;

    fs.writeFileSync(filename, buffer);

    exec(`${__dirname}/pycrc/${cmd}`, (err, reference) => {
      fs.unlinkSync(filename);
      callback(err, (reference || '').replace(/^0x|\n$/g, ''));
    });
  }
}

function getReferenceValueForString(
  model: string,
  checkString: string,
  initial: number | undefined,
  expected: string | undefined,
  callback: Callback
) {
  if (expected) {
    callback(null, expected);
  } else {
    const initialArg = typeof initial !== 'undefined' ? `--xor-in=0x${initial.toString(16)}` : '';
    const cmd = `pycrc.py --model=${model} ${initialArg} --check-string="${checkString}"`;
    exec(`${__dirname}/pycrc/${cmd}`, (err, reference) =>
      callback(err, (reference || '').replace(/^0x|\n$/g, ''))
    );
  }
}

function testStringValue(
  crc: CRCModule,
  checkString: string,
  initial: number | undefined,
  expected: string | undefined,
  callback: Callback
) {
  getReferenceValueForString(crc.model, checkString, initial, expected, (err, reference) => {
    if (err) {
      callback(err);
    } else {
      crc(checkString, initial).toString(16).should.equal(reference);
      callback();
    }
  });
}

function testBufferValue(
  crc: CRCModule,
  buffer: Buffer,
  initial: number | undefined,
  expected: string | undefined,
  callback: Callback
) {
  getReferenceValueForBuffer(crc.model, buffer, initial, expected, (err, reference) => {
    if (err) {
      callback(err);
    } else {
      crc(buffer, initial).toString(16).should.equal(reference);
      callback();
    }
  });
}

function testStringSplitValue(
  crc: CRCModule,
  testValue: string,
  initial: number | undefined,
  expected: string | undefined,
  callback: Callback
) {
  const middle = testValue.length / 2;
  const chunk1 = testValue.substr(0, middle);
  const chunk2 = testValue.substr(middle);
  const v1 = crc(chunk1, initial);
  const v2 = crc(chunk2, v1);

  getReferenceValueForString(crc.model, testValue, initial, expected, (err, reference) => {
    if (err) {
      callback(err);
    } else {
      v2.toString(16).should.equal(reference);
      callback();
    }
  });
}

function testBufferSplitValue(
  crc: CRCModule,
  testValue: Buffer,
  initial: number | undefined,
  expected: string | undefined,
  callback: Callback
) {
  const middle = testValue.length / 2;
  const chunk1 = testValue.slice(0, middle);
  const chunk2 = testValue.slice(middle);
  const v1 = crc(chunk1, initial);
  const v2 = crc(chunk2, v1);

  getReferenceValueForBuffer(crc.model, testValue, initial, expected, (err, reference) => {
    if (err) {
      callback(err);
    } else {
      v2.toString(16).should.equal(reference);
      callback();
    }
  });
}

interface Params {
  crc: CRCModule;
  value?: string | Buffer;
  expected?: string;
  initial?: number;
}

export default function crcSuiteFor({ crc, value, expected, initial }: Params) {
  if (value) {
    if (Buffer.isBuffer(value)) {
      describe(`BUFFER: ${value.toString('base64')}`, () => {
        it('should calculate a full checksum', (done) =>
          testBufferValue(crc, value, initial, expected, done));
        it('should calculate a checksum for multiple data', (done) =>
          testBufferSplitValue(crc, value, initial, expected, done));
      });
    } else {
      describe(`STRING: ${value}`, () => {
        it('should calculate a full checksum', (done) =>
          testStringValue(crc, value, initial, expected, done));
        it('should calculate a checksum for multiple data', (done) =>
          testStringSplitValue(crc, value, initial, expected, done));
      });
    }
  } else {
    TEST_VALUES.forEach((testValue) =>
      describe(`STRING: ${testValue}`, () => {
        it('should calculate a full checksum', (done) =>
          testStringValue(crc, testValue, initial, expected, done));
        it('should calculate a full checksum with initial 0x0', (done) =>
          testStringValue(crc, testValue, 0, expected, done));
        it('should calculate a checksum for multiple data', (done) =>
          testStringSplitValue(crc, testValue, initial, expected, done));
        it('should calculate a checksum for multiple data with initial 0x0', (done) =>
          testStringSplitValue(crc, testValue, 0, expected, done));
      })
    );
  }
}
