"""카피 린트: 한국어 랜딩 카피에서 AI 티 패턴을 찾는다. 규칙과 근거는 docs/08-copy.md.

usage: python3 tools/copy_lint.py <content.md | index.html> [...]

- content.md는 표 행(`|`로 시작)만, index.html은 <script>/<style>을 뺀 텍스트만 읽는다.
- 심각도: S1 = 한 번만 나와도 고친다. S2 = 페이지에서 정한 횟수를 넘으면 고친다. 쿼터는 RULES의 `max`.
- 린트는 1차 거름망이다. 걸린 줄은 사람이 읽고 판단한다(08-copy.md §7 오탐). 안 걸렸다고 통과는 아니다.
- S1이 하나라도 남으면 exit 1.
"""
import html
import re
import sys
from pathlib import Path

# (id, 심각도, 페이지당 허용 횟수, 정규식, 처방)
# 허용 횟수: S1은 0, S2는 그 횟수까지 조용히 둔다.
RULES = [
    # 구조: 세워 놓고 넘어뜨리기 (im-not-ai C-8·A-21·D-7, blader §1)
    ("strawman", "S1", 0, r"단순(한|히) .{0,15}?아(니|닙|닌)|그 이상의|[을를] 넘어선?|더 이상 [^ ]+ 아(니|닙|닌)", "아무도 안 한 주장을 세워 넘어뜨리지 않는다. 긍정문 하나로"),
    ("contrast", "S2", 1, r"(이|가) 아니라|이 아닌,|가 아닌,", "대구는 페이지에 1개. 지우는 대상이 구체적이고 독자가 실제로 믿는 것일 때만"),
    ("cleft", "S1", 0, r"(중요한|필요한|핵심적인) (것은|건) |핵심은 |관건은 ", "'X는 Y다'로 바로 말한다"),
    ("epigram", "S1", 0, r"[이가] 곧 [^ ]+(이다|입니다|예요)|의 언어(다|입니다)|의 문법", "경구 대신 사실 하나"),
    # 부풀리기 (im-not-ai D-2·D-4·A-23, k-skill D-4·D-8, DaleSeo 14·38)
    ("hype", "S2", 0, r"혁신적|획기적|압도적|독보적|폭발적|파격적|전례 없는|차원이 다른|새로운 차원|새로운 지평|지평을 열|패러다임|게임 ?체인저|극대화|한 단계 더|무한한 가능성|놀라운|완벽한", "숫자나 화면으로 바꾼다. 같은 문장에 수치가 있으면 둬도 된다"),
    ("vague-verb", "S1", 0, r"선사(합|해|하)|자리매김|방증|향연|다채로운|시사하는 바|주목할 만|귀추", "무엇이 일어나는지 동사로 쓴다"),
    ("smooth", "S2", 1, r"손쉽게|간편하게|매끄럽게|원활(한|하게)|스마트(한|하게)|최적화된|효율적(인|으로)|다양한", "무엇이 얼마나 쉬운지 구체로"),
    # 결말 공식 (k-skill D-6, DaleSeo 37)
    ("ending", "S1", 0, r"할 때(입니다|예요|다)[.!]?$|지금이야말로|시점입니다|기대(됩니다|돼요)|결론적으로|요약하면|본질적으로", "마지막 문장은 구체적 사실이나 행동으로"),
    # 번역투 (k-skill A, DaleSeo 25~36)
    ("trans-s1", "S1", 0, r"에 있어(서)? |가지고 있(습|어|다)|되어지|보여지|에 의해 |로부터의|에서의 |으로의 ", "번역투. 조사를 바로 잇는다"),
    ("trans-s2", "S2", 2, r"[을를] 통해 |에 대해 |와 관련(하여|된)|과 관련(하여|된)|에 기반(하여|한)|[을를] 바탕으로", "두 번까지. 그 이상이면 '로/를'로 줄인다"),
    ("can", "S2", 2, r"할 수 있(습니다|어요|다)", "증거가 있는 혜택은 단정. 진짜 가능성·허가는 둔다"),
    ("formal-noun", "S1", 0, r"해당 |본 서비스|당사|동 기능", "'이', 제품명으로"),
    ("meet", "S1", 0, r"만나 ?보세요|경험(하세요|해 ?보세요)|지금 바로", "Meet·Experience 직역. 실제 행동을 쓴다"),
    # 챗봇 잔재 (k-skill K, blader §22)
    ("chatbot", "S1", 0, r"좋은 질문|도움이 되(셨|었)으면|언제든(지)? (문의|물어)|궁금하신 점이 있으시면", "FAQ 답은 첫 문장에 답부터"),
    # 구두점 (DaleSeo 1·3·6·7, im-not-ai C-11·J-3)
    ("dash", "S1", 0, r"—|(?<!\d)–(?!\d)| -- ", "줄표 대신 쉼표나 마침표. 숫자 범위(14:00–14:30)의 –는 괜찮다"),
    ("conn-comma", "S2", 3, r"[가-힣](고|며|지만|는데|어서|아서|면서),\s", "연결어미 뒤 쉼표. 빼고 읽어서 숨이 차지 않으면 뺀다"),
    ("triple", "S2", 0, r"[가-힣]+(고|며),\s?[가-힣]+(고|며),?\s?[가-힣]+", "3연속 나열. 형용사(빠르고, 안전하며…)면 고친다. 구체적 행동 순서면 둔다"),
    ("bang", "S1", 0, r"!!|！", "느낌표는 하나까지"),
    ("emoji", "S2", 0, r"[\U0001F300-\U0001FAFF✅✨❌⭐]", "아이콘은 디자인에서. 카피에는 넣지 않는다"),
]

