#!/usr/bin/env python3
"""
يقرأ من: courses/courses-registry.json
ويولّد تلقائياً: courses-config.js بالألوان والأيقونات المتناسقة
"""
import json
from pathlib import Path

# إعداد المسارات بناءً على مكان المجلد الرئيسي للمشروع
ROOT = Path(__file__).resolve().parent.parent
COURSES = ROOT / "courses"
REGISTRY_FILE = COURSES / "courses-registry.json"
OUTPUT_FILE = ROOT / "assets" / "js" / "courses-config.js"

# مصفوفة الألوان المتناسقة لتوزيعها تلقائياً على المواد
COLOR_PALETTES = [
    {"color": "linear-gradient(135deg, #dbeafe, #bfdbfe)", "iconBg": "#eff6ff"},  # أزرق
    {"color": "linear-gradient(135deg, #d1fae5, #a7f3d0)", "iconBg": "#ecfdf5"},  # أخضر
    {"color": "linear-gradient(135deg, #ede9fe, #ddd6fe)", "iconBg": "#f5f3ff"},  # بنفسجي
    {"color": "linear-gradient(135deg, #fce7f3, #fbcfe8)", "iconBg": "#fdf2f8"},  # وردي
    {"color": "linear-gradient(135deg, #fef3c7, #fde68a)", "iconBg": "#fffbeb"},  # برتقالي
    {"color": "linear-gradient(135deg, #f1f5f9, #e2e8f0)", "iconBg": "#f8fafc"}   # رمادي
]

# معجم ذكي لتخمين الأيقونات بناءً على اسم الفولدر
DEFAULT_ICONS = {
    "اتصالات": "📡",
    "ألياف": "🌐",
    "تحكم": "🎛️",
    "كهرب": "⚡",
    "طبي": "🔬",
    "روبوت": "🤖",
    "ميكروويف": "🛰️",
    "أشياء": "🔌",
    "حساسات": "🌡️",
    "إلكترون": "📟",
    "مدمجة": "💾",
}

def get_icon_by_name(folder_name: str) -> str:
    for key, icon in DEFAULT_ICONS.items():
        if key in folder_name:
            return icon
    return "📚"  # أيقونة افتراضية

