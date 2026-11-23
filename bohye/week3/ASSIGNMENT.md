# Week 3 과제 기준

- GitHub Issue: [#46 3주차](https://github.com/juwonlee-dev/study-ai/issues/46)
- 작업 브랜치: `week3/bohye`
- 마감 기한: 2026-11-23 (월) 23:59 (과제 1, 2 공통)
- 공통: 모든 과제는 AI를 사용하며, Claude Code를 메인으로 사용한다.

## 과제 1. CLAUDE.md 작성

### 목표

Claude Code가 `bohye/` 작업 시 따를 지침 파일 `CLAUDE.md`를 작성한다.

### 필수 요구사항

- 이번 주차 1번 과제만 예외적으로 주차 폴더가 아닌 `bohye/` 바로 아래에서 작업한다. → `bohye/CLAUDE.md`
- 60줄 내외로 작성한다.
- 참고 가능(선택): [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)

## 과제 2. 오픈소스 프로젝트 취약점 보고서

### 목표

분석 대상 프로젝트의 보안 취약점을 찾아 보고서를 작성한다.

- 분석 대상: https://github.com/juwonlee-dev/KurbyPdf

### 필수 요구사항

- 작업 디렉터리: `bohye/week3/`
- 과제 1에서 작성한 `CLAUDE.md`를 사용한다.
- 보고서 파일명: `REPORT.md` → `bohye/week3/REPORT.md`
- 발견한 취약점마다 현재 소스코드 기준의 조치 방안을 함께 정리한다.
- 취약점 위험도를 단계별로 구분한다.
- 보고서 첫 장에 위험도 단계별 탐지 취약점 수 통계를 구성한다.
- 작성한 보고서는 반드시 2차 검토 절차를 거친다.

## 제출 및 리뷰

- 개별 브랜치(`week3/bohye`)에 커밋한 뒤 `main` 대상 PR을 제출한다.
- PR 본문 최상단에 `Issue: #46`을 표기하고 작업 내용을 설명한다.
- 필수 리뷰어 `@juwonlee-dev`, `@juhwanHeo` + 추가 리뷰어 1명 이상을 지정한다.
- 미완성이어도 마감까지 PR을 제출하고, 미완성 부분은 마감 후 7일 이내 완료한다.

## 검증 기준

- `bohye/CLAUDE.md`가 존재하고 약 60줄 분량이다.
- `bohye/week3/REPORT.md` 첫 장에 위험도별 건수 통계가 있고, 본문 건수와 일치한다.
- 각 취약점에 위험도, 근거(파일·라인), 조치 방안이 있다.
- 2차 검토를 수행하고 그 결과가 보고서에 반영되었다.

## 과제와 분리한 운영 안내

- 다음 주차 스터디 일정(26.11.24 22:00)과 발표자·발표 주제는 구현 요구사항에 포함하지 않는다.
- PR 병합·브랜치 삭제는 마지막 리뷰어가 수행한다.
