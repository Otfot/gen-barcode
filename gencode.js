const { createCanvas, registerFont } = require("canvas")
const jsbarcode = require("jsbarcode")
const fs = require("fs")

registerFont("DejaVuSansMono.ttf", { family: "DejaVu Sans Mono" })

function gen_code128_number(num, bit) {
    var numArray = new Array(num)
  arr = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

  for (var i = 0; i < num; i++) {
    let str = ""
    for (var j = 0; j < bit; j++) {
      pos = Math.round(Math.random() * (arr.length - 1))
      str += arr[pos]
    }
    numArray[i] = str
    // console.log(numArray[i]);
  }
  return numArray
}

function checksum(str) {
  var c1 = 0
  var c2 = 0

  for (var i = 0; i < str.length; i += 2) {
    var c = str.charAt(i)
    var n = c - "0"
    c1 += n
  }

  for (var i = 1; i < str.length; i += 2) {
    var c = str.charAt(i)
    var n = c - "0"
    c2 += n
  }

  var cc = c1 + c2 * 3
  var check = cc % 10
  check = (10 - (cc % 10)) % 10
  return check
}
function gen_ean13_number(num, bit) {
  var numArray = new Array(num)
  arr = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
  for (var i = 0; i < num; i++) {
    let str = ""
    for (var j = 0; j < bit - 1; j++) {
      pos = Math.round(Math.random() * (arr.length - 1))
      str += arr[pos]
    }
    // console.log(str)
    var code = checksum(str)
    console.log("code:" + code)
    numArray[i] = str + code
  }
  return numArray
}

function gen(num, bit, style_option) {
  num = Number(num)
  bit = Number(bit)
  if (style_option["format"] == "code128") {
    var numArray = gen_code128_number(num, bit)
  }
  if (style_option["format"] == "EAN13") {
    var numArray = gen_ean13_number(num, bit)
  }
  for (var i = 0; i < num; i++) {
    var canvas = createCanvas()
    jsbarcode(canvas, numArray[i], style_option)
    var out = fs.createWriteStream(__dirname + "/raw/" + numArray[i] + ".png")
    var stream = canvas.createPNGStream()
    stream.pipe(out)
  }
}
