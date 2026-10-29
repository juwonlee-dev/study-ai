# Week2 AI Prompt Log

## 사용 AI

- Devin (Cognition, SWE-2 High)

## 사용 목적

Week1에서 생성한 자기소개 이미지(`gunsang/week1/profile.png`)를 `<img>` 태그 없이 HTML/CSS만으로 재현하기 위해 사용했습니다. 이미지 분석, 단일 HTML 파일 작성, 브라우저 렌더링 검증, 코드 리뷰 서브에이전트 실행까지 한 세션에서 수행하기 위해 Devin을 사용했습니다.

---

# 전체 대화 기록

> 아래 내용은 Week2 과제 작업을 위해 Devin과 진행한 대화를 정리한 기록(정리본)입니다.
> 사용자 질문은 입력 원문을 옮겼고, Devin 응답은 실제로 화면에 표시된 내용을 바탕으로 읽기 쉽게 정리·요약한 정리본입니다.
> `(수행 내용)` 항목은 실행한 도구 호출(파일 읽기/작성, 브라우저 검증, 서브에이전트 리뷰)을 요약한 것이고,
> `(리뷰 결과 요약)` 항목은 서브에이전트 응답 원문이 아니라 핵심 지적사항만 추린 요약입니다.

---

## 1. Git 브랜치 및 프로젝트 경로 확인

### 사용자

현재 작업 중인 Git 브랜치 이름과 프로젝트 경로를 확인해 줘.
파일은 수정하지 마.

### Devin

(실행한 명령: `pwd && git branch --show-current && git rev-parse --show-toplevel`)

- Git 브랜치: `week2/gunsang`
- 프로젝트 경로: `C:\Users\Seeds\orca\workspaces\study-ai\week2-gunsang`

---

## 2. 한글 설명 요청

### 사용자

한글로 설명해

### Devin

방금 확인한 내용을 설명하면:

- **Git 브랜치 `week2/gunsang`**: 현재 이 프로젝트에서 작업 중인 브랜치 이름입니다. `main`이나 `master`가 아니라 `week2/gunsang`이라는 별도 브랜치에 체크아웃되어 있는 상태입니다.

- **프로젝트 경로 `C:\Users\Seeds\orca\workspaces\study-ai\week2-gunsang`**: 현재 작업 디렉터리이자 Git 저장소의 루트(최상위) 경로입니다. `study-ai`라는 워크스페이스 안에 `week2-gunsang` 폴더가 있고, 이 폴더 자체가 하나의 Git 저장소입니다.

즉, 지금 `week2-gunsang` 프로젝트 폴더에서 `week2/gunsang` 브랜치로 작업 중인 상태입니다. 파일은 수정하지 않았습니다.

---

## 3. Week2 과제 요청

### 사용자

현재 `study-ai` 저장소의 `week2/gunsang` 브랜치에서 Week2 과제를 진행하려고 합니다.

**과제 요구사항**

1. `gunsang/week1/profile.png` 파일을 분석해주세요.
2. 이미지의 텍스트, 색상, 카드 디자인, 레이아웃 등을 HTML/CSS로 최대한 동일하게 구현해주세요.
3. 결과물은 `gunsang/week2/profile.html` 경로에 생성해주세요.
4. 기존 이미지를 `<img>` 태그로 그대로 출력하는 방식은 금지합니다. HTML 요소와 CSS를 활용해서 직접 구현해주세요.
5. HTML 파일 하나만 브라우저에서 실행해도 정상적으로 표시되도록 작성해주세요.
6. `gunsang/week0`, `gunsang/week1` 및 다른 사람의 폴더는 절대 수정하지 마세요.
7. 생성된 HTML을 브라우저에서 검증하고 원본 이미지와 비교해주세요.
8. 현재 세션에서 제가 입력한 프롬프트와 AI 응답 전체를 생략 없이 `gunsang/week2/prompt.md`에 Markdown 형식으로 기록해주세요. 대화 기록에 직접 접근할 수 없다면 임의로 작성하지 말고 알려주세요.
9. 작업 완료 후 변경한 파일 목록과 검증 결과를 알려주세요.

Git Commit과 Push는 제가 별도로 요청하기 전까지 진행하지 마세요.

### Devin

Week2 과제를 시작하겠습니다. 먼저 디렉터리 구조와 원본 이미지를 확인합니다.

(수행 내용)
- `find` 명령으로 저장소 파일 구조 확인 → `gunsang/week1/profile.png`, `gunsang/week1/prompt.md` 등 확인
- `gunsang/week1/profile.png` 이미지 파일을 읽어 시각적으로 분석
- `gunsang/week1/prompt.md`, `gunsang/week1/README.md` 읽어 기존 작업 맥락 확인

