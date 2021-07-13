export default function defineCrc(model, calc) {
  const fn = (value, previous) => calc(value, previous) >>> 0;
  fn.signed = calc;
  fn.unsigned = fn;
  fn.model = model;

  return fn;
}
