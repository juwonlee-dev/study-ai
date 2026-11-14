# 최대준 Week3 – KurbyPdf 보안 취약점 분석 대화 기록

> 오픈소스 프로젝트 [KurbyPdf](https://github.com/juwonlee-dev/KurbyPdf)의 보안 취약점을 분석해 보고서(`daejun/week3/REPORT.md`)를 작성한 작업의 **전체 대화 기록**입니다.
> 본인이 작성한 프롬프트와 AI 응답을 순서대로 정리했습니다.

| 항목 | 내용 |
| --- | --- |
| 사용 AI 에이전트 | Claude Code (CLI, Windows) |
| 모델 | Claude Opus 5.5 (`claude-opus-5-5`) |
| 작업 브랜치 | `week3/daejun` |
| 과제 이슈 | [#46 3주차](https://github.com/juwonlee-dev/study-ai/issues/46) |
| 결과물 | `daejun/CLAUDE.md`, `daejun/week3/REPORT.md`, `daejun/week3/prompt.md` |

---

## 1. CLAUDE.md 작성

### 🙋 질문

> https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md 여기 깃허브 접속해서 내용 참고해서 C:\AI\study-ai\daejun 안에 CLAUDE.md 파일 만들어줘. CLAUDE.md 파일 내용은 60줄 내외로 작성해주고 CLAUDE AI를 더 잘 활용하기 위한 내용으로 작성이 필요해.

### 🤖 답변

**작업 내용**
- 참고 CLAUDE.md를 가져와 4가지 원칙(코딩 전 생각하기 / 단순함 우선 / 외과적 수정 / 목표 중심 실행)을 확인
- 한국어로 정리하고, "Claude 활용 팁"과 "study-ai 저장소 규칙" 섹션을 추가해 `daejun/CLAUDE.md`(59줄) 작성

**응답**

> `C:\AI\study-ai\daejun\CLAUDE.md`를 만들었어요. 59줄입니다.
>
> 1. 코딩 전에 먼저 생각하기 — 가정 명시, 여러 해석 시 선택지 제시, 불확실하면 질문
> 2. 단순함 우선 — 요청받지 않은 기능·과한 추상화·불필요한 예외 처리 금지
> 3. 외과적 수정 — 필요한 부분만 수정, 기존 스타일 유지, 바뀐 모든 줄이 요청으로 설명돼야 함
> 4. 목표 중심 실행 — 검증 가능한 목표로 바꾸고 "단계 → 검증" 형식으로 계획
> 5. Claude 활용 팁 — 목표/제약/완료 기준을 함께 적기, 단계별로 나눠 맡기기, 구체적으로 피드백하기
> 6. study-ai 저장소 규칙 — `daejun/` 폴더 안에서만 작업, 브랜치 이름 규칙, `prompt.md` 제출, 커밋·PR 전 승인
>
> 커밋이나 PR은 아직 안 했어요. 진행할까요?

---

## 2. 3주차 과제 수행 (보안 취약점 분석)

### 🙋 질문

> C:\AI\study-ai\ASSIGNMENT.md 해당 파일 참고해서 작업 시작해

### 🤖 답변

**작업 내용**
1. `ASSIGNMENT.md` 요구사항 확인 → `origin/main` 기준으로 `week3/daejun` 브랜치 생성, `daejun/week3/` 폴더 생성
2. KurbyPdf 저장소를 별도 임시 폴더에 clone하고 **저장소 18개 파일 전체를 라인 번호와 함께 읽음** (Java 소스 9개, 테스트, Gradle 설정, README)
3. 1차 분석: 공격 표면(검증 대상 PDF = 외부 입력, 워터마크된 PDF 수신자)을 정하고 취약점 후보 도출
4. 의존성 점검: OSV(api.osv.dev)에서 PDFBox 2.0.30 / Jackson 2.17.1 CVE 조회 → Jackson에서 16건 확인, PDFBox는 0건
5. **PoC로 실제 재현**: 원본 소스를 `javac --release 8`로 컴파일하고 시나리오 7개 실행
   - 본문 변조·워터마크 이식 후에도 `valid=true` (V-01)
   - 1MB 압축 폭탄 PDF로 `OutOfMemoryError` (V-02)
   - `/_k1` 삭제로 워터마크 제거 (V-03), 가짜 스트림 1개로 검증 실패 (V-04)
   - owner==user 암호일 때 소유자 권한 획득, 기본 권한 과다 (V-05), 1바이트 HMAC 키 허용 (V-07)
6. **조치 방안 검증**: 원본 사본에 조치 코드를 적용해 같은 PoC를 다시 실행하고, 기존 테스트 흐름(사용자 암호 + owner 자동 생성)이 그대로 통과하는지 회귀 확인
7. **2차 검토** (ASSIGNMENT.md의 검증 기준 6가지)
   - 오탐 제외 6건 (Jackson 역직렬화, HMAC 정규화, 타이밍 공격, IV 재사용, 에러 메시지, KeyUtil)
   - 누락 점검으로 V-06(취약한 의존성) 추가, 위험도 2건 조정, 항목 병합·분리 각 1건
   - 조치 검증 중 V-02의 메모리 상한 256MB가 힙 크기와 같으면 OOM이 계속 발생함을 발견 → 64MB로 수정 후 재검증
   - 통계(High 1 / Medium 2 / Low 4 / Info 3 = 10건)와 본문 항목 수, 라인 번호 대조
   - 보고서 자체 검토에서 문장 오류·건수 오기 3곳 수정
8. `daejun/week3/REPORT.md`, `daejun/week3/prompt.md` 작성

**응답 (요약)**

> 보고서를 `daejun/week3/REPORT.md`에 작성했습니다.
>
> | 위험도 | 건수 |
> |---|---|
> | Critical | 0 |
> | High | 1 |
> | Medium | 2 |
> | Low | 4 |
> | Info | 3 |
>
> 가장 중요한 발견은 **V-01**입니다. 워터마크 서명이 문서 내용과 연결되지 않아, 본문을 고치거나 다른 사람의 워터마크를 다른 문서로 옮겨도 검증이 `valid=true`로 나옵니다. 출력 PDF의 SHA-256을 비교하는 오버로드를 추가하는 방식으로 조치했고, PoC로 차단되는 것을 확인했습니다.
>
> 커밋·푸시·PR은 승인해 주시면 진행하겠습니다.

---

## 3. 커밋·푸시·PR

### 🙋 질문

> 작업 완료한 사항 커밋·푸시·PR 해줘

### 🤖 답변

**작업 내용**
- `daejun/CLAUDE.md`, `daejun/week3/REPORT.md`, `daejun/week3/prompt.md`를 커밋 (로컬 과제 안내 파일 `ASSIGNMENT.md`는 제외)
- `week3/daejun` 브랜치를 push하고, `main` 대상 PR `week3/daejun` 생성
- 리뷰어: `juwonlee-dev`, `juhwanHeo` (필수) + `LSHgy` (추가)
