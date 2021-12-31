import createBuffer from './create_buffer.js';
import { CRCCalculator, CRCModule } from './types.js';

export default function defineCrc(model: string, calculator: CRCCalculator<Uint8Array>): CRCModule {
  const result: CRCModule = (value, previous) => calculator(createBuffer(value), previous) >>> 0;

  result.signed = (value, previous) => calculator(createBuffer(value), previous);
  result.unsigned = result;
  result.model = model;

  return result;
}
