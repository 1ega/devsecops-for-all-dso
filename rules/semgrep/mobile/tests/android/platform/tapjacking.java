// ruleid:android.mobsf.android_detect_tapjacking
webView.getView().setFilterTouchesWhenObscured(true);
    super.initialize(cordova, webView);
    Activity activity = this.cordova.getActivity();