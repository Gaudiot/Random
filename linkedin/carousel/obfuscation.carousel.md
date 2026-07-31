---

# 🎠 Carousel — Code Obfuscation

---

# Slide 1 — What is it?

## Title

### **What Is Code Obfuscation?**

## Body

Code obfuscation makes software harder for humans to understand without changing its behavior.

It is not the same as encryption.

Encryption transforms data into an unreadable format and requires a key to restore it.

Obfuscated code remains executable—it is simply harder to inspect and understand.

Simplified example:

```dart
// Original code
int addNumbers(int left, int right) {
  int sum = left + right;
  return sum;
}

// Simplified obfuscated code
int a(int b, int c) {
  int d = b + c;
  return d;
}
```

The behavior stays the same.

The meaning becomes less obvious.

---

# Slide 2 — Why use it in production?

## Title

### **Why Use It in Production?**

## Body

Once an application is distributed, attackers can inspect its compiled binary and try to understand its internal behavior.

Obfuscation can help:

* make reverse engineering more difficult
* protect proprietary business logic
* discourage tampering and client-side abuse
* increase the time and effort required to analyze the app

It is especially relevant for applications containing valuable algorithms, subscription rules, financial logic, or other business-critical behavior.

Obfuscation does not make reverse engineering impossible.

It makes it more expensive.

---

# Slide 3 — Hidden malware

## Title

### **The Dark Side: Hidden Malware**

## Body

Obfuscation is only a tool—and it can also be used maliciously.

Malware authors use it to:

* conceal malicious behavior
* hide suspicious URLs and commands
* evade automated security analysis
* make app-store reviews more difficult
* embed malicious payloads inside apparently harmless files

For example, an obfuscated JavaScript file may reconstruct a malicious URL or download additional code at runtime.

Heavily obfuscated code is not automatically malicious.

But it can make malicious behavior significantly harder to detect and analyze.

---

# Slide 4 — Flutter

## Title

### **How To Use It in Flutter**

## Body

Flutter supports Dart code obfuscation in release builds.

For Android:

```bash
flutter build appbundle --obfuscate \
  --split-debug-info=build/symbols/android
```

For iOS:

```bash
flutter build ipa --obfuscate \
  --split-debug-info=build/symbols/ios
```

The `--obfuscate` flag renames Dart symbols.

The `--split-debug-info` flag generates symbol files required to interpret production crash reports.

Keep those files safe and separated for every release.

Without the matching symbols, production stack traces may remain unreadable.

---

# Slide 5 — Limitations

## Title

### **It’s Not Enough**

## Body

Obfuscation should be treated as one layer of defense—not as the application’s entire security model.

Combine it with:

* server-side validation
* secure secret management
* proper authentication and authorization
* integrity and tampering protections
* secure architecture

Obfuscation does not safely protect hardcoded API keys, credentials, or sensitive client-side decisions.

Make attacks harder.

But never assume the client can be trusted.
