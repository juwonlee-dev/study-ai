# Codex Prompt Log — Week1

- 사용 AI: ChatGPT/Codex
- 사용 스킬: `imagegen`
- 기록 범위: Week1 과제 확인부터 이미지 생성·검증까지의 대화 흐름

---

## 1. 과제 확인

### User

```text
Issue #14의 해당 부분에서 어떤 과제를 해야할까?
```

### Codex

```text
자기소개 README를 기반으로 profile.png를 만들고, 프롬프트 로그와 함께
hyunjin/week1/에 커밋하여 PR로 제출하는 과제입니다.
```

## 2. 스킬 선택

### User

```text
'스킬'이 무엇인지 이해하고, 어떤 스킬을 사용할지 고민해볼래.
```

### Codex

```text
스킬은 AI가 특정 작업을 일관되게 수행하도록 돕는 재사용 가능한 작업 지침입니다.
이번 과제에는 raster 이미지를 생성하는 imagegen 스킬을 사용합니다.
```

## 3. 작업 기준 확정

### User

```text
과제를 단계별로 수행하고 검증받고 진행해줘.
작업 경로는 /Users/hapyjin_macbook/happyjin/study-ai/hyunjin 이다.
```

### Codex

```text
week1/hyunjin 브랜치와 hyunjin/week1/ 작업 폴더를 만들고,
README 원문을 기준으로 이미지 내용을 검증하는 흐름으로 진행합니다.
```

## 4. README 정보 추출

### User

```text
README에서 추출한 자기소개 정보가 맞아.
```

### Codex

```text
이미지에 김현진, 25살 여자, 인프라 엔지니어, ENFP, 보라색·노란색,
스터디 목적, 취미, 음식, 애착 캐릭터, 이모티콘을 모두 반영합니다.
```

## 5. 디자인 결정

### User

```text
진행해.
```

### Codex

```text
보라색·노란색 중심의 포근한 프로필 인포그래픽으로 제작합니다.
이미지 생성 모델의 한글 오탈자를 피하기 위해, 배경은 AI로 생성하고
README 원문 텍스트는 정확하게 합성합니다.
```

## 6. imagegen에 제출한 프롬프트

### Codex → imagegen

```text
Use case: infographic-diagram
Asset type: square background illustration for a Korean personal profile infographic
Primary request: Create a polished, cozy background illustration with generous quiet areas for later text overlays. It should feel like a warm personal introduction for an adult infrastructure engineer who balances focused work and enjoyable rest.
Scene/backdrop: a cozy room-and-cafe inspired workspace, with a tidy desk, a warm drink, soft lamp glow, subtle house-interior decor, and very small abstract cloud/server/network motifs.
Subject: no person; add only a few original, generic cute round decorative mascots. They must not resemble any existing copyrighted character.
Style/medium: clean modern flat editorial illustration, refined and friendly rather than childlike.
Composition/framing: square composition; a clear header area at top, a centered feature area, and four calm readable zones in the lower half. Keep the center and section areas uncluttered for Korean text to be added later.
Lighting/mood: warm, soft, comforting, optimistic.
Color palette: purple and yellow as the dominant colors, with cream and soft gray accents.
Text (verbatim): no text at all; leave all text areas blank.
Constraints: original artwork only; visual hierarchy suitable for a profile infographic; no person; no readable letters, numbers, logos, or watermark.
Avoid: character lookalikes, copied franchise elements, dense clutter, dark mood, photorealism.
```

### imagegen 응답

```text
보라색·노란색의 아늑한 작업 공간, 서버·클라우드 장식, 네 개의 텍스트 영역을
갖춘 배경 일러스트를 생성했습니다.
```

## 7. 최종 이미지 합성

### Codex

```text
생성 배경에 README 원문을 합성해 profile.png를 만들었습니다.
한글과 이모지는 AppleSDGothicNeo 및 Apple Color Emoji 글꼴로 렌더링했습니다.
```

## 8. 검증 결과

| README 항목 | profile.png 검증 |
| --- | --- |
| 이름, 나이, 성별, 직업, MBTI, 좋아하는 색 | 일치 |
| 열심히 일하고 열심히 놀기 🙌 | 일치 |
| 스터디 참여 목적 | 일치 |
| 취미 | 일치 |
| 좋아하는 음식의 식당·메뉴·후기 | 일치 |
| 양파쿵야·별의 커비와 이유 | 일치 |
| `:)`, `ㅡㅡ`, `><` | 일치 |
| 이모지 + 텍스트 스타일 문구 | 일치 |

## 9. 산출물

- [profile.html](./profile.html): 이미지 미리보기와 내용 확인용 HTML
- [profile.png](./profile.png): 최종 제출 이미지
