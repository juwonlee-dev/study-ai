# Week 1 자기소개 이미지 제작 기록

## 사용한 AI와 스킬

| AI·도구·스킬 | 사용한 부분 | 사용 이유 |
| --- | --- | --- |
| Codex | Issue 분석, 작업 규칙 확인, 정보 구조 설계, 파일 작성, 이미지 합성 및 검증 | GitHub Issue의 과제 내용과 운영 안내를 구분하고, README의 내용을 빠짐없이 산출물에 반영하기 위해 사용했습니다. |
| `superpowers:using-superpowers` | 작업 시작 절차 점검 | 작업에 맞는 스킬을 먼저 확인하고 정해진 절차에 따라 진행하기 위해 사용했습니다. |
| `superpowers:brainstorming` | 포스터 스타일과 구성 설계 | 이미지 제작 전에 목적, 산출물, 검증 방법을 정리하고 사용자 승인을 받기 위해 사용했습니다. |
| `imagegen` | 텍스트가 없는 테크 인포그래픽 배경 생성 | 생성형 AI의 시각적 표현력을 활용하면서, 한글 오탈자 위험은 분리하기 위해 사용했습니다. |
| Swift·AppKit | README 기반 한글 텍스트와 카드 레이아웃 합성 | 생성형 이미지 모델이 한글을 잘못 생성할 가능성을 없애고 정확한 문구를 렌더링하기 위해 사용했습니다. |
| `superpowers:systematic-debugging` | OCR 검증 오류 진단 | macOS Vision OCR이 샌드박스에서 실패한 원인을 추측하지 않고 재현·격리하기 위해 사용했습니다. |
| `superpowers:verification-before-completion` | 최종 산출물 검증 | 완료를 보고하기 전에 파일 형식, 크기, 필수 문구, 기록 누락과 Git 변경 범위를 새로 확인하기 위해 사용했습니다. |
| macOS Vision OCR | 완성 이미지의 텍스트 인식 확인 | 최종 PNG에 텍스트가 실제로 표시되고 잘리지 않았는지 보조 검증하기 위해 사용했습니다. |

## 대화 기록

### 1. 작업 요청

#### 사용자

> bohye 라는 폴더에서 작업을 할거야. 그 폴더안의 규칙대로 작업시작하자<br>
> 이슈번호는 14번이야.<br>
> https://github.com/juwonlee-dev/study-ai/issues/14

#### Codex

> `bohye` 폴더의 작업 규칙과 이슈 14의 실제 요구사항을 먼저 맞춰보겠습니다. 이번에는 작업 착수 절차를 놓치지 않도록 `using-superpowers`를 먼저 적용하고, 변경 작업이 확인되면 `brainstorming`으로 요구사항과 범위를 정리한 뒤 진행할게요.

> `using-superpowers`의 Codex 절차를 확인했습니다. 이제 `brainstorming` 규칙에 따라 이슈의 목표와 완료 조건을 코드 변경 전에 확정하겠습니다. 이 스킬이 요구하는 범위 확인을 마치기 전에는 구현 파일을 수정하지 않겠습니다.

> 아직 이슈 내용을 읽기 전이라 범위 분류는 보류하고, 허용된 읽기 작업만 하겠습니다. `bohye` 폴더의 지침 파일, 현재 Git 상태와 최근 작업 흐름, GitHub 이슈 14를 함께 확인한 뒤 `bounded / architectural` 중 하나로 분류해 말씀드릴게요.

> 이 작업은 기존 `bohye/week0/README.md`를 정확한 원문으로 삼아 이미지 1장과 대화 기록을 만드는, 범위가 명확한 **bounded 작업**으로 분류하겠습니다. 따라서 별도 설계 문서까지 만들기보다는 짧은 디자인을 채팅에서 승인받은 뒤 구현하는 흐름이 적절합니다.
>
> 확인된 상태는 다음과 같습니다.
>
> - 현재 브랜치는 이미 규칙에 맞는 `week1/bohye`이고 작업 트리는 깨끗합니다.
> - 산출물은 `bohye/week1/profile.png`와 `bohye/week1/prompt.md`입니다.
> - README의 이름, 생년월일, 성별, 역할, MBTI, 관심 기술, 참여 목적, AI 활용 내용이 빠지거나 달라지면 안 됩니다.
> - 이미지 생성 후 README와 대조 검증한 기록이 반드시 필요합니다.
> - 이슈가 운영 안내와 과제 내용이 섞여 있으므로 폴더 규칙에 따라 `bohye/week1/ASSIGNMENT.md`도 만들어 작업 기준만 정리하는 방향이 적절합니다.
> - 마감은 2026-09-28 23:59로 현재 시점에는 지났습니다. 완성 전이라도 기한 내 PR 제출이 원칙이었고, 미완성분은 마감 후 7일 이내 보완하도록 되어 있습니다.
> - 커밋·푸시·PR·리뷰어 지정은 각각 별도 승인 전에는 실행하지 않겠습니다.

