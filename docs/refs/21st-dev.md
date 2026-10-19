# 21st.dev

- https://21st.dev/ : 디자인 엔지니어들이 만든 React와 Tailwind 컴포넌트의 커뮤니티 레지스트리(12,000개 이상). 셰이더와 그라데이션도 있다.
- **패키지가 아니라 레지스트리**다. 코드를 내 레포에 복사해 넣고, 내가 소유하고 수정한다. 각 컴포넌트는 shadcn 레지스트리 형식이다.
- 설치
  - 에이전트 연동: `npx @21st-dev/cli@latest init --client claude`
  - 컴포넌트 페이지마다 shadcn CLI 설치 명령이 있다. 정확한 URL 형식은 실제로 쓸 때 페이지에서 확인한다.
  - "Copy prompt"로 에이전트가 코드베이스에 맞게 다시 만들게 할 수도 있다.
- 에이전트 문서: https://21st.dev/mcp.md , https://21st.dev/ai.md
- 요금: 무료는 하루 2회 복사까지다. 멤버십을 쓰면 무제한이다. 21st AI는 유료이고 크레딧제다.
- **라이선스**: 페이지에 일괄 라이선스가 적혀 있지 않다. 상업적으로 쓰기 전에 작성자 페이지와 https://21st.dev/pricing.md 를 확인한다.

## 이 프로젝트에서의 위치

**필름이 아닌 일반 섹션(T0)의 부품 창고**로 쓴다. 필름 엔진은 직접 만들고, 다음 섹션은 여기서 고른 뒤 우리 토큰으로 다시 입힌다.

| 쓰는 곳 | 카테고리(개수) | 눈여겨볼 것 |
|---|---|---|
| 히어로(필름이 없는 버전) | Heroes (1152) | [scroll-expansion-hero](https://21st.dev/@arunachalam/components/scroll-expansion-hero), [scroll-morph-hero](https://21st.dev/@prashantsom75/components/scroll-morph-hero), [animated-hero](https://21st.dev/@tommyjepsen/components/animated-hero) |
| 제품 화면 등장 | Scroll Areas (293) | [container-scroll-animation](https://21st.dev/@manuarora700/components/container-scroll-animation) |
| 텍스트 효과(키네틱) | Texts (663) | [morphing-text](https://21st.dev/@klyv-ui/components/morphing-text) |
| 배경 / 질감 | Backgrounds (365), Shaders, Gradients | [background-paths](https://21st.dev/@kokonutd/components/background-paths), [ambient-glare-shader](https://21st.dev/@1haim/components/ambient-glare-shader), [flow-field](https://21st.dev/@klyv-ui/components/flow-field) |
| 기능 / 벤토 | Features (318) | — |
| 후기 | Testimonials (161) | [testimonials-columns-1](https://21st.dev/@efferd/components/testimonials-columns-1) |
| CTA | Calls to Action (501) | [liquid-glass-button](https://21st.dev/@designali-in/components/liquid-glass-button) |
| 포인트 | — | [ai-orb](https://21st.dev/@konsstepnov/components/ai-orb), [spotlight-card](https://21st.dev/@jahed/components/spotlight-card), [splite (Spline)](https://21st.dev/@serafimcloud/components/splite) |

위 목록은 2026-10-16에 메인과 컴포넌트 목록 첫 페이지에서 고른 것이다. 인기순일 뿐이고 품질을 검증한 목록은 아니다.

## 쓰는 규칙

1. 가져온 컴포넌트는 **곧바로 우리 토큰으로 바꾼다.** 컬러, 폰트, 라운드, 이징을 모두 바꾼다. 원본 그대로 두면 "21st 느낌"이 나서 페이지 전체의 일관성이 깨진다.
2. framer-motion, three 같은 의존성이 따라오는지 확인한다. 필름 엔진과 무거운 렌더러가 겹치지 않아야 한다.
3. reduced-motion 대응이 빠져 있으면 직접 추가한다.
