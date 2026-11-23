# Week3 — 프롬프트 기록

> **사용 도구**: Orca + Claude Code (CLI)
> **사용 모델**: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
> **작업 브랜치**: `week3/yiseul`
> **산출물**: `yiseul/CLAUDE.md`(Task1), `yiseul/week3/REPORT.md`(Task2), `yiseul/week3/prompt.md`
> **과제 이슈**: #46

대화를 순서대로 기록했습니다. 도구 호출은 `🔧`로 무엇을 했고 어떤 결과가 나왔는지 적었습니다.

---

## 1. 👤 User

```
'--permission-mode'
```

## 2. 🤖 Claude

```
`'--permission-mode'`만 전달되었고 요청 내용이 없습니다. 이 문자열은 Claude Code 실행 옵션(`claude --permission-mode <모드>`)의 이름처럼 보이는데, 메시지로 잘못 들어온 것 같습니다.

원하시는 작업이 무엇인지 알려주세요. 권한 모드 설정에 관한 질문이라면 어떤 모드(예: `default`, `acceptEdits`, `plan`)를 쓰려는지 알려주시면 도와드리겠습니다.
```

## 3. 👤 User

```
https://github.com/juwonlee-dev/study-ai/issues/46
작업 진행
```

## 4. 🤖 Claude

🔧 **도구 사용 내역**
- `gh issue view 46` → 3주차 과제 확인
  - Task1: `yiseul/CLAUDE.md`를 60줄 내외로 작성
  - Task2: https://github.com/juwonlee-dev/KurbyPdf 보안 취약점 보고서(`REPORT.md`) 작성, 위험도별 통계 첫 장, 조치 방안, 2차 검토
- 저장소 구조와 기존 `yiseul/CLAUDE.md`(39줄), 브랜치 목록 확인 → `week3/yiseul` 브랜치로 전환
- 분석 대상을 임시 디렉터리(scratchpad)에 클론하고 소스 9개 전체를 읽음(약 630줄)
- OSV API로 `pdfbox 2.0.30`(조회 결과 없음), `jackson-databind 2.17.1`(GHSA 12건), `commons-logging 1.2`(없음) 조회
- 커밋 이력에서 시크릿 검색(키 이름 상수 외 없음)
- 의존성 JAR을 내려받아 PoC를 컴파일·실행하려는 명령 → **자동 권한 분류기가 거부**함. 우회하지 않고 정적 분석으로 진행
- `yiseul/CLAUDE.md`를 56줄로 갱신(작업 원칙, week3 구조, 보안 보고서 규칙 추가)
- `yiseul/week3/REPORT.md` 작성(총 14건: Medium 4, Low 6, Info 4) 후 줄 번호를 grep으로 재확인해 수정

```
이슈 #46의 두 과제를 `week3/yiseul` 브랜치에 작성했습니다. 커밋, 푸시, PR은 아직 하지 않았습니다.

1번 과제: yiseul/CLAUDE.md
- 기존 39줄을 56줄로 늘렸습니다(60줄 내외 조건).
- 작업 원칙(코딩 전 생각, 단순함, 외과적 변경, 검증 중심, 분석 대상 불신)을 추가했습니다.
- week3 구조, 보안 보고서 규칙, PR 본문 규칙을 추가했습니다.
- 원칙 5개는 multica-ai 스킬 저장소를 직접 열어 보지 않고 쓴 것입니다. 이슈의 참고 링크와 맞는지 확인이 필요합니다.

2번 과제: yiseul/week3/REPORT.md
- 첫 장 통계는 Critical 0, High 0, Medium 4, Low 6, Info 4로 총 14건입니다.
- Medium 4건: 워터마크 문서 비결합(이식 가능), 검증 시 압축 해제 제한 없음, 빈 사용자 비밀번호 시 암호화 생략, 권한 설정 느슨/워터마크 제거 불가 방지 못함.
- 2차 검토 표는 6장에 있습니다. jackson-databind 건은 High에서 Low로 낮췄습니다.

한계
- PoC 실행이 권한 분류기에 거부되어 모든 항목이 코드 읽기 기반이고 "미재현"으로 표기했습니다. 재현 절차는 7장에 있습니다.

남은 일
- week3/prompt.md 작성, 마감(11/23) 후 7일 이내 완료, 커밋·푸시·PR 진행 여부 확인
```

## 5. 👤 User

```
리뷰어 추가 현진

남은 일 진행
```

## 6. 🤖 Claude

🔧 **도구 사용 내역**
- `gh pr list`로 현진의 GitHub 계정을 확인(`hapyjin`, PR #55 `week3/hyunjin` 등)
- `yiseul/week2/prompt.md` 형식을 참고

## 7. 👤 User

```
진행


API Error: Sonnet 5.5's safeguards flagged this message (https://www.anthropic.com/legal/aup). This sometimes happens with safe, normal conversations. Claude Code can't respond to this message with Sonnet 5.5.
(이하 요청 ID 등 오류 상세 생략 없이 사용자가 붙여넣은 내용: Double press esc to edit your last message, or try a different model with /model. Details: `[reasoning_extraction]`)
```

## 8. 🤖 Claude

🔧 **도구 사용 내역**
- 이 기록 파일(`prompt.md`) 작성
- 커밋, 푸시, PR 생성(리뷰어: `juwonlee-dev`, `juhwanHeo`, `hapyjin`)
