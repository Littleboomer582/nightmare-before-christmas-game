package com.deadenddepot.zombies;

import android.app.Activity;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.provider.OpenableColumns;
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

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
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
    private static final int PICK_MUSIC = 7;

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

    // The player chose a song for the menu: copy it into the app's private files and hand the game its path.
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != PICK_MUSIC || resultCode != RESULT_OK || data == null || data.getData() == null) return;
        final Uri uri = data.getData();
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    String name = "Your song";
                    Cursor c = getContentResolver().query(uri, null, null, null, null);
                    if (c != null) {
                        int col = c.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                        if (col >= 0 && c.moveToFirst() && c.getString(col) != null) name = c.getString(col);
                        c.close();
                    }
                    String ext = ".mp3";
                    int dot = name.lastIndexOf('.');
                    if (dot > 0 && name.length() - dot <= 5) ext = name.substring(dot).toLowerCase();
                    File dir = getFilesDir();
                    File[] old = dir.listFiles();
                    if (old != null) for (File f : old) if (f.getName().startsWith("menu-music")) f.delete();
                    File out = new File(dir, "menu-music" + ext);
                    InputStream in = getContentResolver().openInputStream(uri);
                    if (in == null) return;
                    OutputStream os = new FileOutputStream(out);
                    byte[] buf = new byte[65536];
                    long total = 0;
                    int n;
                    while ((n = in.read(buf)) > 0 && total < 80L * 1024 * 1024) { os.write(buf, 0, n); total += n; }
                    in.close();
                    os.close();
                    final String js = "javascript:window.onMenuMusicPicked && onMenuMusicPicked("
                        + jsString("file://" + out.getAbsolutePath()) + "," + jsString(name) + ")";
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() { web.loadUrl(js); }
                    });
                } catch (Exception ignored) { }
            }
        }).start();
    }

    // A JavaScript string literal for a javascript: URL: anything but plain letters, digits and a few
    // path characters is written as a backslash-u escape, so names with quotes, % or # can't break out.
    private static String jsString(String s) {
        StringBuilder b = new StringBuilder("'");
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if ((ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || (ch >= '0' && ch <= '9') || ch == '/' || ch == '.' || ch == '-' || ch == '_' || ch == ':') b.append(ch);
            else b.append(String.format("\\u%04x", (int) ch));
        }
        return b.append('\'').toString();
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
        public void pickMenuMusic() {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    Intent i = new Intent(Intent.ACTION_GET_CONTENT);
                    i.setType("audio/*");
                    i.addCategory(Intent.CATEGORY_OPENABLE);
                    try { startActivityForResult(Intent.createChooser(i, "Choose menu music"), PICK_MUSIC); } catch (Exception ignored) { }
                }
            });
        }

        @JavascriptInterface
        public void stopSpeaking() {
            if (tts != null) tts.stop();
        }
    }
}
