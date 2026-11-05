import com.android.apksig.ApkSigner;
import com.android.apksig.ApkVerifier;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.security.KeyStore;
import java.security.PrivateKey;
import java.security.cert.X509Certificate;
import java.util.Collections;

/**
 * Signs an APK with APK Signature Scheme v2 using Google's apksig library, then verifies the result
 * the way an Android device would. The app needs Android 7.0+ (API 24), which checks v2, so the
 * legacy v1 JAR signature is left off (this apksig release's v1 signer relies on JDK internals that
 * modern Java removed).
 *
 *   java -cp apksig.jar:. Sign <keystore.p12> <password> <alias> <unsigned.apk> <signed.apk> <minSdk>
 */
public class Sign {
    public static void main(String[] args) throws Exception {
        KeyStore ks = KeyStore.getInstance("PKCS12");
        try (InputStream in = new FileInputStream(args[0])) { ks.load(in, args[1].toCharArray()); }
        PrivateKey key = (PrivateKey) ks.getKey(args[2], args[1].toCharArray());
        X509Certificate cert = (X509Certificate) ks.getCertificate(args[2]);
        int minSdk = Integer.parseInt(args[5]);

        ApkSigner.SignerConfig signer = new ApkSigner.SignerConfig.Builder("CERT", key, Collections.singletonList(cert)).build();
        new ApkSigner.Builder(Collections.singletonList(signer))
                .setInputApk(new File(args[3]))
                .setOutputApk(new File(args[4]))
                .setMinSdkVersion(minSdk)
                .setV1SigningEnabled(false)
                .setV2SigningEnabled(true)
                .setCreatedBy("Dead End Depot build")
                .build()
                .sign();

        ApkVerifier.Result r = new ApkVerifier.Builder(new File(args[4])).setMinCheckedPlatformVersion(minSdk).build().verify();
        for (ApkVerifier.IssueWithParams e : r.getErrors()) System.out.println("ERROR " + e);
        for (ApkVerifier.IssueWithParams w : r.getWarnings()) System.out.println("WARNING " + w);
        System.out.println("verified=" + r.isVerified() + " v1=" + r.isVerifiedUsingV1Scheme() + " v2=" + r.isVerifiedUsingV2Scheme()
                + " signer=" + r.getSignerCertificates().get(0).getSubjectX500Principal());
        if (!r.isVerified()) System.exit(1);
    }
}
