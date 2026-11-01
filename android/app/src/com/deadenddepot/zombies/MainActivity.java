package com.deadenddepot.zombies;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.util.HashMap;
import java.util.Locale;

/**
 * Runs the game full-screen in landscape. The whole game ships inside the APK's assets
 * (index.html, three.min.js and the fonts), so it plays offline.
 */
public class MainActivity extends Activity {
    // SYSTEM_UI_FLAG_IMMERSIVE_STICKY | FULLSCREEN | HIDE_NAVIGATION | LAYOUT_STABLE | LAYOUT_HIDE_NAVIGATION | LAYOUT_FULLSCREEN
    private static final int IMMERSIVE = 0x1000 | 0x0004 | 0x0002 | 0x0100 | 0x0200 | 0x0400;
    private WebView web;
    private TextToSpeech tts;           // the phone's speech engine, for the survivor's quotes
    private volatile boolean ttsReady;

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
        tts = new TextToSpeech(this, new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int status) {
                if (status != TextToSpeech.SUCCESS) return;
                int lang = tts.setLanguage(Locale.US);
                ttsReady = lang != TextToSpeech.LANG_MISSING_DATA && lang != TextToSpeech.LANG_NOT_SUPPORTED;
            }
        });
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
        if (tts != null) tts.stop();
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
        if (tts != null) tts.shutdown();
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

        @JavascriptInterface
        @SuppressWarnings("deprecation")   // the HashMap form works on every Android version we support
        public void speak(String text, float pitch, float rate, float volume) {
            if (!ttsReady || text == null) return;
            tts.setPitch(pitch);
            tts.setSpeechRate(rate);
            HashMap<String, String> params = new HashMap<String, String>();
            params.put(TextToSpeech.Engine.KEY_PARAM_VOLUME, String.valueOf(volume));
            tts.speak(text, TextToSpeech.QUEUE_FLUSH, params);
        }

        @JavascriptInterface
        public void stopSpeaking() {
            if (tts != null) tts.stop();
        }
    }
}
