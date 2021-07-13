import fs from 'fs';
import chai from 'chai';
import { exec } from 'child_process';

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

function getReferenceValueForBuffer(model, buffer, initial, expected, callback) {
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

function getReferenceValueForString(model, string, initial, expected, callback) {
  if (expected) {
    callback(null, expected);
  } else {
    const initialArg = typeof initial !== 'undefined' ? `--xor-in=0x${initial.toString(16)}` : '';
    const cmd = `pycrc.py --model=${model} ${initialArg} --check-string="${string}"`;
    exec(`${__dirname}/pycrc/${cmd}`, (err, reference) => callback(err, (reference || '').replace(/^0x|\n$/g, '')));
  }
}

function testStringValue(crc, string, initial, expected, callback) {
  getReferenceValueForString(crc.model, string, initial, expected, (err, reference) => {
    if (err) {
      callback(err);
    } else {
      crc(string, initial)
        .toString(16)
        .should.equal(reference);
      callback();
    }
  });
}

function testBufferValue(crc, buffer, initial, expected, callback) {
  getReferenceValueForBuffer(crc.model, buffer, initial, expected, (err, reference) => {
    if (err) {
      callback(err);
    } else {
      crc(buffer, initial)
        .toString(16)
        .should.equal(reference);
      callback();
    }
  });
}

function testStringSplitValue(crc, value, initial, expected, callback) {
  const middle = value.length / 2;
  const chunk1 = value.substr(0, middle);
  const chunk2 = value.substr(middle);
  const v1 = crc(chunk1, initial);
  const v2 = crc(chunk2, v1);

  getReferenceValueForString(crc.model, value, initial, expected, (err, reference) => {
    if (err) {
      callback(err);
    } else {
      v2.toString(16).should.equal(reference);
      callback();
    }
  });
}

function testBufferSplitValue(crc, value, initial, expected, callback) {
  const middle = value.length / 2;
  const chunk1 = value.slice(0, middle);
  const chunk2 = value.slice(middle);
  const v1 = crc(chunk1, initial);
  const v2 = crc(chunk2, v1);

  getReferenceValueForBuffer(crc.model, value, initial, expected, (err, reference) => {
    if (err) {
      callback(err);
    } else {
      v2.toString(16).should.equal(reference);
      callback();
    }
  });
}

export default function crcSuiteFor({
  crc, value, expected, initial,
}) {
  if (value) {
    if (Buffer.isBuffer(value)) {
      describe(`BUFFER: ${value.toString('base64')}`, () => {
        it('should calculate a full checksum', (done) => testBufferValue(crc, value, initial, expected, done));
        it('should calculate a checksum for multiple data', (done) => testBufferSplitValue(crc, value, initial, expected, done));
      });
    } else {
      describe(`STRING: ${value}`, () => {
        it('should calculate a full checksum', (done) => testStringValue(crc, value, initial, expected, done));
        it('should calculate a checksum for multiple data', (done) => testStringSplitValue(crc, value, initial, expected, done));
      });
    }
  } else {
    TEST_VALUES.forEach((testValue) => describe(`STRING: ${testValue}`, () => {
      it('should calculate a full checksum', (done) => testStringValue(crc, testValue, initial, expected, done));
      it('should calculate a full checksum with initial 0x0', (done) => testStringValue(crc, testValue, 0, expected, done));
      it('should calculate a checksum for multiple data', (done) => testStringSplitValue(crc, testValue, initial, expected, done));
      it('should calculate a checksum for multiple data with initial 0x0', (done) => testStringSplitValue(crc, testValue, 0, expected, done));
    }));
  }
}
