package com.deadenddepot.zombies;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/**
 * Runs the game full-screen in landscape. The whole game ships inside the APK's assets
 * (index.html, three.min.js and the fonts), so it plays offline.
 */
public class MainActivity extends Activity {
    // SYSTEM_UI_FLAG_IMMERSIVE_STICKY | FULLSCREEN | HIDE_NAVIGATION | LAYOUT_STABLE | LAYOUT_HIDE_NAVIGATION | LAYOUT_FULLSCREEN
    private static final int IMMERSIVE = 0x1000 | 0x0004 | 0x0002 | 0x0100 | 0x0200 | 0x0400;
    private WebView web;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        Window w = getWindow();
        w.addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN | WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        try {   // draw behind the camera notch (API 28+), looked up by name so older phones skip it
            WindowManager.LayoutParams lp = w.getAttributes();
            lp.getClass().getField("layoutInDisplayCutoutMode").setInt(lp, 1);
            w.setAttributes(lp);
        } catch (Exception ignored) { }

        web = new WebView(this);
        web.setBackgroundColor(Color.BLACK);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);          // settings, leaderboards and restarts use web storage
        s.setAllowFileAccess(true);
        s.setAllowFileAccessFromFileURLs(true);
        try {   // let menu music and sound start without an extra tap (API 17+)
            s.getClass().getMethod("setMediaPlaybackRequiresUserGesture", boolean.class).invoke(s, false);
        } catch (Exception ignored) { }
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient());
        web.addJavascriptInterface(new Bridge(), "AndroidApp");
        setContentView(web);
        hideSystemUi();
        web.loadUrl("file:///android_asset/index.html");
    }

    private void hideSystemUi() {
        web.setSystemUiVisibility(IMMERSIVE);
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) hideSystemUi();
    }

    @Override
    public void onBackPressed() {
        // The game decides: pause during play, step back through menus, exit from the title screen.
        web.loadUrl("javascript:window.androidBack ? androidBack() : AndroidApp.exit()");
    }

    @Override
    protected void onPause() {
        web.loadUrl("javascript:window.onAppPause && onAppPause()");
        web.onPause();
        super.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
        hideSystemUi();
        web.loadUrl("javascript:window.onAppResume && onAppResume()");
    }

    @Override
    protected void onDestroy() {
        web.destroy();
        super.onDestroy();
    }

    /** Called from the game's JavaScript as window.AndroidApp. */
    public class Bridge {
        @JavascriptInterface
        public void exit() {
            runOnUiThread(new Runnable() {
                @Override
                public void run() { finish(); }
            });
        }
    }
}
