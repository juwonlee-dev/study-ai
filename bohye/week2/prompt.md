# Week 2 Orca + Codex 대화 기록

- 사용 환경: Orca
- AI 에이전트·모델: Codex / GPT-6-Sol
- 이슈: [#22 2주차](https://github.com/juwonlee-dev/study-ai/issues/22)
- 범위: 이 대화에서 사용자가 직접 입력하거나 선택한 내용과 Codex가 사용자에게 보낸 응답을 순서대로 기록
- 코드 결과: [profile.html](./profile.html)

## 1. 작업 요청

### 사용자

> bohye 디렉토리 하위에서 작업할거야. 그 디렉토리 안의 규칙대로 작업 시작하자.
> 이슈번호는 22번이야 https://github.com/juwonlee-dev/study-ai/issues/22

### Codex

> `bohye` 디렉토리의 작업 규칙과 22번 이슈 내용을 먼저 확인하겠습니다. 그다음 현재 브랜치와 변경 사항을 살펴보고, 규칙에 맞춰 작업 범위를 잡겠습니다. 작업 절차에는 `using-superpowers` 스킬을 적용하겠습니다.

## 2. 이슈와 원본 확인

Codex는 GitHub Issue #22, `bohye/AGENTS.md`, `bohye/week1/profile.png`, `bohye/week0/README.md`를 읽었다. 현재 브랜치가 `main`이고 루트의 `.DS_Store`가 기존 미추적 파일임을 확인했다. Orca CLI가 설치되어 있으며 실행 전 상태는 `not_running`이었다. `gh issue list/view`는 네트워크 연결 오류가 발생해, 같은 이슈를 GitHub 연결 도구로 확인했다.

### Codex

> 22번 이슈를 확인했습니다. 이번 작업은 `bohye/week1/profile.png`를 바탕으로 `bohye/week2/profile.html`을 만들고, AI와 주고받은 내용 전체를 제출하는 과제입니다. `bohye/AGENTS.md`에 브랜치 생성·커밋·푸시·PR은 각각 별도 승인 후 실행하도록 되어 있어, 우선 로컬 산출물 준비를 진행하겠습니다. 이미지 구성과 Orca 설치 상태를 이어서 확인하겠습니다.

## 3. 디자인 방향 선택

### Codex가 제시한 선택 질문

> 1주차 이미지를 웹페이지로 옮길 때, 원본의 세로형 포스터 구성을 최대한 충실히 재현할까요? 저는 데스크톱에서는 원본 배치를 살리고 모바일에서는 카드가 자연스럽게 쌓이도록 만드는 방향을 추천합니다.
>
> - 원본에 충실하게 재현 (추천)
> - 웹페이지에 맞게 자유롭게 재구성

### 사용자

> 1

첫 번째 선택지, 즉 원본에 충실한 재현을 선택했다.

### Codex

> 원본에 충실한 방향으로 정리했습니다. `brainstorming` 스킬의 설계 확인 단계를 진행하겠습니다.
>
> - **결과물:** `bohye/week2/profile.html` 한 파일에 내용과 스타일을 담습니다. 1주차 PNG를 페이지에 삽입하지 않고, 문구·카드·원형 장식·배경선을 HTML/CSS로 재현합니다.
> - **화면 구성:** 데스크톱은 원본의 세로형 포스터 흐름을 살립니다. 좁은 화면에서는 기본 정보와 기술 카드가 세로로 쌓이게 합니다.
> - **기록:** 이 대화의 사용자 요청, 선택, AI 응답과 이후 Orca 사용 내용을 `bohye/week2/prompt.md`에 정리합니다. 길게 섞여 있는 이슈의 과제 기준은 `ASSIGNMENT.md`에 따로 적습니다.
> - **검증:** 원본 문구와 HTML 텍스트를 대조하고, Orca에서 데스크톱·모바일 화면을 확인합니다. 22번 이슈의 다른 사람 PR 리뷰는 별도 작업으로 이어가겠습니다.
>
> Orca는 이미 설치돼 있고 현재 실행 중이지 않습니다. 이 설계로 제작을 진행해도 되는지 확인을 요청드립니다.

### Codex가 제시한 설계 승인 질문

> 위 설계대로 `bohye/week2/`의 HTML과 대화 기록을 제작할까요? 이 확인은 `brainstorming` 스킬에서 구현 전에 설계 승인을 받도록 요구하기 때문에 필요합니다.
>
> - 설계대로 제작 (추천)
> - 설계 수정 후 제작

### 사용자

> 1

첫 번째 선택지인 설계대로 제작을 승인했다.

## 4. 계획과 브랜치

### Codex

> 설계가 승인됐습니다. `writing-plans` 스킬로 파일별 작업과 검증 순서를 짧게 정리한 뒤, `bohye/week2/`에서 제작을 시작하겠습니다. 원본 PNG는 1600×2000이고, 주요 문구와 섹션 배치를 확인했습니다.

Codex는 [PLAN.md](./PLAN.md)와 [ASSIGNMENT.md](./ASSIGNMENT.md)를 작성하고 Orca를 실행했다. Orca 실행 결과 `runtimeState: ready`를 확인했다.

### Codex가 제시한 브랜치 승인 질문

> `bohye/AGENTS.md`는 브랜치 생성·전환에 명시적 승인을 요구하고, 구현 절차도 main에서 바로 제작하지 않도록 합니다. 과제 규칙의 `week2/bohye` 브랜치를 지금 만들어 이동해도 될까요?
>
> - week2/bohye 브랜치 생성·전환 승인 (추천)
> - 현재 main에서만 작업

### Codex

> 작업 계획은 `bohye/week2/PLAN.md`에 정리했고 Orca 실행도 확인했습니다. 현재 체크아웃이 `main`이라, `bohye/AGENTS.md`의 브랜치 변경 승인 규칙에 따라 `week2/bohye` 브랜치 승인 답변을 기다리고 있습니다. 그동안 이슈 요구사항과 원본 문구를 계속 대조하겠습니다.

### 사용자

> 1

첫 번째 선택지인 `week2/bohye` 생성·전환을 승인했다.

브랜치 전환의 첫 시도는 Git ref를 잠글 수 없어 실패했다. 권한 승인을 받은 재시도에서 `Switched to a new branch 'week2/bohye'`가 출력되었다.

### Codex

> 승인하신 `week2/bohye` 브랜치로 전환했습니다. 이제 `profile.html`을 작성하고 Orca에서 실제 렌더링을 확인하겠습니다. `PLAN.md`와 `ASSIGNMENT.md`는 이미 `bohye/week2/` 아래에 작성했습니다.

## 5. HTML 생성과 Orca 검증

Codex는 원본 이미지의 파란 세로선, 이름과 역할, KB 원형 장식, 기본 정보 4칸, 관심 기술 카드 3개, 스터디 목적, AI 활용, 하단 다짐을 HTML/CSS로 작성했다. 전체 코드 응답은 [profile.html](./profile.html)에 들어 있다. PNG, 외부 이미지, 스크립트, 외부 스타일 의존성은 사용하지 않았다.

Orca 브라우저에서 로컬 `profile.html`을 열었다. 접근성 트리에는 이름, 기본 정보, 기술 카드 3개, 스터디 목적, AI 활용, 다짐 문구가 순서대로 표시되었다. 데스크톱 뷰포트에서는 `innerWidth: 1929`, `scrollWidth: 1914`로 가로 넘침이 없었다. 데스크톱 캡처를 원본 PNG와 육안 대조하여 카드 순서, 색상, 글자 가독성을 확인했다.

### Codex

> Orca의 데스크톱 렌더링에서 원본의 섹션 순서, 카드 구성, 주요 문구가 확인됐습니다. 다음으로 Orca의 모바일 기기 에뮬레이션에서 가로 넘침과 텍스트 잘림을 확인하고, 확인 결과를 대화 기록에 반영하겠습니다.

Orca의 `iPhone 12` 에뮬레이션은 폭 390px이었다. 브라우저에서 `innerWidth: 390`, `document.documentElement.scrollWidth: 390`, 기본 정보 2열, 기술 카드 1열을 확인했다. 상단과 하단의 모바일 캡처에서 글자 잘림·겹침을 발견하지 않았다.

## 6. Task 2 PR 검토

Codex는 GitHub에서 현재 Week 2 PR과 기존 리뷰를 읽고, PR #44, #40, #42의 diff를 각각 검토했다. 다른 참여자의 파일은 수정하지 않았다. #40은 Orca에서 실제로 열어 820px iPad 에뮬레이션으로 재현했다. `screen.width: 820`에서 정보 표가 4열을 유지했고, 마지막 셀의 오른쪽 좌표가 911px까지 늘어나 페이지 레이아웃 폭이 910px으로 확장되었다. #44의 `prompt.md`는 일부 AI 응답을 표와 요약으로 대체하고, 전체 코드 응답을 기록하지 않았다. #42의 PR 본문과 프롬프트 문서는 사용 모델 표기가 서로 다르며, 기존 리뷰도 이 점을 지적했다.

### Codex

> 모바일에서는 390px 화면에서 가로 스크롤이 없고, 기술 카드와 기본 정보가 의도한 열 수로 배치됐습니다. 하단까지 확인해 문구 잘림도 발견되지 않았습니다. Task 2는 PR #44·#40·#42의 diff와 기존 리뷰를 읽었고, 확인된 근거만으로 리뷰 초안을 정리하겠습니다. 실제 GitHub 리뷰 등록은 `bohye/AGENTS.md`의 외부 변경 규칙에 따라 초안을 보여드린 뒤 진행하겠습니다.

### PR #44 리뷰 초안

> Issue #22의 경로와 HTML/CSS 구현, 이미지 미삽입은 확인했습니다. 다만 `hyunjin/week2/prompt.md`는 AI 응답을 분석 표·구현 요약·보정 표로 정리했고, 첫 요청에서 요구한 완성 코드와 수정 응답 원문은 포함하지 않았습니다. 이슈의 “프롬프트와 AI 응답 결과를 생략 없이” 조건을 충족할 수 있도록 실제 대화 응답을 턴 순서대로 보완해 주세요.

### PR #40 리뷰 초안

> `juhwan/week2/profile.html`의 761~약 900px 구간에서 정보 표가 카드 폭을 넘습니다. Orca의 iPad 820px 에뮬레이션에서 `dl`은 여전히 `126px 190px 126px auto` 4열이고 마지막 셀 오른쪽이 911px까지 확장됐습니다. 모바일 전환 기준이 760px이라 이 구간에서는 내용을 다 보려면 가로로 이동하거나 브라우저가 페이지를 축소합니다. 2열 전환 기준을 올리거나 중간 폭용 열 구성을 추가해 주세요. 그 외 HTML/CSS 구현은 확인했습니다.

### PR #42 리뷰 초안

> `gunsang/week2/profile.html`은 원본 디자인의 카드와 장식을 HTML/CSS·인라인 SVG로 구현했고, Task 2 리뷰 기록도 포함되어 있습니다. 다만 PR 본문에는 “Devin CLI / Claude Sonnet 5 (Low)”라고 적혀 있는데, `prompt.md`와 `task2-prompt.md`에는 “Devin (Cognition, SWE-2 High)”로 적혀 있습니다. Issue #22에서 AI 에이전트와 모델 표기를 요구하므로 실제 사용 모델을 확인해 세 곳의 정보를 맞춰 주세요. 이 불일치는 기존 리뷰에도 보고되어 있습니다.

### 리뷰 등록 승인

#### Codex가 제시한 선택 질문

> `bohye/AGENTS.md`가 GitHub 상태 변경에 명시적 승인을 요구합니다. `prompt.md`의 초안대로 열린 PR #44(의견), #40(변경 요청), #42(의견)에 리뷰를 등록할까요?
>
> - 세 건 모두 등록 승인 (추천)
> - 초안만 보관

#### 사용자

> 1

세 건 모두 등록을 승인했다. GitHub 연결 도구는 첫 등록 시 `Resource not accessible by integration`(403)을 반환했다. Codex는 로그인된 GitHub 브라우저에서 같은 내용을 제출했고, 각 PR의 대화 화면에 `bobo-h`의 리뷰가 나타난 것을 확인했다.

- [PR #44 의견 리뷰](https://github.com/juwonlee-dev/study-ai/pull/44#pullrequestreview-5661905441): AI 응답 원문 기록 보완 요청
- [PR #40 변경 요청 리뷰](https://github.com/juwonlee-dev/study-ai/pull/40#pullrequestreview-5661908305): 820px 화면 정보 표 넘침 수정 요청
- [PR #42 의견 리뷰](https://github.com/juwonlee-dev/study-ai/pull/42#pullrequestreview-5661909943): AI 모델 표기 불일치 확인 요청

## 7. AI가 생성한 전체 HTML 응답

아래 코드는 `profile.html`에 저장한 결과와 동일하다.

```html
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#eaf3ff" />
    <title>김보혜 | AI-Powered Full-Stack Developer</title>
    <style>
      :root {
        color-scheme: light;
        --navy: #142f5c;
        --blue: #1366e8;
        --muted: #52688a;
        --cyan: #08afd4;
        --surface: rgba(255, 255, 255, 0.9);
        font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo",
          "Malgun Gothic", "Noto Sans KR", sans-serif;
      }

      * { box-sizing: border-box; }

      body {
        margin: 0;
        color: var(--navy);
        background:
          radial-gradient(circle at 91% 8%, rgba(81, 111, 255, 0.28), transparent 27%),
          radial-gradient(circle at 3% 91%, rgba(81, 163, 255, 0.26), transparent 25%),
          radial-gradient(circle at 94% 89%, rgba(82, 163, 255, 0.22), transparent 28%),
          #f5faff;
      }

      body::before {
        content: "";
        position: fixed;
        inset: 0;
        z-index: -1;
        pointer-events: none;
        background:
          linear-gradient(132deg, transparent 38%, rgba(68, 135, 238, 0.1) 38.12%, transparent 38.24%),
          linear-gradient(44deg, transparent 60%, rgba(68, 135, 238, 0.1) 60.12%, transparent 60.24%),
          radial-gradient(circle at 5% 5%, #a3c1ff 0 4px, transparent 5px),
          radial-gradient(circle at 93% 45%, #9ed2ff 0 9px, transparent 10px),
          radial-gradient(circle at 8% 72%, #8db8f1 0 8px, transparent 9px);
      }

      .poster {
        width: min(100% - 80px, 1450px);
        margin: 68px auto;
        padding: 48px 40px 46px;
        position: relative;
        overflow: hidden;
        isolation: isolate;
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid rgba(255, 255, 255, 0.9);
        border-radius: 46px;
        box-shadow: 0 28px 90px rgba(71, 120, 186, 0.09);
      }

      .poster::before,
      .poster::after {
        content: "";
        position: absolute;
        z-index: -1;
        pointer-events: none;
        border: 2px solid rgba(36, 114, 239, 0.16);
        border-radius: 50%;
      }

      .poster::before {
        width: 650px;
        height: 650px;
        right: -290px;
        top: -350px;
        box-shadow: 0 0 0 74px rgba(110, 159, 255, 0.04), 0 0 0 146px rgba(110, 159, 255, 0.035);
      }

      .poster::after {
        width: 520px;
        height: 520px;
        right: -250px;
        bottom: -365px;
        box-shadow: 0 0 0 62px rgba(110, 159, 255, 0.04), 0 0 0 125px rgba(110, 159, 255, 0.035);
      }

      .hero {
        min-height: 315px;
        display: grid;
        grid-template-columns: minmax(0, 1fr) 310px;
        gap: 32px;
        align-items: center;
        position: relative;
        padding: 0 18px 0 46px;
      }

      .hero::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 12px;
        width: 12px;
        border-radius: 20px;
        background: var(--blue);
      }

      .eyebrow {
        margin: 0 0 22px;
        color: var(--blue);
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.025em;
        text-transform: uppercase;
      }

      h1 {
        margin: 0 0 14px;
        font-size: clamp(48px, 5vw, 70px);
        line-height: 1.15;
        letter-spacing: -0.065em;
        font-weight: 850;
      }

      .role {
        margin: 0 0 24px;
        color: var(--muted);
        font-size: 28px;
        font-weight: 700;
        line-height: 1.45;
        letter-spacing: -0.035em;
      }

      .intro {
        max-width: 900px;
        margin: 0;
        font-size: 23px;
        font-weight: 650;
        line-height: 1.65;
        letter-spacing: -0.04em;
      }

      .identity-art {
        width: 292px;
        aspect-ratio: 1;
        display: grid;
        place-items: center;
        justify-self: end;
        position: relative;
        border-radius: 50%;
        background:
          radial-gradient(circle at 62% 29%, rgba(255,255,255,.9) 0 17%, transparent 18%),
          radial-gradient(circle at 36% 38%, rgba(235,246,255,.9) 0 31%, transparent 32%),
          radial-gradient(circle at 64% 69%, rgba(140,181,247,.22) 0 38%, transparent 39%),
          linear-gradient(140deg, #f4faff, #d5e6ff);
      }

      .identity-art::before,
      .identity-art::after {
        content: "";
        position: absolute;
        border-radius: 50%;
        pointer-events: none;
      }

      .identity-art::before {
        width: 375px;
        height: 375px;
        border: 2px solid rgba(42, 120, 245, 0.23);
        box-shadow: 0 0 0 33px rgba(77, 132, 243, 0.04);
      }

      .identity-art::after {
        width: 190px;
        height: 190px;
        transform: rotate(-35deg) scaleX(1.38);
        border: 25px solid rgba(152, 190, 247, 0.14);
      }

      .monogram {
        z-index: 1;
        width: 148px;
        aspect-ratio: 1;
        display: grid;
        place-items: center;
        border: 5px solid var(--blue);
        border-radius: 50%;
        background: #f9fcff;
        color: var(--blue);
        font-size: 42px;
        font-weight: 800;
      }

      .facts {
        margin: 8px 0 48px;
        padding: 22px 24px;
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 24px;
        background: var(--surface);
        border-radius: 28px;
      }

      .facts div { min-width: 0; }
      .facts dt {
        margin-bottom: 5px;
        color: var(--blue);
        font-size: 18px;
        font-weight: 800;
      }
      .facts dd {
        margin: 0;
        font-size: 25px;
        line-height: 1.35;
        font-weight: 800;
        letter-spacing: -0.035em;
      }

      .section-heading {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        gap: 20px;
        margin: 0 0 24px;
      }

      h2 {
        margin: 0;
        font-size: 37px;
        line-height: 1.35;
        font-weight: 850;
        letter-spacing: -0.055em;
      }

      .section-heading span {
        color: var(--blue);
        font-size: 20px;
        font-weight: 800;
        letter-spacing: .025em;
      }

      .skills {
        margin-bottom: 44px;
      }

      .skill-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 28px;
        padding: 27px 24px 36px;
        background: var(--surface);
        border-radius: 30px;
      }

      .skill-title {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 18px;
      }

      .skill-number,
      .goal-number {
        flex: none;
        display: grid;
        place-items: center;
        border-radius: 50%;
        color: white;
        font-weight: 800;
      }

      .skill-number {
        width: 48px;
        height: 48px;
        background: var(--blue);
        font-size: 20px;
      }

      h3 {
        margin: 0;
        font-size: 29px;
        line-height: 1.35;
        font-weight: 800;
        letter-spacing: -0.03em;
      }

      .skill-grid p {
        margin: 0;
        color: var(--muted);
        font-size: 21px;
        font-weight: 650;
        line-height: 1.65;
        letter-spacing: -0.035em;
      }

      .goals,
      .ai-use {
        border-radius: 30px;
        padding: 30px 34px 34px;
      }

      .goals {
        margin-bottom: 38px;
        background: rgba(236, 245, 255, 0.86);
      }

      .goals > p,
      .ai-use p {
        color: var(--muted);
        font-size: 21px;
        font-weight: 650;
        line-height: 1.75;
        letter-spacing: -0.037em;
      }

      .goals > p { margin: 16px 0 36px; }

      .goal-list {
        list-style: none;
        margin: 0;
        padding: 0;
        display: grid;
        gap: 15px;
      }

      .goal-list li {
        display: flex;
        align-items: center;
        gap: 19px;
        font-size: 22px;
        line-height: 1.45;
        font-weight: 750;
        letter-spacing: -0.035em;
      }

      .goal-number {
        width: 45px;
        height: 45px;
        background: var(--cyan);
        font-size: 20px;
      }

      .ai-use {
        background: var(--surface);
      }

      .ai-use p { margin: 15px 0 35px; }
      .ai-use p:last-child { margin-bottom: 0; }
      .ai-use .record {
        color: var(--blue);
        font-weight: 800;
      }

      .closing {
        margin-top: 42px;
        padding: 31px 24px;
        border-radius: 29px;
        background: #1b3764;
        color: #fff;
        text-align: center;
        font-size: 23px;
        font-weight: 800;
        line-height: 1.5;
        letter-spacing: -0.04em;
      }

      @media (max-width: 900px) {
        .poster { width: min(100% - 32px, 760px); margin: 16px auto; padding: 28px 22px; border-radius: 28px; }
        .hero { grid-template-columns: minmax(0, 1fr) 190px; gap: 18px; padding-left: 28px; min-height: 230px; }
        .hero::before { width: 8px; }
        .identity-art { width: 170px; }
        .identity-art::before { width: 220px; height: 220px; }
        .identity-art::after { width: 110px; height: 110px; border-width: 15px; }
        .monogram { width: 92px; border-width: 3px; font-size: 29px; }
        .eyebrow { font-size: 17px; margin-bottom: 12px; }
        h1 { font-size: 48px; }
        .role { font-size: 21px; margin-bottom: 12px; }
        .intro { font-size: 18px; }
        .facts { gap: 16px; }
        .facts dt { font-size: 15px; }
        .facts dd { font-size: 19px; }
        h2 { font-size: 29px; }
        .skill-grid { gap: 16px; }
        .skill-title { gap: 10px; }
        .skill-number { width: 36px; height: 36px; font-size: 16px; }
        h3 { font-size: 21px; }
        .skill-grid p, .goals > p, .ai-use p, .goal-list li { font-size: 17px; }
      }

      @media (max-width: 640px) {
        .poster { width: min(100% - 20px, 480px); padding: 24px 16px; border-radius: 22px; }
        .hero { display: block; min-height: 0; padding: 0 0 0 20px; }
        .hero::before { bottom: 0; width: 6px; }
        .identity-art { display: none; }
        .eyebrow { font-size: 13px; margin-bottom: 9px; }
        h1 { font-size: 42px; margin-bottom: 10px; }
        .role { font-size: 17px; }
        .intro { font-size: 16px; }
        .facts { grid-template-columns: repeat(2, minmax(0, 1fr)); margin: 28px 0 32px; padding: 18px; gap: 18px 12px; }
        .facts dt { font-size: 13px; }
        .facts dd { font-size: 17px; }
        .section-heading { margin-bottom: 16px; }
        .section-heading span { font-size: 13px; }
        h2 { font-size: 26px; }
        .skills { margin-bottom: 24px; }
        .skill-grid { grid-template-columns: 1fr; padding: 18px; gap: 22px; }
        .skill-title { margin-bottom: 8px; }
        .skill-grid p { padding-left: 45px; }
        .goals, .ai-use { padding: 22px 19px; border-radius: 22px; }
        .goals { margin-bottom: 24px; }
        .goals > p { margin: 13px 0 24px; }
        .goal-list { gap: 14px; }
        .goal-list li { align-items: flex-start; gap: 11px; }
        .goal-number { width: 32px; height: 32px; font-size: 15px; }
        .ai-use p { margin-bottom: 22px; }
        .closing { margin-top: 24px; padding: 22px 15px; font-size: 17px; border-radius: 21px; }
      }

      @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { scroll-behavior: auto !important; }
      }
    </style>
  </head>
  <body>
    <main class="poster">
      <header class="hero">
        <div>
          <p class="eyebrow">AI-POWERED FULL-STACK DEVELOPER</p>
          <h1>김보혜</h1>
          <p class="role">Full-Stack Developer&nbsp; · &nbsp;AI를 효율적으로 활용하는 개발자</p>
          <p class="intro">반복되는 개발 과정은 더 안정적으로, 새로운 기술은 더 깊이 있게 배우고 싶습니다.</p>
        </div>
        <div class="identity-art" aria-hidden="true"><span class="monogram">KB</span></div>
      </header>

      <dl class="facts" aria-label="기본 정보">
        <div><dt>생년월일</dt><dd>1995.11.06</dd></div>
        <div><dt>성별</dt><dd>여성</dd></div>
        <div><dt>직업·역할</dt><dd>풀스택 개발자</dd></div>
        <div><dt>MBTI</dt><dd>ENTJ</dd></div>
      </dl>

      <section class="skills" aria-labelledby="skills-title">
        <div class="section-heading">
          <h2 id="skills-title">관심 기술과 학습 분야</h2>
          <span>INTERESTS</span>
        </div>
        <div class="skill-grid">
          <article>
            <div class="skill-title"><span class="skill-number" aria-hidden="true">01</span><h3>AI Engineering</h3></div>
            <p>AI를 개발 과정에 안정적이고 효율적으로 적용하는 방법</p>
          </article>
          <article>
            <div class="skill-title"><span class="skill-number" aria-hidden="true">02</span><h3>NestJS</h3></div>
            <p>구조적이고 확장 가능한 백엔드 애플리케이션 개발</p>
          </article>
          <article>
            <div class="skill-title"><span class="skill-number" aria-hidden="true">03</span><h3>Flutter</h3></div>
            <p>하나의 코드베이스를 활용한 크로스 플랫폼 앱 개발</p>
          </article>
        </div>
      </section>

      <section class="goals" aria-labelledby="goals-title">
        <h2 id="goals-title">스터디 참여 목적</h2>
        <p>AI를 단순한 코드 생성 도구로 사용하는 데 그치지 않고, 개발 과정 전반에서 더 효율적으로 활용하는 방법을 배우기 위해 참여했습니다.</p>
        <ol class="goal-list">
          <li><span class="goal-number" aria-hidden="true">1</span>역할과 기능에 맞는 AI 프롬프트 작성법</li>
          <li><span class="goal-number" aria-hidden="true">2</span>불필요한 컨텍스트 사용을 줄이는 토큰 관리법</li>
          <li><span class="goal-number" aria-hidden="true">3</span>AI를 활용하면서도 품질을 지킬 수 있는 TDD 개발 방향</li>
        </ol>
      </section>

      <section class="ai-use" aria-labelledby="ai-title">
        <h2 id="ai-title">AI 활용</h2>
        <p>Codex를 사용해 AGENTS.md를 작성하고, 주차별 과제에서 반복되는 폴더 생성·브랜치 생성·작업 범위 등의 규칙을 미리 정의했습니다. 이를 통해 이후 과제를 일관된 방식으로 진행하고 반복 작업의 실수를 줄이고자 했습니다.</p>
        <p>또한 GitHub Issue에서 실제 과제 요구사항과 스터디 운영 정보를 구분해 작업 범위를 정리하고, 자기소개에 필요한 정보는 질문을 통해 구체화한 뒤 README의 구조와 내용을 작성하는 데 활용했습니다.</p>
        <p class="record">Codex와 주고받은 프롬프트 및 응답은 codex-prompt.txt에 기록했습니다.</p>
      </section>

      <footer class="closing">AI와 함께 더 효율적으로 개발하고, 배운 내용을 꾸준히 실전에 연결하겠습니다. 🌱</footer>
    </main>
  </body>
</html>
```

## 8. 제출 요청

### Codex

> 이슈 #22 작업을 `week2/bohye` 브랜치의 `bohye` 디렉토리에서 진행했습니다. `profile.html`은 1주차 이미지를 HTML/CSS로 재현했고 Orca에서 데스크톱과 모바일 화면을 확인했습니다. `prompt.md`에는 작업 대화와 HTML 전체 코드, 리뷰 결과를 기록했습니다. 서로 다른 참여자의 PR #44, #40, #42에 리뷰를 등록했습니다. 파일은 아직 미추적 상태이며 커밋·푸시·본인 PR 생성은 진행하지 않았습니다.

### 사용자

> 내 작업도 커밋 푸시진행해줘

### Codex

> 현재 브랜치와 `bohye` 디렉토리의 규칙, 커밋 대상 파일을 다시 확인한 뒤 요청하신 작업만 커밋하고 푸시하겠습니다.

현재 브랜치 `week2/bohye`와 `bohye/AGENTS.md`의 커밋 범위 규칙을 확인했다. 미추적 루트 `.DS_Store`는 이번 과제와 관련이 없어 커밋 대상에서 제외한다. HTML 구문, 이미지·스크립트 참조 미사용, 이 문서의 전체 HTML 코드 및 리뷰 링크 포함을 다시 확인했다.
