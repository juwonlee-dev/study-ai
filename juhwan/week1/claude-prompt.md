# Claude Prompt Log — Week1

- 사용 AI: Claude Code (모델: Opus 5.5)
- 기록 범위: Week1 과제 시작 요청부터의 모든 대화

---

## Turn 1 — User

```
https://github.com/juwonlee-dev/study-ai/issues/14
를 읽고 과제 시작해주세요.
```

## Turn 2 — Assistant

> 작업 과정 (도구 실행 요약)
> 1. `gh issue view 14` → 인증 실패(HTTP 401) → GitHub 공개 API(`curl`)로 이슈 본문 조회
> 2. `juhwan/week0/README.md` 확인 (이름/생년월일/나이/성별/MBTI/사용 이유)
> 3. `juhwan/week1/profile.html` 작성 (README 내용을 카드 형태로 배치한 HTML/CSS)
> 4. 헤드리스 Chrome으로 `profile.html` → `profile.png` (1200x675) 렌더링
> 5. 검증 ① 생성된 PNG를 Claude가 직접 이미지로 열어 README 항목과 대조
> 6. 검증 ② 스크립트로 README의 모든 값이 이미지 소스에 포함되는지 확인
>
> ```
> OK   허주환
> OK   1999-06-30
> OK   28
> OK   남
> OK   INFJ
> OK   업무 생산성 향상을 목적으로 사용했습니다.
> ```

```
이슈 #14 과제(자기소개 이미지 만들기)를 끝냈고 week1/juhwan 브랜치에 push했습니다. PR은 아직 못 만들었습니다. gh 로그인이 만료되어서 gh 명령이 인증 오류로 실패합니다. 이슈 내용은 공개 API로 읽었습니다.

## 만든 파일 (juhwan/week1/)
- profile.png: 자기소개 이미지 (1200x675)
- profile.html: 이미지 원본 HTML/CSS 파일입니다. 헤드리스 Chrome으로 열어 PNG로 저장했습니다.
- claude-prompt.md: 이번 대화의 프롬프트 로그입니다. 이슈에서 여러 AI를 쓰면 chatgpt-prompt.md처럼 AI 이름을 붙이라고 해서, week0처럼 이 파일명으로 했습니다.

## 검증 결과
| 항목 | README | 이미지 |
|---|---|---|
| 이름 | 허주환 | ✅ |
| 생년월일 | 1999-06-30 | ✅ |
| 나이 | 28 | ✅ |
| 성별 | 남 | ✅ |
| MBTI | INFJ | ✅ |
| 사용 이유 | 업무 생산성 향상을 목적으로 사용했습니다. | ✅ |

- 이미지로 확인: 만든 PNG를 제가 직접 열어서 README 항목과 하나씩 대조했습니다.
- 스크립트로 확인: README의 값 6개가 모두 이미지 원본 HTML에 들어 있습니다. 이 검사는 PNG가 아니라 원본 HTML을 대상으로 했습니다.

## 이 방식을 쓴 이유
이미지 생성 AI는 한글 글자를 틀리게 그리는 경우가 많아서, README와 내용이 달라지면 안 된다는 조건을 맞추기 어렵습니다. 그래서 HTML로 카드를 만들고 PNG로 저장해 글자가 README와 똑같이 나오게 했습니다. PR 본문에도 이 내용을 적겠습니다.

## 확인 부탁드릴 것
- 나이: 생년월일(1999-06-30)로 계산하면 오늘 기준 만 나이는 27세입니다. README에 적힌 대로 28로 넣었는데, 바꿔야 하면 말씀해 주세요.
- 로그 수정분: 커밋은 이미지와 로그로 나눠 2개 했습니다. push한 뒤 로그의 push 관련 문장 하나를 고쳤는데, 이건 아직 커밋하지 않았습니다. 다음 로그 추가분과 함께 커밋하겠습니다.

## 남은 작업
1. ! gh auth login을 실행해 주세요.
2. 로그인되면 PR을 만들겠습니다. 제목은 Week1 / juhwan, 본문에는 #14 태그, 사용한 AI와 이유, 이미지를 넣습니다. 리뷰어는 @juwonlee-dev, @juhwanHeo입니다.
3. 이슈에서 리뷰어를 1명 이상 더 지정하라고 합니다. 누구를 추가할지 알려주세요.

![profile](juhwan/week1/profile.png)
```

## Turn 3 — User

```
! gh auth login
로그인 했습니다.
```

## Turn 4 — Assistant

> 작업 과정 (도구 실행 요약)
> 1. `gh auth status`로 로그인 확인 (juhwanHeo)
> 2. `gh pr create`로 PR 생성 (제목 `Week1 / juhwan`, 본문에 #14 태그, 사용한 AI/이유, 이미지, 검증 결과 포함), 리뷰어 @juwonlee-dev 지정
> 3. `gh pr edit --add-reviewer juhwanHeo` 시도 → PR 작성자 본인이라 GitHub가 리뷰어로 등록하지 않음
> 4. 프롬프트 로그에 이번 대화 추가 후 커밋 / push

```
PR을 만들었습니다: https://github.com/juwonlee-dev/study-ai/pull/15

- 제목: Week1 / juhwan
- 본문: #14 태그, 사용한 AI와 이유, 이미지, 검증 결과 (이미지는 커밋 SHA 링크라 브랜치가 삭제돼도 보입니다)
- 리뷰어: @juwonlee-dev만 지정됐습니다. @juhwanHeo는 PR 작성자 본인이라 GitHub가 리뷰어로 받아주지 않습니다.
- 프롬프트 로그에 이번 대화를 추가했습니다. 지난 응답(Turn 2)이 요약본으로 기록돼 있어서 실제 응답 전문으로 바꿨습니다. 커밋과 push까지 했고 PR에 자동 반영됩니다.

남은 것
- 이슈 조건인 "추가 리뷰어 1명 이상"은 아직 지정하지 않았습니다. 누구를 추가할지 알려주세요.
- 이전 질문: 나이 28(README 값)을 그대로 둘지 알려주세요. 만 나이로는 27세입니다.
```
