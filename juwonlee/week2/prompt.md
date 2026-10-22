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

**Claude — PR 생성**

> PR #37(https://github.com/juwonlee-dev/study-ai/pull/37)을 생성하고 리뷰어로 @juhwanHeo, @LSHgy를 지정했습니다. 클립보드의 미리보기 이미지를 PR 본문 편집 화면에 붙여넣어 달라고 안내했습니다.

### 7. 미리보기 이미지 업로드

**사용자**

> gh attach 명령어를 사용해

**Claude — 확인 질문**

> 이 PC에는 `gh attach`가 설치돼 있지 않습니다(기본 명령이 아닌 서드파티 gh 확장). 어떤 확장을 설치할까요?
> - sudosubin/gh-attach (Recommended)
> - atani/gh-attach
> - 설치하지 않음

**사용자 — 선택**

> sudosubin/gh-attach

**Claude — 진행 내용**

> - `gh extension install sudosubin/gh-attach`로 설치하고, `gh attach preview.png -R juwonlee-dev/study-ai`로 미리보기 이미지를 업로드했습니다.
> - 출력된 `https://github.com/user-attachments/assets/2c74cfd4-...` 링크를 `<img>` 태그로 바꿔 PR 본문 "결과물 미리보기"에 넣었습니다(`gh pr edit 37 --body-file`).
> - GitHub이 렌더링한 PR 본문의 이미지 URL이 200(image/png, 원본과 같은 크기)을 반환하는 것을 확인했습니다.

**Claude — 결과 보고**

> PR #37 본문 "결과물 미리보기"에 `gh attach`로 올린 `user-attachments` 이미지 링크를 넣었습니다. `prompt.md`는 아직 커밋 전이며, 커밋·푸시 여부를 확인 요청했습니다.

### 8. PROJECT.md 지침 반영

**사용자**

> 미리보기나 결과물 스크린샷 캡쳐 등을 PR 본문에 첨부해야하는 경우에는 gh attach를 설치해서 사용하도록 PROJECT.md에 지침을 반영하고 커밋 푸시해줘

**Claude — 진행 내용**

> `juwonlee/PROJECT.md` §6에 PR 본문 이미지 첨부 지침을 추가했습니다. 저장소에 커밋해 링크하지 않고, `gh attach`(sudosubin/gh-attach)로 업로드한 `user-attachments` URL을 `<img>` 태그로 넣은 뒤 렌더링을 확인하는 내용입니다. 이어서 PROJECT.md 변경과 대화 기록을 각각 커밋해 푸시했습니다.

**Claude — 결과 보고**

> `ab0cba3`(PROJECT.md 지침 추가)와 `0fad7dd`(대화 기록)를 `week2/juwonlee`에 푸시했습니다.

### 9. Issue 연결 금지 지침

**사용자**

> PROJECT.md 파일에 의미가 누락되거나 왜곡없이 동일하게 전달되는 조건으로 아래 문장을 압축해서 지침에 반영해줘
> - PR을 등록할 때, Development에 해당 이슈를 등록하게 되면 해당 PR이 병합되면 이슈가 close되므로 등록해서는 안돼. PR 본문 최상단에 Issue: #22와 같은 형식으로만 기록해

**Claude — 진행 내용**

> `PROJECT.md` §6을 수정했습니다. 기본 구성에서 `Closes #<Issue>`를 빼고 맨 앞에 `Issue: #<번호>`(최상단)를 두었으며, 다음 지침을 추가했습니다.
> - PR을 Issue의 Development에 연결하지 않는다(`Closes #<번호>` 같은 closing 키워드 포함). 연결하면 PR 병합 시 Issue가 닫힌다. Issue는 본문 최상단에 `Issue: #22` 형식으로만 기록한다.

**Claude — 확인 요청**

> PR #37 본문에 `Closes #22`가 있어 Issue #22가 Development에 연결돼 있습니다. PROJECT.md·prompt.md 커밋·푸시와 PR #37 본문 수정(`Closes #22` 삭제, 최상단 `Issue: #22` 추가)을 진행할지 확인을 요청했습니다.

### 10. 커밋·푸시와 PR 본문 수정

**사용자**

> 진행해

**Claude — 진행 내용**

> PROJECT.md 지침 변경과 대화 기록을 각각 커밋해 푸시했습니다. PR #37 본문에서 `Closes #22`를 지우고 최상단에 `Issue: #22`를 넣은 뒤, Issue 연결(`closingIssuesReferences`)이 해제됐는지 확인했습니다.
