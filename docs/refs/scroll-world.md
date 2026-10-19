# scroll-world (oso95/scroll-world)

- 저장소: https://github.com/oso95/scroll-world (MIT). 확인한 커밋은 `71cc36d` (2026-07-28)
- 정체: 에이전트 스킬(SKILL.md). AI로 장면 스틸과 카메라 비행 영상을 만들고, 스크롤로 `video.currentTime`을 스크럽하는 "세계를 날아다니는" 랜딩을 만든다.
- 설치: `/plugin marketplace add oso95/scroll-world`를 실행한 뒤 `/plugin install scroll-world@scroll-world`
- 외부 의존: Monid CLI(Seedance 2.0 영상, 클립당 USD 과금), Higgsfield CLI(gpt_image_2 스틸, 크레딧), ffmpeg, Pillow. Codex CLI는 선택이다.

## 가져올 것

### 1. 이음새의 법칙
커넥터의 시작과 끝은 **이웃 클립에서 실제로 렌더된 프레임**을 쓴다. 원본 스틸을 쓰면 안 된다. 생성할 때마다 결과가 조금씩 달라서, 스틸로 이어 붙이면 이음새에서 장면이 툭 튄다. 크로스페이드는 보험일 뿐이다.

### 2. 카메라 구조
- **A 연속 전진**: 이전 클립의 마지막 프레임을 다음 클립의 start-image로 넣는다. end-image는 넣지 않는다. 순차로만 만들 수 있다. 사실적인 공간이나 워크스루에 맞는다.
- **B 다이브와 공중 커넥터**: 이음새마다 카메라가 뒤로 빠지므로, 미니어처나 디오라마 세계에서만 의도된 연출로 읽힌다.
- **Locked-iso**: A 구조에 "같은 아이소 각도를 유지한다"는 문장을 더한다. 가장 차분하고, 다시 생성할 때도 가장 싸다.
- 클립 **안에서는** 궤도 회전이나 크레인 업 같은 자유로운 움직임이 허용된다. **이음새를 넘을 때** 속도가 뒤집히는 것만 피하면 된다. 그래서 모든 클립은 마지막 1초를 "느리고 일정한 전진"으로 끝내고, 다음 클립은 그 전진을 이어받아 시작한다. 이게 **모션 핸드오프 계약**이다.

### 3. 컨셉별 카메라 문법
| 컨셉 | 클립 중간의 움직임 |
|---|---|
| 제품 / 럭셔리 | 히어로 오브젝트 주위를 반 바퀴 돈 뒤 지나친다 |
| 부동산 / 호스피탈리티 | 문을 지나는 스테디캠, 아트리움에서 크레인 업 |
| 산업 / 공정 / 물류 | 라인을 따라 낮게 옆으로 트래킹, 전경 패럴랙스 |
| 여행 / 야외 | 드론처럼 상승하며 드러낸 뒤 하강 스윕 |
| 푸드 / 크래프트 | 공예 순간으로 밀고 들어갔다가 빠져나온다 |

### 4. 프롬프트 구조
- 스타일 프리앰블을 바이트 단위까지 똑같이 쓴다. 기본값은 "isometric low-poly clay diorama, tilt-shift, warm light"이다. 대안으로 페이퍼크래프트, 글로시 토이, 클레이메이션, 네온 나이트, 포토리얼 건축이 있다.
- 장면 프롬프트는 `[프리앰블] + Subject: [구체적인 소품을 나열한 장면 묘사]` 형태다. `No text, no letters, no logos`를 항상 붙인다. 구도는 중앙에 맞춘다.
- 원본 템플릿은 저장소의 `skills/scroll-world/references/prompts.md`에 있다.

### 5. 스크럽 엔진 (`references/scrub-engine.js`, 바닐라 JS, 의존성 0)
- `mountScrollWorld(el, {sections, connectors, diveScroll, connScroll, crossfade})`
- 클립을 **Blob으로 받아** object URL로 재생한다. 바이트 레인지가 없어도 seek가 된다.
- 섹션별 `scroll`(체류 길이)과 `linger`(카메라가 카피의 정점에서 머무르게 하는 시간 리매핑, ≤0.6)를 둔다.
- 폰 대응: 모바일용 인코딩 사용, seek 합치기(디코더가 아직 seeking 중이면 새 currentTime을 주지 않는다), 첫 페인트 전까지 포스터 유지, 첫 터치에 prime, URL 바 리사이즈 무시, safe-area.
- 테마는 CSS 변수(`--sw-bg`, `--sw-ink`, `--sw-accent`, `--sw-font-*`)로 바꾼다. 기본값은 `@layer sw`에 있다.

### 6. 인코딩
`-crf 20 -g 8 -keyint_min 8 -sc_threshold 0 -an -movflags +faststart` 원본 해상도로, unsharp를 약하게 준다. 모바일은 720 너비, `-g 4`, crf 23이다.

### 7. QA
이음새 앞뒤를 스크린샷으로 비교한다. PSNR이 아니라 **구도**로 판단한다. 정상적인 이음새도 18–25dB가 나온다. `video.seekable.end(0) > 0`인지 확인한다. 모바일은 CPU를 4–6배 스로틀한 상태에서 빠르게 스크롤해 본다.

## 우리와 다른 점

- scroll-world는 **영상 스크럽(T2)** 하나만 다룬다. 스틸에 카메라와 셰이더 전환(T1/T3)을 쓰는 방식은 04 문서를 본다.
- scroll-world는 카피 레이아웃이 단순하다(eyebrow, title, body, tags). 에디토리얼 장치는 우리가 따로 얹어야 한다.
