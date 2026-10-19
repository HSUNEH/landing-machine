> 원본: 2026-10 REA 세션의 정적 리버스엔지니어링 노트(sddaddad-findings.md) 사본. 브라우저 실행 없이 소스만 읽음(§5.4). 인용 라인 번호는 당시 로컬 사본 기준.
> 대상: https://www.studiosddaddad.com/

# How studiosddaddad.com is built (reverse-engineering notes)

Target: https://www.studiosddaddad.com/ (home page only), fetched 2026-10-16 (KST).
"STUDIOS 따따디" (Studios ddaddad) is the creative/marketing agency brand of 더블유더블유디코리아 (WWD Korea).
The page is a **corporate agency home page, not a product landing page**. It is a stock **Imweb** (아임웹)
site with a lot of hand-written CSS and JS pasted into "코드" (code) widgets.

Labels: **[O]** = observed in fetched source or screenshots; **[I]** = inferred.

## Where the evidence lives

All paths are under `scratchpad\sddaddad\` (untrusted downloads; no downloaded JS was executed locally).

| File | What it is |
|---|---|
| `index.html` | Full server-rendered HTML, 673,870 B decoded / 100,505 B on the wire (gzip), 15,468 lines |
| `body.html` | Lines 12200-12900 of `index.html`: header plus all sections (line numbers below are `index.html` lines) |
| `headstyle.css` | Lines 56-11985: one inline `<style>` block (~430 KB). Imweb-generated per-section/per-widget CSS mixed with the code-widget CSS |
| `typekit.css` | Adobe Fonts kit `lgw1hzr` |
| `custom.cm` | Site-wide "custom CSS" endpoint, which returned **0 bytes** |
| `assets.txt`, `asset-sizes.txt` | Image URLs and their HEAD sizes |
| `js.txt`, `js-sizes.txt`, `css.txt`, `css-sizes.txt` | Every `<script src>` and stylesheet, with wire and decoded bytes |
| `shots\pc-hero.png`, `shots\pc-tall.png`, `shots\mo-full.png` | Headless Chrome screenshots (1920×1080, 1920×2400, 390×844 with an iPhone UA) |

Key line ranges in `index.html`:
- 1626-1636: intro CSS. 1638-1678: CSS for the Vimeo background
- 2433-2605: 3D "따/따/디" letter reveal. 2718-2748: "CREATIVE PLANNING AGENCY" and the global `span` font. 2751-2854: widget hiding, scroll snap, scroll lock, hidden scrollbars
- 4908-5462: mobile "track" story CSS (`.mo-*`)
- 8007-9100: PC "track" story CSS (`.section-1` / `.section-2`)
- 11873-11985: CSS for the custom full-screen menu. 12025-12073: Typekit link plus a broken `<style>` block
- 12896-12933: custom cursor CSS. 13658-13684: custom cursor JS
- 13853-13872: intro GIF logic. 13875-13899: Vimeo injection (PC). 13911-14365: wheel-gated hero reveal plus a hand-off to the next section
- 14369-14395: Vimeo injection (mobile). 14399-14607: mobile step story. 14613-15105: PC step story
- 15108-15129: forced scroll-to-top. 15135-15182: mobile page-name label. 15185-15302: JS for the custom sidebar menu

Builder identification **[O]**: `Set-Cookie: IMWEBVSSID…`, `_imweb_login_state` and `vendor-cdn.imweb.me/*` assets, Imweb DOM (`doz_type="section"`, `data-widget-type="code|text|button|padding|hr|image"`), and `imweb.me/_/wkernel/webinit-slim/boot.mjs`. It is served through nginx behind CloudFront (ICN). The site code is `S202511254f6954cda1db5`, with some assets from an older site `S20250924507b4fbd8783e`. Custom images are hot-linked from `ai.esmplus.com/aryatty/WWD/…`, which is a Gmarket/ESM seller image host.
The hero Vimeo video `1126385960` is titled "러너 임시소스" ("runner temp source"), runs 13 s and sits on a free Vimeo account named "웹노바" **[O, oEmbed]**. That suggests a web agency named Webnova built the site **[I]**.

## 1. Page structure, section by section (in DOM order)

PC and mobile are **separate section sets**. Imweb `pc_section mobile_hide` and `mobile_section` toggles decide which set shows **[O]**.

| # | Section id | Device | Content / treatment |
|---|---|---|---|
| 0 | header `s202511258f14094fe2387` / `s202511255be88dc4b192a` | both | **PC [O, 12200-12313, pc-tall.png]:** white bar 97 px tall. Logo PNG on the left (130 px wide, swapped for a separate "scroll logo"). Centred nav: WORK (dropdown: ALL, CREATIVE CAMPAIGN, PRINT AD / FILM, BRANDED CONTENT/PPL, MEDIA PLANNING, SNS MARKETING, GLOBAL MARKETING), ABOUT, SERVICE, CONTACT, PARTNERS, all in uppercase Agenda. **Mobile:** transparent bar with an orange page-name label (`#page-menu-name`, filled by JS per path, 15135-15182) and a hamburger PNG. Tapping the hamburger opens a custom full-screen sidebar (black at 0.9 opacity, slides in from the right over 0.3 s; Agenda 300 23 px links, white turning #ff6600 on hover/active; WORK expands its submenu) **[O, 15185-15302, 11873-11985]** |
| 1 | `s20251125358cc5feb93b6` (PC) | PC | **Intro splash.** A fixed white full-screen layer (z 99999) shows a 4.2 MB logo-motion GIF (`STUDIOS WWD_Logo Motion_FIN.gif`, `object-fit: cover`). It fades in over 1 s, starts fading out at 4.5 s and is removed at 5.5 s. It shows once per session (`sessionStorage 'wwd-intro-shown'`) and is skipped on mobile UAs **[O, 12362-12366, 13853-13872]** |
| 2 | `s2025112555ab693e2ad7e` (PC) | PC | **Hero, two states.** State A: a full-bleed muted, looping Vimeo background (`?background=1…quality=1080p`), with the content widgets at opacity 0. State B (after the first wheel tick): the video fades out over 0.7 s and the widgets fade in, in four staggered groups. The groups are: headline "고객사와 함께 달리는 페이스메이커, / STUDIOS 따따디 입니다" (Pretendard 800 42/1.3, #000, centred); then two pill CTAs, **About us** (white fill, 2 px black border) and **Contact** (#ff6600 fill), both 25 px with 15/100 px padding and `border-radius: 9999px`; then a 2559×182 "sparkle" graphic strip plus "CREATIVE PLANNING AGENCY" (Agenda 600 40 px, white); then three big letter images 따 / 따 / 디 that flip in on the Y axis **[O, 12361-12423, 13911-14365, 2361]** |
| 3 | `s20251125382bd887ed718` (mobile) | mobile | **Mobile hero**: the same Vimeo clip at 720p with `playsinline`. The headline is Pretendard 800 22 px. The About us (white) and Contact (#ff6600) pills use 20 px text with 90 px horizontal padding and Imweb's built-in `fadeIn` widget animation (0.6 s, delays 0.5/0.3 s). The section is pinned with Imweb `SECTION_FIXED` **[O, 12425-12457, 14367-14395, mo-full.png]** |
| 4 | `s2025112555b48f2e057f2` (mobile) | mobile | **Mobile "track" story**: black, 100dvh, a five-step click-through (see 2.3) **[O, 12467-12598]** |
| 5 | `s202511253be0f4d2e0f9a` (PC) | PC | **PC "track" story** (`#section2-animation-container`, height `--track-height` 870 px). *Scene 1*: "BRAND, PACEMAKER" in Kaneda Gothic 900 italic at 220 px, #ff6600. Three Korean lines below it, Pretendard 600 46 px white: "브랜드의 목표를 정확히 이해하고 / 기획부터 실행까지, 브랜드 성장을 이끄는 / 통합 마케팅 솔루션을 제공합니다." A running-track drawing (four horizontal lines plus three concentric stadium arcs, #313333 at 1.5 px) draws itself in. Five emoji "runners" circulate on the track. A blinking sparkle PNG and a floating "NEXT" button complete the scene. *Scene 2*: the track turns vertical and four service pairs step through: "Integrated Marketing Communication" / "Data-Driven Marketing" / "Creative & Branded Content" / "Event & Brand Experience" (Agenda 600 60 px, **#aff03c** lime). Each has a Korean line, e.g. "머리는 차갑게, 감이 아닌 데이터로 증명합니다." (Pretendard 600 44 px white). Back is a round orange "↑" button **[O, 12647-12790, 8031-8642, pc-tall.png]** |
| 6 | `s202512153b3b608258fc7`, `s2025121586ca146cc9405` (PC); `s202512150304722c799dc`, `s20251215e955f616f15e5` (mobile) | both | **Footer**: a 2 px #262626 rule, logo, then company details in Pretendard 16 px (13-14 px on mobile) in **#838989**. These are the Korean legal business-info block (name, CEO, phone, fax, business registration number, email, Seoul Forest L-Tower address), an Instagram icon, "©2025. **Studios 따따디**" (in #ff6600) All Rights Reserved., and links to the privacy policy and terms **[O, 12599-12632, 12800-12831]** |

What is absent **[O]**: product or feature grids, case-study thumbnails, testimonials, logo marquee, pricing, FAQ and forms. Work lives on separate `/WORK-*` pages. The home page is a brand manifesto plus a list of four services. Its only CTAs are the About us and Contact pills and the nav.

## 2. Motion and interaction

### 2.1 No animation library: CSS keyframes + class toggles + `setTimeout` choreography
**[O]** The page has no GSAP, ScrollTrigger, Lenis, Framer Motion, Barba, Lottie, Rive, Spline or custom WebGL. `grep` for these returned nothing. Imweb's vendor bundle does load `ThreeCanvas.js` (three.js r46 as `THREE_IMWEB`) and `snow.js`, but these are Imweb's optional snow effect and nothing on this page uses them **[O for the files, I for "unused": no snow widget and no custom calls]**.
All custom motion is hand-written vanilla JS that adds classes on timers, and CSS `transition`/`@keyframes` that react to those classes. jQuery is only present because Imweb loads it.

### 2.2 PC hero: wheel hijack instead of scroll (13911-14365, 2751-2854)
- **Scroll is disabled on PC**: `html, body { overflow: hidden !important }` at `min-width: 769px`, and scrollbars are hidden everywhere (`::-webkit-scrollbar{display:none}`, `scrollbar-width:none`). `html{scroll-snap-type:y mandatory; scroll-behavior:smooth}` applies too **[O]**.
- A `wheel` listener with `{passive:false}` is attached **3 s after DOMContentLoaded** (`setTimeout(setup, 3000)`) and calls `preventDefault()` while the hero is active **[O]**.
  - First wheel-down (`wheelThreshold: 1`): the video fades to opacity 0 (0.7 s ease-in-out). Widget groups get `.widget-visible` at delays of 0/200/400/600 ms, each an opacity transition of 0.7 s. The last group gets `.is-in` on each letter image with a **150 ms stagger**.
  - Wheel-up reverses this: groups fade out in reverse at 100 ms steps, then the video returns.
  - With all widgets visible, a further 50 units of `deltaY` adds `scroll-enabled` to html/body (re-enabling `overflow-y:auto`) and calls `nextSection.scrollIntoView({behavior:'smooth'})` on the PC track section.
  - When that section is at the top, upward wheel past 50 units calls `scrollTo(0)` to return.
  - Touch has the same logic with ±30 px swipe thresholds.
- Letter flip (2433-2605): `opacity:0; transform: rotateY(-45deg)` changes to `rotateY(0)` with `transition: transform 2s cubic-bezier(.22,.61,.36,1), opacity 2s ease`. Each letter's absolute offset is hand-tuned for five breakpoints: 769-1024, 1025-1439, 1440-1919, 1920-2559 and ≥2560 px **[O]**.
- `history.scrollRestoration='manual'` plus `scrollTo(0,0)` on load, `pageshow` and `beforeunload`, so the page always restarts at the hero **[O, 15108-15129]**.
- A JS image swap loads a 2560 px "sparkle" PNG at ≥2560 px viewports **[O, 14116-14158]**.

### 2.3 "Track" story: SVG line-draw + CSS `offset-path` runners + click-stepped scenes
This is the signature piece **[O, 8007-8642, 14613-15105; mobile 4908-5462, 14399-14607]**.
- **Line draw**: JS sets `strokeDasharray = strokeDashoffset = getTotalLength()` on each `.track-stroke`. Adding `.in` to the section triggers `@keyframes draw{to{stroke-dashoffset:0}}`.
  - Lines draw over `--line-duration: 0.8s` ease-out.
  - Arcs draw over `--arc-duration: 3.5s` with `cubic-bezier(.25,.46,.45,.94)` and a delay of `calc(var(--line-duration) - .1s)`.
  - `vector-effect: non-scaling-stroke` keeps the 1.5 px hairline crisp under `scale(1.1)`.
- **Start trigger**: `IntersectionObserver`, threshold 0.9 on PC and 0.3 on mobile. It fires once, then disconnects.
- **Headline curtain reveal**: the big word has a black `::after` overlay. On PC scene 1 it has a 100 px left gradient feather and slides away with `translateX(100%)`. In scene 2 it is a top/bottom-feathered block that collapses with `clip-path: inset(50% 0 50% 0)`. Both use `--big-curtain-dur: .4s` with `--big-curtain-ease: cubic-bezier(.22,.61,.36,1)` and run 1.3 s (PC scene 1) or 1.2 s (scene 2) after start.
- **Body lines** slide in from `translateX(100px)` with opacity 0→1 over 0.6 s ease-out, with delays of 1.8, 2.0 and 2.2 s.
- **Blink**: the sparkle PNG uses a hard on/off `fadeInBlink` loop of 0.6 s starting at 2.1 s.
- **Emoji runners on the track**: each `<img>` gets a CSS `offset-path: path('M … A … Z')` (a closed stadium loop) and `offset-rotate: auto`. `@keyframes moveEmoji` animates `offset-distance` from `var(--start-pos)` to `+100%` over `--emoji-duration: 7s`, linear and infinite, after 3 s. The images visibly "run laps" with no JS per frame.
- **Scene 2** has no scrolling. A floating "NEXT" PNG button (`floatUpDown` ±15 px over 2 s, ease-in-out, infinite) advances the steps through `click`. The step functions are `startSection2` → `transitionToNextContent` → `…Third` → `…Fourth`.
  - Each step fades the current pair out, then runs about 800 ms `setTimeout` chains to show the next title and description. Text rises from `translateY(100px)` (`slideUpText 0.4s cubic-bezier(.22,.61,.36,1)`) inside an `overflow:hidden` mask.
  - Each step also moves the emojis by per-emoji CSS custom properties (`--end-top`, `--move-distance{,2,3}`, `--move-x{,2,3}`, `--rotate2/3`), read with `getComputedStyle`. They animate through `transition: top/left/transform 2s cubic-bezier(.22,.61,.36,1)` with a double-rAF to force a reflow.
  - Each step also shifts the arc SVG up 150 px (`.move-up/2/3`, a 2 s transition).
- **Back button**: `quickFadeToStep(n)` snaps to the precomputed state of an earlier step without replaying the choreography.
- **Mobile version** (`.mo-*`): the same idea re-laid out vertically for 100dvh. It is a five-step state machine (step0 plus steps 1-4). Each step adds `.mo-stageN` to the emojis and arcs: the arcs SVG is mirrored (`rotateY(180deg) translateX(-400px) scaleX(2)`) with 1.5 s transitions. Navigation is by tapping a "next" image and a back button. `overscroll-behavior: none` is set on the body and section.

### 2.4 Smaller interactions
- **Custom cursor** (≥769 px): a 45 px PNG in a fixed div, `pointer-events:none`, `translate(-50%,-50%)`. Its position updates in a rAF-throttled `mousemove` handler that sets `left/top`. The system cursor is hidden with `cursor:none !important` on body, a, button, input, select and textarea. There is no lerp or trailing, so it tracks 1:1 **[O, 12896-12933, 13658-13684]**.
- **Imweb built-ins**: `$('body').smoothScroll({speed:1200, easing:'easeInOutExpo'})` for anchor links; `_fade_link` page-transition class on nav links; `SITE_ANIMATION` (`animate.css`) handles widgets flagged `data-widget-anim="fadeIn"` on scroll; header `scrollToFixed` swaps to the scroll logo **[O, 13734-13738, 13790-13792, site_animation.js]**.
- **Pill hover**: the custom back button goes from 20% orange to full #ff6600 and its "↑" glyph flips to black over 0.3 s **[O, 8463-8501]**.

### 2.5 Reduced motion and mobile
- `@media (prefers-reduced-motion: reduce){ .track-stroke{stroke-dasharray:none;stroke-dashoffset:0} *{animation:none !important} }` appears twice (5460, 8639) **[O]**.
  - It covers only the keyframe animations. The transition-based curtains, letter flips, emoji moves, the wheel hijack and the 4.2 MB GIF intro are unaffected **[O/I]**.
  - Because the line-draw is a keyframe, reduced-motion users see the track fully drawn. The emoji runners stop, but they never reach `opacity:1` via keyframe, so they likely just sit visible at the path start **[I]**.
- Mobile is detected three ways: a UA regex (intro skip), `innerWidth <= 768` checks in JS, and Imweb's separate mobile sections. The mobile build uses normal scrolling, a 720p video, no cursor and a different step layout **[O]**.
- **Accessibility/robustness issues [O→I]**:
  - On PC, `overflow:hidden` plus wheel-only advance means **keyboard users (Space, PageDown, arrow keys) and trackpad-less users who do not wheel cannot move past the hero**.
  - The steps are `<img>`/`<button>` elements with no labels; the back button is an empty `<button>`.
  - The 3 s artificial delay before the wheel works.
  - 35 `console.log` calls are left in.
  - Everything is absolutely positioned in px (`top: 422px`, `left: 200px`) and patched per breakpoint.

### 2.6 Loading strategy
The HTML is fully server-rendered (curl gets all copy). The custom JS runs inline at the end of `<body>`. The Vimeo iframes are injected by JS. Nothing is lazy-loaded or code-split for the custom parts.

## 3. Design tokens

### 3.1 Colours (hex counts are from `headstyle.css`; many are Imweb defaults)
| Role | Value | Evidence |
|---|---|---|
| Brand orange (big type, Contact pill, active nav, © name, back button) | **#ff6600** | 8135, 2361, 11939, 12821 |
| Lime accent (service titles) | **#aff03c** | 8332 |
| Canvas, story and footer background | #000000 | section `background-color` |
| Hero text and outlines | #000 on #fff (after the video fades) | 12377, 2361 |
| Track lines and ghost headline | #313333 | 4909, 8283 |
| Footer rule | #262626 (2 px), rgba(131,137,137,.5) (1 px) | 12608, 12817 |
| Footer and legal text | #838989 / rgb(131,137,137) | 12812 |
| Mobile sidebar overlay | rgba(0,0,0,.9) | 11882 |
| Theme colour meta | #363636 | `<meta name="theme-color">` |

The system is **black + white + one hot orange + one lime**. The emoji PNGs and the 따/따/디 letter art carry the illustrative colour.

### 3.2 Fonts
- **Kaneda Gothic** (Adobe Fonts, kit `lgw1hzr`): condensed display grotesk. Only 900 italic is used, for "BRAND, PACEMAKER" at 220 px (PC scene 1), 140 px (scene 2) and smaller on mobile **[O, 8130, 8278]**.
- **Agenda** (Adobe Fonts, same kit; weights 100-800, roman and italic): nav, pills, service titles (600) and sidebar links (300). A global rule `span { font-family: "agenda" !important }` forces every `<span>` into Agenda **[O, 2738-2742]**.
- **Pretendard** (Imweb CDN, static and variable dynamic subsets): all Korean copy, weights 600 and 800 **[O]**.
- The Typekit kit declares 28 faces, all with `font-display:auto` **[O, typekit.css]**. The `<style>` block right after the kit link (12026-12073) contains declarations without selectors, which is invalid CSS and has no effect **[O]**.

### 3.3 Type scale (as used, PC)
220 (display) · 140 (ghost display) · 60 (service title, Agenda 600 / 1.1) · 46 (track body, Pretendard 600) · 44 (service description / 1.3) · 42 (hero headline, Pretendard 800 / 1.3) · 40 (CREATIVE PLANNING AGENCY) · 25 (pill CTA) · 16/13 (footer).
On mobile: 22 (hero headline), 20 (pills, page label), 23 (sidebar), 14/12 (footer).
There is no fluid `clamp()`; breakpoints are handled by overriding fixed px values **[O]**.

### 3.4 Layout, spacing, radii, shadows, easing
- **Grid**: Imweb 12-column `doz_row`/`col-dz-*` with gutters off (`grid_gutter_0`). The hero letters sit in three `col-dz-4` columns. The story sections are full-bleed (`extend_section`). Inside the code widgets, layout is **absolute px**, with a left text inset of 200 px on PC and 30 px on mobile.
- **Story height**: `--track-height` is 870 px (PC default), 700 px (1000-1439), 1100 px (≥2560) and 610 px (mobile root).
- **Spacing**: vertical rhythm comes from Imweb "여백" (padding) widgets of 128/40/23/168/33/15/221/90/39/61 px, so there is no spacing scale **[O]**.
- **Radii**: pills use 9999 px; the back button is 50%. No other rounding.
- **Shadows**: none in the custom code.
- **Easing**: the signature curve is **`cubic-bezier(.22,.61,.36,1)`** (an ease-out-cubic-like curve). It is used for the curtains, letter flips, emoji moves and arc shifts. Also used: `cubic-bezier(.25,.46,.45,.94)` (arc draw), `ease-out` (lines, text), `ease-in-out` (fades, float) and `easeInOutExpo` (Imweb anchor scroll).
- **Durations**: 0.3 s (UI hover), 0.4 s (curtain, text rise), 0.5 s (scene cross-fade), 0.6 s (text slide), 0.7 s (hero fades), 0.8 s (line draw, step gaps), 1.5-2 s (track/emoji moves, letter flips), 3.5 s (arc draw), 7 s (emoji lap).

## 4. Tech stack, page weight, loading

- **Stack [O]**: Imweb SaaS builder (legacy jQuery runtime plus new `wkernel` module boot and `magnet-shell` web components for shop/chat). Libraries from the platform: jQuery, jQuery UI, Bootstrap 3, lodash, moment-with-locales, owl.carousel 1+2, slick, lightGallery, masonry, ThreeCanvas (three r46), Datadog RUM, Naver analytics, Imweb CRM and analytics SDKs, Kakao postcode. Shop scripts load on a page with no shop.
- **Custom code**: about 1,450 lines of vanilla JS and several thousand lines of CSS, pasted into Imweb code widgets and inlined into the HTML. Fonts come from Adobe Fonts; images are hot-linked from `ai.esmplus.com`; video comes from Vimeo (free account).
- **Weight [O, measured with curl, not a browser waterfall]**:
  - HTML: 100.5 KB on the wire (gzip), 674 KB decoded, of which about 430 KB is inline CSS.
  - JS: 98 script URLs, **~1.72 MB on the wire / 5.05 MB decoded**. The largest are `jquery-ui.design.js` (710 KB, served uncompressed), `site_shop.js` (132 KB gz), `moment-with-locales` (108 KB gz), the CRM SDK (77 KB) and the analytics SDK (76 KB). The count includes a few IE-only conditional scripts that modern browsers skip **[I]**.
  - CSS: 26 stylesheets, **~456 KB on the wire / 2.48 MB decoded**.
  - Images: the custom PNGs total about 150 KB (emojis about 3 KB each; letters 8-12 KB). The exceptions are the **intro GIF at 4.22 MB** and the **favicon .ico at 192 KB**.
  - Video: Vimeo adaptive stream (1080p on PC, 720p on mobile), not measured.
  - Fonts: up to 28 Typekit faces are declared; browsers download only the faces used **[I]**. Pretendard uses dynamic subsets.
- **Loading behaviour [O]**: everything is render-blocking and synchronous (about 90 classic `<script>` tags at the end of `<body>`, no `defer` except a few modules). The custom choreography depends on fixed timers (3 s setup delay, 4.5 s intro, 4.8 s until NEXT appears) rather than on load events. In the headless screenshots the Vimeo spinner was still showing after 9-16 s of virtual time, so the hero can be a black screen with a spinner for a while **[O, pc-hero.png]**.
- **Not measured**: a real browser waterfall, LCP/CLS, CPU time and memory. The headless screenshots only show the PC hero in state A, the PC track section after it started, and the mobile hero.

## 5. Takeaways for our two landing pages

### 5.1 What makes it feel distinctive (observed techniques)
1. **One metaphor carried through every element.** The brand idea is "pacemaker / runner", and the whole story section is a literal **running track**: hairline lanes, stadium curves, and emoji "runners" lapping it through CSS `offset-path`. The copy ("BRAND, PACEMAKER", "가슴은 뜨겁게 / 머리는 차갑게") matches the drawing.
2. **Huge condensed italic display type in one hot colour** (Kaneda Gothic 900 italic, 220 px, #ff6600) on pure black. A second accent (lime #aff03c) is reserved for section titles.
3. **Revealed, not scrolled**: curtain wipes on headlines, line-by-line text rising from a mask, staggered 3D letter flips. Every reveal uses the same easing, `cubic-bezier(.22,.61,.36,1)`, and a 0.8 s cadence, which makes the motion feel coherent.
4. **Illustrated "type as mascot"** (the 따/따/디 letter characters, emoji runners, custom cursor icon) adds personality cheaply: small PNGs, no 3D.

### 5.2 Worth borrowing (techniques, not assets)
- **SVG self-drawing diagrams**: compute `getTotalLength()` once, set `stroke-dasharray`/`stroke-dashoffset`, and animate on an IntersectionObserver trigger. Add `vector-effect: non-scaling-stroke` for crisp hairlines. This works well for "how it works" flow lines or architecture diagrams on a product page.
- **CSS `offset-path` motion**: moves small objects along a product-relevant path (data packets along a pipeline, cursors along a workflow) with zero JS per frame and a natural reduced-motion fallback.
- **Curtain reveal** for hero words: a `::after` overlay that collapses with `clip-path: inset(50% 0 50% 0)` or slides with `translateX(100%)`, over about 0.4 s.
- **Masked line rise** (`overflow:hidden` wrapper with the child going from `translateY(100%)` to 0) for headline lines.
- **Per-element motion parameters in CSS custom properties** (`--end-top`, `--move-x2`…), read by a small step controller. This keeps choreography data in CSS. Better still, drive it from `data-step` and `transition`, with no `getComputedStyle` parsing.
- **Step-through "chapters" with explicit NEXT/BACK controls**, as an alternative to scroll-jacking for a 3-5 point feature tour. Rebuild it as real buttons with labels and keyboard support, and let normal scroll also advance (IntersectionObserver per step or `position: sticky` with `scroll-timeline`).
- **Avoid**: blocking scroll with `overflow:hidden` and wheel-only advance (breaks keyboard, trackpad and assistive tech); a 3 s artificial setup delay; px-absolute layouts patched across 5 breakpoints (use grid, `clamp()` and container units); a 4 MB GIF splash (use a short muted `<video>` or Lottie, or drop it); hot-linked third-party image hosts; free-tier Vimeo for a hero (self-host an MP4/WebM with a poster); and a builder runtime that ships 1.7 MB of unrelated JS.

### 5.3 Not verified
- The animations were not observed frame-by-frame in a browser; only three headless screenshots were taken. The behaviour above is derived from source.
- The intro GIF content, the Vimeo clip content, the letter and emoji art and the hover states were not viewed.
- The PC hero's state B (after a wheel tick) and story scene 2 were not screenshotted.
- No Lighthouse/LCP, network waterfall, CPU or memory figures.
- Other pages (/ABOUT, /SERVICE, /WORK-*) were not examined.
