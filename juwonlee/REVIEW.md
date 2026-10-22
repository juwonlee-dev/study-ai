# PR 리뷰 규칙

GitHub Issue로 출제된 과제에 대해 지정된 PR을 시니어 리뷰어 관점에서 검토한다.
입력: 과제 Issue 번호, 리뷰 대상 PR 번호. 저장소: `juwonlee-dev/study-ai`.

## 1. 원칙

- 리뷰 중에는 저장소 파일을 수정하지 않는다. 수정 제안은 리뷰 코멘트로만 한다.
- Issue에 적힌 요구사항을 기준으로 판단하고, Issue에 없는 개인 취향을 필수 수정으로 요구하지 않는다.
- 모든 지적에는 **근거(Issue 문구, 코드 위치, 재현 방법)**, **이유**, **구체적인 수정안**을 함께 적는다.
- 확인하지 못한 내용은 문제로 단정하지 않는다. "확인 필요"로 표시하거나 질문으로 남긴다.
- 리뷰는 한국어로 하고, 존중하는 어조로 쓴다. 잘된 점도 1~2개 짚는다.

## 2. 수집

```bash
gh api user --jq .login    # 리뷰 실행 계정(ME)
gh issue view <ISSUE>
gh pr view <PR> --json number,title,author,headRefName,headRefOid,baseRefName,body,files,reviewRequests,reviews,createdAt,isDraft,state
gh pr diff <PR>
gh pr checks <PR>          # CI가 없으면 생략
git fetch origin pull/<PR>/head    # 로컬 브랜치를 만들지 않음
git show FETCH_HEAD:<path>         # 변경 파일 전체 내용 확인
```

Issue에 여러 Task가 있으면 PR 작성자에게 해당하는 Task를 특정한다. 대상이 불분명하면 사용자에게 확인한다.

### 2-1. 리뷰어 등록 확인

- ME가 `reviewRequests`에 있거나 `reviews`에 ME의 리뷰가 있으면 등록된 리뷰어로 본다. GitHub는 리뷰를 제출한 사람을 요청 목록에서 빼므로 두 곳을 모두 확인한다.
- 둘 다 아니면 리뷰를 시작하기 전에 사용자에게 묻는다: **"리뷰어로 등록한 뒤 리뷰 진행 / 등록하지 않고 리뷰 진행 / 중단"**
- 등록을 선택하면 아래 명령을 실행하고, `gh pr view <PR> --json reviewRequests`로 등록됐는지 확인한다.
  ```bash
  gh api repos/juwonlee-dev/study-ai/pulls/<PR>/requested_reviewers --method POST -f "reviewers[]=<ME>"
  ```
- ME가 PR 작성자이면 리뷰어로 등록할 수 없으므로 묻지 않고 `COMMENT` 리뷰로 진행한다(§4).

### 2-2. 최초 리뷰 / 재리뷰 판별

`reviews`에 ME의 이전 리뷰(`APPROVED`, `CHANGES_REQUESTED`, `COMMENTED`)가 있으면 **재리뷰**로 진행한다. ME가 이미 리뷰했는데 `reviewRequests`에 다시 있으면 작성자가 Re-request review를 한 것이다.

재리뷰에서 추가로 수집하는 정보:

```bash
# ME의 마지막 리뷰와 그 시점의 커밋
gh api repos/juwonlee-dev/study-ai/pulls/<PR>/reviews --jq '[.[] | select(.user.login=="<ME>")] | last | {id, state, commit_id, body}'
# ME가 남긴 인라인 코멘트와 작성자 답글
gh api repos/juwonlee-dev/study-ai/pulls/<PR>/comments --paginate
# 이전 리뷰 이후 변경분 (git fetch origin pull/<PR>/head 후)
git diff <이전 commit_id> FETCH_HEAD
```

- `git diff`가 실패하면(force push 등으로 이전 커밋이 없음) 전체 diff로 최초 리뷰처럼 다시 검토하고, 그 사실을 리뷰 본문에 적는다.
- 이전 리뷰 이후 새 커밋이 없으면 리뷰를 등록하지 않고 사용자에게 알린다.

## 3. 체크리스트

### A. 제출 규칙 (Issue 공통 안내)
- 브랜치 이름 `weekN/<작성자이름>`, base `main`
- 변경 파일이 작성자 폴더 안에만 있는지(다른 사람 폴더·공용 파일 변경 여부)
- Issue가 지정한 경로와 파일명을 정확히 지켰는지(대소문자 포함)
- PR 생성 시각이 마감 기한 안인지(늦었다면 사실만 기록)
- 리뷰어 지정: 필수 리뷰어와 추가 리뷰어 1인 이상
- PR 본문 필수 항목(예: 사용 AI 에이전트·모델, 리뷰어, 작업 설명)

### B. 과제 요구사항
- Issue의 필수 요구사항과 완료 조건을 항목별로 `충족 / 부분 충족 / 미충족 / 확인 불가`로 판정한다.
- 원본 대조형 과제(README → 이미지 → HTML 등)는 원본 파일을 직접 읽고 누락·불일치를 실제로 대조한다.
- 금지 사항 위반 여부(예: "이미지를 그대로 첨부하지 말고 HTML/CSS로 구현" → `<img src="profile.png">`로 통째 삽입했는지).
- 대화 기록(`prompt.md` 등): 존재, 파일명 규칙, 사용자 프롬프트와 AI 응답이 모두 들어 있는지, 생략 표시나 요약만 있는지, 마크다운 가독성.

