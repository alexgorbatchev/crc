import { Buffer } from 'buffer';

export type BufferInput = string | ArrayBuffer | Buffer | any[];

export interface CRCCalculator<T = BufferInput | Uint8Array> {
  (value: T, previous: number): number;
}

export interface CRCModule extends CRCCalculator<BufferInput> {
  signed: CRCCalculator<BufferInput>;
  unsigned: CRCCalculator<BufferInput>;
  model: string;
}