이미지 분석 완료. 디자인 요소를 정리하면:

- **배경**: 어두운 원목 테이블(짙은 갈색, 나무결)
- **카드**: 크림색 종이 질감, 시계방향으로 기울어지고 약간의 원근감
- **상단**: 반짝임 장식, `— THANK YOU —` 레터스페이싱, 큰 명조체 `이건상`, 손글씨체 `Lee Gunsang`
- **우측**: 앉아있는 강아지 실루엣 + 발자국, 이탤릭 인용구
- **6개 정보 행**: 컬러 원형 아이콘 + 라벨 + 세로 구분선 + 값이 들어간 필(pill) 형태 행
- **하단**: 세피아톤 산/숲 풍경 일러스트 + `Keep Growing Always` 손글씨

이제 `gunsang/week2/profile.html`을 작성합니다.

(수행 내용)
- `gunsang/week2/` 디렉터리 생성
- `gunsang/week2/profile.html` 작성 — 단일 HTML 파일, Google Fonts(Noto Serif KR, Noto Sans KR, Great Vibes) 사용, `<img>` 없이 CSS gradient + inline SVG(아이콘 6종, 강아지 실루엣, 발자국, 반짝임, 산/숲/호수 풍경)로 구현

`profile.html` 작성 완료. AGENTS.md 규칙에 따라 `global-code-reviewer`를 백그라운드로 실행한 뒤, 브라우저 검증을 진행합니다.

(수행 내용)
- `global-code-reviewer` 서브에이전트를 백그라운드로 실행(1차 리뷰)
- Playwright MCP로 렌더링 검증 준비 — `file://` 접근이 차단되어 `python -m http.server 8765` 로컬 서버를 백그라운드로 실행
- `http://127.0.0.1:8765/gunsang/week2/profile.html` 접속 후 뷰포트 1280×1000에서 전체 페이지 스크린샷 촬영(`verify-render.png`)
- 콘솔 오류 확인 → `favicon.ico` 404 외 오류 없음

1차 렌더링 결과와 원본 비교 후 다음 사항을 보정했습니다.

- 아이콘 원과 라벨 텍스트 간격 부족 → `.label`에 `margin-left: 15px` 추가
- 강아지 실루엣이 덩어리처럼 보임 → SVG path 전면 교체(머리/주둥이/귀/앉은 몸통/꼬리 구분)
- 인용구가 좁게 줄바꿈되고 행 아래에 깔림 → `.dog-area` 폭 185px로 확대, `z-index: 3` 부여, 폰트 14.5px로 조정
- `body`의 `overflow: hidden`으로 카드 상하단 잘림 + 스크롤 불가 → `overflow-x: hidden`으로 변경(세로 스크롤 허용)
- c4 아이콘 중복 path 제거, 호수 물결 path에 `fill="none"` 명시

(global-code-reviewer 1차 리뷰 결과 요약)
- `<img>` 미사용, 단일 파일 동작, `gunsang/week2` 외부 수정 없음 등 요구조건 준수 확인
- HIGH: `overflow: hidden`으로 카드 상하단 잘림 → 위와 같이 수정
- MEDIUM: 인용구와 행 겹침 → z-index·폭 조정으로 해소(원본에서도 인용구가 우측 행 끝 영역 위에 위치)
- LOW: 중복 path, `fill` 미지정 → 정리 완료

수정 후 재렌더링·스크린샷으로 원본과 비교 확인: 레이아웃, 색상, 행 구성, 하단 풍경, 인용구, 모토 문구가 원본 이미지와 유사하게 재현됨을 확인했습니다.

(수행 내용)
- 수정된 `profile.html`에 대해 `global-code-reviewer` 서브에이전트 재실행(2차 리뷰)
- `gunsang/week2/prompt.md`(본 파일) 작성

(global-code-reviewer 2차 리뷰 결과)
- 당시 세션에서 2차 리뷰를 실행했으나, 결과 원문이 이 기록에 별도로 남아 있지 않아 상세 지적사항은 기술할 수 없습니다(원문 미보존).
- 기록으로 확인 가능한 사실: 2차 리뷰 이후 추가 코드 수정 없이 `profile.html`이 최종 상태로 커밋되어 PR #42에 반영되었습니다.

---

## 4. 검증 결과 요약

