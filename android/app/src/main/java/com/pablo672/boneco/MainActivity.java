package com.pablo672.boneco;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebSettings;
import android.widget.TextView;
import android.view.Gravity;

public class MainActivity extends Activity {
    // Troque pela URL HTTPS pública do servidor do Boneco antes de compilar.
    private static final String BONECO_PUBLIC_URL = "https://example.com/";

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        if (BONECO_PUBLIC_URL.equals("https://example.com/")) {
            TextView message = new TextView(this);
            message.setText("Boneco do Abismo\n\nConfigure BONECO_PUBLIC_URL em MainActivity.java com o endereço HTTPS do servidor e compile novamente.");
            message.setGravity(Gravity.CENTER);
            message.setPadding(32, 32, 32, 32);
            setContentView(message);
            return;
        }
        WebView web = new WebView(this);
        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        web.setWebViewClient(new WebViewClient());
        setContentView(web);
        web.loadUrl(BONECO_PUBLIC_URL);
    }
}
