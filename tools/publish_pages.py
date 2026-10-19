"""랜딩 시안(웹페이지)만 배포 레포로 복사한다. 방법론(docs/templates/tools, *.md)은 복사하지 않는다.

usage: python3 -I tools/publish_pages.py [--dest ../landing-machine-pages]

- 원본: 이 레포의 sites/<제품>/<버전>/ (index.html + assets 등)
- 대상: 배포 레포 클론의 sites/
- 제외: *.md (content.md, BRIEF.md, look.md), shots/ (QA 스크린샷)
- 대상 sites/는 매번 원본과 똑같이 맞춘다(원본에서 사라진 파일은 지운다).
- 복사 후 배포 레포에서 직접 확인하고 커밋·push한다.
  뷰어 메뉴는 배포 레포의 app/catalog.ts에서 관리한다.
"""
import argparse
import filecmp
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sites"


def wip_paths(dest_root: Path) -> set:
    """배포 레포 app/catalog.ts에서 status가 "wip"인 시안 경로(예: <제품>/<버전>)를 읽는다."""
    cat = dest_root / "app" / "catalog.ts"
    if not cat.exists():
        return set()
    return set(re.findall(r'v\("[^"]+",\s*"([^"]+)".*"wip"\)', cat.read_text(encoding="utf-8")))


def skip(rel: Path, wip: set) -> bool:
    return (
        rel.suffix.lower() == ".md"
        or "shots" in rel.parts
        or "/".join(rel.parts[:2]) in wip
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", default=str(ROOT.parent / "landing-machine-pages"))
    dest = Path(ap.parse_args().dest).resolve() / "sites"
    if not (dest.parent / ".git").exists():
        sys.exit(f"배포 레포가 아니다: {dest.parent}")

    wip = wip_paths(dest.parent)
    wanted = {p.relative_to(SRC) for p in SRC.rglob("*") if p.is_file() and not skip(p.relative_to(SRC), wip)}
    if wip:
        print("skip (catalog wip):", ", ".join(sorted(wip)))
    copied = removed = 0
    for rel in sorted(wanted):
        s, d = SRC / rel, dest / rel
        if d.exists() and filecmp.cmp(s, d, shallow=False):
            continue
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s, d)
        copied += 1
    if dest.exists():
        for p in sorted(dest.rglob("*"), reverse=True):
            rel = p.relative_to(dest)
            if p.is_file() and rel not in wanted:
                p.unlink()
                removed += 1
            elif p.is_dir() and not any(p.iterdir()):
                p.rmdir()
    print(f"copied {copied}, removed {removed}, total {len(wanted)} files -> {dest}")


if __name__ == "__main__":
    main()
