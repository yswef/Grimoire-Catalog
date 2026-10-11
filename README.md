<div align="center">

# 🔮 Grimoire Catalog

**The official public catalog and release feed for Grimoire, a free Windows installer for ENG.YSWEF tools.**

Pick only the tools you want. Grimoire downloads, verifies, installs, updates and removes them for you.

[![Validate catalog](https://github.com/yswef/grimoire-catalog/actions/workflows/validate-catalog.yml/badge.svg)](https://github.com/yswef/grimoire-catalog/actions/workflows/validate-catalog.yml)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)
![Privacy](https://img.shields.io/badge/telemetry-none-brightgreen)
![Price](https://img.shields.io/badge/price-free-success)

[English](#english) · [العربية](#العربية)

</div>

---

## English

### What is Grimoire?
Grimoire is a lightweight Windows launcher and installer for the tools published by **ENG.YSWEF**. Instead of hunting for downloads one by one, you open Grimoire, choose the tools you need, and it installs only those.

This repository is the **public side** of Grimoire. It holds the catalog the app reads and the Releases it downloads from. The Grimoire app itself is closed source and lives in a private repository.

### Features
- **Choose what you install.** Nothing is bundled or installed that you did not pick.
- **Verified downloads.** Every tool lists a SHA256 hash and file size in the catalog. Grimoire refuses any file that does not match.
- **Install, update, roll back, remove.** Per-tool actions, each with a preview, a confirmation, a log and an undo.
- **Offline first.** A cached catalog keeps the app usable without a connection.
- **No telemetry, no tracking.** See [PRIVACY.md](PRIVACY.md).
- **Arabic and English.** Arabic changes the text only. The layout, icons and element positions stay the same.
- **Installer and Portable** builds.
- **Free.** Supported by voluntary donations (see [Support](#support-the-developer)).

### How it works
```
Grimoire app ──reads──▶ catalog.json (this repo, main branch)
      │
      └──downloads──▶ GitHub Release asset of the selected tool
                          │
                          └──▶ SHA256 + size check ──▶ install
```
1. The app fetches `catalog.json` and validates it against `catalog.schema.json`.
2. You select a tool.
3. The app downloads **only that tool's** release asset, from `https://github.com/yswef/...` and nowhere else.
4. The file's SHA256 and size must equal the values in the catalog, otherwise the install is aborted.
5. Install steps run only after a dry-run preview and your confirmation.

### Repository layout
| Path | Purpose |
|---|---|
| `catalog.json` | The tool list read by Grimoire |
| `catalog.schema.json` | JSON Schema (v1) every catalog must satisfy |
| `config/support.json` | Shared developer-support links used by every YSWEF app |
| `.github/workflows/validate-catalog.yml` | CI: schema validation and secret scanning |
| `PRIVACY.md` | Privacy policy |
| `CHANGELOG.md` | Change history |

### Catalog entry format
```json
{
  "id": "example-tool",
  "name": "Example Tool",
  "name_i18n": { "ar": "أداة مثال" },
  "version": "1.0.0",
  "description": "What the tool does, in one sentence.",
  "description_i18n": { "ar": "ماذا تفعل الأداة في جملة واحدة." },
  "license": "Proprietary",
  "min_windows": "10",
  "data_dir": "%APPDATA%\\YSWEF\\ExampleTool",
  "release": {
    "url": "https://github.com/yswef/example-tool/releases/download/v1.0.0/ExampleTool-Setup.exe",
    "asset": "ExampleTool-Setup.exe",
    "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
    "size": 12345678,
    "kind": "installer"
  }
}
```
Rules enforced by the schema: `release.url` must be an `https://github.com/yswef/...` Releases URL; `sha256` is 64 lowercase hex characters; `data_dir` must live under `%APPDATA%\YSWEF\`; `version` is semantic.

### Verifying a download manually
```powershell
Get-FileHash .\ExampleTool-Setup.exe -Algorithm SHA256
```
Compare the result with the `sha256` value in `catalog.json` (or in the Release's `SHA256SUMS.txt`).

### Code signing
Binaries are **not code-signed yet**, so Windows SmartScreen may show a warning on first run. Until signing is in place, integrity is guaranteed by the SHA256 check above. Always download from this organization's official Releases only.

### Security
- Downloads are limited to `github.com/yswef/*`.
- No shell command is built from catalog text; all catalog fields are treated as untrusted input.
- Path traversal and symbolic links are blocked when extracting or writing files.
- Found a vulnerability? Please open a private report through GitHub Security Advisories or email the address below. Do not post exploits publicly.

### Support the developer
Grimoire and every ENG.YSWEF tool are free. If they help you, you can support the work:
- ☕ Buy Me a Coffee: https://buymeacoffee.com/yswef
- 📱 Jeeb wallet: `1606895` (name: يوسف عادل عبد الرحيم يوسف الحمزي)

Bugs and suggestions: [open an issue](https://github.com/yswef/grimoire-catalog/issues).

### License
The Grimoire app is closed source. Catalog data and documentation in this repository are © ENG.YSWEF, all rights reserved, unless a LICENSE file states otherwise. Each listed tool carries its own license, shown in its catalog entry.

### Contact
ENG.YSWEF · yswefalhmzy@gmail.com · [@yswef](https://github.com/yswef)

---

## العربية

<div dir="rtl">

### ما هو Grimoire؟
Grimoire مشغّل ومثبّت خفيف لنظام ويندوز لأدوات **ENG.YSWEF**. بدل البحث عن كل أداة وتنزيلها على حدة، تفتح Grimoire وتختار ما تحتاجه فقط، فيثبّته لك.

هذا المستودع هو **الجانب العام** من Grimoire: يحوي الكتالوج الذي يقرؤه التطبيق، والـReleases التي يُنزِّل منها. أما التطبيق نفسه فمغلق المصدر في مستودع خاص.

### المميزات
- **أنت تختار ما يُثبَّت.** لا يُثبَّت شيء لم تحدده.
- **تنزيلات موثّقة.** لكل أداة بصمة SHA256 وحجم في الكتالوج، ويرفض Grimoire أي ملف لا يطابقها.
- **تثبيت وتحديث وتراجع وإزالة** لكل أداة، وكل عملية بمعاينة وتأكيد وسجل وتراجع.
- **يعمل أوفلاين أولاً** بكتالوج مخزّن مؤقتاً.
- **بلا تتبع ولا إرسال بيانات.** انظر [PRIVACY.md](PRIVACY.md).
- **عربي وإنجليزي.** العربية تغيّر النصوص فقط، ولا تعكس التخطيط ولا الأيقونات ولا مواضع العناصر.
- نسخة **مثبّت** ونسخة **Portable**.
- **مجاني**، ويُدعم بتبرعات اختيارية.

### كيف يعمل
1. يجلب التطبيق `catalog.json` ويتحقق منه بالمخطط `catalog.schema.json`.
2. تختار أداة.
3. يُنزِّل أصل الإصدار **لتلك الأداة فقط** من `https://github.com/yswef/...` ولا من مكان آخر.
4. يجب أن تطابق SHA256 والحجم القيم في الكتالوج، وإلا يُلغى التثبيت.
5. لا تُنفَّذ خطوات التثبيت إلا بعد معاينة (dry-run) وتأكيدك.

### التوقيع الرقمي
الملفات **غير موقّعة رقمياً حالياً**، فقد يعرض SmartScreen تحذيراً عند أول تشغيل. إلى أن يتوفر التوقيع، يضمن فحص SHA256 سلامة الملف. نزّل دائماً من Releases الرسمية فقط.

### الدعم
- ☕ Buy Me a Coffee: https://buymeacoffee.com/yswef
- 📱 محفظة جيب: `1606895` (الاسم: يوسف عادل عبد الرحيم يوسف الحمزي)

### التواصل
ENG.YSWEF · yswefalhmzy@gmail.com · [@yswef](https://github.com/yswef)

</div>

---

<sub>© ENG.YSWEF — yswefalhmzy@gmail.com</sub>
