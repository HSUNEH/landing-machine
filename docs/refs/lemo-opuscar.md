# Lemo-Opuscar (lemomo-ai/lemo-opuscar)

- 저장소: https://github.com/lemomo-ai/lemo-opuscar (MIT). 확인한 커밋은 `d33bdea` (2026-10-16), 카탈로그는 `508848a` (2026-10-18)에서 다시 확인했다. 갤러리: https://lemomo-ai.github.io/lemo-opuscar/
- 정체: **코드로만 만든 영화 스타일 51종**(`styles/` 아래 폴더 52개 중 1개는 `my-style` 템플릿)을 10개 분류로 모은 라이브러리이자 스킬이다. 장면마다 canvas, WebGL, three.js 페이지를 프레임 단위로 렌더하고, 음악·효과음·TTS 내레이션까지 코드로 만든다. 영상 생성 모델이나 스톡 소스는 쓰지 않는다.
- 설치: `claude plugin marketplace add lemomo-ai/lemo-opuscar`를 실행한 뒤 `claude plugin install lemo-opuscar@lemolab`
- 작성자 말로는 스타일이 Opus 5.5에 맞춰 튜닝되어 있다.

## 가져올 것 ①: "그림은 시간의 함수"

```js
window.DUR = 54.2;
window.render = (t) => { /* t초의 프레임을 그린다. 결정적이어야 한다 */ };
window.READY = true;
```

- **결정적으로 만든다.** `Date.now()`와 시드 없는 `Math.random()`을 쓰지 않고, 이전 프레임의 상태를 이어받지 않는다. 그래서 어느 프레임이든, 어떤 순서로든 따로 그릴 수 있다.
- 2D는 Canvas 2D, 3D는 three.js, 후처리(필름 손상, CRT, 잉크)는 WebGL2로 한다.
- 스톱모션·픽셀·셀 룩은 **2프레임마다** 그리되, **카메라와 조명은 매 프레임 부드럽게** 둔다. 카메라까지 계단식이면 랙처럼 보인다.
- **world→screen 변환 함수는 하나만 둔다.** 대상을 따라가는 효과(아이리스, 줌, 스포트라이트)는 모두 이 함수를 거친다. 화면 좌표를 직접 쓰지 않는다. "배경과 오버레이가 카메라를 공유한다"와 같은 원리다.
- `window.TEXTS(t)`로 화면에 보이는 모든 텍스트와 그 박스를 보고하게 하면 읽기 시간을 자동으로 검사할 수 있다(`readcheck`).

**랜딩으로 옮기면 `t`를 스크롤 진행값으로 바꾸면 된다.** `render(progress)`가 결정적이면 스크롤로 앞뒤로 스크럽해도 항상 같은 그림이 나온다. 이게 **코드 필름 티어**다([04-motion-and-tech.md](../04-motion-and-tech.md)). 영상 파일이 없으니 용량이 작고, 어떤 DPR에서도 선명하고, 카피를 실제 텍스트로 넣을 수 있어 현지화가 쉽다.

## 가져올 것 ②: 스타일 스펙 형식 (`styles/<slug>/STYLE.md`)

스타일마다 아래 항목을 고정된 순서로 적는다. 우리 룩 스펙 양식([templates/look.md](../../templates/look.md))의 원형이다.

1. 본질, 그리고 **무엇이 아닌가**
2. 재료와 렌더링
3. 색 논리
4. 타입과 자막
5. 모션 품질
6. **카메라 문법**(움직임 → 표현하는 것 → 쓸 수 있는 상황, 표로)
7. 사운드 팔레트
8. 고유 무브(이 매체만 할 수 있는 연출 메뉴)
9. 매체의 함정
10. 엔진
11. **변주 공간**(구조, 오프닝, 엔딩 후보)

레퍼런스에서는 문법만 배운다. 캐릭터, UI, 음악, 숏은 복제하지 않는다.

## 가져올 것 ③: 연출 규칙 (DIRECTOR.md)

- **읽기 시간**: 텍스트가 다 나타난 뒤 **한국어·중국어는 (글자 수 ÷ 4.5 + 1.5)초, 영어는 (글자 수 ÷ 15 + 1.5)초** 유지한다. 자막은 1.8s 이상, 타이틀 카드는 4s 이상이다.
  - 랜딩에서는 카피가 화면에 온전히 보이는 스크롤 구간이 이 시간보다 길어야 한다. 기준 스크롤 속도로 자동 스크롤해 검사한다([06-quality-gate.md](../06-quality-gate.md)).
- **속도에 변화를 준다.** 빠르고 느린 구간을 번갈아 두고, 확실한 가속이나 감속을 한 번 넣고, 숨 쉴 구간(긴 테이크나 멈춤)을 하나 둔다. 일정한 속도의 필름은 실패다. 빠르게 하려면 컷을 줄이는 게 아니라 화면당 단어 수를 줄인다.
- **모든 숏에는 이유가 있어야 한다**(카메라 문법 표).
- 사실을 말하는 필름은 `FACTS.md`에 출처를 남긴다. 우리 콘텐츠 모델의 "주장 ↔ 증거"와 같다.

## 랜딩에 쓸 만한 스타일

