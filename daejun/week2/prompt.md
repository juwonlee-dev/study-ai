# 최대준 Week2 – 자기소개 이미지 HTML 변환 대화 기록

> Week1에서 만든 자기소개 이미지(`daejun/week1/profile.png`)를 HTML/CSS 페이지(`daejun/week2/profile.html`)로 구현한 작업의 **전체 대화 기록**입니다.
> 본인이 작성한 프롬프트와 AI 응답을 생략 없이 순서대로 정리했습니다.

| 항목 | 내용 |
| --- | --- |
| 사용 AI 에이전트 | Claude Code (CLI, Windows) |
| 모델 | Claude Opus 5.5 (`claude-opus-5-5`) |
| 작업 브랜치 | `week2/daejun` |
| 과제 이슈 | [#22 2주차](https://github.com/juwonlee-dev/study-ai/issues/22) |
| 결과물 | `daejun/week2/profile.html`, `daejun/week2/images/*.png`, `daejun/week2/prompt.md` |
| PR | [#36](https://github.com/juwonlee-dev/study-ai/pull/36) |

> 1차 구현(3장)은 그림을 inline SVG로 직접 그렸고, 사용자 요청에 따라 5장에서 **Week1 이미지에서 잘라낸 PNG 그림을 넣는 방식**으로 다시 작업했습니다.

---

## 1. GitHub 저장소 계정 연동

### 🙋 질문

> https://github.com/juwonlee-dev/study-ai 해당 깃허브 경로에 계정 연동해서 작업 할꺼야.

### 🤖 답변

**작업 내용**
- `git --version`, `gh --version`, `gh auth status`, `git config --global user.name/email` 로 환경 확인

**응답**

> Git(2.45.1)과 GitHub CLI(2.101.0)는 설치되어 있지만, GitHub에는 아직 로그인되어 있지 않습니다. `C:\AI` 폴더는 현재 비어 있습니다.
>
> **1. GitHub 로그인 (직접 실행해 주세요)**
>
> 로그인은 브라우저 인증이 필요해서 제가 대신 할 수 없습니다. 프롬프트에 아래를 입력해 주세요.
>
> ```
> ! gh auth login -h github.com -p https -w
> ```
>
> 터미널에 일회용 코드가 표시되고 브라우저가 열립니다. `juwonlee-dev` 계정으로 로그인한 뒤 그 코드를 입력하면 됩니다. 이 과정에서 git이 같은 계정으로 push할 수 있도록 설정됩니다.
>
> **2. 로그인이 끝나면 제가 할 일**
> - 로그인이 됐는지와 저장소에 접근할 수 있는지 확인
> - `C:\AI`에 `study-ai` 저장소 clone
> - 커밋 작성자 정보 확인. 지금 git 전역 설정은 `DJ <joon5380@gmail.com>`입니다. 커밋을 `juwonlee-dev` 계정 이름으로 남기고 싶으면 이 저장소에만 다른 이름과 이메일을 설정할 수 있으니 알려 주세요.
>
> 로그인이 끝나면 말씀해 주세요.

---

## 2. GitHub CLI 로그인 실행

### 🙋 입력 (터미널 직접 실행)

```
! gh auth login -h github.com -p https -w
```

```
! One-time code (DA2C-C387) copied to clipboard
Open this URL to continue in your web browser: https://github.com/login/device
✓ Authentication complete.
- gh config set -h github.com git_protocol https
✓ Configured git protocol
✓ Logged in as joon5380
```

### 🤖 답변

**작업 내용**
- `gh auth status` 로 로그인 계정 확인 → `joon5380`, 토큰 scope `gist, read:org, repo`
- `gh repo view juwonlee-dev/study-ai` 로 권한 확인 → `viewerPermission: WRITE`
- `git clone https://github.com/juwonlee-dev/study-ai.git C:\AI\study-ai` 실행 후 최근 커밋·폴더 구조 확인

**응답**

> 저장소를 `C:\AI\study-ai`에 clone했고, 이제 이 저장소에서 작업할 수 있습니다. `joon5380` 계정으로 로그인했는데, 이 계정은 저장소에 쓰기 권한이 있어서 push도 됩니다.
>
> **저장소 구조**
> - 멤버별로 폴더가 하나씩 있습니다: `bohye`, `gunsang`, `inseo`, `juhwan`, `juwonlee`, `siyoungwoo`, `yiseul`
> - 작업 방식은 `week0/<이름>` 브랜치에서 작업한 뒤 PR을 올리고 `main`에 merge하는 흐름입니다(예: PR #13 `week0/yiseul`).
>
> **참고할 점**
> - 루트에 README나 기여 규칙 문서는 없습니다.
> - 커밋 작성자는 전역 설정인 `DJ <joon5380@gmail.com>`으로 남습니다.
>
> 본인 폴더가 어느 것인지, 이번에 할 작업(예: `week1/<이름>` 브랜치 만들기)이 무엇인지 알려 주시면 바로 시작하겠습니다.

---

## 3. Week2 과제 수행 요청

### 🙋 질문

> git issues에 2주차 과제 작업을 진행할꺼야. ASSIGNMENT.md 파일에 내용 기준으로 작업해줘. Week1 자기소개 이미지를 HTML 페이지로 만들어줘.

### 🤖 답변

#### 3-1. 과제 기준 확인

- `gh issue list` 로 이슈 확인 → `#22 2주차`, `#14 1주차`, `#1 0주차`
- `ASSIGNMENT.md` 확인 → 작업 브랜치 `week2/daejun`, 결과물 `daejun/week2/profile.html`, 프롬프트 기록 `prompt.md`
- 이슈 #14(1주차) 공통 규칙 확인 → 본인 폴더에서만 작업, 리뷰어 `@juwonlee-dev` `@juhwanHeo` 필수 + 1인 이상 추가
- Week1 원본 이미지 확인: `C:\Users\DJ\IdeaProjects\AI_study\daejun\week1\profile.png` (원격 `origin/week1/daejun` 브랜치에도 동일 파일 존재)

> 과제 기준을 확인했습니다. 이번 과제는 `week2/daejun` 브랜치에서 `daejun/week2/profile.html`을 만드는 것입니다. 이제 Week1 이미지를 보겠습니다.

#### 3-2. 원본 이미지 분석

원본 `profile.png`에서 읽어낸 내용과 디자인 요소입니다.

| 영역 | 내용 | 디자인 |
| --- | --- | --- |
| 헤더 | `Hello, I'm` / `최대준!` | 굵은 둥근 손글씨체, 이름 아래 노란 형광펜 밑줄, 노란 꽃·반짝이 장식 |
| 역할 배지 | `</> Developer` \| `🏢 ABL생명` | 노란 알약(pill) 배지 |
| 일러스트 | 노란 후드티 남자 캐릭터 + 노트북(`</>`), 전구, `Better Together ♥`, 고양이 | 우측 상단 |
| About Me | 성별 남자 / 직업 개발자 / 취미 영화 / 관심사 AI / MBTI INFJ | 해바라기 아이콘 제목, 5행 표, 행별 아이콘(♂, 노트북, 클래퍼보드, 로봇, 새싹) |
| My Interests | Movie / Artificial Intelligence / Development | 3칸 카드, 아이콘 + 노란 알약 라벨 |
| 소개 문구 | “기술을 통해 더 나은 가치를 만들어가는 개발자, 최대준입니다.” | 노란 띠, 양옆 해바라기 |
| 푸터 | `Thanks for visiting!` / `Have a nice day!` | 반짝이 별, 스마일 배지, 하단 구름 |

#### 3-3. 브랜치 생성 및 구현

```powershell
git checkout -b week2/daejun origin/main
New-Item -ItemType Directory -Force daejun\week2
```

> 이미지 내용을 확인했습니다. 먼저 `main`에서 `week2/daejun` 브랜치를 만들겠습니다.
>
> 이제 이미지의 디자인과 내용을 HTML/CSS로 옮기겠습니다. 아이콘과 캐릭터는 이미지 파일을 쓰지 않고 inline SVG로 그립니다.

구현 방식
- **이미지 첨부 없이** HTML/CSS + inline SVG로만 구현 (`<img>`, `.png`, base64 사용 0건)
- 아이콘(해바라기, 꽃, 노트북, 클래퍼보드, 로봇, 새싹, 빌딩, 별, 스마일)은 `<symbol>`로 정의하고 `<use>`로 재사용
- 캐릭터·고양이·전구·하단 구름도 SVG path로 직접 드로잉
- 폰트: Google Fonts `Jua`(제목), `Gaegu`(손글씨), `Gowun Dodum`(본문)
- 색상은 `:root` CSS 변수로 노란 파스텔 톤 정의
- 모바일(560px 이하)에서 헤더를 세로로 쌓는 반응형 적용

#### 3-4. 렌더링 검증 및 수정 (1차)

Edge headless로 데스크톱(700px)·모바일 스크린샷을 찍어 원본과 비교했습니다.

> 첫 렌더링에서 고칠 부분이 네 가지 보입니다.
> - 데스크톱에서 "Better Together"가 오른쪽 가장자리에서 잘립니다.
> - 소개 문구와 "Artificial Intelligence"가 원본과 달리 두 줄로 넘어갑니다.
> - 모바일 화면이 가로로 넘칩니다. headless 브라우저의 최소 창 너비 때문일 수도 있어서 iframe으로 따로 확인하겠습니다.

수정 내용
- 캐릭터 위치(`right: 34px`)·크기 조정, `Better Together` 위치·크기 조정
- 관심사 라벨 `font-size: 15px; white-space: nowrap`
- 소개 문구 `word-break: keep-all`
- 모바일 역할 배지 크기 축소
- 375px iframe 테스트 페이지로 모바일 레이아웃 재확인

#### 3-5. 렌더링 검증 및 수정 (2차)

> 모바일은 375px 안에 맞게 들어옵니다. 남은 부분은 두 가지입니다. 모바일에서 "관심사"가 두 줄로 줄바꿈되고, 데스크톱에서 소개 문구가 두 줄로 나옵니다. 원본처럼 한 줄로 맞추겠습니다.

수정 내용
- 표 라벨 `white-space: nowrap` → 모바일 `관심사` 줄바꿈 해결
- 데스크톱 소개 문구 한 줄 고정(`white-space: nowrap`, 18px), 모바일에서는 줄바꿈 허용
- 하단 여백 축소

#### 3-6. 최종 내용 검증

> 데스크톱과 모바일 모두 원본 이미지와 같은 레이아웃으로 나옵니다. 창이 페이지보다 길 때 카드가 아래로 늘어나는 문제만 하나 고치고, 이미지에 있는 텍스트가 HTML에 빠짐없이 들어갔는지 확인하겠습니다.

- `body`에 `align-items: flex-start` 추가 (페이지가 창 높이만큼 늘어나는 현상 수정)
- 원본 이미지의 모든 텍스트를 HTML 소스에서 자동 검사 (bash `grep -F`, 표는 `라벨 → 값` 쌍 단위로 검사)

```
OK   이름
OK   역할
OK   소속
OK   성별=남자
OK   직업=개발자
OK   취미=영화
OK   관심사=AI
OK   MBTI=INFJ
OK   Movie
OK   AI 관심사
OK   Development
OK   소개 문구
OK   Hello
OK   Better Together
OK   Thanks
OK   Nice day
table rows: 5
row order: 성별 직업 취미 관심사 MBTI
이미지 파일 참조(img/png/jpg/base64): 0
```

> 이미지의 텍스트 16개 항목이 모두 HTML에 들어 있습니다. 표는 원본과 같이 5개 행이고 순서도 같으며, 이미지 파일은 하나도 참조하지 않습니다. 다음으로 이번 대화를 생략 없이 정리한 `prompt.md`를 작성하겠습니다.

---

## 4. 커밋 · 리뷰어 지정 · PR 생성 (1차)

### 🤖 답변 (3장에서 이어짐)

> 파일 두 개를 모두 작성했습니다. 커밋하고, PR에 추가할 리뷰어 후보를 확인하겠습니다.

- PowerShell에서 `git commit -F -`로 메시지를 표준 입력으로 넘기려 했으나 전달되지 않아 실패

> PowerShell에서는 커밋 메시지가 표준 입력으로 넘어가지 않아 커밋이 만들어지지 않았습니다. 메시지를 파일로 저장해서 다시 커밋하겠습니다.

- Bash heredoc으로 커밋 성공: `a04e3d3 week2 자기소개 이미지 HTML 페이지 구현`
- `gh api repos/juwonlee-dev/study-ai/collaborators` 로 리뷰어 후보 조회

> 로컬 커밋까지 끝났습니다. push하고 PR을 만들기 전에 추가 리뷰어를 정해야 합니다. 필수 리뷰어 2명 외에 최소 1명이 더 필요합니다.

**AI 질문:** 필수 리뷰어(@juwonlee-dev, @juhwanHeo) 외에 추가로 지정할 리뷰어는 누구인가요?

### 🙋 선택

> LSHgy

### 🤖 답변

> 추가 리뷰어는 LSHgy로 정했습니다. push하고 PR을 만들겠습니다.

- 첫 push 실패: `fatal: could not read Username for 'https://github.com': terminal prompts disabled`

> GitHub CLI 로그인 정보가 git에 연결되어 있지 않아 push가 실패했습니다. 그래서 PR도 만들어지지 않았습니다. `gh auth setup-git`으로 연결한 뒤 다시 시도하겠습니다.

- `gh auth setup-git` 후 push 성공 → `gh pr create` 로 PR [#36](https://github.com/juwonlee-dev/study-ai/pull/36) 생성, 리뷰어 `juwonlee-dev`, `juhwanHeo`, `LSHgy`

**최종 응답**

> 2주차 과제 PR을 올렸습니다: https://github.com/juwonlee-dev/study-ai/pull/36
>
> - **브랜치와 파일:** `week2/daejun` 브랜치에 커밋해 push했고, PR에는 두 파일만 들어 있습니다.
>   - `daejun/week2/profile.html`: Week1 이미지를 HTML/CSS로 다시 만든 페이지입니다. 이미지 파일은 쓰지 않았고, 아이콘·캐릭터·고양이·구름은 모두 SVG 코드로 직접 그렸습니다.
>   - `daejun/week2/prompt.md`: 이번 대화의 프롬프트와 응답을 정리한 기록입니다.
> - **리뷰어:** @juwonlee-dev, @juhwanHeo, @LSHgy
> - **PR 본문:** 사용한 AI(Claude Code / Claude Opus 5.5)와 검증 결과를 적었습니다.
>
> **어떻게 확인했나요**
> - 브라우저(Edge)로 데스크톱과 휴대폰 너비(375px) 화면을 캡처해 원본과 비교했고, 두 번 고쳤습니다.
> - 이미지에 있는 텍스트 16개 항목이 HTML에 빠짐없이 들어 있습니다. About Me 표도 원본처럼 5행이고 순서가 같습니다.
>
> **알아두실 점**
> - **생년월일:** 과제 검증 기준에는 생년월일이 있지만 Week1 이미지에는 없습니다. 원본과 내용이 달라지지 않게 넣지 않았고, PR 본문에도 이 점을 적었습니다.
> - **관심사 설명:** 검증 기준의 "관심사 각 설명"도 이미지에는 라벨(Movie / Artificial Intelligence / Development)만 있어서, 그 라벨만 넣었습니다.
> - **prompt.md 누락 부분:** prompt.md를 작성한 뒤에 진행한 커밋, 리뷰어 선택, push, PR 생성 과정은 기록에 아직 없습니다. 과제의 "생략 없이" 조건에 맞추려면 이 부분을 추가해 PR에 다시 올리겠습니다.
> - **push 설정 변경:** push가 처음에 인증 오류로 실패해서 `gh auth setup-git`을 실행했습니다. 이 설정으로 이제 git이 `joon5380` 계정의 GitHub 로그인 정보로 push합니다.
> - **ASSIGNMENT.md:** 저장소 루트에 있는 `ASSIGNMENT.md`는 커밋하지 않았습니다.

---

## 5. 그림을 이미지로 교체하는 재작업

### 🙋 질문

> 이미지를 SVG로 직접 그리지 말고 이미지 생성해서 넣는걸로 다시 해줘. 그리고 커밋과 PR 올리기 전에 나한테 먼저 컨펌받고 작업해.

### 🤖 답변

#### 5-1. 작업 규칙 저장 및 이미지 생성 방법 확인

- "커밋·push·PR 전에 반드시 사용자 확인" 규칙을 Claude Code 메모리에 저장
- 이미지 생성 수단 확인: 이미지 생성 API 키·CLI 없음, Python도 미설치

> 이 PC에는 이미지 생성 API 키나 이미지 생성 CLI(codex, gemini 등)가 없습니다. 저(Claude Code)도 그림을 새로 생성하는 기능은 없습니다. 그래서 그림을 어떻게 만들지 정해 주셔야 합니다.

**AI 질문:** 페이지에 넣을 그림(캐릭터, 고양이, 아이콘 등)을 어떻게 만들까요?
- 다른 AI로 직접 생성 (추천)
- Week1 이미지에서 잘라내기
- API 키로 제가 생성

### 🙋 선택

> Week1 이미지에서 잘라내기

#### 5-2. 그림 요소 잘라내기

> Week1 이미지에서 그림 부분만 잘라 쓰고, 글자는 모두 HTML로 유지하겠습니다.

- Python이 없어 PowerShell 기본 내장 .NET `System.Drawing`으로 이미지 처리
- 원본(1024×1536)에서 영역을 잘라 좌표 확인 → 그림 요소 21개 좌표 확정
- **배경 투명화**: 잘라낸 영역의 테두리에서 시작해 배경색과 비슷한 픽셀만 따라가며(flood fill) 투명하게 처리. 그림 안쪽 흰색(고양이, 꽃 가운데 등)은 외곽선으로 막혀 있어 유지됨
- **글자 제거**: 캐릭터 이미지에 포함된 손글씨 `Better Together ♥`는 배경색으로 지운 뒤, HTML 텍스트로 다시 작성

처리 중 발생한 문제와 해결

| 문제 | 원인 | 해결 |
| --- | --- | --- |
| C# 컴파일 오류 | PowerShell 5.1이 BOM 없는 UTF-8 스크립트를 ANSI로 읽어 한글 주석이 깨짐 | 스크립트를 UTF-8(BOM)으로 저장 |
| 함수 대신 다른 명령 실행 | `R`이 PowerShell 기본 별칭(Invoke-History)과 겹침 | 함수 이름을 `Rect`로 변경 |
| 고양이 몸통이 투명해짐 | 흰 고양이 색이 크림색 배경과 비슷함 | 캐릭터 이미지의 투명 처리 기준을 더 엄격하게 조정 |
| 구름 이미지가 반대로 투명해짐 | 테두리 대부분이 구름이라 구름색을 배경으로 판단 | 배경색을 뽑을 위치를 직접 지정 |
| 반짝이 선 이미지에 꽃·밑줄 조각 포함 | 자른 영역이 옆 요소와 겹침 | 겹친 부분을 지우는 영역 추가 |

> 고양이는 잘 살아났습니다. 사람 머리 주변에 남은 연한 테두리는 원본 배경색이라, 페이지 배경을 같은 크림색으로 맞추면 보이지 않습니다. 다만 구름은 반대로 됐습니다. 잘라낸 영역의 테두리 대부분이 구름이라 구름 색을 배경으로 잘못 판단했습니다. 구름은 배경색을 뽑을 위치를 직접 지정하겠습니다.

생성된 이미지 (`daejun/week2/images/`)

| 파일 | 용도 |
| --- | --- |
| `hero.png` | 캐릭터 + 노트북 + 전구 + 고양이 |
| `flower-left.png`, `flower-right.png` | 헤더 노란 꽃 |
| `sparks-top.png`, `sparks-left.png`, `sparks-right.png` | 헤더 반짝이 선 |
| `icon-building.png` | 역할 배지 빌딩 아이콘 |
| `sunflower.png`, `sunflower-small.png` | 섹션 제목·소개 문구 해바라기 |
| `icon-male.png`, `icon-laptop.png`, `icon-clapper.png`, `icon-robot.png`, `icon-sprout.png` | About Me 표 아이콘 |
| `interest-movie.png`, `interest-ai.png`, `interest-dev.png` | My Interests 아이콘 |
| `twinkle.png`, `smile.png` | 푸터 별·스마일 |
| `cloud-left.png`, `cloud-right.png` | 하단 구름 |

#### 5-3. HTML 재작성

> 색상을 추출했습니다. 이제 SVG를 모두 빼고, 잘라낸 PNG를 `<img>`로 넣은 HTML로 다시 작성하겠습니다. 글자는 전부 HTML 텍스트로 유지합니다.

- 원본 이미지에서 배경·카드·표·배지 색상을 픽셀 단위로 추출해 CSS 변수에 반영 (예: 배경 `#fdf3c8`, 역할 배지 `#fed968`, 관심사 라벨 `#fde89e`)
- inline SVG 전부 제거 → `<img src="images/...">` 로 교체
- 텍스트(이름, 표, 관심사, 소개 문구, 인사말, Better Together)는 모두 HTML 텍스트 유지

> 원본과 거의 같은 모습입니다. 두 군데만 고치겠습니다.
> - 역할 배지의 빌딩 아이콘이 컬러 이모지(🏢)로 나옵니다. 원본의 갈색 빌딩 아이콘을 잘라서 넣겠습니다.
> - 모바일에서 "Better Together"가 전구와 겹칩니다.

#### 5-4. 최종 검증

> 데스크톱과 모바일 모두 정상입니다. 텍스트 내용, 이미지 경로, SVG가 남아 있는지를 다시 검사하겠습니다.

```
OK   이름 / 역할 / 소속
OK   성별=남자 / 직업=개발자 / 취미=영화 / 관심사=AI / MBTI=INFJ
OK   Movie / Artificial Intelligence / Development
OK   소개 문구 / Hello / Better Together / Thanks / Nice day
table rows: 5
svg 사용: 0
img 참조 21개 → 파일 모두 존재, 참조되지 않는 이미지 없음 (총 496KB)
```

> 검사를 모두 통과했습니다. 이제 `prompt.md`에 빠져 있던 커밋·PR 과정과 이번 재작업 내용을 추가하겠습니다.

- 이후 커밋·push·PR 업데이트는 **사용자 확인 후** 진행

---

## ✅ 검증 기준 대조표

| ASSIGNMENT.md 검증 기준 | 원본 이미지 | profile.html | 결과 |
| --- | --- | --- | --- |
| 이름 | 최대준 | `최대준!` | ✅ 일치 |
| 생년월일 | *(이미지에 없음)* | *(추가하지 않음)* | ➖ 원본 미기재 |
| 성별 | 남자 | 남자 | ✅ 일치 |
| 역할 | Developer / 직업: 개발자 | Developer / 직업: 개발자 | ✅ 일치 |
| MBTI | INFJ | INFJ | ✅ 일치 |
| 관심사 (표) | AI | AI | ✅ 일치 |
| 관심사 (My Interests) | Movie / Artificial Intelligence / Development | Movie / Artificial Intelligence / Development | ✅ 일치 |

> 생년월일은 Week1 이미지에 없는 정보라서, 원본과 다른 내용이 생기지 않도록 HTML에 넣지 않았습니다.

---

## 📁 최종 결과물

- `daejun/week2/profile.html` – Week1 자기소개 이미지를 HTML/CSS로 구현한 페이지 (글자는 모두 HTML 텍스트, 그림은 PNG, 반응형)
- `daejun/week2/images/*.png` – Week1 이미지에서 잘라 배경을 투명하게 만든 그림 21개
- `daejun/week2/prompt.md` – 본 대화 기록
