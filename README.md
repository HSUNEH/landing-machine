# landing-machine

기깔나는 랜딩페이지를 반복해서 만들기 위한 방법론 저장소. 이 레포에는 레퍼런스를 뜯어보고 얻은 원칙, 프로세스, 수치, 체크리스트를 쌓는다. 구현은 그다음이다.

## 북극성 레퍼런스 (양 극)

제품 하나에 대해 이 두 극 사이에서 **여러 버전**(Film / Hybrid / Clear)을 만들어 제시한다. → [docs/07-versions.md](docs/07-versions.md)

- **화려한 쪽, Film**: 스크롤로 넘기는 한 편의 필름이다. 손그림 플레이트 위로 카메라가 움직이고, WebGL 셰이더 전환과 에디토리얼 타이포, 실제 제품 UI 투어를 지나 포스터 CTA로 끝난다.
- 룩 레퍼런스: [pasteup](docs/refs/pasteup.md)(페이퍼 콜라주 스톱모션, 요소를 만들고 코드로 조립), [lemo-opuscar](docs/refs/lemo-opuscar.md)(코드로 그리는 스타일 51종, 결정적 `render(t)`), [scroll-world](docs/refs/scroll-world.md)(AI 디오라마 플라이스루). 버전은 **골격(Film / Hybrid / Clear) × 룩**으로 조합한다.
- **깔끔한 정보전달 쪽, [Tiro](https://tiro.ooo/ko/)**: 섹션을 쌓은 구조다. HTML로 재현한 제품 데모가 히어로에서 스크립트대로 재생되고, 신뢰 스택(인증, 로고, 후기, 보안, 가격, FAQ)이 이어진다. 따뜻한 무채색에 브랜드 1색을 쓰고, 깊이는 그림자 대신 표면 색 변화로 만든다. → [분해 노트](docs/refs/tiro-teardown.md)

## 문서 지도

| 문서 | 내용 |
|---|---|
| [docs/01-process.md](docs/01-process.md) | 브리프부터 출시까지 8단계와 각 단계의 게이트 |
| [docs/02-narrative.md](docs/02-narrative.md) | 이야기 구조("하루의 삶" 외), 비트 표, 카피 규칙 |
| [docs/03-visual.md](docs/03-visual.md) | 스타일 선택, 타이포·컬러 토큰, 에디토리얼 장치, 질감 |
| [docs/04-motion-and-tech.md](docs/04-motion-and-tech.md) | 진행값과 장면 배열 골격, T0~T3 티어, 카메라, 전환, 이징, 오프닝, 투어 |
| [docs/05-assets.md](docs/05-assets.md) | 에셋 목록, AI 생성 파이프라인, 인코딩 |
| [docs/06-quality-gate.md](docs/06-quality-gate.md) | 출시 전 체크리스트 |
| [docs/07-versions.md](docs/07-versions.md) | 여러 버전 제시: Film / Hybrid / Clear, 변주 축, 공통 콘텐츠 모델, 고르는 기준 |
| [docs/08-copy.md](docs/08-copy.md) | 카피 문장 규칙: AI 티 금지·쿼터, 자리별 규칙, 사람 카피 기법, 표기 |
| [templates/brief.md](templates/brief.md) | 새 랜딩을 시작할 때 채우는 브리프와 비트 표 |
| [templates/content.md](templates/content.md) | 제품을 받으면 가장 먼저 채우는 콘텐츠 모델(모든 버전이 공유) |
| [templates/look.md](templates/look.md) | 룩 스펙 양식(본질, 재료, 색, 타입, 모션, 카메라 문법, 고유 무브, 함정, 변주) |
| [tools/copy_lint.py](tools/copy_lint.py) | 카피 린트(08의 금지·쿼터 패턴, 히어로 14자, 어조 혼용) |
| [tools/seam_check.py](tools/seam_check.py) | 영상 체인 이음새 검사(PSNR과 경계 프레임 추출) |

레퍼런스 노트:

- [docs/refs/tiro-teardown.md](docs/refs/tiro-teardown.md): 섹션 구조, 스크립트 데모, 토큰, 무게와 로딩 함정 (원본 보존)
- [docs/refs/pasteup.md](docs/refs/pasteup.md): 콜라주 룩, 요소 먼저 만드는 원칙, 스톱모션 케이던스 수치, DOM 이식 방법
- [docs/refs/lemo-opuscar.md](docs/refs/lemo-opuscar.md): 결정적 렌더 계약, STYLE 스펙 형식, 읽기 시간 규칙, 랜딩에 쓸 만한 스타일 표
- [docs/refs/scroll-world.md](docs/refs/scroll-world.md): AI 영상 체인과 이음새 법칙, 스크럽 엔진
- [docs/refs/21st-dev.md](docs/refs/21st-dev.md): 일반 섹션용 컴포넌트 레지스트리
- [docs/refs/ko-humanizer.md](docs/refs/ko-humanizer.md): 한국어 AI 티 제거 오픈소스 4종(im-not-ai, k-skill, DaleSeo, blader)의 실측과 원칙
- [docs/refs/ad-copy.md](docs/refs/ad-copy.md): 한국·해외 광고 슬로건과 랜딩 헤드라인 예시 뱅크, 카피 원칙 출처
- [docs/refs/styles-2026.md](docs/refs/styles-2026.md): 2026 웹 디자인 스타일 13가지와 업종 궁합

## 한 장 요약

1. **이야기 먼저.** 비트 하나에는 역할 하나만 준다. 증거는 이야기 세계 안에서 등장시킨다.
2. **진행값 하나와 장면 배열 하나.** 모든 연출은 `scenes` 데이터에서 읽는다.
3. **네이티브 스크롤에 지수 스무딩(τ≈45ms).** 스크롤을 빼앗지 않고 무게감만 준다.
4. **배경과 오버레이는 같은 카메라를 공유한다.** 대부분의 비트는 느린 푸시인 하나면 충분하다.
5. **시그니처 전환은 2~3개.** RIPPLE, APERTURE, GRAIN.
6. **에디토리얼 타이포.** 얇은 한글 세리프, 모노 마이크로 라벨, 번호 캡션, 헤어라인 그리드.
7. **아트 디렉션의 일관성이 엔진보다 중요하다.** 프리앰블을 똑같이 쓰고, 소스와 모델은 하나만 쓴다.
8. **폴백은 처음부터 함께 만든다.** reduced-motion, WebGL 없음, 모바일.

## 열려 있는 결정

- 구현 스택: 제안은 바닐라 TS 필름 엔진, Next.js App Router 껍데기, 21st.dev 부품 조합이다. 첫 제품 브리프를 받고 확정한다.
- 첫 적용 대상 제품과 에셋 소스(외주 일러스트 / AI 생성).
