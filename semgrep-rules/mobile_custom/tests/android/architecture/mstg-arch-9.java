// ruleid: MSTG-ARCH-9
public class SplashScreen extends AppCompatActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        test();
    }
    private void test(){
        //AppUpdateManager appUpdateManager = AppUpdateManagerFactory.create(context);
        //appUpdateManager.startUpdateFlowForResult(appUpdateInfo,AppUpdateType.IMMEDIATE,this,MY_REQUEST_CODE);
    }
}
// ok: MSTG-ARCH-9
public class SplashScreen extends AppCompatActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        test();
    }
    private void test(){
        AppUpdateManager appUpdateManager = AppUpdateManagerFactory.create(context);
        appUpdateManager.startUpdateFlowForResult(appUpdateInfo,AppUpdateType.IMMEDIATE,this,MY_REQUEST_CODE);
    }
 
}
// ruleid: MSTG-ARCH-9
public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }
}
// ok: MSTG-ARCH-9
public class LauncherActivity extends AppCompatActivity {
    private AppUpdateManager appUpdateManager;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        appUpdateManager = AppUpdateManagerFactory.create(this);
        checkForUpdate();
    }
    private void checkForUpdate() {
        appUpdateManager.startUpdateFlowForResult(appUpdateInfo, activityResultLauncher, AppUpdateOptions.defaultOptions(AppUpdateType.IMMEDIATE));
    }
}
// ok: MSTG-ARCH-9
public class Helper extends Object {
    public void onCreate(Bundle b) {
    }
}
