> 원본: 2026-10 REA 세션의 정적 리버스엔지니어링 노트(homeflix-findings.md) 사본. 브라우저 실행 없이 소스만 읽음(§5.4). 인용 라인 번호는 당시 로컬 사본 기준.
> 대상: https://www.homeflix.kr/

# How www.homeflix.kr is built (reverse-engineering notes)

How the work was done: on 2026-10-16 I downloaded the HTML with curl. I also downloaded every linked CSS, JS, image and video file, or measured its size, and read the files without running any of the site's code. The page is **server-rendered by the Imweb (아임웹) site builder**. All the custom work sits in Imweb "코드" (code) widgets as hand-written HTML/CSS/JS, and this code ships **unminified and heavily commented in Korean**. Most of the comments are dated (2026.08.24 to 2026.09.18) and give the reason behind each value, often with a "실측" measurement. So most statements below cite `index.html` line numbers directly. There are no source maps (no bundler is involved). No browser was run. I did not need REA's browser observation, because curl returned all of the content. As a result there are no screenshots and no runtime measurements.

Labels used below: **Observed** = read in the HTML/CSS/JS or measured with curl. **Inferred** = my reasoning from that evidence, not verified in a browser.

## Where the evidence lives


| File | What it is |
|---|---|
| `homeflix/index.html` (524 KB raw, 128 KB gzip; cited as `HTML:L`) | The whole page. Imweb boilerplate plus six custom code widgets |
| `HTML:1617-1949` | Hero CSS (`.hf-hero`) |
| `HTML:2753-2876` | Section 2 CSS overrides for the native Imweb text widget (gold gradient, Korean line breaks) |
| `HTML:3500-3795` / `4424-4695` / `5321-5585` / `6209-6402` | CSS for sections 3 (`.hf3`), 4 (`.hf4`), 5 (`.hf5`) and the footer (`.hff`) |
| `HTML:6884-7322` | Body markup of all sections |
| `HTML:8107-8139` | Lenis smooth-scroll setup |
| `HTML:8322-9391` | All custom section JS (hero intro, viewport-height freeze, section 3 IO reveal, section 4 three.js and ScrollTrigger, section 5 GSAP) |
| `homeflix/urls.txt`, `homeflix/transfer.txt` | The 130 resource URLs and the compressed transfer size of each (measured) |
| `homeflix/media/*` | Hero MP4, the three card photos, the AURUM logo PNG |

