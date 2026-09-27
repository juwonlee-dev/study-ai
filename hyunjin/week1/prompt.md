# Week 1 프롬프트 로그

> 상태: **완료**

## 사용 AI·스킬

- AI: ChatGPT/Codex
- 스킬: `imagegen`
- 사용 목적: 자기소개 프로필 이미지의 배경 일러스트를 생성한다. 한국어 자기소개 텍스트는 생성 모델의 오탈자를 피하기 위해 README 원문과 대조 가능한 별도 레이아웃으로 정확히 합성한다.

## 실제 제출 프롬프트

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

## AI 응답 결과

- 생성 결과: [background.png](./background.png)
- 최종 합성 이미지: [profile.png](./profile.png)
- 응답 요약: 보라색·노란색 기반의 포근한 작업 공간 배경과 텍스트 배치 영역을 생성함.

## 텍스트 합성 및 검증

README와 [profile.png](./profile.png)를 대조했다.

| README 항목 | 결과 |
| --- | --- |
| 이름, 나이, 성별, 직업, MBTI, 좋아하는 색 | 일치 |
| “열심히 일하고 열심히 놀기 🙌” | 일치 |
| 스터디 참여 목적 | 일치 |
| 취미 | 일치 |
| 좋아하는 음식의 식당·메뉴·후기 | 일치 |
| 양파쿵야·별의 커비, 이유 | 일치 |
| `:)`, `ㅡㅡ`, `><` | 일치 |
| 이모지 + 텍스트 스타일 문구 | 일치 |
