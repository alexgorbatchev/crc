import { Buffer } from 'buffer';

export type BufferInput = string | ArrayBuffer | Uint8Array | Buffer | any[];

export interface CRCCalculator {
  (value: BufferInput, previous: number): number;
}

export interface CRCModule extends CRCCalculator {
  signed: CRCCalculator;
  unsigned: CRCCalculator;
  model: string;
}

export default function defineCrc(model: string, calculator: CRCCalculator) {
  const result: CRCModule = (value, previous) => calculator(value, previous) >>> 0;

  result.signed = calculator;
  result.unsigned = result;
  result.model = model;

  return result;
}
