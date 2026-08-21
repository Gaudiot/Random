---

# 🎠 Carrossel — Internationalization in Flutter

---

# Slide 1 — What is it?

## Title

### **More Than Translating Text**

## Body

Internationalization (i18n) is making your app able to support many languages and regions.

But it goes way beyond words:

* time zones
* currency formats
* date and number formats
* images and icons that only make sense in one region

Some languages are written RTL (right to left) instead of the LTR we are used to in the west.

The whole layout gets mirrored, not just the text.

---

# Slide 2 — i18n vs l10n

## Title

### **i18n Is Not l10n**

## Body

Right next to i18n you will always see l10n, short for localization.

Both abbreviations are built the same way: i18n is an "i", 18 letters, then "n". That is why people mix them up, but they are different jobs.

(Visual element - scaffold)
i18n builds the scaffold that allows l10n to work as expected. Support RTL, price per region and etc.

(Visual element - office worker)
l10n is to adapt the content to a given region. Not only translation, but also which image fits best and date/time formats.

---

# Slide 3 — When they collide

## Title

### **When l10n Blocks The Release**

## Body

A bad i18n can block a release.

Imagine the company decides to support Arabic. The l10n team makes the required adjustments, but when the app is tested the layout is still rendered LTR instead of RTL.

The launch needs to be postponed until the developers add RTL support.

(Visual element - LTR and RTL)

Together the two jobs feed into g11n (globalization): the goal of expanding operations into new markets.

---

# Slide 4 — Do it early

## Title

### **Do it early**

## Body

i18n is mostly a one time cost. Once done, there is little maintenance.

Instead of `Text("Welcome")` you write `Text(t.welcome)`.

In English it renders "Welcome", in Portuguese "Bem-vindo".

Leaving it for later means hunting hardcoded strings, fixing layouts for RTL and replacing fixed icons across the whole codebase.

It becomes technical debt fast the day the CEO decides the product launches in Germany, Japan and Russia next semester.

(Visual element - Phone with search icon over it)

---

# Slide 5 — Flutter setup

## Title

### **Flutter setup**

## Body

The Flutter team has official docs on this. Here is the short path.

Add the dependencies:

`flutter pub add flutter_localizations --sdk=flutter`

`flutter pub add intl:any`

In `pubspec.yaml`, add `generate: true` under the `flutter` property.

Not required, but strongly recommended: create an `l10n.yaml` at the project root. This is the template I use and like:

```yaml
arb-dir: lib/l10n
output-dir: lib/l10n/output
template-arb-file: app_en.arb
output-localization-file: app_localizations.dart
untranslated-messages-file: lib/l10n/output/untranslated_messages.txt
```

---

# Slide 6 — What comes for free

## Title

### **Localization You Get For Free**

## Body

By default Flutter only ships American English.

Adding `flutter_localizations` translates the framework's own widgets for you, from the date picker to the dialog buttons, without writing a single translation.

The global delegates do the work:

* `GlobalWidgetsLocalizations.delegate` → sets the text direction, and this is what mirrors the layout for RTL

* `GlobalMaterialLocalizations.delegate` and `GlobalCupertinoLocalizations.delegate` → provides the framework strings

All of it arrives with the dependency.

---

# Slide 7 — The .arb files

## Title

### **Where The Strings Live**

## Body

`.arb` files store your strings and live in `lib/l10n`, one file per language.

The name follows `app_{ct}.arb`, where ct is the ISO2 code:

* app_en.arb
* app_pt.arb
* app_fr.arb

They look a lot like JSON:

```json
{
  "@@locale": "en",
  "helloWorld": "Hello World!",
  "@helloWorld": {
    "description": "The conventional newborn programmer greeting"
  }
}
```

The `@key` block is only a description. Not mandatory, but Flutter warns when it is missing.

Keep keys declarative and follow a convention so two of them never map to the same sentence.

---

# Slide 8 — Regional variants

## Title

### **Going Beyond The Language Code**

## Body

Brazil's Portuguese is different from Portugal's. Although they have the same language code, your app needs to reflect the nuances.

It's possible to do this through an `.arb` file with a given country code, although Flutter requires a base file for the language.

* `app_pt.arb` → the base, mandatory
* `app_pt_PT.arb` → the regional variation

Same idea on the English side:

* `app_en.arb`
* `app_en_GB.arb`

The variation only needs the keys that actually change. The rest falls back to the base file.

---

# Slide 9 — Strings outside the code

## Title

### **Copy Without A Developer**

## Body

The strings live in resource files, separate from the product code. They can be imported and exported without touching the codebase.