COMPILED = [(i, s, m, re.compile(p), fix) for i, s, m, p, fix in RULES]
HANGUL = re.compile(r"[가-힣]")


def lines_of(path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".html", ".htm"):
        blank = lambda m: "\n" * m.group(0).count("\n")  # 줄번호를 보존한다
        text = re.sub(r"<(script|style)\b.*?</\1>", blank, text, flags=re.S | re.I)
        text = re.sub(r"<!--.*?-->", blank, text, flags=re.S)
        out = []
        for n, raw in enumerate(text.splitlines(), 1):
            s = html.unescape(re.sub(r"<[^>]+>", " ", raw))
            s = re.sub(r"\s+", " ", s).strip()
            if HANGUL.search(s):
                out.append((n, s))
        return out
    out = []
    for n, raw in enumerate(text.splitlines(), 1):
        if not raw.startswith("|") or set(raw) <= set("|-: "):
            continue
        cells = [c.strip() for c in raw.strip().strip("|").split("|")]
        if cells and cells[0] in ("id", "step", "Q", "#"):
            continue
        s = " | ".join(cells)
        if HANGUL.search(s):
            out.append((n, s))
    return out


def sentence(s, m):
    """매치가 든 문장(마침표, 물음표, 느낌표, 표 칸 경계 사이)."""
    a = max(s.rfind(c, 0, m.start()) for c in ".!?|") + 1
    ends = [i for i in (s.find(c, m.end()) for c in ".!?|") if i != -1]
    return s[a:min(ends) if ends else len(s)]


def tone_mix(s):
    """한 셀(단락) 안에서 합니다체와 해요체가 섞였는지."""
    return bool(re.search(r"[가-힣]니다[.!?]", s)) and bool(re.search(r"[가-힣]요[.!?]", s))


def check_h1(path):
    """content.md의 hero.h1.short: `/`로 나눈 각 줄이 14자 이하(02-narrative.md 카피 규칙)."""
    probs = []
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        cells = [c.strip() for c in raw.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[0] == "hero.h1.short":
            for part in cells[2].split("/"):
                k = len(part.strip().replace(" ", ""))
                if k > 14:
                    probs.append((n, f"hero.h1.short 한 줄 {k}자(공백 제외) > 14: {part.strip()}"))
    return probs


def lint(path):
    rows = lines_of(path)
    hits = {i: [] for i, *_ in COMPILED}
    for n, s in rows:
        for i, sev, mx, rx, fix in COMPILED:
            for m in rx.finditer(s):
                if i == "hype" and re.search(r"\d", sentence(s, m)):
                    continue
                hits[i].append((n, m.group(0), s))
    s1 = 0
    print(f"\n# {path}")
    for i, sev, mx, rx, fix in COMPILED:
        found = hits[i]
        if len(found) <= mx:
            continue
        s1 += sev == "S1"
        print(f"\n[{sev}] {i}  {len(found)}회 (허용 {mx}) - {fix}")
        for n, word, s in found:
            print(f"  L{n}: «{word}»  {s[:110]}")
    mixed = [(n, s) for n, s in rows if tone_mix(s)]
    if mixed:
        print(f"\n[S2] tone-mix  한 단락 안 합니다체와 해요체 혼용 {len(mixed)}곳")
        for n, s in mixed:
            print(f"  L{n}: {s[:110]}")
    # 페이지 단위: 한쪽 어조가 대부분인데 다른 어조 줄이 섞였는지(08 §6 페이지 어조는 하나)
    hamnida = [(n, s) for n, s in rows if re.search(r"[가-힣]니다[.!?]", s) and not tone_mix(s)]
    haeyo = [(n, s) for n, s in rows if re.search(r"[가-힣]요[.!?]", s) and not tone_mix(s)]
    if hamnida and haeyo:
        minor, name = (hamnida, "합니다체") if len(hamnida) <= len(haeyo) else (haeyo, "해요체")
        print(f"\n[S2] tone-page  페이지 어조와 다른 {name} 줄 {len(minor)}곳 (aria-live 안내도 읽힌다)")
        for n, s in minor:
            print(f"  L{n}: {s[:110]}")
    if path.suffix.lower() == ".md":
        for n, msg in check_h1(path):
            s1 += 1
            print(f"\n[S1] h1-length  L{n}: {msg}")
    if not s1 and not any(len(hits[i]) > mx for i, _, mx, *_ in COMPILED) and not mixed:
        print("  걸린 것 없음")
    return s1


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    total = sum(lint(Path(p)) for p in sys.argv[1:])
    print(f"\nS1 규칙 위반: {total}")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
