# 최대준 Week2 – 자기소개 이미지 HTML 변환 대화 기록

> Week1에서 만든 자기소개 이미지(`daejun/week1/profile.png`)를 HTML/CSS 페이지(`daejun/week2/profile.html`)로 구현한 작업의 **전체 대화 기록**입니다.
> 본인이 작성한 프롬프트와 AI 응답을 생략 없이 순서대로 정리했습니다.

| 항목 | 내용 |
| --- | --- |
| 사용 AI 에이전트 | Claude Code (CLI, Windows) |
| 모델 | Claude Opus 5.5 (`claude-opus-5-5`) |
| 작업 브랜치 | `week2/daejun` |
| 과제 이슈 | [#22 2주차](https://github.com/juwonlee-dev/study-ai/issues/22) |
| 결과물 | `daejun/week2/profile.html`, `daejun/week2/prompt.md` |

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

- `daejun/week2/profile.html` – Week1 자기소개 이미지를 HTML/CSS + inline SVG로 구현한 페이지 (이미지 첨부 없음, 반응형)
- `daejun/week2/prompt.md` – 본 대화 기록