> 이미지 스타일은 어떤 방향이 좋을까요? 추천은 **깔끔한 테크 인포그래픽 포스터**이고, 대안은 일러스트형 프로필 포스터 또는 이력서형 카드입니다.

### 2. 스타일 선택

#### 사용자

> 깔끔한 테크 인포그래픽 포스터로 해줘

#### Codex

> 짧은 디자인안은 다음과 같습니다.
>
> - 세로형 `1600×2000px` 테크 인포그래픽
> - 네이비·코발트·시안 계열, 밝은 배경과 정돈된 카드형 레이아웃
> - 실물 외모를 임의로 만들지 않고 `KB` 모노그램과 AI·코드 네트워크 그래픽 사용
> - 상단: 이름, 역할, 기본 정보
> - 중앙: 관심 기술 3개와 스터디 참여 목적 3개
> - 하단: AI 활용 방식과 학습 방향
> - 배경 그래픽은 `imagegen`으로 만들고, 한글 텍스트는 오탈자를 막기 위해 별도로 정확하게 합성
> - `profile.png`, `prompt.md`, `ASSIGNMENT.md` 모두 `bohye/week1/`에만 생성
> - 완성 후 이미지의 문구를 README 항목별로 대조하고 시각적 잘림·가독성까지 검증
>
> 이 디자인대로 제작을 시작해도 될까요?

### 3. 제작 승인

#### 사용자

> 이슈 속 과제 내용 조건을 잘 지켜주면서 제작해줘

#### Codex

> 승인된 디자인으로 제작을 시작하겠습니다. 과제에서 “어떤 AI와 스킬을 왜 사용했는지”까지 설명해야 하므로, 먼저 `imagegen` 스킬의 제작·검증 절차를 적용합니다. 이 스킬에 따라 생성형 그래픽과 정확한 한글 정보 레이어를 분리해 작업하고, 최종 검증 근거도 `prompt.md`에 남기겠습니다.

> 이제 `imagegen`으로 텍스트 없는 세로형 테크 배경을 생성합니다. 한글은 생성 이미지에 직접 맡기지 않고 이후 정확한 정보 레이어로 합성해, 이슈의 “README와 다른 내용이 없어야 한다”는 조건을 우선하겠습니다.

## 이미지 생성 도구 입력

아래 프롬프트를 Codex 내장 `imagegen` 도구에 입력했습니다.

```text
Use case: infographic-diagram
Asset type: portrait self-introduction infographic background for a software developer
Primary request: Create a polished, clean technology-themed vertical poster background with no written words, no letters, and no numbers. The final design will receive Korean typography later, so reserve generous readable negative space and use a disciplined modular grid.
Scene/backdrop: warm off-white to very pale blue background with subtle abstract AI neural-network lines, code-inspired geometric nodes, circuit traces, tiny grid dots, and restrained layered translucent panels.
Subject: an abstract personal identity motif using a sophisticated circular monogram-like geometric emblem, but do not render any actual letters; no human face or body.
Style/medium: premium flat vector-inspired digital illustration, editorial technology infographic, minimal and professional, crisp edges, subtle depth, not a UI screenshot.
Composition/framing: portrait orientation. Visual interest concentrated around the top-right and outer edges; broad clean central and left regions for later text. Clear visual rhythm suitable for a header, identity section, three topic cards, a goals section, and a footer section. Do not draw empty card outlines that could conflict with later layout.
Lighting/mood: bright, intelligent, confident, calm.
Color palette: navy, cobalt blue, cyan, soft lavender accents, white and very light gray.
Constraints: absolutely no text, no letters, no numerals, no logos, no watermark, no people, no fake interface labels. Keep the center uncluttered and typography-safe.
Avoid: cyberpunk darkness, neon overload, photorealism, busy circuit boards, gradients with poor text contrast, random symbols that resemble characters.
```

## 이미지 생성 도구 응답

`imagegen`은 1024×1536 세로형 PNG 배경을 생성했습니다. 생성 결과에는 글자, 숫자, 로고, 사람, 워터마크가 없었고 중앙에 충분한 여백이 있었습니다. 이 배경을 1600×2000 캔버스에 맞춘 뒤 README의 내용을 코드로 합성했습니다.

## 제작 중 Codex 응답

> 배경 시안은 텍스트 없이 생성되어 조건에 맞습니다. 다음으로 README 내용을 카드형 정보 구조에 정확히 배치하고, 원문 대조가 가능하도록 과제 기준과 대화 기록 파일을 함께 작성하겠습니다.

> 텍스트 정확성을 위해 최종 PNG는 생성형 배경 위에 코드로 한글을 합성합니다. 지금 `bohye/week1/` 안에 과제 기준과 재현 가능한 이미지 조립 소스를 만들고, 이후 렌더링 결과만 최종 산출물로 남기겠습니다.

> 초기 합성본이 생성되었습니다. 지금부터는 실제 이미지를 눈으로 확인해 텍스트 잘림·겹침·가독성을 점검하고, README 원문과 항목별로 대조하겠습니다. 문제가 보이면 한 번에 한 가지씩 수정하겠습니다.

