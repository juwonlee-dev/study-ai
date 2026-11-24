# Week3 과제 프롬프트 로그

이 문서는 study-ai Week3 과제(이슈 #46: CLAUDE.md 작성 + KurbyPdf 보안 취약점 보고서) 관련 대화와 에이전트 간 지시·보고를 화자별로 기록한다. Turn 5 말미와 §2-4에는 기존 요약이 포함돼 있다. 두 구간의 원문과 PR 생성 후 코디네이터의 마지막 응답은 확보하지 못해 해당 위치에 표시했다.

## 작업 분담 구조

| 역할 | 에이전트 / 모델 | 한 일 |
|---|---|---|
| 코디네이터 Claude | Claude Code (Orca 코디네이터 세션) | 사용자와 대화하며 과제·리뷰를 Orca 워커로 분배·감독. PR 리뷰도 함께 오케스트레이션 |
| 워커 Claude B | Claude Code (Orca 워커, claude-opus) | Task1 `juhwan/CLAUDE.md`, Task2 `juhwan/week3/REPORT.md` 1차 작성(Phase 1) 및 2차 검토 반영·프롬프트 로그·커밋·푸시·PR(Phase 2) |
| 워커 Claude C | Claude Code (Orca 워커, claude-opus, 독립 세션) | Task2 보고서 2차 검토(독립 재clone·재분석·로컬 PoC) → `week3-review.md` 산출 |

참고: 과제 조건은 "Claude Code를 메인으로 사용"이고, 사용자의 글로벌 규칙은 리뷰·분석을 Codex에 맡기도록 되어 있다. 그래서 2차 검토를 OpenAI Codex(`gpt-6.2-astra`) 워커에 맡기려 했으나, 보안 취약점 보고서가 OpenAI의 사이버보안 안전장치에 걸려 Codex가 실행을 거부했다. 사용자가 "보안 리뷰는 Claude 워커로 진행"을 선택해, 2차 검토도 별도 Claude 워커(C)가 수행했다.

---

# 1. 코디네이터 Claude

> 사용자 ↔ 코디네이터 Claude Code 대화 기록(Week3 관련 턴).

# 코디네이터 Claude (사용자 ↔ Claude Code, Orca 코디네이터)

> 이 세션은 남은 PR 리뷰와 과제를 함께 오케스트레이션했다. 아래는 그중 Week3 과제와 관련된 사용자 발화와 코디네이터 응답 기록이다. (오케스트레이션 시스템 알림 "You have 1 orchestration message..."는 사용자 발화가 아니라 Orca 자동 알림이다.)

## Turn 1 — User

제게 남은 PR 리뷰, 과제들 오케스트레이션 시작해주세요

## Turn 2 — Assistant (질문)

남은 일을 정리했습니다. 워커를 띄우기 전에 정해 주셔야 할 것이 있습니다.

**남은 리뷰 7건** (#44·#12는 제가 수정 요청한 뒤 새 커밋이 없어서 뺐습니다)
- 새로 리뷰: #48 week3/juwonlee, #47 week3/daejun, #18 week1/hyunjin
- 새 커밋이 올라와 다시 리뷰: #42 week2/gunsang, #39 week2/suhyeon, #37 week2/juwonlee, #6 week0/hyunjin

**남은 과제**
- PR #40(week2) 수정 요청 반영: 브레이크포인트를 1080px로 올리기, 프롬프트 로그 구조 정리, 빠진 워커 B 로그와 마지막 응답 추가
- Week3(#46, 마감 11/23)
  - Task1: `juhwan/CLAUDE.md`(60줄 내외)
  - Task2: KurbyPdf 보안 취약점 보고서 `juhwan/week3/REPORT.md`(2차 검토 포함)
  - 참고: 루트 `.gitignore`가 `CLAUDE.md`를 무시하므로 Task1 파일은 `git add -f`로 올려야 합니다.

질문 1. PR 리뷰를 GitHub에 어떻게 올릴까요? — 초안 확인 후 게시 / 바로 게시
질문 2. Week3 과제는 'Claude Code를 메인으로 사용'이 조건인데, 글로벌 규칙은 리뷰·분석을 Codex에 맡기라고 되어 있습니다. 보안 보고서(Task2)는 어느 쪽으로 할까요? — Claude 워커 / Claude 작성 + Codex 2차 검토 / Codex 중심
질문 3. 과제(#40 수정, Week3)는 어디까지 진행할까요? — 커밋까지, 푸시 전 확인 / 푸시·PR까지 진행

## Turn 3 — User (선택)

- 리뷰 게시: 초안 확인 후 게시
- Week3 모델: Claude 작성 + Codex 2차 검토
- 푸시/PR: 푸시·PR까지 진행

## Turn 4 — Assistant

I've started the work as four Orca workers. Each of the three Codex workers shows `GPT-6.2-Sol` on its own terminal, so the model is confirmed.

| Worker | Job | Where |
|---|---|---|
| Codex Sol (A) | Fix PR #40: move the breakpoint to 1080px, clean up the prompt log, then commit and push | current worktree (`week2/juhwan`) |
| Codex Sol (R1) | Review drafts for #48, #47, #6 | read-only |
| Codex Sol (R2) | Review drafts for #42, #39, #37, #18 | read-only |
| Claude (B) | Week3 Task1 `juhwan/CLAUDE.md` and Task2 `REPORT.md` draft | new worktree `week3-juhwan` (based on origin/main) |

- Reviews are drafts only. Nothing gets posted to GitHub until you approve.
- Week3 next steps: when the draft is done, a Codex `gpt-6.2-astra` worker does the second review. Then worker B applies it, writes the prompt log, and commits, pushes and opens the PR. The PR body starts with `Issue: #46`. Reviewers: `juwonlee-dev` and `LSHgy` (you're the author, so GitHub won't let me request you; your name goes in the body instead).

## Turn 5 — Assistant (Codex 차단 보고)

R1 is working again on a narrower scope:

- **#6:** it finishes the re-review draft first.
- **#48, #47:** it checks only the assignment requirements: file paths, `CLAUDE.md` line count, the stats table, the 2nd-review record, the prompt log and the PR body. It won't verify whether the reported vulnerabilities are real, and each draft will say so.

**This affects the Week3 second review.** You picked Codex `gpt-6.2-astra` for it, and it will probably hit the same block, since a security report is exactly what the safeguard flags. Your rules say to hold a task when the chosen model can't run it, so if that happens I'll stop and ask you rather than switch on my own. Your options at that point:

1. Have a Claude worker do the second review instead. This also fits the week3 condition of using Claude Code as the main tool.
2. Apply for OpenAI's Daybreak access and then use Codex.

The other three workers (A, R2, B) haven't reported any trouble.

> **요약 (원문 미확보):** 이후 R1이 다시 차단되어 #6은 새 Codex 워커 R3로 옮기고 #48·#47은 보류했다.

## Turn 6 — User

지금 중단된 거는 뭔가요?

## Turn 7 — Assistant

Only one thing is stopped: **R1, the review drafts for #48 and #47.**

- **Why it stopped:** OpenAI's cybersecurity safeguard on Codex `gpt-6.2-sol` blocked it twice. Both PRs are Week3 vulnerability reports, so they count as security content.
- **Current state:** the worker is still open but idle. I haven't stopped it. It produced no drafts for #48 or #47.
- **What it needs from you:**
  1. **Claude worker (recommended):** hand #48 and #47 to a Claude worker.
  2. **Daybreak:** apply for OpenAI's Daybreak access and keep them on Codex.

**On hold in advance: the Week3 second review.** It hasn't started yet, but it was planned for Codex `gpt-6.2-astra` and will likely hit the same block. Your answer above covers it too.

**Everything else is running or finished:**

| Work | Status |
|---|---|
| A: PR #40 fixes | Done and pushed |
| R3: #6 re-review draft | Just finished (draft saved; report not received yet) |
| R2: drafts for #42, #39, #37, #18 | Running |
| B: Week3 `CLAUDE.md` and `REPORT.md` | Running |

Tell me which option you want, and I'll restart #48, #47 and the Week3 second review with it.

## Turn 8 — User (선택)

- 리뷰 게시: #6, #42, #39·#37, #18 모두 게시
- 보안 리뷰(#48·#47, Week3 2차 검토): Claude 워커로 진행

## Turn 9 — Assistant

I posted all five reviews to GitHub and handed #48 and #47 to a Claude worker.

**Posted reviews:** #6 request changes, #42 request changes, #39 approved, #37 approved, #18 request changes.

**Reassignment of #48 and #47**
- I stopped the Codex worker (R1) that the safeguard blocked.
- A new Claude worker, R4, is drafting reviews for #48 and #47. It will clone KurbyPdf and check the High and Critical findings in each report against the real code. It uses static analysis only and runs no attacks.
- Nothing will be posted until you approve.

**Week3 second review:** this will also be done by a Claude worker. Once worker B finishes the draft, I'll start the review in the same worktree.

R4 and B are still running.

## Turn 10 — Assistant (Week3 Phase 1 완료 보고)

Worker B finished Phase 1 of Week3 in the `week3/juhwan` worktree.
- `juhwan/CLAUDE.md`, 56 lines: the four principles from the karpathy skill, plus rules for this repo and for security analysis.
- `juhwan/week3/REPORT.md`, 7 findings on KurbyPdf commit `74d3aed`: Critical 0 / High 1 (KP-01 Flate 압축폭탄) / Medium 1 (KP-02) / Low 3 (KP-03, KP-04, KP-05) / Info 2 (KP-06, KP-07).
- Second review started: a separate Claude worker, C, is reviewing the report on its own and writes its results to a separate file.
- Next: apply C's review and fill in the "2차 검토" section, write `juhwan/week3/claude-prompt.md`, then commit, push and open the PR.

## Turn 11 — Assistant (2차 검토 완료 후)

2차 검토 워커 C가 끝났습니다(KP-01·02·03·05 수정 필요, KP-04·06·07 확인, 새 취약점·오탐 없음). 워커 B에게 Phase 2(2차 검토 반영, 프롬프트 로그 작성, 커밋·푸시·PR)를 보냅니다.

## PR 생성 후 코디네이터 응답

> **기록 누락 (원문 미확보):** PR 생성 후 코디네이터의 마지막 응답은 확보하지 못했다.

---

# 2. 워커 Claude B (CLAUDE.md·REPORT.md 작성)

## 2-1. Phase 1 지시서 (코디네이터 → 워커 B)

> 아래는 워커 B가 받은 Phase 1 지시서(TASK 블록) 전문이다.

```
Target: study-ai Week3 과제(이슈 #46, `gh issue view 46 -R juwonlee-dev/study-ai`로 원문 확인), 사용자 juhwan. 이 worktree는 origin/main 기반 새 worktree다.

Phase 1 (이번 Task):
0. 현재 브랜치가 `week3/juhwan`이 아니면 `git branch -m week3/juhwan`(원격에 이미 있으면 보고 후 중단).
1. Task1: `juhwan/CLAUDE.md` 작성 — 60줄 내외, Claude Code가 이 사용자의 스터디 과제(특히 Task2 같은 보안 분석·보고서 작성)를 할 때 따를 규칙. 참고: https://github.com/multica-ai/andrej-karpathy-skills (읽을 수 있으면 핵심 원칙: 가정 명시, 단순하게, 외과적 변경, 검증 가능한 목표 등을 반영). 아래 공통 저장소 규칙 중 이 폴더에 필요한 것도 포함. 일반론 나열 말고 구체적 규칙으로.
2. Task2: `juhwan/week3/REPORT.md` 작성 — https://github.com/juwonlee-dev/KurbyPdf 를 저장소 밖 임시 디렉토리(mktemp -d)에 clone하고 분석 시점 커밋 SHA를 보고서에 기록. 방금 쓴 juhwan/CLAUDE.md를 읽고 그 규칙을 따라 작업(보고서에 그 사실 명시).
   - 첫 장: 위험도 단계(Critical/High/Medium/Low/Info)별 탐지 수 통계 표.
   - 취약점마다: ID, 위험도와 근거(CVSS 3.1 벡터 권장), 위치(파일:행), 설명, 재현/공격 시나리오, 현재 소스코드 기준 조치 방안(구체적 수정 코드 예시).
   - 추측은 "확인 필요"로 표시, 오탐 없게 실제 코드 경로를 추적. 의존성 취약점은 실제 버전 기준.
   - 마지막에 "2차 검토" 섹션 자리만 만들어 둔다(검토는 별도 Codex 워커가 수행 후 반영).
3. 커밋/푸시/PR은 아직 하지 말 것. worker_done에 두 파일 경로, KurbyPdf SHA, 위험도별 건수, clone 경로를 보고.

Phase 2는 코디네이터가 follow-up으로 보낸다(2차 검토 반영, juhwan/week3/claude-prompt.md 작성, 커밋·푸시·PR).
Constraints: juhwan/ 밖 수정 금지. KurbyPdf 저장소에 이슈/PR/코멘트 등 아무것도 게시하지 말 것. 실제 공격 실행 금지(로컬 정적 분석과 로컬 테스트만).
Ownership: juhwan/CLAUDE.md, juhwan/week3/REPORT.md.
Observable acceptance: 두 파일 존재, CLAUDE.md 줄 수(wc -l) 50~70, REPORT.md 첫 섹션이 통계 표이고 표의 건수 합계가 본문 취약점 수와 일치.
[공통 저장소 규칙 — study-ai (GitHub juwonlee-dev/study-ai), 사용자 GitHub 계정 juhwanHeo]
- 브랜치 `week{N}/juhwan`, 작업은 `juhwan/` 아래에서만. 다른 멤버 폴더는 읽기만.
- 커밋은 의미 단위로 나누고 메시지 형식은 `week{N}/juhwan: {한글 설명}`. `Co-Authored-By: Claude ...` 등 AI 트레일러 금지.
- PR 본문에 "Generated with Claude Code" 같은 AI 도구 홍보 문구/링크 금지. PR 본문 최상단에 `Issue: #{번호}`.
- 프롬프트 로그(`claude-prompt.md`)는 과제 관련 모든 사용자 발화와 AI 응답을 생략 없이 턴 단위로 기록. 여러 AI/워커를 썼으면 구분해서 기록.
- 루트 `.gitignore`(untracked)가 `CLAUDE.md`를 무시하므로, 추적해야 하는 CLAUDE.md는 `git add -f`.
```

## 2-2. Phase 1 완료 보고 (워커 B → 코디네이터)

> 워커 B가 `worker_done`으로 보고한 Phase 1 완료 요약 전문이다.

```
브랜치를 week3/juhwan으로 변경했고(원격에 같은 브랜치 없음) juhwan/CLAUDE.md(56줄, karpathy 4원칙과 저장소·보안분석 규칙)와 juhwan/week3/REPORT.md를 작성했다. KurbyPdf SHA 74d3aedeea9204694a8bc1e04e75edaa75add94d를 /var/folders/lk/1mm7j3815g120x8z7skfzz4c0000gn/T/tmp.nsgGxU8OtN/KurbyPdf에 clone해 분석했고, 결과는 Critical 0 / High 1(KP-01 _k1 Flate 압축폭탄 OOM, 1MB PDF로 RSS 2.49GB까지 로컬 재현, 패치도 로컬 검증) / Medium 1(KP-02 워터마크 이식·본문변조 미탐지, 재현) / Low 3(KP-03 제거·검증무력화, KP-04 키 검증 없음, KP-05 jackson 2.17.1 OSV 16건이나 GCM 뒤라 도달 불가) / Info 2(KP-06 PDF 권한, KP-07 테스트 암호 출력)로 합계 7건이며 통계 표와 일치한다. 남은 일은 Phase 2(2차 검토 섹션 채우기, claude-prompt.md, 커밋·푸시·PR)이며, 참고로 이 worktree에서는 juhwan/CLAUDE.md가 ignored가 아니라 untracked(??)로 보이고 PoC 코드는 scratchpad에만 있다.
```

## 2-3. Phase 2 지시서 (코디네이터 → 워커 B)

> 아래는 워커 B가 받은 Phase 2 지시서(TASK 블록) 전문이다.

```
Phase 2 (Week3 마무리). 같은 worktree(/Users/heojuhwan/orca/workspaces/study-ai/week3-juhwan, 브랜치 week3/juhwan)에서 진행.

1. 2차 검토 반영: /private/tmp/claude-501/-Users-heojuhwan-intellij-workspace-git-study-ai-juhwan/f7177d8c-752b-4b14-bcca-7a2f80e8f868/scratchpad/week3-review.md (독립 Claude 워커 C의 2차 검토 결과)를 읽고 REPORT.md에 반영.
   - KP-01: PdfWatermarkInspector.java:56 두 번째 sink(FlateDecode+JPXDecode Image XObject) 추가, MemoryUsageSetting 필수화.
   - KP-02: ContentDigest 조치가 마지막 content stream·resources·annotations를 놓치는 점 수정, 주장 범위를 이식 탐지로 한정.
   - KP-03: catch에 java.security.ProviderException 포함.
   - KP-04: verifyBase64 decode를 try 밖에서 처리하는 부분 보강(PdfVerificationUtil.java:26-27).
   - KP-05: OSV 12/4 표기, looksLikeValidNumber 도달 불가 근거, CVSS 없음 각주.
   - KP-06: userPassword가 비면 ownerPassword가 무시되는 점 반영.
   - §5의 'Codex 워커' 문구를 실제 수행자(Claude 워커, Orca)로 고침 — 2차 검토는 OpenAI 사이버보안 안전장치 때문에 Codex 대신 Claude 워커가 수행했다는 사실을 명시.
   - 파서 재귀 한도는 "확인 필요"로 남기거나 확인 가능하면 확인.
   - "2차 검토" 섹션에 week3-review.md의 요약 블록을 넣고 판정 반영 결과(반영/미반영 사유)를 표로. 통계 표와 본문 건수 일치 재확인.
2. juhwan/week3/claude-prompt.md 작성(생략 없이 턴 단위, 화자 구분):
   - "# 1. 코디네이터 Claude": /private/tmp/claude-501/-Users-heojuhwan-intellij-workspace-git-study-ai-juhwan/f7177d8c-752b-4b14-bcca-7a2f80e8f868/scratchpad/coordinator-log.md 전문을 그대로 넣는다. 이후 코디네이터 턴이 더 오면 append.
   - "# 2. 워커 Claude B (CLAUDE.md·REPORT.md 작성)": 네가 받은 Phase 1 지시서 전문(/private/tmp/claude-501/-Users-heojuhwan-intellij-workspace-git-study-ai-juhwan/f7177d8c-752b-4b14-bcca-7a2f80e8f868/scratchpad/specs/B-week3.md), 네 Phase 1 완료 보고 전문, 이 Phase 2 지시서 전문(/private/tmp/claude-501/-Users-heojuhwan-intellij-workspace-git-study-ai-juhwan/f7177d8c-752b-4b14-bcca-7a2f80e8f868/scratchpad/specs/B-phase2.md), Phase 2 완료 보고 전문.
   - "# 3. 워커 Claude C (2차 검토)": 지시서 전문(/private/tmp/claude-501/-Users-heojuhwan-intellij-workspace-git-study-ai-juhwan/f7177d8c-752b-4b14-bcca-7a2f80e8f868/scratchpad/specs/C-review.md), 완료 보고 전문(아래 원문).
   - C 완료 보고 원문: "Independently re-cloned KurbyPdf@74d3aed into a fresh mktemp dir, re-checked every file:line, re-queried OSV (2026-11-20), and ran local PoCs; results are in .../scratchpad/week3-review.md with a paste-ready 2차 검토 block. Verdicts: KP-01 수정 필요 (second sink at PdfWatermarkInspector.java:56: a FlateDecode+JPXDecode Image XObject OOMs at -Xmx256m with no _k1 present, so MemoryUsageSetting must be mandatory; it rejects the PoC in 948ms); KP-02 수정 필요 (the ContentDigest fix skips the last content stream unchecked and ignores resources/annotations, so body tampering still passes; limit the claim to transplant detection); KP-03 수정 필요 (the fix's catch misses java.security.ProviderException, which the PoC actually throws, reproduced on JDK17); KP-04 확인 (add verifyBase64 decode outside try, PdfVerificationUtil.java:26-27); KP-05 수정 필요 (format only: OSV 12/4 matches, looksLikeValidNumber is confirmed unreachable, and the table needs a footnote for the missing CVSS); KP-06 확인 (ownerPassword is silently ignored when userPassword is empty); KP-07 확인. No new independent vulnerabilities and no false positives; the stats table (7) matches the body; still left: apply the 6 edits to REPORT.md, replace the 'Codex 워커' line in §5, and check the parser recursion limit (확인 필요)."
   - 맨 위에 작업 분담 구조(코디네이터/워커 B/워커 C, 각 에이전트·모델) 요약.
3. 커밋(의미 단위 3개: CLAUDE.md / REPORT.md / claude-prompt.md; 형식 'week3/juhwan: {한글 설명}', AI 트레일러 금지) → git push -u origin week3/juhwan.
4. gh pr create -R juwonlee-dev/study-ai --base main --head week3/juhwan --title "Week3 / juhwan" --reviewer juwonlee-dev,LSHgy. 본문(한글): 최상단 "Issue: #46", Task1/Task2 작업 내용, 위험도별 통계 표, 2차 검토 수행 방식(Codex 차단으로 Claude 워커 수행), 사용 에이전트/모델(Claude Code, Orca 오케스트레이션), 지정 리뷰어 @juwonlee-dev @juhwanHeo @LSHgy(작성자 본인은 GitHub 리뷰 요청 불가라 본문에만). "Generated with Claude Code" 류 문구 금지.
Constraints: juhwan/ 밖 수정 금지, KurbyPdf에 아무것도 게시 금지, PoC 코드는 커밋하지 않는다(보고서에 재현 절차만).
Observable acceptance: 커밋 해시 3개, PR URL, REPORT.md 최종 위험도별 건수, 2차 검토 반영표 요약을 worker_done에.
```

## 2-4. Phase 2 완료 보고 (워커 B → 코디네이터)

**요약 (원문 미확보)** — 아래 인용문은 워커 B의 Phase 2 완료 보고를 정리한 기존 문구다.

> 워커 C의 2차 검토(`week3-review.md`)를 읽고 REPORT.md에 반영했다. KP-01에 두 번째 sink(`PdfWatermarkInspector.java:56` Image XObject `[/FlateDecode /JPXDecode]` 폭탄)와 세 번째 sink(깊은 중첩 PDF의 파서 `StackOverflowError`)를 추가하고 `MemoryUsageSetting` 상한을 필수 조치로 명시했으며, (b)는 상한 적용 시 948ms에 거부·(c)는 pdfbox 2.0.37에서 거부됨을 로컬로 확인해 넣었다. KP-02는 ContentDigest가 마지막 콘텐츠 스트림·리소스·주석을 놓쳐 본문 변조를 못 막는 점을 반영해 조치 범위를 "이식 탐지"로 한정하고 변조 탐지는 발급 기록 대조로 보완했다. KP-03 catch에 `java.security.ProviderException`을 추가, KP-04에 `verifyBase64` 디코딩 위치(`:26-27`)와 검증 경로 `Result.fail` 권고 추가, KP-05는 OSV 12/4건 표기·`looksLikeValidNumber` 도달 불가 확인·CVSS 미산정 각주, KP-06은 `userPassword`가 비면 `ownerPassword`가 무시되는 점을 반영했다. "2차 검토" 섹션(§5)에 검토자(Codex 차단으로 Claude 워커 수행)·방법·항목별 판정과 반영 내역 표를 넣었고, 통계 표 합계(7) = 본문 `### KP-`(7) 일치를 재확인했다. 파서 재귀 한도는 "확인 필요"로 남기지 않고 로컬에서 확인해 KP-01(c)로 편입했다(건수 7 유지). 이어서 `juhwan/week3/claude-prompt.md`를 작성하고, 의미 단위 커밋 3건(CLAUDE.md / REPORT.md / claude-prompt.md, 메시지 `week3/juhwan: …`, AI 트레일러 없음)으로 나눠 `week3/juhwan`에 푸시한 뒤 `juwonlee-dev/study-ai`에 PR을 생성했다. 최종 위험도별 건수는 Critical 0 / High 1 / Medium 1 / Low 3 / Info 2(합계 7), 오탐·새 취약점 없음. (구체적 커밋 해시 3건과 PR URL은 코디네이터에게 보낸 `worker_done` 메시지에 기록 — 이 로그 파일 자체의 커밋 이후 생성되므로 여기에는 싣지 않는다.)

---

# 3. 워커 Claude C (2차 검토)

## 3-1. 2차 검토 지시서 (코디네이터 → 워커 C)

> 아래는 워커 C가 받은 지시서(TASK 블록) 전문이다.

```
Target: study-ai Week3 Task2 보안 보고서 2차 검토. 대상 파일: /Users/heojuhwan/orca/workspaces/study-ai/week3-juhwan/juhwan/week3/REPORT.md (작성: 다른 Claude 워커). 작업 규칙: 같은 worktree의 juhwan/CLAUDE.md를 읽고 따른다. 과제 원문: `gh issue view 46 -R juwonlee-dev/study-ai`.
분석 대상: https://github.com/juwonlee-dev/KurbyPdf, 커밋 74d3aedeea9204694a8bc1e04e75edaa75add94d. 1차 clone(/var/folders/lk/1mm7j3815g120x8z7skfzz4c0000gn/T/tmp.nsgGxU8OtN/KurbyPdf)은 읽기만 하거나, 새 임시 디렉토리(mktemp -d)에 독립적으로 clone해서 확인한다.

Change: 독립적인 2차 검토를 수행하고 결과를 /private/tmp/claude-501/-Users-heojuhwan-intellij-workspace-git-study-ai-juhwan/f7177d8c-752b-4b14-bcca-7a2f80e8f868/scratchpad/week3-review.md 에 쓴다.
- 취약점 7건(KP-01~07) 각각: 파일:행과 코드 경로가 실제 소스와 맞는지, 위험도/CVSS 벡터가 타당한지, 재현 시나리오 논리, 조치 방안이 현재 소스에 적용 가능하고 충분한지. 판정: 확인 / 수정 필요(구체적 수정안) / 오탐.
- 누락 탐지: 입력 검증, 경로 처리, 암호/키 관리, 역직렬화, 리소스 소비, 의존성 버전(빌드 파일 기준) 등 1차에서 빠진 취약점이 있는지 소스를 직접 훑는다. 새로 찾으면 1차와 같은 형식(ID, 위험도, 위치, 설명, 시나리오, 조치)으로 제시.
- 과제 형식: 첫 장 위험도별 통계 표와 본문 건수 일치, 위험도 단계 구분, 조치 방안 포함 여부.
- 마지막에 REPORT.md "2차 검토" 섹션에 그대로 넣을 수 있는 요약 블록(검토자·일시·방법·항목별 판정 표·반영 필요 사항)을 작성.

Constraints: REPORT.md 및 저장소 파일 수정 금지(결과 파일만 작성). 커밋·푸시 금지. 실제 공격 실행 금지 — 정적 분석과 로컬 단위 실행만. KurbyPdf에 아무것도 게시하지 말 것.
Observable acceptance: week3-review.md에 7건 각각 판정과 근거(파일:행), 누락 탐지 결과(없으면 "없음"과 확인한 범위), 2차 검토 요약 블록. worker_done에 항목별 판정 한 줄 요약.
```

## 3-2. 2차 검토 완료 보고 (워커 C → 코디네이터)

> 워커 C가 `worker_done`으로 보고한 완료 요약 원문이다(영문 원문 그대로).

```
Independently re-cloned KurbyPdf@74d3aed into a fresh mktemp dir, re-checked every file:line, re-queried OSV (2026-11-20), and ran local PoCs; results are in .../scratchpad/week3-review.md with a paste-ready 2차 검토 block. Verdicts: KP-01 수정 필요 (second sink at PdfWatermarkInspector.java:56: a FlateDecode+JPXDecode Image XObject OOMs at -Xmx256m with no _k1 present, so MemoryUsageSetting must be mandatory; it rejects the PoC in 948ms); KP-02 수정 필요 (the ContentDigest fix skips the last content stream unchecked and ignores resources/annotations, so body tampering still passes; limit the claim to transplant detection); KP-03 수정 필요 (the fix's catch misses java.security.ProviderException, which the PoC actually throws, reproduced on JDK17); KP-04 확인 (add verifyBase64 decode outside try, PdfVerificationUtil.java:26-27); KP-05 수정 필요 (format only: OSV 12/4 matches, looksLikeValidNumber is confirmed unreachable, and the table needs a footnote for the missing CVSS); KP-06 확인 (ownerPassword is silently ignored when userPassword is empty); KP-07 확인. No new independent vulnerabilities and no false positives; the stats table (7) matches the body; still left: apply the 6 edits to REPORT.md, replace the 'Codex 워커' line in §5, and check the parser recursion limit (확인 필요).
```

> 워커 C의 상세 검토 노트(항목별 판정·근거·로컬 PoC 출력)는 scratch의 `week3-review.md`에 있으며, 과제 산출물이 아니므로 저장소에는 커밋하지 않는다.
