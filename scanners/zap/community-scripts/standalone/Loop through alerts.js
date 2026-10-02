// This script loops through all of the alerts - change it to do whatever you want to do :)
//
// This is a standalone script which you can run from the Script Console

var ExtensionAlert = Java.type(
  "org.zaproxy.zap.extension.alert.ExtensionAlert"
);
var Alert = Java.type("org.parosproxy.paros.core.scanner.Alert");

extAlert = control.getExtensionLoader().getExtension(ExtensionAlert.NAME);
if (extAlert != null) {
  var alerts = extAlert.getAllAlerts();
  for (var i = 0; i < alerts.length; i++) {
    var alert = alerts[i];
    print(alert.uri);
    print("\tName:\t" + alert.name);
    print("\tRisk:\t" + Alert.MSG_RISK[alert.risk]);
    print("\tConfidence:\t" + Alert.MSG_CONFIDENCE[alert.confidence]);
    // For more alert properties see https://static.javadoc.io/org.zaproxy/zap/latest/org/parosproxy/paros/core/scanner/Alert.html
  }
}
