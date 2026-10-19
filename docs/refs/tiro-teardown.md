> 원본: 2026-10 REA 세션의 정적 리버스엔지니어링 노트(tiro-findings.md)를 그대로 보존한 사본. 사이트가 sourcesContent 포함 소스맵을 공개하고 있어 원본 TSX 기준으로 인용됨. 브라우저 실행·계측은 하지 않음(§5.4). 인용 경로는 당시 로컬 사본 기준이라 이 레포에는 없다.
> 대상: https://tiro.ooo/ko/

# How tiro.ooo/ko is built (reverse-engineering notes)

How the work was done: I downloaded the HTML, CSS, JS chunks and images with curl (2026-10-16) and read them without running any of the site's code. **The site serves full source maps with `sourcesContent`** (every `/_next/static/**.js.map` and the CSS map returned 200), so most statements below cite the original TypeScript/TSX files, not minified code. I unpacked the maps with `scratchpad/tools/unmap.py` (node_modules excluded). No browser was run, so there are no screenshots and no runtime measurements. REA's browser observation was not needed because the page is server-rendered, and the source maps answered the motion questions directly.

Labels used below: **Observed** = read in HTML/CSS/source or measured with curl. **Inferred** = my reasoning from that evidence, not verified in a browser.

## Where the evidence lives


| File | What it is |
|---|---|
| `tiro/index.html` (1,024 KB raw, 279 KB compressed) | SSG HTML. 142 KB markup, 674 KB `__NEXT_DATA__` (i18n strings) |
| `tiro/outline.txt` (cited as `OUT:L`) | A tag/class/text outline of `<body>` made by `tools/outline.py` |
| `tiro/nextdata.json` | `__NEXT_DATA__`, pretty-printed |
| `tiro/src/src/components/pages/Global/**` | **Original landing source** from the source maps (cited by file:line) |
| `tiro/src/src/pages/index.tsx` | Next.js Pages Router page with `getStaticProps` |
| `tiro/src/__/packages/tds/dist/stylesheet.css` | "TDS" (Tiro Design System) token sheet, 35 KB |
| `tiro/css/6023872b24fc3c37.css` | Compiled Tailwind + TDS + fonts + KaTeX, 381 KB raw / 62 KB compressed |
| `tiro/maps/*.map`, `tiro/js/*`, `tiro/media/*` | Raw maps, chunks and sample images |
| `tiro/transfer.txt`, `tiro/media.txt` | Compressed transfer sizes I measured |

---

## 1. Page structure, section by section (in DOM order)

The whole page is `GlobalPage` = `GlobalHeader` + `GlobalContent` + `GlobalFooter` (`Global/index.tsx`). The content is all in one 722-line component, `Global/Content/index.tsx`. **No section uses scroll-driven animation.** The visual rhythm comes from alternating background surfaces: cream → white → cream feature cards → dark-brown band → dark-brown security block → white pricing → white FAQ → dark-brown footer.

