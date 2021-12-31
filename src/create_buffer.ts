/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable no-prototype-builtins */
import { Buffer } from 'buffer';
import { BufferInput } from './types.js';

const createBuffer = (value: BufferInput, encoding?: BufferEncoding) =>
  Buffer.from(value as any, encoding);

export default createBuffer;
