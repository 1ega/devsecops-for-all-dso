// This script gives details about all of the scan rules installed

var ExtensionActiveScan = Java.type(
  "org.zaproxy.zap.extension.ascan.ExtensionActiveScan"
);
var ExtensionPassiveScan2 = Java.type(
  "org.zaproxy.addon.pscan.ExtensionPassiveScan2"
);

extAscan = control.getExtensionLoader().getExtension(ExtensionActiveScan.NAME);

plugins = extAscan
  .getPolicyManager()
  .getDefaultScanPolicy()
  .getPluginFactory()
  .getAllPlugin()
  .toArray();

print("Plugin ID\tName\tType\tStatus");
for (var i = 0; i < plugins.length; i++) {
  try {
    print(
      plugins[i].getId() +
        "\t" +
        plugins[i].getName() +
        "\tActive" +
        "\t" +
        plugins[i].getStatus()
    );
  } catch (e) {
    print(e);
  }
}

extPscan = control
  .getExtensionLoader()
  .getExtension(ExtensionPassiveScan2.NAME);

plugins = extPscan.getPassiveScannersManager().getScanRules();

for (var i = 0; i < plugins.length; i++) {
  try {
    print(
      plugins[i].getPluginId() +
        "\t" +
        plugins[i].getName() +
        "\tPassive" +
        "\t" +
        plugins[i].getStatus()
    );
  } catch (e) {
    print(e);
  }
}