| # | Section (id) | Purpose | Key copy (KO, exact) | Visual treatment | CTA |
|---|---|---|---|---|---|
| 0 | Header `nav.fixed` (`Header/index.tsx:56`) | Navigation | 제품 소개 · 가격 안내 · 도입 견적 · 사용 가이드 · 블로그 · 언론 보도 · 개발자 문서 · 앱 다운로드 | Fixed bar, 76 px tall on mobile and 64 px on `sm`+. Cream `bg-baseWarm`, `backdrop-blur-sm`, hairline bottom border. Logo is a CSS `mask-image` span, so it can be recoloured | "로그인" (text button), "도입 문의" (dark-brown pill) |
| 1 | Hero `#hero` (`HeroSection/index.tsx:111-152`) | Value proposition | Trust chip "ISO/IEC 27001:2022 · SOC 2 Type 2" → sub-line "대화에만 집중할 수 있게," → H1 "가장 정확한 AI 회의록" → "실시간 요약 · 다국어 동시 번역으로 자신있게 대화하고 / 원하는 양식의 문서를 **3초 만에 완성**하여 공유해보세요" | Centred text only on a cream page (`--tds-color-stone-cream #fffef7`). H1 is 30→64 px, bold, `tracking-[-0.045em]`, `leading-[1.04]`. The trust chip is a pill whose arrow slides on hover | **OS-aware CTAs, rendered only on the client** (see 2.6): "무료로 시작하기" (filled brown pill) + "{macOS/Windows 앱} 다운로드" (outlined pill). On mobile: "iOS 앱/Android 앱 다운로드" + "데스크탑 앱 다운로드" |
| 2 | Product demo (`ProductDemo/index.tsx`, 1,300 lines) | Shows the product working | Note "Untitled" → auto-titled "티로 제품 소개 회의". Tabs 문서/원본 and 요약/스크립트. Ask Tiro panel "무엇을 도와드릴까요?" with chips 핵심 내용 요약 / 할 일 정리 / 결정사항 정리 / 한 줄 요약 | **A fully HTML/React fake of the web app**, not a video or image: macOS traffic-light dots (`--landing-signal-*`), lucide icons, `rounded-[20px]` shell, `h-[780px]`, `max-w-7xl`. It plays a scripted meeting (details in 2.1) | Inside the demo: "기록 종료" with tooltip "이제 기록을 종료해보세요", then "다시 보기" |
| 3 | Customer logos (`Content/index.tsx:153-170`) | Social proof | "이미 **300+개 기업**이 티로와 함께합니다" (accent word in brown `fg-primary`, the rest grey) | Two opposite-direction CSS marquees of grayscale logos with edge-fade masks (2.2). Logos are next/image PNG/SVG/WebP | — |
| 4 | Testimonials `#testimonials` (`TestimonialsSection/index.tsx`) | Social proof | Six quotes. Example: "티로 사용 후로 미팅의 질이 달라졌습니다…" — 조유진, 스마일게이트인베스트먼트 팀장 | Arrow-driven carousel of `bg-subtle` cards (180→300 px wide), white gradient edge fades, round avatars | Prev/next buttons |
| 5 | Key feature 1 `#key-features-1` (`:255-339`) | Accuracy + translation | H2 "언제 어디서나, 어떤 언어든 걱정 없어요"; H3 "고품질 실시간 기록 & 완벽한 요약 노트" (+5 check bullets, e.g. "발화 0.5초 이내 텍스트 변환"); H3 "15+개 언어 실시간 번역 & 다국어 동시 기록" | 2-col grid. Each card is **an image (PNG screenshot/composite) on an amber-50 `#fffbeb` card**, `rounded-xl`, `aspect-[16/10]`, with the image anchored to the bottom so it looks like it "rises" out of the card. Images are localised per locale (ko/en/ja imports) | — |
| 6 | Key feature 2 `#key-features-2` (`:342-401`) | Works on every device | H2 "모든 디바이스, 모든 대화 상황에서"; list "앱 설치 없이도 바로 사용 가능한 **웹 브라우저**" / "…**데스크탑 앱**" / "…**모바일 앱**" | Grid `0.8fr 1fr`: device composite image on amber card plus a check list with bolded nouns via `<Trans>` | — |
| 7 | Key feature 3 `#key-features-3` (`:404-502`) | Templates / auto-documents | H2 "매일 쌓이는 기록을 가치있는 자산으로 만들어드려요"; "내가 원하는 양식 그대로, 3초 만에 문서 완성"; H4 "원클릭 템플릿", "나만의 템플릿 만들기" | Two equal image cards (`object-cover`, 240/300/330 px tall) with captions below | — |
| 8 | Key feature 4 `#key-features-4` (`:505-587`) | Sharing + integrations | H2 "중요한 대화를 필요한 곳에 자동으로 전해드려요"; H3 "더 쉬운 협업, 회의 이후 공유까지도 한 번에"; H3 "캘린더·워크스페이스·사내 메신저·CRM·ATS 연동" | Same card pattern. The integrations card is a static grid of third-party app icons (Notion, Slack, Confluence, Teams, Outlook, Google Calendar/Meet, HubSpot…) — `media/global-keyfeature4-workflow.png` | — |
| 9 | Ask Tiro band (`:590-614`) | AI Q&A feature | "모든 대화를 지식으로 바꾸는 Ask Tiro" | **First dark section**: full-bleed `bg-primary` (brown-800 `#3d261c`). Phone-style screenshot with a bottom gradient fade into the band colour (`from-tds-bg-primary`) | — |
| 10 | Security `#security` (`SecuritySection.tsx`) | Enterprise trust | "보안 및 개인정보 보호"; six cards (데이터 전면 암호화 · 철저한 접근 제한 · 음성·데이터 즉시 폐기 · AI 모델 재학습 이용 금지 · …); "국제 보안 인증 취득"; second list in amber-100 headings (SSO/MFA, RBAC/SCIM, IP whitelisting, hotline) | A 240–360 px **photo banner** (amber sunset with a halftone dot screen, `media/security-bg.png`, used as CSS `background-image`) under an `amber-300/55 → amber-500/30 → brown` gradient, so it melts into the dark section. Glass cards: `border-white/10 bg-white/[0.08] backdrop-blur-[2px]`. ISO and SOC2 badge PNGs | "엔터프라이즈 문의" (amber-100 button) |
| 11 | Pricing `#pricing` (`PricingSection.tsx`) | Plans | "가격 안내" / "다양한 플랜으로 제공되는 티로를 만나보세요"; free-trial card "무료로 시작하고, 유연하게 확장하세요" / "3주간 최대 300분의 무료 체험을 드려요"; 개인용 Lite/Pro/Max; 기업용 팀 플랜/엔터프라이즈 | Monthly/annual toggle (Radix switch). **Prices are fetched on the client** (`useSubscriptionPlansInDisplay`, `:294`); the SSR HTML has `animate-pulse` skeletons (`:194`). Max and Team CTAs are filled brown; the others are outlined | "무료 체험 시작하기", "시작하기", "팀플랜 시작하기", "문의하기" |
| 12 | FAQ `#faq` (`:627-722`) | Objection handling | "자주 묻는 질문" / "티로에 대해 더 알고 싶으신가요?"; 8 Qs, e.g. "화상회의도 기록할 수 있나요?" | Accordion with hairline top borders, `max-h` + opacity transition at 300 ms. The first item is open by default. The same keys also feed `FAQPage` JSON-LD (`pages/index.tsx`) | Inline "[문의하기]" opens a contact popup |
| 13 | Final CTA `#final` (`SubHero`) | Repeat the hero | Tiro symbol + "대화에만 집중할 수 있게," + "가장 정확한 AI 회의록" (50 px) | Hero bookend, centred on white | Same OS-aware CTAs (client-rendered) |
| 14 | Footer (`Footer/index.tsx`) | Links + legal | Columns 프로덕트 / 개발자 도구 (API, CLI, MCP Server, Webhook) / 서비스 비교 (Tiro vs CLOVA Note, 다글로, Plaud, Otter.ai, Fireflies, tl;dv) / 고객 지원 / 약관·보안 | Dark brown with a 22 px **dot-grid** (`radial-gradient` 1 px dots, 8% white) masked by a radial ellipse. A hand-drawn **signature line SVG** across the top draws in on view (2.3). Serif tagline "We make something wonderful." Language drop-up | — |

