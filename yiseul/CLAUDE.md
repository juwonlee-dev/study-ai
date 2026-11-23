# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 저장소 성격

이 저장소는 공용 스터디 저장소 `study-ai`(GitHub: `juwonlee-dev/study-ai`) 안의 개인 폴더(`yiseul/`)이며, 애플리케이션이 아니다. 빌드 시스템, 패키지 매니페스트, 린터, 테스트가 없다. 각 `weekN/` 디렉터리에는 해당 주차 과제 산출물이 들어 있고, 과제 내용은 원본 저장소의 GitHub 이슈에 정의되어 있다(예: week2 = 이슈 #22). `gh issue view`가 아무것도 출력하지 않으면 `gh api repos/juwonlee-dev/study-ai/issues/<N>`로 조회한다.

작업은 `yiseul/` 안에서만 하고, 다른 팀원의 폴더는 수정하지 않는다. 브랜치 이름은 `weekN/yiseul[-k]` 형식이며 PR로 `main`에 병합한다.

## 구조와 주차별 연결

각 주차의 산출물은 이전 주차 결과물에서 이어진다.

- `week0/README.md` — 원본 자기소개 문서(`<p align="center">`와 shields.io 뱃지 `<img>` 태그가 섞인 GitHub 스타일 Markdown). `week0/Claude_prompt.txt`는 대화 기록이다.
- `week1/profile.png` — `week0/README.md`를 이미지로 렌더링한 결과(`md-to-png` 스킬로 생성). `week1/claude-propmpt.md`는 대화 기록이다(파일명 오타는 원래 그대로이므로 유지한다).
- `week2/profile.html` — `week1/profile.png`를 다시 구현한 단일 자체 완결형 HTML 페이지. `week2/prompt.md`는 대화 기록이며, Task2 PR 리뷰 대화(13번 이후)도 포함한다.

`profile.html`을 수정할 때는 `week1/profile.png`를 기준으로 비교하고 README의 모든 요소가 빠지지 않게 유지한다. `<img>`, `<script>`, 외부 URL 허용 여부 같은 제약은 해당 이슈에서 확인한다.

## 프롬프트 기록 규칙

매주 대화 전체를 해당 주차의 기록 파일(`prompt.md` / `claude-propmpt.md`)에 **요약이나 생략 없이 원문 그대로** 저장해야 한다(사용자 프롬프트, 순서대로 AI 응답, 도구 호출은 간략히 표기). 동료 리뷰어가 이 부분을 확인하므로 요약이나 표로 대체하지 않는다.

## 프로젝트 스킬 (`.claude/skills/`)

- `md-to-png` — headless Chrome/Edge로 Markdown을 PNG로 렌더링하고 결과를 검증한다(Python 3.10+, CDN과 뱃지 로딩을 위한 네트워크 필요).
  ```
  python .claude/skills/md-to-png/scripts/md_to_png.py <input.md> <output.png> [--width 900] [--scale 2]
  python .claude/skills/md-to-png/scripts/verify.py   <input.md> <output.png> [--width 900] [--scale 2]
  ```
  두 명령에 같은 `--width/--scale` 값을 쓴다. 검증 스크립트는 DOM만 확인하므로 PNG도 직접 눈으로 확인한다.
- `pr-review` — `gh`로 동료 PR을 리뷰하는 절차(대상 선정, Approve/Request changes 판정, 간략한 한글 초안, 등록). 리뷰를 등록하기 **전에** 반드시 요약과 초안 전문을 사용자에게 보여주고 승인을 받아야 한다.

## 컨벤션

- 커밋 메시지는 스코프를 `yiseul`로 한 Conventional Commits 형식이며 한글로 쓴다. 예: `docs(yiseul): week2 Task2 PR 리뷰 대화 기록 추가`, `feat(yiseul): ...`
- 문서와 기록은 한국어로 작성한다.
- PR 본문에는 사용한 AI와 도구, 리뷰어 지정, 검증 방법을 적고 과제 이슈를 링크한다(`Refs #N`).
