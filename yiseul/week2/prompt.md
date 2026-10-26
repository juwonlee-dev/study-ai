# Week2 Task1 — 프롬프트 기록

> **사용 도구**: Orca + Claude Code (CLI)
> **사용 모델**: Claude Opus 5.5 (`claude-opus-5-5`)
> **작업 브랜치**: `week2/yiseul-2`
> **산출물**: `yiseul/week2/profile.html`, `yiseul/week2/prompt.md`

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
