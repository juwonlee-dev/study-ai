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
Issue #14 요약: README 기반 자기소개 이미지 juhwan/week1/profile.png 생성 + README와 일치하는지
검증 단계 + 프롬프트 로그 + PR.

## 작업 결과

- juhwan/week1/profile.png — 자기소개 이미지 (1200x675)
- juhwan/week1/profile.html — 이미지 원본 (HTML/CSS, 헤드리스 Chrome으로 PNG 렌더링)
- juhwan/week1/claude-prompt.md — 프롬프트 로그

## 검증

| README 항목 | README 값 | 이미지 |
|---|---|---|
| 이름 | 허주환 | 허주환 ✅ |
| 생년월일 | 1999-06-30 | 1999-06-30 ✅ |
| 나이 | 28 | 28 ✅ |
| 성별 | 남 | 남 ✅ |
| MBTI | INFJ | INFJ ✅ |
| Claude Code(AI) 사용 이유 | 업무 생산성 향상을 목적으로 사용했습니다. | 동일 ✅ |

- 시각 검증: 렌더링된 PNG를 Claude가 직접 열어 항목별 대조
- 텍스트 검증: README 값 전부가 이미지 소스에 포함되는지 스크립트로 확인 (6/6 OK)

## 방식 선택 이유

이미지 생성 AI(DALL·E 등)는 한글 텍스트가 깨지거나 글자가 바뀌는 경우가 많아
"README와 내용이 달라서는 안 된다"는 조건을 맞추기 어렵습니다. 그래서 Claude Code가
HTML/CSS로 카드를 디자인하고 Chrome으로 PNG를 렌더링해, 텍스트가 README와
정확히 일치하도록 했습니다.

커밋은 의미 단위로 나눠 완료했습니다. push / PR 생성은 gh 인증이 만료되어
`! gh auth login` 실행이 필요합니다.
```
