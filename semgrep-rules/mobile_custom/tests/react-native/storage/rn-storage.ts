async function unsafeStorage(token: string, pii: string) {
  // ruleid: react-native.storage.asyncstorage-sensitive-data
  await AsyncStorage.setItem("auth_token", token);
  // ruleid: react-native.storage.asyncstorage-pii
  await AsyncStorage.setItem("user_email", pii);

  // ruleid: react-native.storage.redux-persist-unencrypted
  const persistConfig = {key: "auth", storage: AsyncStorage};
  // ruleid: react-native.storage.mmkv-without-encryption-key
  const secureCache = new MMKV({id: "auth-session"});
  // ruleid: react-native.storage.realm-without-encryption-key
  const realm = await Realm.open({schema: UserAuthSchema});
  // ruleid: react-native.storage.expo-secure-store-weak-accessibility
  await SecureStore.setItemAsync("token", token, {keychainAccessible: SecureStore.ALWAYS});
  const password = token;
  // ruleid: react-native.storage.sensitive-clipboard-write
  Clipboard.setString(password);
}
