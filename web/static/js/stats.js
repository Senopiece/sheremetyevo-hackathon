function priceSorter(a, b) {
    var aa = a.replace('₽', '').replace('+', '')
    var bb = b.replace('₽', '').replace('+', '')
    return aa - bb
  }