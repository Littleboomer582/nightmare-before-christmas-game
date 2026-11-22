package android.webkit;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * Compile-time stand-in for the framework annotation (added in API 17, newer than the API stubs we
 * compile against). It is only on the javac classpath; the real one comes from the phone at runtime.
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface JavascriptInterface {
}