### C. 품질 (시니어 관점)
- 정확성: 동작 오류, 깨진 링크와 경로, 인코딩(한글 깨짐), 렌더링 문제
- HTML/CSS: 시맨틱 마크업, `lang`/`charset`/`viewport`, 접근성(alt, 대비, 제목 계층), 반응형, 외부 리소스 의존성
- 유지보수성: 불필요한 파일(임시 파일, 백업, `.DS_Store`), 중복, 과도한 복잡도
- 보안: 커밋된 토큰·키·개인정보
- 가능하면 실제로 실행하거나 렌더링해서 확인한다(예: Edge headless로 HTML 스크린샷). 임시 산출물은 저장소 밖에 둔다.

### D. 재리뷰 추가 확인
- 이전에 지적한 항목(🔴 우선, 🟡/🟢 포함)을 하나씩 `해결 / 미해결 / 부분 해결 / 반영 안 함(사유 답글 있음)`으로 판정한다. 작성자 답글에 적힌 사유가 타당하면 받아들인다.
- 새로 바뀐 부분은 A~C 체크리스트로 검토하고, 수정 과정에서 생긴 회귀(기존에 충족하던 요구사항이 깨졌는지)를 확인한다.
- 이미 해결된 지적을 다시 달지 않는다. 미해결 인라인 지적은 새 코멘트를 달지 않고 기존 스레드에 답글로 남긴다.

## 4. 심각도와 판정

| 등급 | 의미 | 예 |
| --- | --- | --- |
| 🔴 필수(Blocker) | 과제 요구사항 미충족, 규칙 위반, 동작 오류 | 지정 파일명 불일치, 대화 기록 누락, 원본과 다른 내용 |
| 🟡 권장(Suggestion) | 품질 개선, 승인을 막지 않음 | 접근성, 시맨틱 태그, 코드 정리 |
| 🟢 참고(Nit/Question) | 사소한 의견이나 질문 | 네이밍, 스타일 |

- 🔴 1개 이상 → `REQUEST_CHANGES`
- 🔴 없음 → `APPROVE` (🟡/🟢 코멘트는 함께 남김). 재리뷰에서 승인하면 이전의 `CHANGES_REQUESTED` 상태가 해제된다.
- 작성자가 리뷰 실행 계정과 같으면(GitHub에서 본인 PR은 승인할 수 없음) → `COMMENT`
- PR이 Draft이거나 이미 병합·종료됐으면 리뷰를 등록하지 않고 사용자에게 알린다.

## 5. 코멘트 작성

- 특정 라인의 지적은 인라인 코멘트로 단다. 코멘트할 라인은 PR diff에 포함된 라인(RIGHT side)이어야 한다.
- 바로 반영할 수 있는 수정은 GitHub suggestion 블록으로 제안한다(대체할 라인 전체를 적는다).

  ````markdown
  🟡 **권장** 이미지 대체 텍스트가 비어 있어 스크린리더가 내용을 읽지 못합니다.

  ```suggestion
  <img src="avatar.svg" alt="이주원 프로필 아바타">
  ```
  ````
- 파일 전체나 PR 단위의 지적은 리뷰 본문에 적는다.
- 리뷰 본문 형식:

  ```markdown
  ## 리뷰 요약 (Issue #<ISSUE> / <Task명>)
  **판정:** 승인 | 수정 요청 | 코멘트

  ### 요구사항 충족 여부
  | 요구사항 | 결과 | 근거 |
  | --- | --- | --- |

  ### 잘된 점
  ### 필수 수정 (🔴)
  ### 권장 사항 (🟡/🟢)

  > 🤖 Claude Code로 리뷰했습니다.
  ```
- 재리뷰는 제목을 `## 재리뷰 요약 (이전 리뷰 <날짜>, <short sha>..<short sha>)`로 쓰고, `요구사항 충족 여부` 앞에 다음 표를 넣는다.

  ```markdown
  ### 이전 지적 반영 여부
  | 지적 | 등급 | 결과 | 근거 |
  | --- | --- | --- | --- |
  ```

## 6. 등록

1. 판정, 리뷰 본문, 인라인 코멘트 목록을 사용자에게 초안으로 보여 주고 등록 승인을 받는다.
2. 승인 후 리뷰 하나로 등록한다(코멘트를 따로따로 달지 않는다).

   ```bash
   # review.json: {"commit_id": "<head sha>", "event": "APPROVE|REQUEST_CHANGES|COMMENT", "body": "...",
   #               "comments": [{"path": "...", "line": 12, "side": "RIGHT", "body": "..."}]}
   gh api repos/juwonlee-dev/study-ai/pulls/<PR>/reviews --method POST --input review.json
   ```
   `commit_id`는 `gh pr view <PR> --json headRefOid`로 얻는다. `review.json`은 저장소 밖 임시 경로에 만든다.
   재리뷰에서 기존 스레드에 답글을 달 때는 리뷰를 등록하기 전에 실행한다.
   ```bash
   gh api repos/juwonlee-dev/study-ai/pulls/<PR>/comments/<comment_id>/replies --method POST -f body="..."
   ```
3. 등록 결과 URL을 보고한다. 병합은 하지 않는다.
