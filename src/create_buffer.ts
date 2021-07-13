import { Buffer } from 'buffer';
import { BufferInput } from './define_crc';

const createBuffer =
  Buffer.hasOwnProperty('from') &&
  Buffer.hasOwnProperty('alloc') &&
  Buffer.hasOwnProperty('allocUnsafe') &&
  Buffer.hasOwnProperty('allocUnsafeSlow')
    ? (value: BufferInput) => Buffer.from(value as any)
    : // support for Node < 5.10
      // eslint-disable-next-line no-buffer-constructor
      (value: BufferInput) => new Buffer(value as any);

export default createBuffer;
