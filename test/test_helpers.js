import fs from 'fs';
import chai from 'chai';
import { exec } from 'child_process';

const VALUES = [
  '1234567890',
  'cwd String Current working directory of the child process',
  'env Object Environment key-value pairs',
  "encoding String (Default: 'utf8')",
  'timeout Number (Default: 0)',
  'maxBuffer Number (Default: 200*1024)',
  "killSignal String (Default: 'SIGTERM')",
];

chai.should();

export default function crcSuiteFor({ crc, value, expected, initial }) {
  function getReferenceValueForBuffer(model, buffer, initial, callback) {
    if (expected) return callback(null, expected);

    const filename = `${__dirname}/tmp`;
    fs.writeFileSync(filename, buffer);
    initial = typeof initial !== 'undefined' ? `--xor-in=0x${initial.toString(16)}` : '';
    exec(
      `${__dirname}/pycrc/pycrc.py --model=${model} ${initial} --check-file="${filename}"`,
      function(err, reference) {
        fs.unlinkSync(filename);
        callback(err, (reference || '').replace(/^0x|\n$/g, ''));
      }
    );
  }

  function getReferenceValueForString(model, string, initial, callback) {
    if (expected) return callback(null, expected);

    initial = typeof initial !== 'undefined' ? `--xor-in=0x${initial.toString(16)}` : '';
    exec(
      `${__dirname}/pycrc/pycrc.py --model=${model} ${initial} --check-string="${string}"`,
      function(err, reference) {
        callback(err, (reference || '').replace(/^0x|\n$/g, ''));
      }
    );
  }

  function testStringValue(string, initial, callback) {
    getReferenceValueForString(crc.model, string, initial, function(err, reference) {
      if (err) return callback(err);
      crc(string, initial)
        .toString(16)
        .should.equal(reference);
      callback();
    });
  }

  function testBufferValue(buffer, initial, callback) {
    getReferenceValueForBuffer(crc.model, buffer, initial, function(err, reference) {
      if (err) return callback(err);
      crc(buffer, initial)
        .toString(16)
        .should.equal(reference);
      callback();
    });
  }

  function testStringSplitValue(value, initial, callback) {
    const middle = value.length / 2;
    const chunk1 = value.substr(0, middle);
    const chunk2 = value.substr(middle);
    const v1 = crc(chunk1, initial);
    const v2 = crc(chunk2, v1);

    getReferenceValueForString(crc.model, value, initial, function(err, reference) {
      if (err) return callback(err);
      v2.toString(16).should.equal(reference);
      callback();
    });
  }

  function testBufferSplitValue(value, initial, callback) {
    const middle = value.length / 2;
    const chunk1 = value.slice(0, middle);
    const chunk2 = value.slice(middle);
    const v1 = crc(chunk1, initial);
    const v2 = crc(chunk2, v1);

    getReferenceValueForBuffer(crc.model, value, initial, function(err, reference) {
      if (err) return callback(err);
      v2.toString(16).should.equal(reference);
      callback();
    });
  }

  if (value) {
    if (Buffer.isBuffer(value)) {
      describe(`BUFFER: ${value.toString('base64')}`, function() {
        it('should calculate a full checksum', done => testBufferValue(value, initial, done));
        it('should calculate a checksum for multiple data', done =>
          testBufferSplitValue(value, initial, done));
      });
    } else {
      describe(`STRING: ${value}`, function() {
        it('should calculate a full checksum', done => testStringValue(value, initial, done));
        it('should calculate a checksum for multiple data', done =>
          testStringSplitValue(value, initial, done));
      });
    }
  } else {
    VALUES.forEach(value =>
      describe(`STRING: ${value}`, function() {
        it('should calculate a full checksum', done => testStringValue(value, initial, done));
        it('should calculate a full checksum with initial 0x0', done =>
          testStringValue(value, 0, done));
        it('should calculate a checksum for multiple data', done =>
          testStringSplitValue(value, initial, done));
        it('should calculate a checksum for multiple data with initial 0x0', done =>
          testStringSplitValue(value, 0, done));
      })
    );
  }
}