| 스타일 | 용도 | 우리 쓰임 |
|---|---|---|
| **living-screencast** | 제품 튜토리얼, 기능 런칭, 온보딩 | **Clear 데모의 상위 버전.** HTML로 다시 그린 실제 UI 안에서 픽셀 마스코트가 소프트웨어의 동작을 연기한다. 커서는 사용자, 마스코트는 소프트웨어다. 줌·랙포커스·휩팬 카메라 문법을 쓴다 |
| dark-keynote | 제품 런칭, SaaS | 다크 테크 Film 룩 |
| iso-infographic | 프로세스 설명, 공급망 | scroll-world 디오라마의 코드 버전. 영상 크레딧이 들지 않는다 |
| dataviz / data-physical | 리포트, 수치 | 수치 증거 섹션 |
| swiss-motion / pictogram-motion | 브랜드 아이덴티티 | 키네틱 타이포 히어로 |
| blueprint / teardown / hologram-hud | 하드웨어, 스펙 설명 | 제품 해부형 내러티브 |
| halftone-dossier / risograph / silkscreen-poster | 유머, 인디 브랜드, 포스터 | pasteup 콜라주와 인접한 인쇄 룩 |
| whiteboard / midcentury-toon / one-line | 설명, 도움말 | 친근한 How 섹션 |
| glass-product / paper-popup / brick-toy | 제품 런칭(3D) | 히어로 오브젝트 |
| briefing-board / satellite-briefing | 옵션 비교, 브리핑 | 비교·결정 섹션 |

전체 목록은 저장소의 `styles/README.md`에 있고, 스타일마다 `style.json`에 `uses`(용도)가 적혀 있다.

## 부산물: 런칭 필름

같은 `render(t)` 페이지를 헤드리스 크롬으로 프레임 단위로 캡처하면 MP4가 된다. 랜딩의 코드 필름에서 **SNS용 런칭 영상과 OG 비디오**를 거의 공짜로 뽑을 수 있다. 툴체인(Node 20+, ffmpeg, Python 3.11+)은 Windows에서는 WSL을 권장한다고 적혀 있다.

## 전체 카탈로그와 랜딩 적합도 (508848a 기준)

**opuscar는 룩 하나가 아니라 룩 51개의 묶음이다.** 14개 시안의 C(코드 드로잉)는 이 중 swiss-motion, dark-keynote, dataviz 몇 개의 문법만 섞어 썼다. 스타일마다 재료, 색 논리, 카메라 문법이 달라서 각각 별도 룩으로 세울 수 있다. 모두 코드로 그리므로 생성 크레딧이 들지 않는다.

적합도 기준은 소프트웨어 제품 랜딩이다. ◎ 바로 쓸 만함 / ○ 제품에 따라 / △ 브랜드 톤이 맞을 때만.

| 분류 | 스타일(폴더) | 원래 용도(style.json `uses`) | 랜딩 |
|---|---|---|---|
| Evidence Films | satellite-briefing, briefing-board, lidar-survey, white-model, data-physical, teardown, microscope, archive-lighttable | 브리핑, 옵션 비교, 리포트, 제품 해부, 아카이브 | briefing-board ○(비교 섹션), archive-lighttable ○(문서·기록 제품), teardown ○, data-physical ○(수치 증거), 나머지 △ |
| Hand-drawn & Painting | crayon-book, watercolor, ink-wash, impasto, one-line, whiteboard, urban-sketch | 그림책, 브랜드 스토리, 설명 | whiteboard ○(How 섹션), one-line ○(미니멀 브랜드), 나머지 △ |
| East Asian Traditions | shadow-puppet, ukiyoe, papercut-red, paper-lantern | 명절, 문화 브랜드 | △ |
| Print & Printmaking | risograph, halftone-dossier, woodcut, engraving, silkscreen-poster | 인디 브랜드, 유머, 포스터 | risograph·halftone-dossier ○(B 콜라주와 인접), 나머지 △ |
| Graphic & Type | swiss-motion, spy-titles, art-deco, blueprint, stained-glass, pictogram-motion, ascii-crt | 브랜드 아이덴티티, 하드웨어, 개발자 도구 | swiss-motion ◎, ascii-crt ◎(개발자·AI 도구), blueprint ○, pictogram-motion ○, spy-titles ○(티저) |
| Information & Keynote | dataviz, iso-infographic, dark-keynote, living-screencast, hologram-hud | 제품 런칭, SaaS, 튜토리얼, 프로세스 설명 | **living-screencast ◎, dark-keynote ◎, iso-infographic ◎**, dataviz ○, hologram-hud ○ |
| Cartoon & Anime | rubber-hose, cel-anime-80s, scifi-toon, midcentury-toon | 설정 가이드, 도움말, 뮤직비디오 | **midcentury-toon ◎**(3단계 사용법), 나머지 △ |
| Games | pixel-rpg, hd-2d, microgame, game-show | 게임 트레일러, 온보딩, 연대기 | microgame ○(온보딩), game-show ○(연대기), pixel-rpg ○(게임사 톤) |
| Cinema & Eras | silent-film, backrooms | 코미디, 미스터리 티저 | △ |
| Materials & 3D | brick-toy, paper-popup, tilt-shift, lowpoly-island, glass-product | 제품 런칭, 세계관 | paper-popup ○(문서·종이 제품), lowpoly-island ○(E 디오라마의 코드 버전), glass-product ○(하드웨어) |

- 갤러리에서 스타일별 데모 필름을 볼 수 있다: https://lemomo-ai.github.io/lemo-opuscar/
- living-screencast 데모의 마스코트(Clawd)는 Anthropic의 캐릭터다. 문법만 가져오고 마스코트는 제품에 맞게 새로 만든다.
