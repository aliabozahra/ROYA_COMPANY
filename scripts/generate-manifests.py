#!/usr/bin/env python3
"""
يولّد:
  - courses/courses-registry.json  (مسار كل مقرر — يدعم الفولدر الخارجي)
  - courses/.../quizzes|activities/manifest.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSES = ROOT / "courses"
REGISTRY_FILE = COURSES / "courses-registry.json"
HTML_EXT = {".html", ".htm"}

SECTION_ALIASES = {
    "quizzes": ["quizzes", "كويزات"],
    "activities": ["activities", "أنشطة"],
}
SECTION_FOLDER_NAMES = frozenset(name for names in SECTION_ALIASES.values() for name in names)


def safe_print(msg: str) -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))


def list_html_files(folder: Path) -> list[str]:
    return sorted(
        (
            f.name
            for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in HTML_EXT and not f.name.startswith(".")
        ),
        key=str.casefold,
    )


def has_section_folder(course_dir: Path) -> bool:
    return any((course_dir / name).is_dir() for name in SECTION_FOLDER_NAMES)


def looks_like_course_dir(path: Path) -> bool:
    if not path.is_dir() or path.name.startswith("."):
        return False
    if has_section_folder(path):
        return True
    return bool(list_html_files(path))


def discover_courses(base: Path, parts: list[str] | None = None) -> list[dict]:
    """يكتشف المقررات مباشرة أو داخل فولدر خارجي (أرقام / timestamp)."""
    parts = parts or []
    found: list[dict] = []

    if not base.is_dir():
        return found

    for child in sorted(base.iterdir(), key=lambda p: p.name.casefold()):
        if not child.is_dir() or child.name.startswith("."):
            continue

        child_parts = parts + [child.name]

        if looks_like_course_dir(child):
            prefix = Path("courses", *child_parts).as_posix()
            found.append({"folder": child.name, "pathPrefix": prefix})
            continue

        # فولدر خارجي (أرقام، timestamp، إلخ) → ادخل وابحث عن مقررات بداخله
        found.extend(discover_courses(child, child_parts))

    return found


def scan_section(section_dir: Path) -> list[dict]:
    manifest: list[dict] = []
    if not section_dir.is_dir():
        return manifest

    for category_dir in sorted(section_dir.iterdir(), key=lambda p: p.name.casefold()):
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue

        items: list[dict] = []
        for item_dir in sorted(category_dir.iterdir(), key=lambda p: p.name.casefold()):
            if not item_dir.is_dir() or item_dir.name.startswith("."):
                continue
            files = list_html_files(item_dir)
            if files:
                items.append({"name": item_dir.name, "files": files})

        if items:
            manifest.append({"name": category_dir.name, "items": items})

    return manifest


def resolve_section_dir(course_dir: Path, aliases: list[str]) -> Path | None:
    for name in aliases:
        path = course_dir / name
        if path.is_dir():
            return path
    return None


def write_manifest(section_dir: Path, data: list[dict]) -> bool:
    out = section_dir / "manifest.json"
    if not data:
        if out.exists():
            out.unlink()
        return False
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def process_course_on_disk(course_dir: Path, path_prefix: str) -> int:
    written = 0
    rel = course_dir.relative_to(ROOT)
    for _kind, aliases in SECTION_ALIASES.items():
        section = resolve_section_dir(course_dir, aliases)
        if not section:
            continue
        data = scan_section(section)
        if write_manifest(section, data):
            n_items = sum(len(c.get("items", [])) for c in data)
            safe_print(f"  {rel / section.name}: {len(data)} categories, {n_items} items")
            written += 1
    return written


def write_registry(entries: list[dict]) -> None:
    # إزالة تكرار بنفس folder — نفضّل المسار الأقصر (مباشر تحت courses/)
    by_folder: dict[str, dict] = {}
    for entry in entries:
        folder = entry["folder"]
        existing = by_folder.get(folder)
        if not existing or len(entry["pathPrefix"]) < len(existing["pathPrefix"]):
            by_folder[folder] = entry

    registry = sorted(by_folder.values(), key=lambda e: e["folder"].casefold())
    REGISTRY_FILE.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    safe_print(f"Registry: {len(registry)} course(s) -> {REGISTRY_FILE.relative_to(ROOT)}")


def main() -> int:
    if not COURSES.is_dir():
        safe_print("courses folder missing.")
        return 1

    registry_entries = discover_courses(COURSES)
    write_registry(registry_entries)

    prefix_to_dir: dict[str, Path] = {}
    for entry in registry_entries:
        prefix_to_dir[entry["pathPrefix"]] = ROOT / Path(*entry["pathPrefix"].split("/"))

    total_manifests = 0
    for entry in registry_entries:
        course_dir = prefix_to_dir.get(entry["pathPrefix"])
        if course_dir and course_dir.is_dir():
            safe_print(entry["folder"])
            total_manifests += process_course_on_disk(course_dir, entry["pathPrefix"])

    safe_print(f"Done: {total_manifests} manifest file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
