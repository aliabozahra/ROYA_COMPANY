# 🎓 EduPortal — دليل الاستخدام

## هيكل المشروع

```
edu-portal/
├── index.html
├── course.html
├── assets/
│   ├── css/main.css
│   └── js/courses-config.js   ← بيانات المقررات
└── courses/
    └── اسم المقرر/             ← اسم الفولدر = اسم المقرر
        ├── المحتوى.html         ← ملف المحتوى الرئيسي
        ├── المصادر.html         ← ملف المراجع
        ├── كويزات/
        │   ├── manifest.json    ← قائمة الكويزات والملفات
        │   ├── اسم الكويز 1/
        │   │   ├── السؤال الأول.html
        │   │   └── السؤال الثاني.html
        │   └── اسم الكويز 2/
        │       └── السؤال الأول.html
        └── أنشطة/
            ├── manifest.json    ← قائمة الأنشطة والملفات
            └── اسم النشاط/
                └── التمرين.html
```

---

## شكل manifest.json

```json
[
  {
    "name": "اسم الكويز أو النشاط (= اسم الفولدر بالضبط)",
    "files": [
      "اسم الملف الأول.html",
      "اسم الملف الثاني.html"
    ]
  }
]
```

> **مهم:** `name` لازم يطابق اسم الفولدر بالضبط.

---

## إضافة مقرر جديد

### الخطوة 1 — أنشئ الفولدر
```
courses/اسم المقرر الجديد/
├── المحتوى.html
├── المصادر.html
├── كويزات/
│   ├── manifest.json
│   └── اسم الكويز/
│       └── ملف.html
└── أنشطة/
    ├── manifest.json
    └── اسم النشاط/
        └── ملف.html
```

### الخطوة 2 — أضف في courses-config.js
```javascript
{
  folder:      "اسم المقرر الجديد",   // نفس اسم الفولدر بالضبط
  code:        "XXX-101",
  icon:        "📘",
  color:       "linear-gradient(135deg, #dbeafe, #bfdbfe)",
  iconBg:      "#eff6ff",
  category:    "التصنيف",
  description: "وصف قصير للمقرر",
}
```

---

## تشغيل على الجهاز

```bash
# VS Code + Live Server (الأسهل)
# افتح المجلد في VS Code → Go Live

# أو Python
cd edu-portal
python -m http.server 8000
# افتح http://localhost:8000
```

## رفع على Vercel (مجاني)
1. ارفع على GitHub
2. vercel.com → New Project → اختر الـ repo
3. Deploy ✅

---

## أسماء ملفات المحتوى المدعومة تلقائياً
الكود بيجرّب هذه الأسماء بالترتيب:
- `المحتوى.html`
- `محتوى المقرر.html`
- `content.html`
- `المحتوى الدراسي.html`

وللمصادر:
- `المصادر.html`
- `المراجع.html`
- `المراجع والمصادر.html`
- `references.html`
