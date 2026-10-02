function execute(dynamicCode: string, token: string) {
  // ruleid: react-native.code.eval-with-dynamic-data
  eval(dynamicCode);
  // ruleid: react-native.code.sensitive-console-logging
  console.log(token);
}

function customEncrypt(value: number, key: number) {
  // ruleid: react-native.code.custom-xor-cryptography
  return value ^ key;
}
