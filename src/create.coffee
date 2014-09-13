module.exports = (calc) ->
  fn = (buf, previous) -> calc(buf, previous) >>> 0
  fn.signed = calc
  fn.unsigned = fn

  fn
