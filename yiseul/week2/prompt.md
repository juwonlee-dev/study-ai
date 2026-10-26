# Week2 Task1 — 프롬프트 기록

> **사용 도구**: Orca + Claude Code (CLI)
> **사용 모델**: Claude Opus 5.5 (`claude-opus-5-5`)
> **작업 브랜치**: `week2/yiseul-2`
> **산출물**: `yiseul/week2/profile.html`, `yiseul/week2/prompt.md`
> **Task2**: 다른 사람 PR 4건(#36, #37, #38, #39) 리뷰 및 승인 — 13번 이후 기록

대화 원문을 생략 없이 순서대로 기록했습니다. 도구 호출은 `🔧` 표시로 무엇을 했고 어떤 결과가 나왔는지 함께 적었습니다.

---

## 1. 👤 User

```
'--permission-mode'
작업 내용은 https://github.com/juwonlee-dev/study-ai/issues/22을 참고
yiseul/* 하위에 작업 진행 예정. 다른 폴더는 수정하지 않음.

작업에 대해 설명 진행 부탁
```

> (Plan 모드 상태에서 요청 — 계획 승인 전까지는 파일 수정 없이 조사만 진행)

## 2. 🤖 Claude

🔧 **도구 사용 내역**
- `gh issue view 22` → 이슈 본문이 출력되지 않아 `gh api repos/juwonlee-dev/study-ai/issues/22`로 재조회 → **2주차 과제** 본문 확인
  - Task1: Orca로 Week1 자기소개 이미지를 HTML 페이지로 구현 (`[이름]/week2/profile.html`, 프롬프트는 `prompt.md`)
  - Task2: 다른 사람 PR 3명 이상 AI로 리뷰
  - PR 본문: 사용 AI 에이전트/모델, 리뷰어(@juwonlee-dev, @juhwanHeo 필수 + 1인 이상)
- `yiseul/` 폴더 구조 확인 → `week0/README.md`, `week1/profile.png`, `.claude/skills/md-to-png/`
- `yiseul/week0/README.md` 읽기 → profile.png의 원본 마크다운(shields.io 뱃지 + 섹션 구성) 확인
- `yiseul/week1/profile.png` 이미지 확인 → 헤더 / 정보 뱃지 / About Me / Tech Stack / Tools / Studying / Links / 푸터 구성
- `git branch -a`, `gh pr list` → 다른 사람들의 week2 PR(#36~#42) 존재, `week2/yiseul` 브랜치에는 아직 작업 없음
- 계획 파일 작성 후 `ExitPlanMode`로 승인 요청

💬 **응답**

> 이슈 #22와 `yiseul/week1/profile.png`를 확인하고 계획을 세웠습니다.
>
> **이번 과제 (Week2 Task1)**
> - Week1에서 만든 자기소개 이미지 `yiseul/week1/profile.png`를 HTML 페이지로 다시 만드는 과제입니다. 이미지를 `<img>`로 그대로 넣으면 안 되고, 내용과 디자인을 HTML/CSS로 직접 구현해야 합니다.
> - 제출할 파일은 두 개입니다.
>   - `yiseul/week2/profile.html`: 완성한 페이지
>   - `yiseul/week2/prompt.md`: AI와 나눈 대화 전체를 생략 없이 마크다운으로 정리한 파일
> - PR 본문에는 사용한 AI(Orca + Claude Code / Claude Opus 5.5)와 리뷰어를 적어야 합니다. 리뷰어는 @juwonlee-dev, @juhwanHeo가 필수이고, 여기에 1명 이상을 더 지정해야 합니다.
> - Task2(다른 사람 PR 3명 이상 리뷰)는 이번 작업 범위에 넣지 않았습니다.
> - 제출 마감(10/25)은 이미 지났지만, 이슈 규정상 미완료분은 7일 안에 마무리하면 됩니다.
>
> **구현 방식**
> - 외부 파일 없이 열리는 HTML 파일 하나로 만들고, GitHub README처럼 보이게 꾸밉니다.
> - 뱃지 21개는 shields.io 이미지 대신 HTML/CSS로 직접 만듭니다. 원본과 같은 색상을 쓰고, 로고는 SVG 코드로 페이지 안에 넣습니다.
> - 원본 이미지에서 `**TA(Technical Architect)**`가 굵게 처리되지 않고 별표가 그대로 보이는데, HTML에서는 굵은 글씨로 바로잡습니다.
> - 확인은 이렇게 할 계획입니다.
>   - 크롬으로 화면을 캡처해 원본 PNG와 나란히 비교합니다.
>   - 모든 텍스트, 뱃지, 링크가 빠짐없이 들어갔는지 점검합니다.
>   - 모바일 폭(375px)에서도 레이아웃이 깨지지 않는지 봅니다.
> - 커밋, push, PR 생성은 요청하실 때만 진행합니다. 수정하는 곳은 `yiseul/week2/` 아래로 한정합니다.

<details>
<summary>📋 승인 요청한 계획 전문 (펼치기)</summary>

```markdown
# Week2 Task1 — 자기소개 이미지(profile.png)를 HTML 페이지로 구현

## Context
- 이슈 #22 (2주차) Task1: Week1에서 만든 `yiseul/week1/profile.png`의 내용과 디자인을 HTML/CSS로 직접 구현한다. 이미지를 `<img>`로 그대로 붙이는 것은 불가.
- 산출물
  - `yiseul/week2/profile.html` — 완성 페이지 (파일명·경로 고정)
  - `yiseul/week2/prompt.md` — AI와의 대화(사용자 프롬프트 + AI 응답) 생략 없이, 마크다운으로 보기 좋게 정리
- 작업 범위: `yiseul/` 하위만 수정. 다른 폴더는 건드리지 않음.
- 마감 26.10.25 이후이나, 이슈 규정상 미완료분은 마감 후 7일 이내 완료 가능. Task2(타인 PR 3명 이상 리뷰)는 이번 작업 범위 밖.
- PR 본문 필수: 사용 AI 에이전트/모델 (Orca + Claude Code / Claude Opus 5.5), 리뷰어(@juwonlee-dev, @juhwanHeo 필수 + 1인 이상).

## 원본 이미지 구성 (profile.png → HTML로 옮길 요소)
1. 헤더(가운데 정렬): `Hi 👋, I'm 한이슬 (Yiseul Han)` (h1, 하단 얇은 구분선) / `Backend Developer → aiming for Technical Architect (TA)` (h3)
2. 정보 뱃지(가운데): GENDER|FEMALE(#ff69b4), BIRTH|1996.12(blueviolet), AGE|만 29세(9cf 하늘색), CAREER|4년차(orange) / 2행: 📍HOMETOWN|강원도 강릉(#0077B5)
3. 굵은 회색 구분선(hr)
4. 🙋‍♀️ About Me — 5개 불릿(이모지 + 굵게 강조). 원본 이미지에서 `**TA(Technical Architect)**`가 렌더링되지 않고 별표가 그대로 노출된 부분은 HTML에서는 굵게로 정상 표현(의도된 디자인 반영)
5. 🛠️ Tech Stack — Java, JavaScript, Vue, Spring Boot / Oracle, MariaDB, PostgreSQL
6. 🧰 Tools — IntelliJIDEA, VS Code, Eclipse / Git, GitHub, GitLab
7. 📚 Studying — Docker, Kubernetes, React
8. 📇 Links — GitHub 뱃지 (https://github.com/LSHgy 링크, 새 탭)
9. 푸터: AI TOOL|CLAUDE 뱃지(#D97757) + 이탤릭 문구 `💜 작년부터 함께해온 Claude와 함께, AI를 더 잘 다루는 개발자로 성장 중입니다.`

## 구현 방식
- 단일 파일 `profile.html` (외부 의존 없이 더블클릭으로 열림, 인라인 `<style>`).
- 레이아웃: GitHub README 스타일 재현 — 흰 배경, 최대폭 ~900px 가운데, 시스템 폰트, h1/h2 하단 1px 구분선, 섹션 사이 4px 회색 hr.
- 뱃지 = 순수 HTML/CSS 컴포넌트 (shields.io 이미지 사용 안 함)
  - `.badge` > `.label`(회색 #555) + `.value`(색상) 2단 구성 / 기술 뱃지는 단색 1단 구성
  - for-the-badge 스타일: 높이 28px, 대문자, letter-spacing, 굵은 글꼴, 모서리 각짐
  - 색상은 원본 README의 hex 그대로 사용
  - 로고: Simple Icons의 SVG path를 인라인 SVG로 삽입. 원본처럼 Java·Oracle 등 로고 없는 뱃지는 텍스트만.
- 이모지는 텍스트 문자 그대로 사용(이미지 아님).
- 시맨틱 마크업: header, section, h1~h3, ul/li, hr, footer, a target="_blank" rel="noopener".
- 반응형: 뱃지는 flex-wrap으로 줄바꿈, 모바일 폭에서도 가로 스크롤 없음.

## 작업 순서
1. `yiseul/week2/` 생성 → `profile.html` 작성
2. Headless Chrome으로 렌더해 스크린샷 → 원본 profile.png와 비교, 차이 보정
3. 요소 누락 체크
4. 대화 내용을 `yiseul/week2/prompt.md`로 정리
5. (요청 시) 커밋 → push → PR 생성

## 검증
- 브라우저에서 직접 확인
- Headless Chrome 스크린샷과 원본 PNG 시각 비교
- grep으로 핵심 텍스트 존재 확인, `<img` 태그 미사용 확인
- 375px 폭에서 레이아웃 확인
```

</details>

---

## 3. 👤 User

> ✅ 계획 승인 (ExitPlanMode → Approve)

## 4. 🤖 Claude

🔧 **도구 사용 내역**

1. `yiseul/.claude/skills/md-to-png/scripts/md_to_png.py` 확인 → Week1 스킬의 Headless Chrome 실행 방식(`--headless=new`, 임시 프로필, `--screenshot`) 재사용
2. `curl`로 Simple Icons(`simple-icons@13.21.0`) SVG 15종 다운로드(스크래치 폴더) → path 데이터 추출
   - googlemaps, javascript, vuedotjs, springboot, mariadb, postgresql, intellijidea, eclipseide, git, github, gitlab, docker, kubernetes, react, anthropic
   - Java / Oracle / VS Code는 원본 이미지에도 로고가 없어 텍스트만 사용
3. **`yiseul/week2/profile.html` 작성**
   - 숨겨진 `<svg>` 안에 `<symbol>`로 아이콘 정의 → 각 뱃지에서 `<use href="#i-...">`로 재사용
   - `.badge > .label + .value` 구조, 색상은 `style="--bg:#007396"`처럼 CSS 변수로 지정
   - 라벨은 Verdana 계열, 값은 굵은(800) 글꼴 + 대문자 + 자간으로 shields.io for-the-badge 느낌 재현
4. Headless Chrome으로 900px / 375px 스크린샷 → 원본과 비교
   - 900px: 원본과 섹션 순서·뱃지 색상·정렬 일치 확인
   - 375px: headless 창 최소 폭 때문에 잘려 보여, 375px `<iframe>`에 넣어 재캡처 → 줄바꿈 정상, 가로 스크롤 없음 확인
   - 한글이 단어 중간에서 끊기는 것을 발견 → `body`에 `word-break: keep-all` 추가
5. 요소 누락 검증
   - 헤더·정보 뱃지·About Me 5개 불릿·기술 뱃지·링크 URL·푸터 문구 전부 존재 확인
   - 이모지 포함 문자열은 Git Bash 인코딩 문제로 grep에서 불일치가 나와, Python(UTF-8)으로 재확인 → 전부 OK
   - 뱃지 총 23개(정보 5 + Tech 7 + Tools 6 + Studying 3 + Links 1 + 푸터 1), `<img>` 태그 0개
6. **`yiseul/week2/prompt.md` 작성** (이 파일)

💬 **응답**

> `yiseul/week2/profile.html`을 만들었고, 원본 이미지와 비교·검증까지 마쳤습니다.
>
> - 원본 `profile.png`의 모든 요소(헤더, 정보 뱃지 5개, About Me 5개 항목, Tech Stack / Tools / Studying / Links 뱃지, 푸터)를 HTML/CSS로 구현했습니다. `<img>` 태그는 사용하지 않았습니다.
> - 뱃지 23개는 모두 CSS로 만들었고, 로고는 Simple Icons의 SVG를 파일 안에 넣어 인터넷 연결 없이도 그대로 보입니다.
> - 원본에서 별표가 그대로 보이던 `**TA(Technical Architect)**`는 굵은 글씨로 바로잡았습니다.
> - 375px 모바일 폭에서도 뱃지가 줄바꿈되어 가로 스크롤 없이 보입니다.
> - 대화 내용은 `yiseul/week2/prompt.md`에 정리했습니다.
> - 커밋, push, PR 생성은 아직 하지 않았습니다. 요청하시면 진행하겠습니다.

---

## 5. 👤 User

```
결과물 파일 경로 부탁. 열러보려고
```

## 6. 🤖 Claude

> 결과물 파일 경로입니다.
>
> - **HTML 페이지**: `C:\Users\his54\orca\workspaces\study-ai\week2-yiseul-2\yiseul\week2\profile.html`
> - **프롬프트 기록**: `C:\Users\his54\orca\workspaces\study-ai\week2-yiseul-2\yiseul\week2\prompt.md`
>
> HTML은 탐색기에서 더블클릭하거나, 아래 주소를 브라우저 주소창에 붙여넣으면 열립니다.
>
> ```
> file:///C:/Users/his54/orca/workspaces/study-ai/week2-yiseul-2/yiseul/week2/profile.html
> ```
>
> 이 세션에서 바로 열려면 프롬프트에 `! start yiseul/week2/profile.html`을 입력하세요.

---

## 7. 👤 User

```
커밋하고 PR 생성 요청
```

> (Plan 모드 상태에서 요청)

## 8. 🤖 Claude

🔧 **도구 사용 내역**
- `gh pr view 37`, `gh pr view 26` → 다른 사람의 Week2 PR과 본인의 Week1 PR 본문 형식 확인
- `gh api .../collaborators` → 리뷰어로 지정 가능한 인원 확인
- `AskUserQuestion`으로 두 가지 질문

❓ **질문 1**: 필수 리뷰어(@juwonlee-dev, @juhwanHeo) 외에 추가로 지정할 리뷰어는 누구인가요?
- 선택지: siyoungwoo / inseokim1 / bobo-h / joon5380
- ✅ **답변: siyoungwoo**

❓ **질문 2**: 브랜치 네이밍 규칙은 `week2/이름`인데 현재 브랜치는 `week2/yiseul-2`입니다. 원격에는 어떤 이름으로 올릴까요?
- 선택지: week2/yiseul (추천) / week2/yiseul-2
- ✅ **답변: week2/yiseul**

- 계획 파일 작성(prompt.md 업데이트 → 커밋 → `git push origin HEAD:week2/yiseul` → `gh pr create`) 후 `ExitPlanMode`로 승인 요청

## 9. 👤 User

> ❌ 계획 거절

```
PR 및 커밋 메시지 결과물 예시 확인 부탁
```

## 10. 🤖 Claude

> 커밋 메시지와 PR 초안을 미리 보여드립니다.
>
> **커밋 메시지**
> ```
> feat(yiseul): week2 자기소개 HTML 페이지 및 프롬프트 기록 추가
>
> - profile.html: week1/profile.png의 내용과 디자인을 HTML/CSS로 구현
>   - shields.io 뱃지 23개를 CSS 컴포넌트 + 인라인 SVG 로고로 재현
>   - <img> 미사용, 외부 의존 없는 단일 파일, 375px 반응형
> - prompt.md: Claude Code와의 대화 기록 (생략 없음)
>
> Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
> ```
>
> **PR**
> - 제목: `Week2/yiseul`
> - 브랜치: `week2/yiseul` → `main`
> - 리뷰어: @juwonlee-dev, @juhwanHeo, @siyoungwoo
> - 본문: Week1 PR #26과 같은 형식 — Issue #22 / 개요 / 변경 사항 / 사용 AI 에이전트·모델(Orca + Claude Code / Claude Opus 5.5) / 검증 결과 표(헤딩 7, About Me 리스트 5, 뱃지 23, 링크 1, 구분선 4, `<img>` 0, 375px 모바일 OK) / `**TA(Technical Architect)**` 굵게 보정 안내 / 리뷰어
>
> 커밋 전에 `prompt.md`에 경로 안내, 커밋 요청, 이번 초안 확인까지의 대화를 덧붙입니다. Week1 PR처럼 결과 미리보기 이미지를 넣고 싶으시면, PR을 만든 뒤 GitHub 웹에서 스크린샷을 붙여넣어 주세요.

- `ExitPlanMode`로 승인 요청

## 11. 👤 User

> ❌ 계획 거절

```
커밋 직전 내용까지 프롬포트 업데이트 후 커밋 + PR 진행
```

## 12. 🤖 Claude

🔧 **도구 사용 내역**
- `yiseul/week2/prompt.md`에 5~12번 대화 추가 (이 내용)
- 이후 커밋 → `git push -u origin HEAD:week2/yiseul` → `gh pr create` 진행
- 결과: 커밋 `4696fdb`, PR [#43](https://github.com/juwonlee-dev/study-ai/pull/43) 생성, 리뷰어 3명 지정 확인

---

# Task2 — 다른 사람의 PR 리뷰

## 13. 👤 User

```
Task2 작업 시작
```

## 14. 🤖 Claude

🔧 **도구 사용 내역**
- `gh pr list`로 열린 PR과 리뷰어 지정 현황 조회, `gh api .../pulls/<N>/reviews`로 PR별 기존 리뷰 확인
  - 본인(LSHgy)이 리뷰어로 지정된 PR: #36, #37, #38, #39
  - 본인이 리뷰한 PR: 없음
- `AskUserQuestion`: 리뷰 대상(#37 / #36 / #38 / #39 중 다중 선택)과 리뷰 형식(초안 확인 후 Comment / 초안 확인 후 Approve / 바로 등록) 질문
  - 사용자가 #37을 고른 뒤 추가 설명을 원해 질문 중단

💬 **응답**

> 리뷰 대상으로 #37(juwonlee)을 고르셨고, 리뷰 형식 질문에는 아직 답이 없습니다. 어떤 부분을 더 확인하고 싶으신가요?
>
> 참고로 과제 조건은 최소 3명 리뷰라서 #37 외에 2개가 더 필요합니다. 리뷰어로 지정되지 않은 PR도 리뷰해도 됩니다. 지금 #37 하나만 먼저 진행하고 나머지는 나중에 고르셔도 됩니다.

## 15. 👤 User

```
리뷰가 작성되지 않은 대상자들 전부 리뷰 작성 진행
```

## 16. 🤖 Claude

🔧 **도구 사용 내역**
- 본인이 아직 리뷰하지 않은 Week2 PR 7개(#36~#42)를 대상으로 잡고, 각 PR 본문·변경 파일·`profile.html`을 `gh pr diff`, `gh api .../contents`로 읽음
- 원본 `week1/profile.png`가 저장소에 있는 PR은 이미지와도 비교
- PR별 상세 리뷰 초안(좋은 점 → 개선 제안, 코드 위치 포함) 작성 후 `ExitPlanMode`로 승인 요청 → ❌ 거절

## 17. 👤 User

```
리뷰 작성 계획 설명 부탁
```

## 18. 🤖 Claude

> 대상(#36~#42 7개), 리뷰 방식(Comment 등록, 좋은 점 → 개선 제안), PR별 핵심 내용을 표로 정리해 설명했습니다.
> 예: #40은 761~1080px에서 정보 표가 카드 밖으로 넘칠 가능성, #42는 모바일에서 `scale(0.55)`로 글자가 7~8px가 됨 등.

- `ExitPlanMode`로 승인 요청 → ❌ 거절

## 19. 👤 User

```
대상은 내가 리뷰하지 않았고 && (리뷰가 없거나 || 리뷰대상자인) PR만 대상으로 진행
리뷰는 html결과물과 프롬포트 작성 관련해서 의견 제시 부탁 (잘한 점과, 개선 관련 의견)으로
리뷰어로 등록된 경우 승인까지 진행(큰 문제가 없는 한)
```

## 20. 🤖 Claude

🔧 **도구 사용 내역**
- 조건에 맞는 대상 재선정 → **#36, #37, #38, #39** (모두 리뷰어 지정, #37은 리뷰 0건). #40~#42는 제외
- 각 PR의 프롬프트 기록(`prompt.md`, `chatgpt-prompt.md`, `codex-prompt.md`) 읽기
- HTML 결과물 + 프롬프트 기록의 잘한 점/개선 의견으로 초안 재작성, 4건 모두 Approve로 계획 → ❌ 거절

## 21. 👤 User

```
각 대상자들에게 어떤 리뷰를 할지 요약 부탁 및 리뷰에는 PR 작성에 대해서 + 커밋 메시지에 대해서도 의견 제시 부탁(필요할 경우)
```

## 22. 🤖 Claude

🔧 **도구 사용 내역**
- `gh pr view <N> --json commits`로 4개 PR의 커밋 메시지 조회
- 초안에 "PR 본문 / 커밋 메시지" 의견 추가, PR별 요약 제시 → ❌ 거절

## 23. 👤 User

```
리뷰 작성시 간략하게 진행 필요
기준: 과제내용이 이슈에 맞게 진행됐는지(문제 없으면 의견 X), 프롬포트 작성 혹은 작성 방법(Skill 사용 및 지침 작성 등)에 대한 의견
PR 본문에 대해 좀 더 추가가 필요하거나, 잘 작성된 점
과제에 대해 이런식으로 만드는 편이 좋았을 것이란 의견 등을 총합해서 작성

-> 프롬포트의 경우 이렇게 하면 토큰 사용량이 줄었거나, 혹은 이렇게 했으면 길게 작업하지 않았을것. 같은 의견도 괜찮음

다시 리뷰 초안 부탁
```

## 24. 🤖 Claude

- 기준에 맞춰 PR별 "👍 한 단락 + 💡 의견 2~3개"로 간략하게 다시 작성 → ✅ 승인
- `gh pr review <N> --approve --body-file -`로 4건 등록, `gh api .../reviews`로 4건 모두 `APPROVED` 확인
- 리뷰 방식(대상 기준, 간략한 형식, 승인 규칙, 등록 전 초안 확인)을 다음 세션에서도 쓰도록 메모리에 저장

📝 **등록한 리뷰 전문**

<details>
<summary>#36 Week2/daejun — ✅ Approve</summary>

```
👍 PR 본문의 검증 기준 대조표와, 작업 중 겪은 문제·해결 방법을 표로 남긴 prompt.md가 좋았습니다. "커밋 전 컨펌" 규칙을 메모리에 저장한 것도 좋은 습관이에요.

💡 의견
- **과제 조건**: Week1 이미지에서 잘라낸 PNG 21개를 `<img>`로 넣은 방식은 "이미지를 그대로 첨부하지 말 것" 조건과 해석이 갈릴 수 있습니다. 반짝이·구름 같은 단순한 장식은 CSS/SVG로, 캐릭터만 이미지로 두는 절충이 더 안전했을 것 같아요.
- **프롬프트**: 처음 SVG로 만든 뒤 PNG로 다시 작업하느라 대화가 길어졌습니다. 첫 요청에 그림 처리 방식(SVG/이미지)을 정해 두었다면 한 번에 끝났을 것 같습니다.
- 기록에 GitHub 인증 코드와 이메일이 남아 있으니 가려 두는 걸 추천합니다.

🤖 Claude Code(Claude Opus 5.5)로 리뷰했습니다.
```

</details>

<details>
<summary>#37 Week2 / juwonlee — ✅ Approve</summary>

```
👍 `/assignment` 스킬로 이슈를 읽어 시작하고, 작업 중 생긴 규칙을 PROJECT.md/REVIEW.md 지침으로 바로 남긴 방식이 좋았습니다. 다음 주차부터 같은 설명을 반복하지 않아도 되니 토큰도 아낄 수 있겠네요. PR 미리보기를 `user-attachments` 링크로 넣은 것도 좋습니다.

💡 의견
- **프롬프트**: 리뷰어 랜덤 지정, `gh attach`, Issue 연결 금지 규칙을 작업 중간에 추가하면서 커밋과 PR 수정이 여러 번 반복됐습니다. 지침을 먼저 정리하고 과제를 시작했다면 더 짧게 끝났을 것 같아요.
- prompt.md의 AI 응답이 "진행 내용"으로 요약돼 있어, "생략 없이" 조건에는 원문 인용이 더 맞을 것 같습니다.
- **PR 본문**: Task1과 무관한 `CLAUDE.md`, `PROJECT.md`, `REVIEW.md`, skills 파일이 함께 들어 있는데 본문에는 언급이 없습니다. 본문에 적거나 별도 PR로 나누면 리뷰 범위가 분명해집니다.

🤖 Claude Code(Claude Opus 5.5)로 리뷰했습니다.
```

</details>

<details>
<summary>#38 week2/inseo — ✅ Approve</summary>

```
👍 첫 프롬프트를 분석·구현·검증·기록·Git 단계로 나누고 "원본이 없으면 만들지 말고 알려달라" 같은 안전장치를 넣은 점이 좋았습니다. 덕분에 week1 이미지가 비어 있는 걸 바로 잡아냈네요. 이미지 없이 SVG/CSS로 다 그린 것도 인상적입니다.

💡 의견
- **PR 본문**: 이슈 필수 항목인 **지정 리뷰어**와 관련 이슈(#22) 링크가 빠져 있습니다. `reference.png`를 넣은 이유도 한 줄 적어 주면 좋겠습니다.
- **프롬프트**: 세션 로그를 그대로 옮겨 `<pasted_content>` 태그와 중복된 세션 제목이 남아 있습니다. 첫 요청에 prompt.md 형식(턴 구분, 인용 블록)을 지정했거나 기록 정리를 스킬로 만들어 두었다면 정리 작업이 줄었을 것 같아요.

🤖 Claude Code(Claude Opus 5.5)로 리뷰했습니다.
```

</details>

<details>
<summary>#39 Week2/suhyeon — ✅ Approve</summary>

```
👍 ChatGPT로 Codex용 프롬프트를 먼저 다듬고 금지 조건(`<img>`·배경 이미지 금지, 정보 임의 추가 금지)을 명확히 적은 덕분에 결과물이 원본과 거의 같게 나왔습니다. PR 본문의 요구사항 체크리스트도 과제 조건과 1:1로 맞아 확인하기 편했어요.

💡 의견
- **프롬프트**: 첫 프롬프트에 과제 조건(`profile.html` 파일명, 단일 파일)이 빠져 한 번 다시 만들었습니다. 처음부터 이슈 본문을 ChatGPT에 같이 붙여 넣었다면 한 번에 끝났을 것 같아요.
- Codex에서 브라우저 검증을 하지 못했다고 남아 있는데, 직접 열어 원본과 비교한 결과를 PR 본문에 한 줄 덧붙이면 좋겠습니다.
- **커밋**: 공용 스킬을 넣었다가 다시 빼는 커밋이 히스토리에 남았습니다. 커밋 전에 `git status`로 본인 폴더 밖 파일이 없는지 확인하는 습관을 추천합니다.

🤖 Claude Code(Claude Opus 5.5)로 리뷰했습니다.
```

</details>

## 25. 👤 User

```
리뷰 관련된 내용들도 프롬포트기록에 추가로 남기고 커밋 후 PR 작성 부탁(수정)
PR에 리뷰 관련해서 추가적으로 작성 진행(누구를 리뷰했고, 어떤 AI를 사용했는지에 대해)
```

## 26. 🤖 Claude

- 계획(기록 추가 → 커밋·push → PR #43 본문에 Task2 섹션 추가) 제시 → ❌ 거절

## 27. 👤 User

```
해당 작업 진행 후 내 PR도 리뷰 부탁
```

## 28. 🤖 Claude

🔧 **도구 사용 내역**
- `yiseul/week2/prompt.md`에 13~28번 대화 추가 (이 내용)
- 커밋 → `git push origin HEAD:week2/yiseul` → `gh pr edit 43`으로 본문에 Task2 섹션 추가
- 이후 PR #43 셀프 리뷰 진행