def generate_config():
    if not REGISTRY_FILE.exists():
        print(f"❌ خطأ: لم يتم العثور على {REGISTRY_FILE.name}! برجاء تشغيل generate-manifests.py أولاً.")
        return

    # قراءة الداتا اللي طلعها السكريبت الأولاني
    with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
        registry_data = json.load(f)

    courses_list = []
    
    for idx, entry in enumerate(registry_data):
        folder_name = entry["folder"]
        path_prefix = entry["pathPrefix"] # المسار الفعلي (سواء مباشر أو جواه فولدر خارجي)
        
        full_course_dir = ROOT / path_prefix
        
        # البحث عن ملفات الـ HTML داخل فولدر المقرر الفعلي
        content_file = ""
        details_file = ""
        references_file = ""
        
        if full_course_dir.is_dir():
            html_files = sorted(
                f.name for f in full_course_dir.iterdir()
                if f.is_file() and f.suffix.lower() in (".html", ".htm")
            )
            preferred_content = f"{folder_name}.html"
            preferred_details = f"{folder_name}_details.html"

            if preferred_content in html_files:
                content_file = preferred_content
            if preferred_details in html_files:
                details_file = preferred_details

            for file in html_files:
                lower = file.lower()
                if "_details" in lower and not details_file:
                    details_file = file
                elif "_references" in lower or "_refs" in lower:
                    references_file = file
                elif lower not in (
                    preferred_content.lower(),
                    preferred_details.lower(),
                ) and not content_file:
                    if "_details" not in lower and "_references" not in lower:
                        content_file = file

            if not content_file and html_files:
                for file in html_files:
                    if "_details" not in file.lower() and "_references" not in file.lower():
                        content_file = file
                        break
        
        # توزيع الألوان بالترتيب (Looping)
        palette = COLOR_PALETTES[idx % len(COLOR_PALETTES)]
        
        # تخمين كود القسم والمادة بشكل ديناميكي
        code_prefix = "GEN"
        category = "عام"
        
        if any(k in folder_name for k in ["طبي", "تصوير"]):
            code_prefix = "MED"
            category = "الأجهزة الطبية"
        elif any(k in folder_name for k in ["اتصالات", "ألياف", "ميكروويف"]):
            code_prefix = "COM"
            category = "هندسة الاتصالات"
        elif any(k in folder_name for k in ["تحكم", "كهرب", "آلات", "حاكمات"]):
            code_prefix = "ELE"
            category = "الهندسة الكهربائية والتحكم"
        elif any(k in folder_name for k in ["روبوت", "ميكاترونكس", "حركة", "ميكانيكية"]):
            code_prefix = "ROB"
            category = "الروبوتات والميكاترونكس"
        elif any(k in folder_name for k in ["أشياء", "مدمجة", "إلكترون"]):
            code_prefix = "EMB"
            category = "الأنظمة المدمجة والإلكترونيات"

        course_code = f"{code_prefix}-{100 + (idx + 1)}"

        # بناء البيانات للمقرر
        course_data = {
            "folder": folder_name,
            "code": course_code,
            "icon": get_icon_by_name(folder_name),
            "color": palette["color"],
            "iconBg": palette["iconBg"],
            "category": category,
            "description": f"مقرر {folder_name} - دراسة المفاهيم التطبيقية والنظرية الكامله.",
            "contentFile": content_file or f"{folder_name}.html"
        }
        
        if details_file: course_data["detailsFile"] = details_file
        if references_file: course_data["referencesFile"] = references_file
        
        # لو السكريبت لقى إن المسار مش مباشر تحت /courses، بيضيف الـ pathPrefix كـ مسار يدوي
        if path_prefix != f"courses/{folder_name}":
            course_data["pathPrefix"] = path_prefix

        courses_list.append(course_data)

    # --- صياغة الملف النهائي وتصديره ---
    header_comment = """/**
 * courses-config.js
 * ══════════════════════════════════════════════════
 * كل اللي محتاج تحطه هنا هو:
 *   - اسم الفولدر (folder) بالضبط زي ما هو على جهازك
 *   - بيانات العرض: الأيقونة، اللون، الوصف
 *
 * الكود يقرأ:
 *   courses/{folder}/ أو courses/فولدر-خارجي/{folder}/  → عبر courses-registry.json
 *   {folder}.html              → المحتوى
 *   {folder}_details.html      → التفاصيل (تبويب جديد)
 *   quizzes/activities/        → فئة/عنصر/ملف (manifest.json)
 *
 * pathPrefix: مسار يدوي لو المقرر داخل فولدر خارجي (اختياري)
 * بعد إضافة ملفات: python scripts/generate-manifests.py
 * ══════════════════════════════════════════════════
 */\n\n"""

    js_objects = []
    for c in courses_list:
        obj_str = "  {\n"
        obj_str += f'    folder: "{c["folder"]}",\n'
        obj_str += f'    code:   "{c["code"]}",\n'
        obj_str += f'    icon:   "{c["icon"]}",\n'
        obj_str += f'    color:  "{c["color"]}",\n'
        obj_str += f'    iconBg: "{c["iconBg"]}",\n'
        obj_str += f'    category: "{c["category"]}",\n'
        obj_str += f'    description: "{c["description"]}",\n'
        obj_str += f'    contentFile: "{c["contentFile"]}",\n'
        if "detailsFile" in c:    obj_str += f'    detailsFile: "{c["detailsFile"]}",\n'
        if "referencesFile" in c: obj_str += f'    referencesFile: "{c["referencesFile"]}",\n'
        if "pathPrefix" in c:     obj_str += f'    pathPrefix: "{c["pathPrefix"]}",\n'
        obj_str += "  }"
        js_objects.append(obj_str)

    config_body = "const COURSES_CONFIG = [\n" + ",\n".join(js_objects) + "\n];\n\n"

    footer_comment = """/**
 * ألوان جاهزة يمكن استخدامها:
 * أزرق:   "linear-gradient(135deg, #dbeafe, #bfdbfe)"  iconBg: "#eff6ff"
 * أخضر:   "linear-gradient(135deg, #d1fae5, #a7f3d0)"  iconBg: "#ecfdf5"
 * بنفسجي: "linear-gradient(135deg, #ede9fe, #ddd6fe)"  iconBg: "#f5f3ff"
 * وردي:   "linear-gradient(135deg, #fce7f3, #fbcfe8)"  iconBg: "#fdf2f8"
 * برتقالي:"linear-gradient(135deg, #fef3c7, #fde68a)"  iconBg: "#fffbeb"
 * رمادي:  "linear-gradient(135deg, #f1f5f9, #e2e8f0)"  iconBg: "#f8fafc"
 */"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header_comment + config_body + footer_comment)

    print(f"OK: wrote {OUTPUT_FILE.relative_to(ROOT)} ({len(courses_list)} courses)")

if __name__ == "__main__":
    generate_config()