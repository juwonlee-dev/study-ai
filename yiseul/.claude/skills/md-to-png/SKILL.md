---
name: md-to-png
description: Markdown(.md, README, 자기소개/프로필 문서 등)을 GitHub에서 보이는 모습 그대로 PNG 이미지로 변환하고, 헤딩·리스트·뱃지 이미지·링크·구분선·모든 텍스트가 이미지에 빠짐없이 들어갔는지 자동 검증한다. 사용자가 "md를 이미지로", "README를 png로", "마크다운 캡처/스크린샷", "프로필 이미지로 만들어줘", "shields.io 뱃지까지 이미지로" 등을 요청하거나, md 문서를 공유용 그림 파일로 바꾸려 할 때 반드시 이 스킬을 사용할 것. 변환 결과의 누락 여부 확인 요청에도 사용.
---

# md-to-png

Markdown 파일을 GitHub 스타일(`github-markdown-css` + `marked`)로 렌더링하고 로컬 Chrome/Edge headless 모드로 전체 페이지를 캡처한다.
README처럼 `<p align="center">`, `<img>` 뱃지 같은 HTML이 섞인 문서도 실제 브라우저로 렌더하므로 GitHub에서 보이는 정렬·뱃지가 그대로 나온다.

## 요구 사항
- Python 3.10+ (표준 라이브러리만 사용)
- Chrome 또는 Edge 설치 (자동 탐지, 없으면 `--browser` 로 경로 지정)
- 인터넷 연결: jsdelivr(marked, CSS)와 뱃지 이미지(shields.io 등)를 렌더 시점에 불러오기 때문

## 사용 절차

1. **변환**
   ```bash
   python <skill-dir>/scripts/md_to_png.py <input.md> <output.png> [--width 900] [--scale 2]
   ```
   - `--width`: 페이지 폭(CSS px). GitHub README 본문 폭과 비슷한 900이 기본값.
   - `--scale`: 해상도 배율. 2면 선명한 레티나급 이미지(폭 1800px).
   - 출력 JSON의 `failedImages`가 비어 있지 않으면 뱃지 URL/네트워크를 먼저 확인한다.

2. **자동 검증** — 변환과 같은 `--width/--scale` 값을 넘긴다.
   ```bash
   python <skill-dir>/scripts/verify.py <input.md> <output.png> [--width 900] [--scale 2]
   ```
   md 원문에서 기대 요소를 뽑아 렌더된 DOM과 대조한다:
   헤딩(태그+텍스트), 리스트 항목, 이미지 src 전부 포함 + 로딩 성공, 링크 href, 구분선 개수,
   모든 텍스트 라인 포함 여부, PNG 크기 = 렌더 페이지 전체 크기(하단 잘림 방지).
   하나라도 실패하면 exit code 1과 함께 누락 항목을 출력한다.

3. **시각 검증** — 생성된 PNG를 직접 열어(Read 도구) 확인한다. 자동 검증은 "DOM에 있다"까지만 보장하므로,
   한글/이모지 폰트 깨짐, 뱃지가 텍스트 대신 깨진 아이콘으로 보이는지, 정렬이 원본 의도와 맞는지는 눈으로 본다.
   이미지가 크면 섹션별로 나눠 확인한다.

4. 사용자에게 검증 결과를 체크리스트(항목 / 기대 / 결과) 표로 보고한다.

## 문제 해결
- `렌더링 결과를 읽지 못했습니다`: CDN 접근 불가. 네트워크/프록시 확인.
- 이미지 로딩 실패: 뱃지 URL 오타, 사내망 차단 여부 확인. 실패 목록은 두 스크립트 모두 출력한다.
- `⚠️ 마크다운 기호가 그대로 표시됨` 경고: 텍스트는 들어갔지만 원본의 `**굵게**` 등이 문법상 해석되지 않은 경우다
  (예: `**TA(...)**를` 처럼 닫는 `**` 앞이 문장부호이고 뒤에 한글이 바로 붙으면 CommonMark/GitHub 모두 굵게 처리하지 않음).
  이미지는 GitHub와 동일하게 나온 것이므로 실패로 치지 않는다. 사용자에게 알리고, 원하면 원본을 `<b>TA(...)</b>를` 로 고치도록 제안한다.
- 이모지가 네모로 보임: OS에 컬러 이모지 폰트가 없는 경우. Windows는 Segoe UI Emoji, macOS는 Apple Color Emoji를 사용한다.