Which means:

* A translator works straight on the file
* Someone from product can fix the wording
* No developer needed for a copy change
* No risk of breaking the app while editing text

The code keeps calling the same key. Only the value changes.

(Visual Element - File updating)

---

# Slide 10 — Generate and wire

## Title

### **Plugging It Into The App**

## Body

Run `flutter gen-l10n` to turn the `.arb` files into Dart.

→ missing keys get reported in `untranslated_messages.txt`.

Now update the `MaterialApp` in `main.dart`.

Then use it inside any widget:

`Text(AppLocalizations.of(context)!.helloWorld)`

---

# Slide 11 — Placeholders

## Title

### **Strings With Placeholders**

## Body

Static text is only the beginning. Strings can also carry dynamic values.

Useful for any sentence that includes user data, like greeting someone by name.

```json
"hello": "Hello {userName}",
"@hello": {
  "description": "A message with a single parameter",
  "placeholders": {
    "userName": {
      "type": "String",
      "example": "Bob"
    }
  }
}
```

Every placeholder is declared inside the `@key` block with its `type`.

The generated method takes the value:

`AppLocalizations.of(context)!.hello("Bob")`

* en → "Hello Bob"
* pt → "Olá Bob"

---

# Slide 12 — Plurals

## Title

### **Singular And Plural**

## Body

Useful when the sentence changes with a count, and every language pluralizes in its own way.

```json
"nWombats": "{count, plural, =0{no wombats} =1{1 wombat} other{{count} wombats}}",
"@nWombats": {
  "description": "A plural message",
  "placeholders": {
    "count": {
      "type": "num",
      "format": "compact"
    }
  }
}
```

On screen:

* `nWombats(0)` → "no wombats"
* `nWombats(1)` → "1 wombat"
* `nWombats(2)` → "2 wombats"

→ one key handles every case, so no conditionals in the widget.

---

# Slide 13 — Select

## Title

### **Matching On A Value**

## Body

`select` picks a branch based on a string.

Useful for sentences that change with the gender of the user, or any other closed set of options.

```json
"pronoun": "{gender, select, male{he} female{she} other{they}}",
"@pronoun": {
  "description": "A gendered message",
  "placeholders": {
    "gender": {
      "type": "String"
    }
  }
}
```

On screen:

* `pronoun("male")` → "he"
* `pronoun("female")` → "she"
* `pronoun("unknown")` → "they"
* `pronoun("Male")` → "they"

That last one is the gotcha: the match is case sensitive, so `"Male"` never hits the `male` branch.

Anything that does not match a branch falls into `other`, so always keep it as the fallback.

---

# Slide 14 — Numbers and currency

## Title

### **Numbers And Currency**

## Body

Useful for prices and metrics, since each region writes the same number differently.

```json
"numberOfDataPoints": "Number of data points: {value}",
"@numberOfDataPoints": {
  "description": "A message with a formatted int parameter",
  "placeholders": {
    "value": {
      "type": "int",
      "format": "compactCurrency",
      "optionalParameters": {
        "decimalDigits": 2
      }
    }
  }
}
```

On screen:

* `numberOfDataPoints(1234567)` → "Number of data points: $1.23M"

The separators flip by locale too. The same plain decimal:

* en-US → `1,234.56`
* pt-BR → `1.234,56`

The `format` does the heavy lifting. There are many available, so check the docs for the one that fits you.

---

# Slide 15 — Dates

## Title

### **Formatting Dates**

## Body

Useful because the same date is written in a different order depending on the region.

```json
"helloWorldOn": "Hello World on {date}",
"@helloWorldOn": {
  "description": "A message with a date parameter",
  "placeholders": {
    "date": {
      "type": "DateTime",
      "format": "yMd"
    }
  }
}
```

On screen, `DateTime(2026, 7, 14)` with `yMd`:

* en-US → `7/14/2026`
* pt-BR → `14/07/2026`
* ru-RU → `14.07.2026`

→ you pass a `DateTime` and the `format` renders it per locale.

---

# Slide 16 — The forgotten step

## Title

### **Don't Forget iOS**

## Body

Flutter handles the localization, but iOS also needs the supported languages declared in the app bundle so they show correctly on the App Store.

* open `ios/Runner.xcodeproj` in Xcode
* select Runner and open the "Info" tab in the project editor
* in the localizations section click "Add" (or "+") and add your languages
* when asked to choose reference files, just hit "Finish"

Xcode generates an empty `.strings` and updates what it needs.

The takeaway: i18n is a small cost today and a huge refactor tomorrow. The tooling is good now, so do it early.
