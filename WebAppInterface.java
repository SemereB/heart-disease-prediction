//WebAppInterface.java
package com.infoscience.hdp;

import android.content.Context;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;
import android.widget.Toast;

public class WebAppInterface {
    private Context mContext;

    /** Instantiate the interface and set the context */
    public WebAppInterface(Context c) {
        mContext = c;
    }

    /** Show a toast from the web page */
    @JavascriptInterface
    public void showToast(String toast) {
        Toast.makeText(mContext, toast, Toast.LENGTH_SHORT).show();
    }

    /** Get some data from Android */
    @JavascriptInterface
    public String getData() {
        return "Data from Android at " + System.currentTimeMillis();
    }

    /** Call JavaScript function from Android */
    public void callJavaScriptFunction(WebView webView, String message) {
        final String jsCode = String.format("javascript:updateMessage('%s')", message);
        webView.post(() -> webView.evaluateJavascript(jsCode, null));
    }
}