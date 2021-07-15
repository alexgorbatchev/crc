import { Buffer } from 'buffer';
import { BufferInput } from './types';

const createBuffer =
  Buffer.hasOwnProperty('from') &&
  Buffer.hasOwnProperty('alloc') &&
  Buffer.hasOwnProperty('allocUnsafe') &&
  Buffer.hasOwnProperty('allocUnsafeSlow')
    ? (value: BufferInput, encoding?: BufferEncoding) => Buffer.from(value as any, encoding)
    : // support for Node < 5.10
      // eslint-disable-next-line no-buffer-constructor
      (value: BufferInput, encoding?: BufferEncoding) => new Buffer(value as any, encoding);

export default createBuffer;