Media types used (observed): **no `<video>`, no `<canvas>`, no Lottie/Rive/Spline/three.js on this page.** Product visuals are (a) the live HTML demo and (b) static PNG composites served through next/image. Illustrations are limited to the security photo and the footer SVG path. (The CSS includes the whole web app's styles — KaTeX, many fonts — because the landing shares one Next.js app with the product.)

---

## 2. Motion and interaction

### 2.1 The hero product demo: a scripted state machine, not a video

- **State machine** (`ProductDemo/timeline.ts:5-54`): `recording → paused → generating → done`, plus `REPLAY`. Steps alternate per paragraph: odd step = raw transcript typing, even step = that paragraph collapses into a heading + bullet summary.
- **Timing constants** (`ProductDemo/index.tsx:70-75`): `CHAR_MS=18` (typewriter speed), `RAW_HOLD_MS=700`, `SUMMARY_HOLD_MS=1300`, `GENERATING_MS=1900`, `ASK_THINKING_MS=1400`. The KO script has 3 paragraphs of 281–292 characters, so auto-play runs about **21.5 s** and then stops at `paused`.
- **Driven by `setTimeout`/`setInterval` in effects** (`:136-158`), not by scroll. It starts on mount and does not use an IntersectionObserver (observed). Inferred: a visitor who scrolls slowly may arrive mid-script, and it runs while off-screen.
- **Typewriter** (`:610-630`): a `setInterval` that adds 1 character every 18 ms. With reduced motion it shows the full text at once.
- **"Paragraph completed" highlight** (`:493-519`, framer-motion): a new summary block fades and rises (`opacity 0→1, y 10→0, 0.35 s easeOut`). A brand-tinted wash sweeps left→right (`scaleX 0→1` in 0.6 s, `transformOrigin:left`, then fades out over 0.8 s after a 0.6 s delay), and a 2 px left accent bar fades out. **This is the most borrowable micro-interaction on the page.**
- **Follow-the-bottom auto-scroll** (`AutoScrollArea`, `:406-423`): a 250 ms interval pins `scrollTop` to the bottom, but only while the user is within 40 px of the bottom. Scrolling up releases it, like a chat log.
- **Fake audio level meter** (`LevelDots`, `:1131-1150`): 5 bars, each with a 7-keyframe height array, `duration 2.2 s, repeat Infinity, easeInOut`, staggered by `i*0.12 s`.
- **Call to interact**: at `paused`, an "기록 종료" pill slides in (`x -8→0, 0.4 s`) with a tooltip "이제 기록을 종료해보세요" (`:955-971`). Clicking it shows a spinner "티로가 문서를 정리하고 있어요" for 1.9 s. Then a one-page document reveals with staggered paragraphs (`0.65 s`, `delay (i+1)*0.22 s`, `:781-797`), and the note title changes from "Untitled" to "티로 제품 소개 회의". "다시 보기" replays.
- **Ask Tiro chips** play a canned Q&A after a 1.4 s "답변을 작성하고 있어요" state (`:1215-1237`).
- Script content lives in `ProductDemo/script.ts` per locale, and it can be swapped through a `script` prop (the comment mentions a lecture-campaign variant).
- Every click is logged (`useActionLog`), so the demo also acts as an engagement probe.

### 2.2 Logo marquee (pure CSS)

- `@keyframes customer-logo-marquee { 0% {translateZ(0)} to {translate3d(-50%,0,0)} }` plus a reverse variant (compiled CSS). Linear and infinite, with `animation-duration:60s` inline.
- The track renders **2 copies × (logos doubled)**, and the second copy is `aria-hidden` with empty `alt` (`Content/index.tsx:109-147`). This makes the −50% loop seamless.
- The edge fade is a mask: `mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent)`.
- Logos are `grayscale opacity-85`, becoming `grayscale-0 opacity-100` on hover (300 ms).
- `motion-reduce:animate-none` stops the marquee.

### 2.3 Footer signature line (IntersectionObserver + clip-path)

`Footer/index.tsx:78-125, 653-690`: a single cubic Bézier SVG path (`viewBox 0 0 1200 120`, `preserveAspectRatio="none"`, `vector-effect:non-scaling-stroke`, stroke brown-300, 2.5 px).

1. JS adds `sig-armed`, which sets `clip-path: inset(0 100% 0 0)`.
2. When the band is ≥25% visible, the IntersectionObserver adds `sig-drawn`. This transitions `clip-path` to `inset(0)` over **1.5 s `cubic-bezier(.22,1,.36,1)`**, then the observer disconnects.

With reduced motion the observer never arms, and CSS also clears the clip.

### 2.4 Smaller interactions

- Testimonials carousel (`TestimonialsSection/index.tsx`): measures `offsetLeft` of each card on resize, centres the active card, clamps, and applies `translate3d(-x)` with `transition-transform duration-500 ease-out` and `will-change-transform`. It loops at the ends. There is no autoplay and no swipe handler (observed: only buttons).
- Hero trust chip: `hover:brightness-[0.96]` plus the arrow `group-hover:translate-x-1` (300 ms ease-out), with `motion-reduce:transform-none`.
- Buttons: `hover:opacity-80 transition-opacity duration-200` everywhere. This is a deliberately plain hover language.
- FAQ: `transition-all duration-300 ease-in-out` on `max-h-0 ↔ max-h-96` plus opacity.
- Pricing skeleton: `animate-pulse` until the plans API resolves.

### 2.5 Libraries, scroll, reduced motion, mobile

- **framer-motion** is the only animation library, and it is used only inside the ProductDemo. Observed: no GSAP, ScrollTrigger, Lenis, Locomotive, `useScroll`, `whileInView` or `useInView` in the app source (grep over the unpacked `src/`).
- **Scroll progress is not used for visuals.** The only scroll maths is analytics: `useScrollDepth` computes `scrollY / (scrollHeight - innerHeight)` and fires 25/50/75/100 milestones. `useSectionView` uses IntersectionObservers (`threshold 0.15`) on the ids hero/product/testimonials/security/pricing/faq/final, sent to PostHog (`lib/analytics/hooks.ts`). The page is native-scroll, with no sticky or pinned sections except the fixed header.
- **Reduced motion is handled carefully throughout**:
  - framer `useReducedMotion()` disables the typewriter, wash, meter and staggers (`initial={reduced ? false : …}`).
  - Tailwind `motion-reduce:` covers the marquee and chip arrow.
  - `matchMedia` gates the footer line.
  - An inline `<style>` in `<head>` also covers the workspace-switch overlay.
- **Mobile** (observed from classes; inferred visual result):
  - The demo stays 780 px tall on phones. The Ask Tiro side panel is `hidden lg:block` (`:1173`), and the conference-mode pill and translate toggle are `hidden sm:flex`. A component comment says "모바일은 부모가 정적 이미지로 대체", but the parent renders `<ProductDemo />` unconditionally (`Content/index.tsx:234`), so the comment is stale.
  - Hero CTAs switch to App Store/Play Store links by user agent.
  - On mobile, the desktop-download button opens a bottom sheet (`DesktopAppDownloadBottomSheet`).
  - In-app browsers get an AppsFlyer redirect instead of the login popup.

### 2.6 Client-only pieces (a loading strategy note)

Observed in the SSR HTML (`OUT:54`, `OUT:~988`): the hero and final CTA containers are **empty**, because buttons render only after `useEffect` detects `deviceOS` (`HeroSection/index.tsx:78-83`). Pricing amounts are also client-fetched. Inferred: a CTA pop-in and possible layout shift after hydration. For our pages, render a default CTA on the server and refine it after hydration.

---

## 3. Design tokens

### 3.1 Colours (from `packages/tds/dist/stylesheet.css`, light theme; a dark theme exists but the page is pinned to `data-theme="light"`)

| Role (semantic token) | Value |
|---|---|
| Page top / hero bg `bg-base-warm` = stone-cream | `#fffef7` |
| Raised / white sections `bg-raised` | `#ffffff` |
| App surface `bg-base` = stone-30 | `#fafaf9` |
| Subtle fill `bg-subtle` = stone-50 | `#f5f5f4` |
| Hairlines `bd-base` = stone-100 / `bd-subtle` = stone-200 | `#e7e5e4` / `#d6d3d1` |
| **Brand / primary** `bg-primary`, `fg-primary`, `bg-brand-dark` = brown-800 | **`#3d261c`** |
| Primary hover / `fg-primary-subtle` = brown-700 | `#523729` |
| Brand tint `alpha-brand-*` (brown-200 at alpha) | `#b3a79b` + alpha (`…29` = 16%, `…66` = 40%) |
| Text base / subtle / muted = stone-800/500/400 | `#1c1917` / `#57534e` / `#78716c` |
| Text on primary = brown-30 | `#f6f3ef` |
| Feature card background = amber-50 | `#fffbeb` |
| Security accent headings / button = amber-100 | `#fef3c7` |
| Security banner overlay | Tailwind amber-300 at 55% → amber-500 at 30% → brown |
| Footer signature stroke = brown-300 | `#9b8c7e` |
| Link `fg-info` = blue-700 | `#1d4ed8` |
| Demo traffic lights (`landingPalette.css`) | `#ff5f57` / `#febc2e` / `#28c840` |

The palette is warm stone neutrals, one deep coffee-brown brand colour and an amber accent family. There is no saturated "SaaS blue". `landingPalette.css` defines about 70 more `--landing-*` tokens: graph colours, an "ambient" field `#3a2018`, radii 9/17/18/24/34 px, and shadows such as `--landing-shadow-raised: 0 26px 70px #78716c24, 0 2px 8px #78716c0f`. Apart from the signal colours, this page does not use them. Inferred: they belong to the sister marketing site tiro.ax, which the code comments reference.

### 3.2 Fonts

| Family | Source | Use |
|---|---|---|
| **Pretendard Variable** (weights 45–920) | Self-hosted, **92 unicode-range woff2 subsets** (about 34 KB each); the browser fetches only the slices it needs | All KO text (`font-sans` stack: Pretendard Variable → Pretendard Std Variable → IBM Plex Sans → sans-serif). H1 uses it explicitly |
| Averia Serif Libre 300/400/700 | Self-hosted woff2 | `--tds-typography-font-family-brand`. The EN hero H1 swaps to it (`HeroSection:58-60`) |
| IBM Plex Sans | `next/font`; 2 woff2 preloaded (40 KB + 46 KB) | Fallback in the sans stack. Inferred: mostly unused on the KO page, so the preload is wasted |
| SF Pro Display | Third-party `fonts.cdnfonts.com` woff, `local()` first | The outer wrapper class `font-sfProDisplay`, overridden by `font-sans` on `<main>` and `<nav>` |
| Geist Mono, Hahmlet, Noto Serif KR/JP, Reckless, etc. | Self-hosted | App and editor fonts bundled in the shared CSS; not used on the landing |

### 3.3 Type scale (as used)

| Element | Size / weight / leading / tracking |
|---|---|
| Hero H1 | 30 px → **64 px** (`sm`), 700, 1.12 → 1.04, **−0.045em** |
| Hero sub-line | heading1 22 px → 30 px, 400, 1.358, brown-700 |
| Hero body | 16 → 18 px, 400, 1.65, stone-500 with a bold stone-800 phrase |
| Final H2 | 30 → 50 px, 700, 1.13, −1.5 px |
| Section H2 (`typography-heading1SemiBold sm:typography-h1`) | 22 px/600 → **36/40 px, 700, −0.025em**, brown colour |
| Card H3 (`typography-h4 sm:typography-h3`) | 20/28 → **24/32 px, 600, −0.02em** |
| Body (`typography-cmp-sm sm:typography-cmp-md`) | 13/18 → 14/20 px, 400, −0.008 to −0.01em |
| Pricing title (`typography-display2SemiBold`) | 40 px |
| FAQ question / answer | 16 → 20 px / 36 lh, 600, −0.4 px / 16 px, 32 lh, 70% opacity |

Note: body copy is small (14 px desktop) and every heading has negative tracking. Korean line breaking uses `break-keep` in the security and testimonial blocks.

### 3.4 Layout, spacing, radii, shadows, motion

- **Containers**: `max-w-screen-lg` **1024 px** for feature sections; `max-w-screen-xl` 1280 px for the hero and logos; `max-w-7xl` 1280 px for the demo; 1200 px for security; 1120 px for the FAQ; 1240 px for the footer. Gutters are `px-4` (16 px) on mobile and `px-6`/`px-10` larger.
- **Vertical rhythm**: sections use `pt-16 md:pt-20` (64/80 px) heading tops and `gap-5/6`; the FAQ uses `py-24`.
- **Radii**: cards `rounded-xl` (12 px); demo shell 20 px; side panel `rounded-2xl` (16 px); buttons and chips `rounded-full`; pricing buttons `rounded-xl`.
- **Shadows**: almost none on the landing. Depth comes from **surface colour changes and 1 px stone-100 hairlines**. The TDS elevations exist (`floating 0 4px 12px -2px stone/16%`, `modal 0 24px 80px`) but are used only on popovers.
- **Gradients**: edge-fade masks (marquee, carousel); a bottom fade from screenshot into band (`from-tds-bg-primary`); the amber security overlay; the radial-masked dot grid in the footer.
- **Easing and durations**: `easeOut` 0.25–0.65 s for reveals; 200 ms opacity hovers; 300 ms accordions and logo hovers; 500 ms carousel; 60 s marquee; 1.5 s `cubic-bezier(.22,1,.36,1)` for the signature (the same curve as `--landing-ambient-ease`).

---

## 4. Tech stack, page weight, loading

**Stack (observed):**
- Next.js **Pages Router** with SSG (`"gsp":true`, `pages/index-*.js`, `getStaticProps`), hosted on **Vercel** (`Server: Vercel`, `X-Vercel-Cache: HIT`, icn1).
- React, Tailwind CSS plus an in-house token package `@plato-corp/tiro-tds`, next-i18next (ko/en/ja), next/image, lucide-react, framer-motion, styled-jsx (footer only), Radix popover/switch.
- Analytics: GTM, PostHog, Vercel Analytics section ids, Datadog and Sentry. These are bundled in `_app` because the landing is the root route of the product web app.
- JSON-LD for Organization, SoftwareApplication, WebSite and FAQPage.

**Weight (compressed as served; measured with curl, `transfer.txt`, `media.txt`):**

| Part | Size | Note |
|---|---|---|
| HTML | **279 KB** (1.02 MB raw) | 66% of it is `__NEXT_DATA__`: the entire ko **and en** `common` i18n namespaces (295 KB + 403 KB raw) for the whole app, including billing and settings strings |
| JS (excl. nomodule polyfills) | **≈ 913 KB** (3.1 MB raw) | `_app` alone is 758 KB compressed / 2.6 MB raw (react-icons, recharts, sentry, mobx, datadog, posthog, date-fns…). Landing-specific code (`pages/index`) is only 4 KB |
| CSS | 62 KB (381 KB raw) | The whole app's CSS, including KaTeX and 276 `@font-face` rules |
| Fonts | ≈ 86 KB preloaded + Pretendard slices on demand | |
| Images | **≈ 4.5 MB (1x DPR) to ≈ 5.9 MB (2x)** | Biggest items: the security banner PNG **2.44 MB**, bypassing next/image as a CSS background; the freee logo WebP **1.21 MB** at every requested width (inferred: animated or un-resizable source, passed through unoptimised); feature images at `quality=100` (templates 669 KB at 1920w) |

**Loading strategy (observed):**
- Six feature images are marked `priority`, so they get `<link rel="preload">` even though they sit below the fold. Inferred: this competes with the hero.
- Logos and testimonials are `loading="lazy"`.
- Hashed assets use `max-age=31536000, immutable`; the HTML uses `max-age=0, must-revalidate` (CDN HIT).
- No code-splitting of the demo: it ships in the page chunk plus the shared framer-motion.

Inferred overall: the page *feels* light because there is no video or WebGL, but its byte cost is high. The causes are app-shell bloat and unoptimised images, not the landing design.

---

## 5. Takeaways for our two landing pages

### 5.1 What makes it feel polished (observed techniques)

1. **The product demo is the hero visual, and it is real UI in HTML.** A scripted reducer replays the core loop: transcript streams → collapses into a summary → user clicks "end" → document appears. It is crisp at any DPR, localisable, cheap (a few KB of code plus framer-motion), and it ends on a click prompt, so it invites the first interaction.
2. **One restrained, warm palette.** Cream page, white sections, amber-50 cards, one coffee-brown for headings, CTAs and dark bands. Depth comes from surface changes and hairlines, not shadows. This reads as "calm productivity", which fits the copy "대화에만 집중할 수 있게".
3. **Tight, large Korean headlines** (Pretendard 700, −0.045em at 64 px), a lighter brown sub-line above, and small grey body text.
4. **Consistent media framing.** Every feature screenshot sits in the same amber card with the same radius and padding, sometimes bottom-anchored. The page feels designed even though the assets are simple PNGs.
5. **Micro-motion only where it carries meaning**: the "paragraph completed" wash, the live meter, the marquee, a one-time signature line. All of it respects reduced motion.
6. **Enterprise trust stack** for B2B: certification chip above the H1 → logos → named testimonials → a dedicated security section with a list of controls → team/enterprise plans → FAQ (also emitted as JSON-LD) → competitor comparison links in the footer.

### 5.2 Worth borrowing for a B2B / productivity landing

- An **interactive scripted demo component**: a pure reducer (`timeline.ts`) plus a locale script file (`script.ts`), a typewriter, a summary wash, chat-style auto-scroll pinning and a "now click here" pill. Improve on Tiro by starting it only when ≥30% visible (IntersectionObserver), pausing it off-screen, and adding a static fallback on phones.
- **CSS-only dual marquee** with the doubled-track −50% trick, a mask fade and `motion-reduce`.
- **Clip-path draw-in** for a single brand stroke (cheaper and more robust than `stroke-dashoffset` with `preserveAspectRatio="none"`).
- **Semantic token layering**: palette ramps → semantic `bg/fg/bd` tokens → Tailwind utilities (`bg-tds-bg-primary`), with a light/dark map. The typography ramp has explicit size, line-height, weight and tracking per step.
- **Section ids shared with analytics** (`useSectionView`) and scroll-depth milestones. These are cheap to add and help when iterating on the page.
- **Avoid**: shipping the app shell and all i18n namespaces on the marketing page; `quality=100` with `priority` on below-fold images; CSS-background photos that bypass the image optimiser; client-only CTAs with no SSR default.

### 5.3 Not verified

- I did not render the page in a browser. Visual claims (layout shift from client CTAs, how the demo looks on phones, wasted preloads) are inferred from markup, CSS and source.
- The prices shown in Pricing are not known (they come from a plans API that I did not call).
- I did not check whether the freee logo is animated. Image sizes depend on the `Accept` header and DPR; my figures use `image/avif,image/webp`, and the server returned WebP or PNG.
- Bundle compression is as served to curl (br or gzip as negotiated). I did not measure tokens, CPU or memory.