Inferred: Imweb splits each code widget into three parts. The `<style>` ends up in `<head>` (the custom CSS sits between Imweb's generated per-section CSS), the markup stays in place, and the `<script>` moves to the end of `<body>`. This explains why one section's CSS, HTML and JS are about 5,000 lines apart.

---

## 1. Page structure, section by section (in DOM order)

Purpose (observed: meta description and copy): the corporate site of **홈플릭스 (Homeflix)**, "Living Operation System for Physical Space" (`HTML:15`). Homeflix is a senior-housing and lifecare company whose consumer brand is "아우름 (AURUM)". The page is a brand and B2B2C landing page, not a SaaS sign-up page. The only conversion path is a consultation/contact request.

| # | Section | Key copy (brief) | Visual treatment | CTA |
|---|---|---|---|---|
| 0 | **Header** (Imweb native, `HTML:6765-6875`) | Logo plus ABOUT / HEALTHCARE / RESIDENCE / NEWS / EVENTS / CONTACT | Overlay header 70 px tall, transparent over the hero, white Poppins/Pretendard menu. It becomes fixed on scroll (`scrollToFixed`, `HTML:8250`) | Blue pill "CONTACT" (`#3208F5`, radius 9999px, 14px; hover turns it white with blue text, `HTML:331`) |
| 1 | **Hero** (`.hf-hero`, `HTML:6886-6966`) | Eyebrow "senior lifecare"; H1 "시니어 주거의 / 혁신을 설계합니다."; sub "공간을 기반으로 건강, 자산, 세금까지 연결하는…" | Full-bleed `100svh` black stage with a looping 1080p background video. Two gradient scrims (left 100° and bottom), headline at mid-left, sub and CTA at bottom-right. A **branded intro card** covers it first (see 2.1) | Glass pill "상담 신청하기 →" to `/Contact` |
| 2 | **Brand statement** (native Imweb text and button widgets, `HTML:6968-7002`) | AURUM wordmark (175 px PNG); gold line "삶의 공간을 다시 설계하는 기업"; a 36 px three-line statement "초고령화 시대에 맞는 새로운 시니어 주거 모델을 제안합니다…" | Centered on white with 70 px spacers. The gold line is a clipped 100° gold gradient (`HTML:2753-2795`). Imweb's built-in `fadeInUp` 0.7 s with 0 / 0.5 / 0.5 / 0.8 s delays | Black rectangle "회사소개 바로가기" to `/about` (hover: gold `#CDA561` with black text, `HTML:2722`) |
| 3 | **BUSINESS STRUCTURE** (`.hf3`, `HTML:7008-7064`) | H2 "공간을 중심으로 / 3가지 케어가 하나로 연결됩니다." Cards: [ HEALTHCARE ], [ RESIDENCE ], [ WEALTH & TAX ] | Rule, eyebrow and H2 opener, then **three 3:4 photo cards stepped down 0 / 32 / 64 px**. Each card has a dark scrim and a big white title at the bottom; the description unfolds on hover | Each card is a link (two internal, one to the external wealth-and-tax site) |
| 4 | **HOW IT WORKS** (`.hf4`, `HTML:7073-7140`) | H2 "공간이 스스로 / 사람을 돌보는 방식"; steps 01 측정 바이탈 프레임 → 02 분석 원격환자모니터링 → 03 연계 메디컬 컨시어지; corner tag "리빙 OS" | **Sticky, scroll-scrubbed three.js particle field** (about 26k points, grey with a blue "sensing" wave) on white. Step text sits on the left with three progress bars. This is the page's one "wow" moment | None |
| 5 | **OUR MISSION** (`.hf5`, `HTML:7149-7234`) | H2 "헌신이 아니라 데이터가 / 사람을 지킵니다."; "Since 2021"; stats 99.2 % 사고감지 정확도 · 17 개소 협약 의료기관 · 5 건 특허출원 · 56 세대 운영 레지던스 | Four **soft-neumorphic stat cards** in a 4-step staircase over a wide blue radial glow. Line icons in blue. 3D tilt and cursor glow on hover. Numbers count up | None |
| 6 | **Footer** (`.hff`, `HTML:7243-7322`) | Logo, company info `<dl>`, social pills, copyright | Dark `#14151C` slab. Logo is an inline base64 PNG made white with `filter: brightness(0) invert(1)` | "문의하기 →" (same glass pill as the hero) |

Observed IA notes:
- The same **section opener** repeats in sections 3, 4, 5 and the footer: a 1 px rule with its first 56 px in ink, then an uppercase eyebrow, then the H2, then a muted lede (`HTML:3557-3593`, `4472-4511`, `5352-5401`, `6340`). This one device makes four hand-built widgets read as one system.
- Only two CTAs, both "contact" (`/Contact`), plus the header CONTACT pill and an "about" button. There is no pricing, FAQ, testimonials or logo wall.
- Platform settings: right-click and Ctrl/Cmd+C are disabled (`HTML:9392-9405`), and the viewport uses `user-scalable=no` (`HTML:28`). Inferred: both hurt accessibility, so don't copy them.

---

## 2. Motion and interaction

### 2.1 Hero: branded intro card, honest loader, masked line reveal (CSS keyframes plus a small vanilla-JS controller)

Observed (`HTML:1769-1880` CSS, `HTML:8322-8546` JS):
- **The intro card** (`.hf-card`) is a full-screen radial gradient (`#0D0B1C → #030308 → #000`) holding the "H" logomark as an inline SVG. The SVG has a 3-stop violet gradient plus a blurred copy behind it as a halo (`feGaussianBlur stdDeviation 12`, `HTML:6926-6942`).
  - Logo "assembly": the mark sits inside an `overflow:hidden` window and rises from `translateY(100%)` to 0 over **2.2 s with `cubic-bezier(.34,.02,.16,1)`**, starting at 0.2 s. The window itself snaps to opacity 1 in 0.3 s. A comment explains why: a slow window fade would turn the reveal into a plain fade (`HTML:1825-1841`).
  - A 1 px progress line (`scaleX`, not `width`) and a tabular-nums % counter fade in at 0.7 s.
- **The loader tells the truth.** The displayed % follows `min(1, elapsed/MIN_INTRO)`, with `MIN_INTRO = 3650 ms`. It is held at **92 %** until the `<video>` fires `playing`. The number eases toward its target with frame-independent exponential damping (`shown += (target-shown)*(1-exp(-dt/0.16))`). Backstops: `MAX_WAIT 7 s` forces readiness, and reveal happens 0.7 s later (`HTML:8459-8556`).
- **Scroll lock during the intro.** Wheel, touchmove and scroll keys are blocked in the capture phase with `stopImmediatePropagation`, so Lenis never sees them, and `__lenis.stop()` is polled until Lenis exists. Exits: Esc, `reveal()`, and an 8 s `LOCK_CEILING`. The lock is skipped under reduced motion, or when the page opens already scrolled (`HTML:8366-8432`). It avoids `overflow:hidden` to prevent a scrollbar layout jump.
- **Once per tab session**: `sessionStorage.hfIntroSeen`. A return visit adds `is-revealed is-skip`, and everything appears in place with no animation (`HTML:8434-8457`, `1797-1807`).
- **Copy reveal** after the card fades out (0.8 s): every line sits in an `overflow:hidden` mask and goes from `translateY(104%)` to 0 over **1.15 s, `cubic-bezier(.19,.72,.25,1)`**, with opacity reaching 1 at 40 %. Delays: label 0.90 s, H1 line 1 at 1.40 s, line 2 at 1.60 s, sub 2.55 s, CTA 3.2 s (`HTML:1769-1787`).
- **Video**: `<video autoplay muted loop playsinline preload="auto">` with `object-fit: cover`. On mobile, `object-position` moves to 76 % (`HTML:1890`). The video is paused by an IntersectionObserver when the hero is off-screen (rootMargin 20 %), to stop decode cost on phones (`HTML:8530-8550`). A comment records that it replaced a Vimeo iframe on 2026.09.07.
- The hero pulls itself up under the header by measuring its own offset into `--hf-pull` (`HTML:8336-8363`).

### 2.2 Section 3: IntersectionObserver reveal and a hover "unfold" card

Observed (`HTML:3550-3795`, JS `HTML:8625-8643`):
- One IntersectionObserver (`threshold 0.16`, unobserves after firing) adds `.is-in`. The header block fades and rises 22 px over **1.3 s silk** (`--ease-silk: cubic-bezier(.34,.02,.16,1)`). Cards follow at **0.95 / 1.37 / 1.79 s** delays (1.15 s each). The comment explains that a 0.16 s gap read as "ripples", while 0.42 s reads as cards "arriving one by one".
- The **staircase offset is a CSS variable** (`--stagger-y`). The reveal offset (`--reveal-y`) is added on the same `translateY`, so the entrance and the layout don't fight.
- **Hover choreography with staggered timings.** The photo scales to 1.055 over 1.9 s. The scrim goes .78 → 1. The footer lifts 4 px. The description **expands with `grid-template-rows: 0fr → 1fr`**, with a comment explaining why not `max-height`. The text fades in at a 0.30 s delay. Entering takes 1.30 s and leaving 0.78 s (`--t-enter` / `--t-leave`).
- Touch: `@media (hover:none)` and ≤980 px always show the description (`HTML:3767-3786`).

### 2.3 Section 4: sticky three.js particle "film" scrubbed by ScrollTrigger (the centrepiece)

Observed (CSS `HTML:4455-4695`, JS `HTML:8645-9188`):
- **Layout**: `.hf4-hdwrap` is `height:100vh`, and inside it the opener is `position:sticky; top:clamp(72px,11vh,132px)`. `.hf4-track` is `height:300vh; margin-top:-103vh`, overlapping the opener so the dots rise behind it. `.hf4-stage` is `position:sticky; top:0; height:100svh`. Net pinned scrub length is ≈ 200vh for three steps (inferred from the heights).
- **Opener crossfade, no ScrollTrigger**: a rAF-throttled scroll handler computes progress `t` across the sticky distance and applies three independent smoothstep phases. Dots rise 30 px over 0–0.34. Step text rises 175 px and fades in over 0.30–0.78. The opener fades out, lifts −18 px and scales to 0.99 over 0.30–0.60. The **different travel of canvas (30 px) and text (175 px) creates the parallax** (`HTML:8690-8780`). It returns early when off-screen to avoid forced layout, and caches the sticky `top`.
- **three.js r160 `THREE.Points` with a custom `ShaderMaterial`** (`HTML:8863-9040`):
  - 20,000 core points plus a 30 % halo on desktop; 9,000 plus halo at ≤980 px. The disc is sampled with `sqrt(random)` for uniform density. Halo radius uses `pow(random, 4)` beyond the field, so the edge dissolves.
  - The vertex shader adds: an expanding "sensing" ring (`band`, phase `fract(uTime*0.055 + uFlow*1.1)`) that lifts and enlarges points; a focus cluster at (2.2, 0.5) that lights up in step 02 (`uFocus`); and in step 03 (`uRoute`) that cluster flows along three direction vectors (담당자 / 보호자 / 의료진). Points also breathe slowly per seed.
  - Colour mixes between dormant `#B4B7C6` and sensed `#3208F5`. Round points come from `gl_PointCoord` with a smoothstep edge. `NormalBlending` is used because additive blending blows out on white.
- **Scroll driver**: `ScrollTrigger.create({ trigger: track, start:'top top', end:'bottom bottom', scrub: 1.1 })`. `onUpdate` only records `state.p`, toggles the active step at 0.34 and 0.67, and fills three `scaleX` progress bars (`HTML:9138-9162`).
- **Smoothing**: there is one `damp(current,target,tau,dt)` (exponential, frame-rate independent) per value: flow τ 1.05, camera 0.85, focus 0.85 over smoothstep(0.24, 0.52), route 1.25 over smoothstep(0.62, 1.0). A comment says per-update `gsap.to(..., overwrite)` tweens caused stutter and were removed (`HTML:9058-9100`).
- **Camera**: FOV 46. It moves along an arc: far (y 5.6, z 14.2) → closer and lower mid-story → slight pull-back, always looking at (0, .25, 0).
- **Rendering hygiene**: `antialias:false`, alpha canvas, DPR capped at 2, `uPix` scaled by DPR. The scene renders on `gsap.ticker` only while an IntersectionObserver (rootMargin 100 %) reports it on-screen. The ticker sleeps on `visibilitychange`. Resizes are ignored when only the height changes on coarse-pointer devices (`HTML:9110-9188`).
- **Fallback**: if motion is reduced, WebGL is missing, or THREE/gsap/ScrollTrigger is missing, the section gets `.is-static`. Sticky is removed and the three steps become a plain 3-column grid with a top hairline (`HTML:4656-4695`, `8826-8841`).
- Scrims: a left white wash (100°) behind the text and a white vignette on the right and bottom, so the dots fade into the page (`HTML:4534-4556`).

### 2.4 Section 5: GSAP entrance, count-up, 3D tilt and cursor glow

Observed (CSS `HTML:5403-5585`, JS `HTML:9244-9391`):
- A tiny `hfGsapReady` loader injects GSAP only if it is not already present. A comment notes that loading ScrollTrigger twice split the trigger registry (`HTML:9244-9284`).
- **The hidden state is set by JS (`gsap.set`), never by CSS**, so if GSAP fails the content stays visible.
- Header: `start:'top 85%'`, `once:true`, then opacity and y 22 → 0, 1.3 s `sine.out`. "Since" counts up 1999 → 2021.
- Grid: starts at `rotationX:7, y:34, transformOrigin:'50% 100%'` (it "stands up"), 1.35 s `power3.out`. Cards stagger 0.14 s, 0.95 s `power2.out`. Stats count up over 1.6 s `power2.out` with `toFixed(dec)` (`HTML:9318-9355`).
- **Tilt**: `gsap.quickTo` on rotationX/Y (±5°) and z 18 px, 0.8 s `power2.out`. Each card has its own `perspective: 900px` and the panel has `perspective: 1800px`. In the same handler, `--mx/--my/--glow` drive a `::after` radial blue glow (`HTML:5462-5481`). This is only enabled for `(hover:hover) and (pointer:fine)`.

### 2.5 Libraries, smooth scroll, reduced motion, mobile

| Item | Observed config |
|---|---|
| **Lenis 1.1.18** (`HTML:8106-8139`) | `duration 1.4`, `smoothWheel:true`, `syncTouch:false` (native touch inertia kept), easing `min(1, 1.001 − 2^(−10t))` (expo-out). Exposed as `window.__lenis` and driven by its own rAF loop. In-page `#` anchors go through `lenis.scrollTo(target,{offset:-80})`. Skipped entirely under `prefers-reduced-motion` |
| **GSAP 3.12.5 + ScrollTrigger** | Plain `<script>` tags from jsDelivr (`HTML:8246-8247`). `ScrollTrigger.config({ignoreMobileResize:true})`. Lenis is bridged with `lenis.on('scroll', ScrollTrigger.update)`, deliberately *not* with `gsap.ticker` (to avoid calling `lenis.raf` twice) |
| **three.js 0.160.1** | `three.min.js` UMD from jsDelivr, used only by section 4 |
| Imweb native | jQuery `smoothScroll` on anchors (1200 ms easeInOutExpo, `HTML:8170-8174`) and animate.css `fadeInUp` for section 2 widgets (`SITE_ANIMATION.init`, `HTML:9427`). `gambit-smoothscroll`, `ThreeCanvas.js` and `snow.js` are loaded by the platform; I found no call to them in the page (inferred unused) |
| Not present | No Framer Motion, Barba or page transitions, no Lottie/Rive/Spline, no marquee, no custom cursor (only the card-local cursor glow) |

- **Reduced motion** is handled in every block. Hero: keyframes become 0.01 ms, and the logo is shown assembled. Section 3: transitions off and descriptions open. Section 4: `.is-static`. Section 5: GSAP does nothing. Footer: no arrow nudge. Lenis and the scroll lock are not started.
- **Mobile viewport-height freeze** (`HTML:8564-8622`, duplicated with a guard at `9195-9240`): a fixed probe measures `100vh` and `100svh` once and writes `--hf-vh/--hf-svh`. It re-measures only when the width changes (orientation change). The comments measured a document bounce of ±365 px from the URL bar. The hero and the section 4 heights use these variables at ≤980 px.
- Breakpoint: **980 px** is used site-wide by the custom code. Container queries (`cqw`) are used in the hero (`container-type: inline-size`).

---

## 3. Design tokens

Each widget **redeclares the same tokens on its own root class** (`.hf-hero`, `.hf3`, `.hf4`, `.hf5`, `.hff`). There is no global sheet. Inferred: this is because every Imweb code widget must be self-contained and paste-able.

### 3.1 Colours

| Role | Hex | Where |
|---|---|---|
| Brand / accent blue | **`#3208F5`** | `--blue`, theme-color meta, header CTA, CTA hover fill, step numbers, progress bars, icons, "sensed" dots, glows `rgba(50,8,245,.10–.55)` |
| Ink | `#14151C` | Headings, rule accent; also the footer background (`--ground`) |
| Muted | `#6E6C79` | Eyebrows, ledes, step descriptions |
| Hairline | `#E4E3EA` | Rules, empty progress bars |
| Panel | `#F5F6F9`; card gradient `#FAFBFD → #F5F6F9 → #F0F2F7` | Section 5 stat cards (with a comment about WCAG 4.59:1 for muted text on the darkest stop) |
| Dormant dots | `#B4B7C6` | Section 4 particles |
| Footer dim | `#9C9AAA`; hairline `rgba(255,255,255,.13)` | Footer labels and links |
| Card base | `#17182D` | Section 3 card background behind photos |
| Intro dark | `#0D0B1C`, `#030308`, `#000` | Intro card radial |
| Logomark gradient | `#B9AFFF → #4A22F0 → #1B0A72`, halo `#4526F5` | Intro SVG |
| Loader digits | `#C6C1DA` | |
| AURUM gold | gradient `#8F6B22 · #977023 · #9F7725 · #A97E28 · #AE8229` (symmetric), fallback `#9F7725`; button hover `#CDA561` | Section 2 only (the sub-brand) |
| Surfaces | `#FFFFFF` (sections 3–5), `#000` (hero) | |

### 3.2 Fonts

- **Pretendard Variable** (jsDelivr `orioncactus/pretendard@v1.3.9`, dynamic-subset), with the fallback stack `"Apple SD Gothic Neo", "Malgun Gothic", -apple-system, sans-serif`. Each widget `@import`s it **and** `<link>`s it (a comment explains that without it the system fallback has no weight 800) (`HTML:1617-1621`).
- Imweb also loads its own Pretendard static and variable subsets plus Poppins (`HTML:61`). The header menu uses `Poppins, Pretendard` (`HTML:196`). Inferred: three Pretendard CSS sources are duplicate work.
- Weights in use: 400 body, 500 step names, 600 CTA, 700 H2 and stat labels, 800 eyebrows, hero H1, card titles and numbers.

### 3.3 Type scale (as used)

| Role | Size | Weight / line-height / tracking |
|---|---|---|
| Hero H1 | `clamp(26px, 3.85cqw, 62px)`; mobile `clamp(26px, 7.2cqw, 40px)` | 800 / 1.32 / −.015em |
| Section H2 | `clamp(24px, 3vw, 48px)`; ≤980 `clamp(24px, 7vw, 30px)`; `text-wrap: balance`, `max-width: min(860px, 62%)` | 700 / 1.32 / −.015em |
| Big step name (section 4) | `clamp(30px, 3.4vw, 54px)` | 500 / 1.32 |
| Stat number | `clamp(34px, 3.4vw, 54px)`, tabular-nums; unit `.36em` 700 muted | 800 / 1 |
| Card title (section 3) | `clamp(25px, 2.1vw, 37px)` | 800 / 1.32 |
| Stat label | `clamp(20px, 2vw, 28px)` | 700 / 1.32 |
| Brand statement (section 2) | 36px (Imweb inline span) | theme / 1.5 |
| Lede | 22px, `max-width: 62ch`, muted | 400 / 1.5 |
| Eyebrow | 20px uppercase muted | 800 / 1.4 |
| Body / description | 18px (13px for mobile card descriptions) | 400 / 1.5 |
| CTA | `clamp(13px, 1.06cqw, 16px)` | 600 / 1 / −.005em |
| Small label | 13px (Since, step num `clamp(11px,.85vw,13px)`), card tag 15px +.06em | 800 |

Global text rule: `word-break: keep-all` on every section, plus `overflow-wrap: break-word` as a safety net, so Korean breaks only at spaces. There is a `<br class="brk-pc">` pattern for desktop-only line breaks (hidden at ≤980 px). For section 2 the logic is reversed: all `<br>` are hidden at ≥981 px and mobile breaks are entered with Shift+Enter in the editor (`HTML:2831-2873`).

### 3.4 Layout, spacing, radii, shadows, motion

- **Grid**: `--grid-max: 1650px`, `padding: 0 24px` (24 px on mobile too). Every custom section breaks out of the Imweb container with `width:100vw; margin-left:calc(50% - 50vw)` and re-centres internally, so all left edges align. A comment notes a 7 px misalignment that this fixed.
- **Section padding**: `clamp(56px, 6vw, 96px)` top / `clamp(60px, 7vw, 120px)` bottom. Opener-to-content gap: `clamp(48px, 5.5vw, 88px)`.
- **Grids**: section 3 has 3 columns, gap `clamp(14px,1.4vw,20px)`, stepped +32 px per card. Section 5 has 4 columns, stepped by `clamp(14px,1.6vw,24px)` per card, with `align-items:start`. Both drop to 1–2 columns with no stagger at ≤980 / ≤560 px.
- **Radii**: 16 px (photo cards), 18 px (stat cards), 999 px (pills), 2.6–4.8 (icon strokes).
- **Shadows**:
  - Glass CTA: `0 6px 26px rgba(0,0,0,.28)`, `backdrop-filter: blur(14px) saturate(150%)`, `rgba(255,255,255,.14)` fill with a `.42` border. On hover it fills with blue and gets `0 8px 30px rgba(50,8,245,.5)`.
  - Stat cards: neumorphic pair `-10px -10px 22px #fff(.95)` + `14px 16px 32px -14px rgba(20,21,28,.22)` + blue under-glow `0 22px 40px -26px rgba(50,8,245,.42)` + two inset highlights.
- **Easing**:
  - `--ease-silk: cubic-bezier(.34,.02,.16,1)`. This is the house curve: a slow start then a long glide. Comments repeatedly reject ease-out curves as making things "pop".
  - `--ease-rv: cubic-bezier(.19,.72,.25,1)` for mask reveals.
  - `--ease-out: cubic-bezier(.16,1,.3,1)` for button micro-interactions.
  - Lenis expo-out. GSAP `sine.out`, `power2.out`, `power3.out`.
- **Durations**: entrances 1.15–1.35 s; hover enter 1.3 s and leave 0.78 s; button 0.28 s; step crossfade 0.7 s.
- **Signature device**: the 56 px ink segment on a 1 px hairline rule (`linear-gradient(90deg, ink 0 56px, hair 56px)`).

---

## 4. Tech stack, page weight, loading

**Stack (observed):**
- **Imweb (아임웹)** hosted site builder: `Set-Cookie: IMWEBVSSID`, `doz_*` markup, `vendor-cdn.imweb.me`, nginx behind CloudFront ICN. The HTML is `no-cache, must-revalidate` and was a CloudFront Miss.
- The legacy platform stack loads on every page: jQuery, jQuery UI, Bootstrap 3, owl/slick carousels, moment-with-locales, lodash, shop/member/booking/CRM SDKs, Datadog RUM, Naver analytics, Kakao postcode and the `fo-shopping` and `fo-chat` web components.
- **Custom layer, hand-written in code widgets**: vanilla JS (ES5 style, IIFEs), Lenis 1.1.18, GSAP 3.12.5 + ScrollTrigger, three.js 0.160.1 (all from jsDelivr, version-pinned). Hero video on Cloudinary. Inline SVG icons.
- Inferred: the dated comments ("요청", "사용자 확인", "실측") read like an AI coding assistant iterating with a non-developer owner, who pastes each section into Imweb code widgets. The content edits that the owner does in the editor are documented in the comments (`HTML:2843-2873`).
- JSON-LD Organization only (`HTML:6456-6470`).

**Weight (compressed bytes as served; measured, `homeflix/transfer.txt`):**

| Part | Size | Note |
|---|---|---|
| HTML | **128 KB** (524 KB raw) | About 174 KB raw is custom code, of which roughly **73 KB is comments** (estimated by line heuristics). The footer logo is a 19 KB base64 PNG inline |
| JS | **≈ 1.86 MB over 96 files** | Platform JS dominates. `jquery-ui.design.js` alone is **694 KB served uncompressed** (no Content-Encoding), plus `site_shop.js` 129 KB and moment-with-locales 106 KB. The custom libraries are about 212 KB (three 162 KB, gsap 28 KB, ScrollTrigger 18 KB, Lenis 3.7 KB) |
| CSS | ≈ 546 KB over 25 files | Imweb vendor and site CSS. The Pretendard static subset CSS (127 KB) is requested under two URLs (with and without a query string) |
| Images | ≈ 537 KB | Three card photos: **baseline JPEG ≈ 166–176 KB each** (1200×1600, and the healthcare one 1280×720 with white side bars, which explains the `background-position: 31.7%` hack, `HTML:3642-3651`). Served as JPEG even with `Accept: image/avif,image/webp`. CSS backgrounds, so no lazy-loading, srcset or alt text |
| Video | **2.56 MB** | `hero_main_web.mp4`, H.264 1920×1080, **12.0 s loop** (≈ 1.7 Mbps), faststart (`moov` before `mdat`). There is **no `poster`**, no mobile or WebM variant and no Cloudinary `f_auto/q_auto`. `preload="auto"` |
| Fonts | not measured | Pretendard dynamic-subset woff2 slices load on demand |
| **Total** | **≈ 5.6 MB before fonts** | Plus modules that `boot.mjs` and the web components load at runtime (not measured) |

**Loading strategy (observed):**
- The intro card hides the video load behind a branded, honest progress bar. Inferred: this turns the slow 2.5 MB first paint into "intro". But the scroll lock (up to about 4–8 s on first visit) is a real cost for impatient users.
- The custom libraries are synchronous `<script>` tags at the end of `<body>`, with no `defer` or module splitting. three.js loads even for users who never scroll to section 4 and even when the section falls back to `.is-static`.
- Work is gated by visibility: the video pauses off-screen, WebGL renders only within ±1 viewport, the scroll handler returns early off-screen, and the ticker sleeps when the tab is hidden.
- Hashed CDN libraries use immutable caching (jsDelivr `max-age=31536000, immutable`). The HTML is never cached.

---

## 5. Takeaways for our two landing pages

### 5.1 What makes it feel polished (observed techniques)

1. **One accent, used as light.** A single electric violet-blue (`#3208F5`) against ink, white and a dark hero. The blue appears only where something "happens": CTA hover, step numbers, progress, sensed particles, under-glows. Surfaces stay neutral. This makes the page feel engineered and calm.
2. **A shared section grammar**: rule with a 56 px ink tick → eyebrow → H2 → lede, the same grid edge everywhere, and staircase grids in sections 3 and 5. These are four separate widgets, but they read as one designed system.
3. **A slow, gliding easing language**: `cubic-bezier(.34,.02,.16,1)` with 1.1–1.3 s entrances, long stagger gaps (0.42 s), separate enter and leave durations, and hover elements that start at different times. Motion reads as "settling", not "popping".
4. **One real centrepiece instead of many effects.** Section 4 is a narrative particle scene (measure → analyse → connect) that turns an abstract product (radar sensing, then RPM, then concierge) into a visual story. A cheap points shader carries most of the effect.
5. **A cinematic hero entrance**: a logomark rising from a masked window, a loader that holds at 92 % until the video actually plays, and masked line-by-line headline reveals.
6. **Unusually careful engineering for a site builder**: reduced-motion and no-WebGL fallbacks that keep all content; the GSAP hidden state set only by JS; mobile URL-bar height freezing; off-screen pausing; DPR caps; WCAG contrast numbers in comments; ≥44 px hit targets.

### 5.2 Worth borrowing for a product landing page

- **The scroll-scrubbed "how it works" stage**: a sticky stage (`track 300vh`, `stage 100svh sticky`), a ScrollTrigger that **only records progress**, and per-value exponential `damp()` in the render loop (no tween churn). Add three crossfading step blocks with segmented `scaleX` progress bars and a static 3-column fallback. A particle field is one option; the same rig can drive product screenshots, a 3D model or SVG.
- **A points shader with an "event" story**: a uniform disc with a dissolving halo, a travelling wave, a focus cluster, then particles flowing outward. This is a good abstract visual for data and AI products (signal → detection → action). Keep `NormalBlending` on light backgrounds and cap point counts on mobile.
- **An honest intro loader** tied to a real readiness signal (video `playing`, or textures loaded) with a hold percentage and a once-per-session skip. Prefer a short or skippable lock, or no lock at all.
- **The mask line reveal** (`overflow:hidden` + `translateY(104%)`) and the **`grid-template-rows: 0fr→1fr`** hover unfold.
- **Soft-neumorphic stat cards** with a blue under-glow, a `quickTo` tilt, a cursor-tracked radial glow driven by CSS variables, and count-ups. Gate them on `(hover:hover) and (pointer:fine)`.
- **The glass pill CTA** (backdrop blur, a translucent fill and border, accent fill on hover, a 4 px arrow nudge), reused identically in the hero and the footer.
- **Mobile hygiene snippets**: freeze `--vh/--svh` on width change only; `ScrollTrigger.config({ignoreMobileResize:true})`; skip resize work when only the height changed on coarse pointers; bridge Lenis with `lenis.on('scroll', ScrollTrigger.update)`, not a second `raf`.
- **Avoid**:
  - Shipping comments and inline base64 in production.
  - Hosting on a builder whose platform JS (≈1.6 MB, including an uncompressed 694 KB file) outweighs the design.
  - A 1080p video with no poster or mobile variant.
  - JPEG backgrounds with no `srcset`.
  - Loading three.js eagerly.
  - Disabling copy and zoom.
  - A first-visit scroll lock.

### 5.3 Not verified

- I did not render the page. I did not see the visual result, the actual frame rate, the intro duration in practice, or how the particle scene looks. Everything in sections 2.1–2.4 is read from the code, and the timings are the coded values.
- I did not view the hero video content (no frame extraction tool was available). I know only its container metadata.
- Whether Imweb's `gambit-smoothscroll`, `ThreeCanvas.js` or `snow.js` do anything automatically, and whether Imweb's jQuery `smoothScroll` and the Lenis anchor handler both fire on `#` links, was not checked at runtime.
- The dynamically loaded modules (`boot.mjs`, `fo-shopping`, `fo-chat`) and the font slices are not included in the weight totals. The comment-byte figure is a heuristic estimate.
- I did not analyse the subpages (`/about`, `/healthcare`, `/residence`). The comments say they share the same token values.
