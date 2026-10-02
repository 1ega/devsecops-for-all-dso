/* Output sample:
 *     Alert_Name	Source:PluginName	WASC	CWE
 *     Cross Site Scripting (DOM Based)	ACTIVE:Cross Site Scripting (DOM Based)	8	79
 *     Non-Storable Content	PASSIVE:Content Cacheability	13	524
 * It's tab separated so you can simply copy/paste it into Excel (or whatever).
 */

var ExtensionAlert = Java.type(
  "org.zaproxy.zap.extension.alert.ExtensionAlert"
);
var ExtensionPassiveScan2 = Java.type(
  "org.zaproxy.addon.pscan.ExtensionPassiveScan2"
);
var Alert = Java.type("org.parosproxy.paros.core.scanner.Alert");
var pf = Java.type("org.parosproxy.paros.core.scanner.PluginFactory");

extAlert = control.getExtensionLoader().getExtension(ExtensionAlert.NAME);

extPscan = control
  .getExtensionLoader()
  .getExtension(ExtensionPassiveScan2.NAME);

printHeaders();

if (extAlert != null) {
  var alerts = extAlert.getAllAlerts();
  for (var i = 0; i < alerts.length; i++) {
    var alert = alerts[i];
    printAlert(alert);
  }
}

function printHeaders() {
  print("AlertName\tSource:PluginName\tWASC\tCWE");
}

function printAlert(alert) {
  var scanner = "";

  // If the session is loaded in ZAP and one of the extensions that provided a plugin for the
  // existing alerts is missing then plugin (below) will be null, and hence scanner will end-up being empty

  if (alert.getSource() == Alert.Source.ACTIVE) {
    var plugin = pf.getLoadedPlugin(alert.getPluginId());
    if (plugin != null) {
      scanner = plugin.getName();
    }
  }
  if (alert.getSource() == Alert.Source.PASSIVE && extPscan != null) {
    plugin = extPscan
      .getPassiveScannersManager()
      .getScanRule(alert.getPluginId());
    if (plugin != null) {
      scanner = plugin.getName();
    }
  }
  print(
    alert.getName() +
      "\t" +
      alert.getSource() +
      ":" +
      scanner +
      "\t" +
      alert.getWascId() +
      "\t" +
      alert.getCweId()
  );
  // For more alert properties see https://static.javadoc.io/org.zaproxy/zap/latest/org/parosproxy/paros/core/scanner/Alert.html
}
