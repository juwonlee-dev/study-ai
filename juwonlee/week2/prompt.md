# 2주차 Task1 프롬프트와 대화 기록

## 작업 정보

- 사용 AI: Claude Code / Claude Opus 5.5
- 원본 자료: `juwonlee/week1/profile.png` (이미지만 참고, week1 HTML 코드는 재사용하지 않음)
- 결과물: `juwonlee/week2/profile.html`, `juwonlee/week2/ASSIGNMENT.md`, `juwonlee/week2/prompt.md`
- 범위: 사용자 프롬프트와 Claude의 사용자 대상 응답을 시간순으로 기록한다. 내부 도구 실행 로그와 이미지 출력은 대화 프롬프트/응답이 아니므로 요약만 남긴다.

## 사용자 프롬프트와 Claude 응답

### 1. 과제 시작

**사용자**

> /assignment 22

**Claude — 진행 내용**

> `juwonlee/PROJECT.md`, `juwonlee/CLAUDE.md`를 읽고, 현재 브랜치(`week2/juwonlee`)와 작업 트리 상태(clean)를 확인한 뒤 Issue #22(2주차) 본문을 조회했습니다.

### 2. 범위 지정

**사용자**

> Task1만 진행해줘. Orca 관련 내용은 제외해.

**Claude — 구현 방식 확인 질문**

> week1에 PNG를 렌더링할 때 쓴 week1/profile.html이 이미 있습니다. week2/profile.html은 어떻게 만들까요?
> - 이미지만 보고 새로 작성 (Recommended)
> - week1 HTML 참고
> - week1 HTML 재사용
>
> 레이아웃 폭은 어떻게 할까요?
> - 반응형 (Recommended)
> - 고정 1600px

**사용자 — 선택**

> - 구현 방식: 이미지만 보고 새로 작성
> - 레이아웃: 반응형

### 3. 구현

**Claude — 진행 내용**

> 1. `week2/ASSIGNMENT.md`에 Task1 요구사항, 제출물, PR 필수 항목만 정리했습니다. (Task2와 Orca 관련 내용 제외)
> 2. `week1/profile.png`(1600 × 3200)를 구간별로 확대해 텍스트를 판독한 뒤, 이미지 첨부 없이 HTML/CSS로 `week2/profile.html`을 새로 작성했습니다.
>    - 구성: 히어로(인사말·부제·인용문·ID 카드) / 기본 프로필 / 기술 스택 / GitHub 경험 / 협업 & 소통 스타일 / 푸터
>    - 색상·라운드 카드·원형 장식은 이미지를 보고 CSS로 재현했습니다.
>    - 860px 이하에서는 1열로 접히는 반응형 레이아웃입니다.
> 3. Microsoft Edge 헤드리스로 1600px, 390px 폭을 렌더링해 원본과 비교했습니다.
>    - 1600px: 원본 대비 콘텐츠 폭이 좁아 `max-width`를 조정했습니다.
>    - 390px: 긴 URL(`BusLocationTrackerUser.ver`) 줄바꿈과 한국어 단어 단위 줄바꿈(`word-break: keep-all`)을 보완했습니다.

### 4. 완료 보고

**Claude — 완료 보고**

> - 변경 파일: `week2/ASSIGNMENT.md`, `week2/profile.html`, `week2/prompt.md` (모두 신규, `juwonlee/` 밖 변경 없음)
> - 충족 요구사항: 지정 경로·파일명 준수, `<img>` 없이 이미지 내용·디자인을 HTML/CSS로 구현, 대화 기록 `prompt.md` 제출
> - 검증: Edge 헤드리스 1600px·390px 렌더링 후 원본 이미지와 섹션·텍스트 대조, `<img>` 태그 0개 확인
> - 남은 일: 커밋·푸시·PR 생성은 승인 후 진행 (PR 본문에 사용 AI·모델과 리뷰어 명시 필요)

### 5. 커밋·푸시

**사용자**

> Task2는 무시하고 진행해

**Claude — 진행 내용**

> Task2는 범위에서 제외하고 PR 본문에 `Closes #22`를 쓰기로 했습니다. `juwonlee/week2/` 변경을 커밋해 `week2/juwonlee` 브랜치에 푸시하고, PR 본문 초안을 확인받은 뒤 PR을 생성합니다.

**Claude — 커밋·푸시 결과와 PR 초안**

> 커밋 `a61a6d7`을 `week2/juwonlee`에 푸시했습니다. PR 본문 초안(작업 내용 / 사용 AI 에이전트·모델 / 검증 / 리뷰어 / `Closes #22`)을 제시하고, 리뷰어와 결과물 미리보기 이미지를 어떻게 처리할지 확인을 요청했습니다.

### 6. 리뷰어와 미리보기 이미지 규칙

**사용자**

> 리뷰어는 필수 지정 이외에는 현재 Git Repo에 Collaborators로 등록한 인원들 중에서 항상 랜덤하게 선택해줘
>
> 함께 커밋해서 링크하게 되면, 해당 브런치가 병합되어 사라지면 보이지 않을 수 있으므로 https://github.com/user-attachments/assets/... 와 같은 형식의 링크로 img태그가 삽입되는 방식으로 PR 본문에 추가해줘. 클립보드의 이미지를 PR 본문 편집 중에 붙여넣으면 이미지가 업로드되며 img태그로 변환되는 방식이야.

**Claude — 진행 내용**

> - 저장소 Collaborators를 조회해, 본인과 필수 리뷰어(@juhwanHeo)를 뺀 후보 중 무작위로 @LSHgy를 골랐습니다. 이 규칙은 이후 PR에도 적용하도록 기억해 두었습니다.
> - `profile.html`을 1600px 폭으로 렌더링한 미리보기 이미지를 클립보드에 복사했습니다.
> - PR 본문의 "결과물 미리보기" 자리에 사용자가 이미지를 붙여넣으면 `user-attachments` 링크로 업로드되도록 PR을 생성합니다.