> 이미지 렌더링 자체는 정상이고 육안 검사는 통과했지만, 보조 OCR 검증이 macOS Vision의 `nilError`로 실패했습니다. `systematic-debugging` 스킬을 적용해 이 검증 도구 실패의 원인만 좁히겠습니다. 이미지나 과제 내용은 수정하지 않고, 검증 경로만 진단합니다.

> 같은 실패가 절대 경로에서도 재현되어 경로 문제는 아니었습니다. 예외가 최상위에서 뭉개져 있어 원인이 보이지 않으므로, 다음 한 번은 예외 도메인·코드와 지원 언어를 출력하도록 진단만 보강하겠습니다.

> 지원 언어에는 `ko-KR`가 포함되어 있어 언어 모델 문제는 아닙니다. 오류 지점이 URL 기반 이미지 입력 처리로 좁혀졌으므로, 같은 PNG를 `CGImage`로 먼저 디코딩한 뒤 Vision에 넘기는 한 가지 변경만 시험하겠습니다.

> OCR은 샌드박스 밖에서 정상 실행됐고, 실패 원인은 이미지가 아니라 macOS Vision의 샌드박스 제약이었습니다. OCR로 주요 문구가 모두 인식됐으며, `AI`를 `Al`로 읽는 영문 오인식과 이모지 오인식만 있었습니다. 원본 이미지 육안 확인에서는 문자가 정상입니다. 이제 이 과정과 사용한 AI·스킬·대화 내용을 `prompt.md`에 정리하겠습니다.

> 산출물과 검증 기록이 작성되었습니다. 완료라고 보고하기 전에 `verification-before-completion` 스킬을 적용해 파일 형식·크기, 요구 문구, Markdown 누락, Git 변경 범위를 새로 확인하겠습니다. 이 검증이 끝난 뒤 임시 렌더링 파일만 정리합니다.

## README 대조 검증

| 검증 항목 | README 내용 | 이미지 반영 | 결과 |
| --- | --- | --- | --- |
| 이름 | 김보혜 | 김보혜 | 일치 |
| 생년월일 | 1995.11.06 | 1995.11.06 | 일치 |
| 성별 | 여성 | 여성 | 일치 |
| 직업·역할 | 풀스택 개발자 | 풀스택 개발자 | 일치 |
| MBTI | ENTJ | ENTJ | 일치 |
| 정체성 문구 | Full-Stack Developer · AI를 효율적으로 활용하는 개발자 | 동일 문구 | 일치 |
| 소개 문구 | 반복되는 개발 과정은 더 안정적으로, 새로운 기술은 더 깊이 있게 배우고 싶습니다. | 동일 문구 | 일치 |
| 관심 기술 | AI Engineering, NestJS, Flutter와 각 설명 | 세 항목과 설명 모두 반영 | 일치 |
| 참여 목적 | 개발 과정 전반에서 AI를 더 효율적으로 활용 | 동일 내용 | 일치 |
| 학습 목표 | 프롬프트 작성법, 토큰 관리법, TDD 개발 방향 | 세 항목 모두 반영 | 일치 |
| AI 활용 | AGENTS.md 규칙, Issue 구분, 질문을 통한 README 작성 | 모두 반영 | 일치 |
| 대화 기록 | codex-prompt.txt에 기록 | 동일 내용 | 일치 |
| 마무리 문구 | AI와 함께 더 효율적으로 개발하고, 배운 내용을 꾸준히 실전에 연결 | 동일 문구 | 일치 |

### 시각 검증

- 최종 크기: 1600×2000 PNG
- 한글과 영문이 깨지지 않고 표시됨
- 텍스트 잘림과 카드 간 겹침 없음
- 배경과 본문 사이의 대비가 충분함
- 실물 외모처럼 README에 없는 정보를 임의로 추가하지 않음
- 생성형 배경에 글자, 로고, 워터마크가 없음

### OCR 보조 검증

macOS Vision OCR을 `ko-KR`, `en-US` 설정으로 실행해 이름, 기본 정보, 관심 기술, 참여 목적, 학습 목표, AI 활용 문단과 마무리 문구가 출력되는 것을 확인했습니다. OCR이 `AI`를 `Al`로, 마지막 이모지를 다른 글자로 인식한 부분은 원본 PNG를 직접 확인해 실제 렌더링이 정상임을 검증했습니다.

### 파일 검증 결과

- `profile.png`: PNG, 1600×2000, 8-bit RGBA, non-interlaced
- README에서 가져온 필수 문구 19개가 합성 원본에 모두 포함됨
- `prompt.md`와 `ASSIGNMENT.md`에 AI·스킬 설명, Issue 링크, README 대조 및 OCR 검증 내용이 포함됨
- 미완성 상태를 나타내는 임시 표시 없음
- 작업 결과가 `bohye/week1/` 안에만 생성됨