- 원본 이미지의 텍스트(이름, 영문 이름, THANK YOU, 인용구, 6개 정보 항목, Keep Growing Always)를 모두 HTML 텍스트로 구현
- 색상(크림색 카드, 짙은 원목 배경, 6색 원형 아이콘, 세피아 풍경)을 CSS로 재현
- 카드 기울기와 원근감을 `perspective + rotateX/Y/Z`로 재현
- `<img>` 태그 미사용 — 모든 그래픽을 inline SVG와 CSS로 구성
- 로컬 HTTP 서버에서 Playwright로 렌더링 확인, 콘솔 오류는 favicon 404 1건뿐(페이지 동작과 무관)
- `gunsang/week0`, `gunsang/week1`, 타인 폴더 미수정
- Git Commit/Push는 요청이 없어 수행하지 않음

---

## 5. PR #42 리뷰 반영 작업 (별도 세션, 2026-10-29)

### 사용자

week2 에서 지금 다 했잖아 근데 거기서 지금 리뷰 달린 게 있을거야 그거 해당 사항 다 수정해서 처리하고 리뷰 다시 요청해 승인 안난건들에 대해서

### Devin

(수행 내용)
- `gh api`로 PR #42(`Week2/gunsang`)의 리뷰·인라인 코멘트 조회 — @juwonlee-dev Approve, @ShsH0920·@bobo-h·@juhwanHeo Comment 상태 확인
- `gunsang/week1/profile.png` 원본 이미지 재확인, `profile.html`·`prompt.md` 읽기
- `profile.html`에 대해 `global-code-reviewer` 서브에이전트 백그라운드 실행(수정 후 리뷰)
- `python -m http.server 8765` 로컬 서버 실행, Playwright MCP로 렌더링 검증

리뷰어들이 지적한 사항을 모두 반영했습니다. 반영 내역:

- **AI 에이전트/모델 표기 불일치** (공통 지적): PR 본문의 `Devin CLI / Claude Sonnet 5 (Low)`를 실제 사용 환경인 `Devin (Cognition, SWE-2 High)`으로 수정해 `prompt.md`·`task2-prompt.md`와 통일
- **뷰포트 상단 잘림** (@juhwanHeo): `html, body { height: 100% }` 선언 삭제 → 1280×800에서 `THANK YOU`가 화면 상단 50px대에 정상 표시됨을 스크린샷으로 확인
- **390px 모바일 겹침·줄바꿈** (@juwonlee-dev 인라인 코멘트): `.card`에 `flex-shrink: 0` 추가, 480px 구간 `scale(0.55)`→`scale(0.45)` → 카드 전체가 찌그러짐·겹침 없이 축소 표시됨을 확인
- **장식 SVG 접근성** (@juhwanHeo): 반짝임 3, 강아지, 발자국, 행 아이콘 6, 풍경 총 12개 장식 SVG에 `aria-hidden="true"` 추가
- **정보 행 시맨틱** (@juhwanHeo): `ul>li` 구조를 `dl>div>dt>dd`로 변환, `.divider` 요소를 `.value::before` 가상요소로 대체(시각 동일)
- **타이포그래피** (@juhwanHeo): `.value`에 `word-break: keep-all`, `.name-en`에 `word-spacing: 6px` 추가
- **강아지 실루엣** (@juwonlee-dev): path 재작업 — 처진 귀와 지면으로 뻗은 꼬리를 별도 path로 분리해 앉은 강아지 윤곽을 강조. `.dog-area` 스크린샷으로 형상 확인
- **prompt.md 정리본 표기 + 2차 리뷰 결과 누락** (@juwonlee-dev 인라인 코멘트): 기록이 원문이 아닌 정리본임을 상단 안내문에 명시하고, 원문이 보존되지 않은 2차 리뷰 결과는 지어내지 않고 미보존 사실을 그대로 표기

(global-code-reviewer 리뷰 결과 요약 — 이번 세션)
- 판정 PASS: `profile.html`의 코드 수정 6건(위 목록 중 2~7번 항목)이 모두 올바르게 반영됐고, `dl>div>dt/dd` 구조가 HTML 명세상 유효함을 확인
- LOW: 저장소 루트의 stray 파일 `nul` 지적 → 커밋 대상에서 제외 처리
- 참고: 모바일 scale 축소 시 `transform: scale()` 특성상 카드 아래 빈 스크롤 영역이 생기는 기존 특성은 유지(리뷰어 제안 방향과 동일)

(수행 내용 — 이후 처리)
- PR 본문 AI 표기 수정(`gh pr edit`)
- 수정분 커밋·푸시 후 미승인 리뷰어(@ShsH0920, @bobo-h, @juhwanHeo)에게 재리뷰 요청
