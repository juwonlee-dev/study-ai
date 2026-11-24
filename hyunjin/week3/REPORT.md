# KurbyPdf 보안 취약점 분석 보고서

- **분석 대상:** [juwonlee-dev/KurbyPdf](https://github.com/juwonlee-dev/KurbyPdf)
- **분석 기준 커밋:** `74d3aed` (master, 2025-09-22)
- **분석 도구:** Claude Code (Claude Opus 4.8) — `hyunjin/CLAUDE.md` 지침 사용
- **검증 환경:** Temurin JDK 17로 `--release 8` 컴파일, 실제 의존성(PDFBox 2.0.30 / Jackson 2.17.1, Maven Central JAR을 SHA-1 대조)으로 PoC 실행
- **대상 라이브러리 요약:** PDF에 보이지 않는 워터마크(클레임 + 타임스탬프 + nonce)를 삽입하고, HMAC-SHA256 서명 후 AES-GCM으로 암호화해 숨긴다. 검증 시 추출·복호·서명 확인을 수행한다.

> ⚠️ 모든 PoC와 패치 사본은 저장소 밖 임시 폴더에서만 빌드·실행했으며 저장소에 커밋하지 않았습니다. 재현에 사용한 키는 테스트 고정값(`0x11…`, `0x22…`)입니다.

---

## 1. 위험도별 탐지 통계

| 위험도 | 건수 | 취약점 ID |
| --- | --- | --- |
| 🔴 Critical (치명) | 1 | V-01 |
| 🟠 High (높음) | 3 | V-02, V-03, V-04 |
| 🟡 Medium (중간) | 4 | V-05, V-06, V-07, V-08 |
| 🟢 Low (낮음) | 3 | V-09, V-10, V-11 |
| ⚪ Info (정보) | 2 | V-12, V-13 |
| **합계** | **13** | |

```
Critical ■                     1
High     ■■■                   3
Medium   ■■■■                  4
Low      ■■■                   3
Info     ■■                    2
```

**위험도 기준**

- **Critical:** 라이브러리의 핵심 보안 목적(워터마크 위변조 검출)을 공격자가 키 없이 무력화함
- **High:** 키 없이 또는 정당한 수신자가 라이브러리의 보증을 우회·위조함
- **Medium:** 가용성 훼손, 또는 설계상 신뢰 경계가 문서와 다름
- **Low:** 입력 검증 미흡 등 안전 강화를 위해 고쳐야 할 결함
- **Info:** 직접적 악용은 어렵지만 알아 두어야 할 의존성·관행

---

## 2. 핵심 원인 한눈에 보기

이 라이브러리의 서명 대상(`WatermarkPayload.buildPayload`, `PdfForensicEmbedder.java`, `PdfWatermarkInspector.decryptAndVerify`)은 **PDF 문서 내용과 전혀 연결돼 있지 않습니다.** HMAC은 `{v, claims, ts, nonce}`에만 걸리고, 이 페이로드는 PDF의 어떤 바이트와도 묶이지 않습니다. 그 결과:

- 문서를 바꿔도 서명은 그대로 유효합니다 (V-02).
- 워터마크를 통째로 다른 문서에 복사해도 유효합니다 (V-03).
- 검증은 "첫 번째로 발견한 워터마크 1개"만 보므로, 공격자가 가짜/남의 워터마크를 앞에 끼워 넣어 결과를 조작할 수 있습니다 (V-01, V-04).

대칭키(HMAC) 구조라 **검증할 수 있는 주체는 위조도 할 수 있습니다** (V-05). 이 세 가지가 보고서의 중심 결함입니다.

---

## 3. 취약점 상세

### V-01 🔴 가짜 워터마크 하나로 검증 전체를 실패시킴 (안티 포렌식 DoS)

- **위치:** `PdfWatermarkInspector.extractFirst` → `extractAll`(getList.get(0)) 및 `decryptAndVerify` (`PdfWatermarkInspector.java:31-34, 96-105`), `PdfVerificationUtil.verifyDetailed:53-55`
- **설명:** `extractAll`은 페이지의 XObject를 순회하며 워터마크를 모읍니다. `extractFirst`는 그중 **첫 번째 하나**만 복호·검증합니다. 그런데 복호 단계(`c.doFinal(ct)`)에서 AES-GCM 태그가 맞지 않으면 `AEADBadTagException`이 던져지고, `verifyDetailed`는 이를 `EXCEPTION:…`으로 잡아 **전체를 실패** 처리합니다. 즉 공격자가 복호 불가능한 쓰레기 스트림을 가진 가짜 워터마크 하나를 문서 앞쪽에 끼워 넣으면, 뒤에 있는 진짜 워터마크를 보기도 전에 검증이 실패합니다.
- **재현(S4):** 진짜 워터마크가 있는 문서(`valid=true`)에 64바이트 랜덤 페이로드를 가진 FormXObject를 페이지 리소스 맨 앞에 삽입.
  ```
  before: valid=true  reason=null  claims={uid=alice}
  after : valid=false reason=EXCEPTION:AEADBadTagException claims={}
  ```
- **영향:** 유출자가 자기 문서의 워터마크를 "무력화"할 수 있습니다. 워터마크가 멀쩡히 들어 있는데도 검증 시스템은 "검증 실패/워터마크 없음"으로 판단하므로, 추적 기능 자체가 쓸모없어집니다. 키가 전혀 필요 없습니다.
- **조치 방안(현재 소스 기준):**
  1. **첫 번째가 아니라 전부를 검증**합니다. `verifyDetailed`가 `extractAll`을 호출해, 하나라도 서명이 유효하면 성공으로 처리합니다.
  2. 개별 워터마크의 복호 실패를 "그 워터마크만 무시"로 바꿉니다. `decryptAndVerify`가 예외를 던지는 대신 `signatureValid=false`인 결과를 반환하거나, `extractAll`이 복호 실패 스트림을 건너뛰도록 합니다.
  - 상세 코드는 §6 패치 참조.

### V-02 🟠 문서 내용 변조 후에도 워터마크가 유효 (무결성 미보장)

- **위치:** `WatermarkPayload.buildPayload:26-38` (서명 대상에 문서 바이트 없음)
- **설명:** HMAC 서명은 `{v, claims, ts, nonce}`에만 걸립니다. 문서의 페이지·텍스트·해시 어느 것도 서명에 포함되지 않습니다.
- **재현(S1):** 워터마크된 문서에 새 페이지("TAMPERED PAGE")를 추가하고 1쪽을 90도 회전.
  ```
  pages: 2 -> 3
  valid=true reason=null claims={uid=alice}
  ```
- **영향:** README는 "위변조 검출"을 장점으로 내세우지만, 실제로는 **문서가 바뀌어도 검출하지 못합니다.** 워터마크는 "이 클레임이 서명됐다"만 증명할 뿐, "이 문서가 그 클레임과 함께 서명됐다"를 증명하지 못합니다.
- **조치 방안(현재 소스 기준):** 삽입 시점에 **문서 내용 다이제스트**를 클레임에 포함시켜 서명 대상에 넣습니다. 예: `PDFTextStripper`로 추출한 텍스트 또는 페이지 수·MediaBox 등 구조 정보를 SHA-256 해시해 `docDigest` 클레임으로 넣고, 검증 시 현재 문서에서 같은 다이제스트를 계산해 대조합니다. (완전한 바이트 단위 무결성은 PDF 증분 저장 특성상 어려우므로, 텍스트+구조 다이제스트가 현실적 절충입니다. §6에 텍스트 다이제스트 방식 예시.)

### V-03 🟠 워터마크를 다른 문서로 이식해도 유효 (바인딩 부재)

- **위치:** `PdfForensicEmbedder.embed` + `WatermarkPayload`(문서와 무관한 페이로드), `PdfWatermarkInspector.java:55-67`
- **설명:** 암호화된 페이로드 바이트는 그 자체로 완결적입니다. 어떤 문서에 들어 있든 복호·서명 검증이 통과합니다.
- **재현(S2):** 워터마크된 문서에서 `_k1` 스트림 바이트(162B)를 그대로 읽어, 내용이 전혀 다른 새 PDF에 `PdfForensicEmbedder.embed`로 붙임. 키는 사용하지 않음.
  ```
  payload bytes copied = 162 (keys not used)
  valid=true reason=null claims={uid=alice}
  ```
- **영향:** 한 번 발급된 워터마크를 임의의 문서에 복사해 "정품"으로 위장할 수 있습니다. 배포 추적·정품 증명 용도가 무너집니다.
- **조치 방안:** V-02와 동일 축(문서 바인딩). 페이로드에 문서 다이제스트를 포함하면, 다른 문서로 옮긴 워터마크는 다이제스트 불일치로 거부됩니다.

### V-04 🟠 타인의 워터마크를 끼워 넣어 누명 씌우기

- **위치:** V-01과 동일 경로(첫 워터마크만 신뢰) + V-03(이식 가능)
- **설명:** `extractFirst`가 **문서에서 먼저 나오는 워터마크 1개**를 그 문서의 결론으로 삼습니다. 공격자가 다른 사용자(bob)의 유효한 워터마크를 피해자(alice) 문서 앞에 끼워 넣으면, 검증은 그 문서를 bob이 유출한 것으로 판정합니다.
- **재현(S5):** alice 워터마크 문서에 bob의 유효 페이로드를 1쪽 리소스 맨 앞에 삽입.
  ```
  alice가 유출한 문서 검증 결과: valid=true reason=null claims={uid=bob}
  ```
- **영향:** 배포 추적의 책임 귀속(attribution)을 조작할 수 있습니다. 무고한 사용자에게 유출 책임을 전가할 수 있습니다.
- **조치 방안:** V-01 조치(전수 검증)로 "첫 1개만 신뢰"는 사라지지만, 여전히 여러 유효 워터마크가 공존하는 모호성은 남습니다. 근본 해결은 V-02/V-03의 문서 바인딩입니다. 바인딩이 있으면 다른 문서에서 떼어 온 워터마크는 다이제스트 불일치로 무효가 됩니다. 추가로, 검증 결과에 **유효 워터마크 목록 전체**를 반환해 단일 결론을 강요하지 않도록 합니다(§6 `verifyAll`).

### V-05 🟡 대칭키 구조 — 검증자가 곧 위조자

- **위치:** `WatermarkPayload.buildPayload:36-38`, `PdfWatermarkInspector.decryptAndVerify:130-136`
- **설명:** 삽입과 검증이 **같은 HMAC 키·AES 키**를 씁니다. 검증을 하려면 이 키들을 가져야 하는데, 키를 가진 쪽은 임의 클레임으로 새 워터마크를 만들 수 있습니다.
- **재현(S3):** 검증용 키(HMAC/AES)만으로 `uid=victim-bob` 워터마크를 신규 생성 → 검증 통과.
  ```
  valid=true reason=null claims={uid=victim-bob}
  ```
- **영향:** 검증 권한을 가진 모든 주체(예: 배포망의 여러 검증 노드)가 임의 사용자 명의의 워터마크를 위조할 수 있습니다. 법적 증거로서의 가치가 없습니다.
- **조치 방안:** 부인방지가 필요하면 대칭 HMAC 대신 **비대칭 서명**(Ed25519/ECDSA)으로 바꿉니다. 삽입자만 개인키를 갖고, 검증자는 공개키만 가집니다. 당장 구조를 못 바꾼다면, 최소한 README에 "검증 키 보유자는 위조가 가능하다"는 신뢰 모델을 명시하고 키 배포 범위를 삽입 주체로 제한해야 합니다.

### V-06 🟡 검증 시 압축 폭탄으로 메모리 고갈 (DoS)

- **위치:** `PdfWatermarkInspector.streamToBytes:80-94` (`createInputStream()`이 필터 전체 복원), 간접적으로 `PDDocument.load`
- **설명:** `_k1` 스트림을 읽을 때 `COSStream.createInputStream()`은 FlateDecode를 끝까지 풀어 메모리로 올립니다. 공격자가 작은 바이트가 거대하게 부풀도록 만든 스트림(압축 폭탄)을 넣으면 `OutOfMemoryError`가 발생합니다.
- **재현(S8):** 1,044,528바이트(약 1MB) PDF, `_k1` FlateDecode 스트림이 1GiB로 팽창. 힙을 256MiB로 제한하고 `verifyDetailed` 호출.
  ```
  maxHeap=256 MiB, input=1044528 bytes
  Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
  ```
  예외 발생 지점(JVM exception 로그): `org.apache.pdfbox.filter.FlateFilter.decompress`. **이 `OutOfMemoryError`는 `verifyDetailed`의 `catch (Exception e)`로도 잡히지 않고(`Error`는 `Exception`이 아님) 호출자 밖으로 던져집니다.**
- **영향:** 검증 서버에 악성 PDF 하나를 보내는 것만으로 프로세스를 다운시킬 수 있습니다. 키가 필요 없습니다.
- **조치 방안(현재 소스 기준):**
  1. **핵심:** 단순히 `streamToBytes`의 복사 루프에 상한을 거는 것으로는 막히지 않습니다. PDFBox의 `COSStream.createInputStream()`은 **스트림을 돌려주기 전에 FlateDecode를 끝까지 메모리로 풀기 때문에**, 복사 루프가 돌기도 전에 이미 OOM이 납니다(아래 재검증에서 실제로 확인). 따라서 `createRawInputStream()`으로 **압축된 원시 바이트를 먼저 상한 내에서 읽고**, 출력 상한을 둔 `java.util.zip.Inflater`로 **직접 해제**해야 합니다. 상한을 넘으면 그 워터마크만 건너뜁니다(정상 페이로드는 수백 바이트라 영향 없음).
  2. `verifyDetailed`의 `catch`를 `catch (Throwable t)`로 넓혀 혹시 남는 `Error`도 안전하게 실패로 처리합니다.
  - §6 패치 참조.

### V-07 🟡 사용자 암호만으로 워터마크·암호화 모두 제거 가능

- **위치:** `PdfProtector.applyUserPassword:9-16`, `KurbyPdf.watermark:40`
- **설명:** PDF 표준 암호화에서 **사용자 암호로 문서를 열면 수정·조립 권한이 따라옵니다.** 코드가 막는 것은 `setCanExtractContent(false)`뿐입니다. 사용자 암호를 받은 수신자는 문서를 열어 `_k1` 참조를 지우고 `setAllSecurityToBeRemoved(true)`로 암호화까지 벗길 수 있습니다.
- **재현(S6):** 사용자 암호로 문서 열기 → 권한 확인 → `_k1` 6개 제거 → 보안 해제 후 저장.
  ```
  opened with user pw: isOwner=false canModify=true canAssemble=true canExtract=false
  removed _k1 refs=6, re-opened without password: encrypted=false pages=2
  valid=false reason=WATERMARK_NOT_FOUND claims={}
  ```
- **영향:** 정당한 열람 권한만 가진 수신자가 워터마크를 손쉽게 제거해 추적을 회피합니다.
- **조치 방안:** PDF 권한 비트는 호환 뷰어에서만 강제되고 라이브러리 수준에서는 우회가 쉽다는 한계를 인정해야 합니다. 완화책으로 (a) 워터마크를 문서 여러 곳에 중복·분산 삽입(이미 다중 삽입하나 모두 같은 `_k1` 키라 일괄 제거됨 → 키 이름을 난독화·분산), (b) 콘텐츠 스트림에 섞어 제거를 어렵게, (c) 핵심은 제거 자체를 막기보다 **제거되면 "원본 아님"으로 판정**되도록 V-02 문서 바인딩과 결합하는 것입니다. README의 "강력한 DRM 대체 아님" 주의와 일관되게, 한계를 문서화합니다.

### V-08 🟡 `extractAll`의 워터마크 개수·크기 상한 부재 (자원 소모)

- **위치:** `PdfWatermarkInspector.extractAll:51-72`
- **설명:** 페이지·XObject 수에 제한이 없어, 워터마크처럼 생긴 FormXObject를 수천 개 넣은 PDF는 검증 시 과도한 반복·메모리를 유발합니다. V-06과 결합하면 증폭됩니다.
- **재현:** 코드 경로 분석 기반(별도 대량 PoC는 생략). `extractAll`은 `seen` 집합에 모든 스트림을 보관하며 무제한 순회합니다.
- **영향:** 중간 규모의 자원 소모 DoS.
- **조치 방안:** 검사하는 워터마크 후보 수에 상한(예: 64개)을 두고 초과 시 중단합니다. `extractFirst`를 쓰는 검증 경로는 유효 워터마크 1개를 찾으면 조기 종료합니다.

### V-09 🟢 키 길이·형식 검증 없음

- **위치:** `WatermarkPayload.buildPayload:36-55`, `KurbyPdf.watermark:24-25`
- **설명:** HMAC/AES 키 길이를 검사하지 않습니다. 1바이트 HMAC 키, 16/24/32가 아닌 AES 키 등 약한/잘못된 키를 그대로 사용합니다. AES 키가 규격 외면 런타임 예외로 이어지고, 짧은 HMAC 키는 보안 강도를 떨어뜨립니다.
- **재현(S7):** 1바이트 HMAC 키로 삽입·검증 → 성공.
  ```
  watermark with 1-byte HMAC key: true
  ```
- **영향:** 호출자의 실수로 보안 강도가 조용히 약해집니다.
- **조치 방안:** `buildPayload`/`watermark` 진입부에서 `hmacKey.length >= 32`, `aesKey.length ∈ {16,24,32}`를 검사하고 위반 시 `IllegalArgumentException`을 던집니다(§6).

### V-10 🟢 IV/페이로드 바이트의 입력 검증 미흡 (복호 경로)

- **위치:** `PdfWatermarkInspector.decryptAndVerify:96-105`
- **설명:** `blob.length < IV_LEN + 1`만 확인하고 복호에 들어갑니다. 손상된 스트림은 다양한 예외를 던지는데, 이것이 V-01처럼 전체 실패로 번집니다. 각 워터마크 단위로 실패를 격리해야 합니다.
- **영향:** V-01/V-06과 함께 안티포렌식·DoS를 쉽게 만드는 보조 요인.
- **조치 방안:** 워터마크별 try/catch로 복호·검증 실패를 "그 항목 무효"로 국한합니다(§6, V-01 조치에 포함).

### V-11 🟢 `sig` Base64 디코딩 예외 미처리

- **위치:** `PdfWatermarkInspector.decryptAndVerify:134-135`
- **설명:** `Base64.getDecoder().decode(sigB64)`는 `sig`가 잘못된 Base64면 `IllegalArgumentException`을 던집니다. 복호가 성공한(=AES 키를 아는) 경우에만 도달하므로 위험도는 낮지만, 예외가 상위로 전파돼 "검증 실패" 대신 "예외"로 표시됩니다.
- **영향:** 낮음(키를 알아야 도달).
- **조치 방안:** `sig` 디코딩을 try/catch로 감싸 실패 시 `signatureValid=false`로 처리합니다.

### V-12 ⚪ 의존성: jackson-databind 2.17.1 공개 권고 다수

- **위치:** `build.gradle.kts:28`
- **설명:** OSV.dev 조회 결과 `com.fasterxml.jackson.core:jackson-databind:2.17.1`에 공개 권고 **12건**이 존재합니다(예: `GHSA-q4xh-88c3-wmh7` Duration 파싱 DoS, `GHSA-hgj6-7826-r7m5`/`GHSA-vvgp-rfg2-7rr6` 역직렬화 시 eager DNS/SSRF, 다수의 PolymorphicTypeValidator 우회).
- **악용 가능성(중요):** 이 라이브러리는 **다형성 역직렬화(`enableDefaultTyping`/`@JsonTypeInfo`)를 쓰지 않고**, `OM.readTree(json)`로 **자신이 AES-GCM으로 암호화해 둔** JSON만 파싱합니다. 따라서 폴리모픽 타입 우회 계열 권고는 현재 코드에서 직접 악용되기 어렵습니다. 다만 Duration/숫자 파싱 DoS 계열은 복호에 성공한 입력에 한해 이론적 여지가 있고, 무엇보다 **의존성 위생** 차원에서 업데이트가 권장됩니다.
- **조치 방안:** jackson-databind를 2.17.x 최신 패치 또는 2.18.x 안정 버전으로 올립니다. 또는 이 라이브러리는 단순 고정 스키마 JSON만 다루므로, Jackson 의존을 제거하고 수동 직렬화로 대체하는 것도 선택지입니다(의존성 표면 축소).

### V-13 ⚪ PDFBox 버전 고정 및 삭제 예외 처리 관행

- **위치:** `build.gradle.kts:27`, 전반의 `catch (Exception ignore) {}`
- **설명:** PDFBox 2.0.30은 OSV 기준 현재 알려진 직접 권고는 없으나, 2.0.x 계열은 유지보수 종료가 다가오는 라인입니다(향후 3.x 이전 권장). 또한 코드 곳곳의 `catch (Exception ignore) {}`는 리소스 종료 실패 등을 조용히 삼켜, 운영 중 문제 진단을 어렵게 합니다.
- **영향:** 정보성. 장기 유지보수·관측성 관점의 지적.
- **조치 방안:** 의존성 정기 점검(OSV/Dependabot) 체계를 두고, 무시하는 예외는 최소한 디버그 로깅을 남깁니다.

---

## 4. 요약 매핑 (원인 ↔ 취약점)

| 근본 원인 | 연결된 취약점 |
| --- | --- |
| 서명이 문서 내용과 바인딩되지 않음 | V-02, V-03, V-04 |
| 검증이 "첫 워터마크 1개"만 신뢰 + 실패 격리 없음 | V-01, V-04, V-10, V-11 |
| 대칭키(검증=위조) | V-05 |
| 자원 상한 부재 | V-06, V-08 |
| 입력·키 검증 부재 | V-09, V-10 |
| 권한 모델 한계 | V-07 |
| 의존성/관행 | V-12, V-13 |

---

## 5. 우선순위 권고

1. **즉시(High+):** V-01/V-06 — 검증 경로를 "전수 검증 + 실패 격리 + `Throwable` 처리 + 스트림 크기 상한"으로 바꿉니다. 코드 변경이 작고 효과가 큽니다(§6 패치로 S4·S8 PoC가 방어됨).
2. **단기:** V-02/V-03/V-04 — 문서 다이제스트 바인딩을 도입합니다. 라이브러리의 핵심 가치를 되살립니다.
3. **구조적:** V-05 — 부인방지가 요건이면 비대칭 서명으로 전환합니다.
4. **위생:** V-09/V-12 — 키 검증 추가, Jackson 업데이트.

---

## 6. 조치 코드(현재 소스 기준 diff)와 재검증

아래 패치는 검증 경로의 High/Medium 항목(V-01, V-06, V-08, V-10, V-11)을 한 번에 처리합니다. 원본 사본에 적용해 PoC를 다시 실행했습니다.

<details>
<summary>패치 1 — PdfWatermarkInspector: 전수 검증 + 실패 격리 + 직접 해제 상한</summary>

```diff
--- a/src/main/java/io/github/juwonlee/kurbypdf/PdfWatermarkInspector.java
+++ b/src/main/java/io/github/juwonlee/kurbypdf/PdfWatermarkInspector.java
@@
-import org.apache.pdfbox.cos.COSName;
+import org.apache.pdfbox.cos.COSArray;
+import org.apache.pdfbox.cos.COSBase;
+import org.apache.pdfbox.cos.COSName;
 import org.apache.pdfbox.cos.COSStream;
@@
-import java.io.ByteArrayInputStream;
 import java.io.ByteArrayOutputStream;
+import java.io.IOException;
 import java.io.InputStream;
@@
     private static final COSName WM_KEY = COSName.getPDFName("_k1");
     private static final int IV_LEN = 12;
+    // 정상 워터마크 페이로드는 수백 바이트. 압축 폭탄 방어용 상한.
+    private static final int MAX_PAYLOAD_BYTES = 1 << 20;   // 1 MiB
+    private static final int MAX_WATERMARKS = 64;           // 과도 순회 방지
@@
     public static DecodedWatermark extractFirst(byte[] pdf, byte[] hmacKey, byte[] aesKey, String password) throws Exception {
         List<DecodedWatermark> list = extractAll(pdf, hmacKey, aesKey, password);
-        return list.isEmpty() ? null : list.get(0);
+        // 유효한 워터마크를 우선 반환(V-01/V-04). 유효한 것이 없으면 첫 항목(또는 null).
+        for (DecodedWatermark dw : list) if (dw.isSignatureValid()) return dw;
+        return list.isEmpty() ? null : list.get(0);
     }
@@
                 for (COSName name : res.getXObjectNames()) {
+                    if (out.size() >= MAX_WATERMARKS) break;
                     PDXObject xo = res.getXObject(name);
                     if (xo instanceof PDFormXObject) {
                         PDFormXObject form = (PDFormXObject) xo;
                         Object wm = form.getCOSObject().getDictionaryObject(WM_KEY);
                         if (wm instanceof COSStream) {
                             COSStream stream = (COSStream) wm;
                             if (!seen.contains(stream)) {
                                 seen.add(stream);
-                                byte[] enc = streamToBytes(stream);
-                                DecodedWatermark rec = decryptAndVerify(enc, hmacKey, aesKey);
-                                out.add(rec);
+                                // 개별 워터마크 실패를 격리(V-01/V-10/V-11): 한 개가 깨져도
+                                // 전체 검증을 실패시키지 않는다.
+                                try {
+                                    byte[] enc = streamToBytes(stream);     // 상한 초과 시 예외
+                                    out.add(decryptAndVerify(enc, hmacKey, aesKey));
+                                } catch (Exception perItem) {
+                                    // 깨졌거나 폭탄인 항목은 "무효 워터마크"로 간주하고 건너뜀
+                                }
                             }
                         }
                     }
                 }
@@
-    private static byte[] streamToBytes(COSStream s) throws Exception {
-        InputStream in = null;
-        try {
-            in = s.createInputStream();
-            byte[] buf = new byte[8192];
-            int r;
-            ByteArrayOutputStream bout = new ByteArrayOutputStream();
-            while ((r = in.read(buf)) != -1) {
-                bout.write(buf, 0, r);
-            }
-            return bout.toByteArray();
-        } finally {
-            if (in != null) try { in.close(); } catch (Exception ignore) {}
-        }
-    }
+    private static byte[] streamToBytes(COSStream s) throws Exception {
+        // createInputStream()은 상한을 적용하기 전에 스트림 전체를 메모리로 풀어
+        // 압축 폭탄에서 OOM이 난다(V-06). 그래서 원시 바이트를 직접 읽고,
+        // 출력 상한을 둔 Inflater로 직접 해제한다.
+        COSBase filterObj = s.getFilters();
+        boolean flate = false;
+        if (filterObj instanceof COSName) {
+            flate = COSName.FLATE_DECODE.equals(filterObj);
+        } else if (filterObj instanceof COSArray) {
+            COSArray arr = (COSArray) filterObj;
+            if (arr.size() > 1) {
+                throw new IOException("unsupported filter chain for watermark stream");
+            }
+            flate = arr.size() == 1 && COSName.FLATE_DECODE.equals(arr.get(0));
+        }
+
+        InputStream raw = null;
+        try {
+            raw = s.createRawInputStream();
+            // 1) 원시(압축) 바이트를 상한 내에서 읽는다.
+            ByteArrayOutputStream rawBuf = new ByteArrayOutputStream();
+            byte[] buf = new byte[8192];
+            int r;
+            while ((r = raw.read(buf)) != -1) {
+                if (rawBuf.size() + r > MAX_PAYLOAD_BYTES) {
+                    throw new IOException("raw watermark stream exceeds " + MAX_PAYLOAD_BYTES + " bytes");
+                }
+                rawBuf.write(buf, 0, r);
+            }
+            byte[] rawBytes = rawBuf.toByteArray();
+            if (!flate) return rawBytes;   // 필터 없음: 그대로 사용
+            // 2) 출력 상한을 둔 Inflater로 직접 해제 → 폭탄이면 상한에서 중단
+            java.util.zip.Inflater inf = new java.util.zip.Inflater();
+            try {
+                inf.setInput(rawBytes);
+                ByteArrayOutputStream out = new ByteArrayOutputStream();
+                byte[] ob = new byte[8192];
+                while (!inf.finished()) {
+                    int n = inf.inflate(ob);
+                    if (n == 0) {
+                        if (inf.finished() || inf.needsDictionary() || inf.needsInput()) break;
+                    }
+                    if (out.size() + n > MAX_PAYLOAD_BYTES) {
+                        throw new IOException("inflated payload exceeds " + MAX_PAYLOAD_BYTES + " bytes");
+                    }
+                    out.write(ob, 0, n);
+                }
+                return out.toByteArray();
+            } finally {
+                inf.end();
+            }
+        } finally {
+            if (raw != null) try { raw.close(); } catch (Exception ignore) {}
+        }
+    }
```
</details>

<details>
<summary>패치 2 — PdfVerificationUtil: Error까지 안전 처리</summary>

```diff
--- a/src/main/java/io/github/juwonlee/kurbypdf/util/PdfVerificationUtil.java
+++ b/src/main/java/io/github/juwonlee/kurbypdf/util/PdfVerificationUtil.java
@@
-        } catch (Exception e) {
-            return Result.fail("EXCEPTION:" + e.getClass().getSimpleName());
+        } catch (Throwable e) {   // OutOfMemoryError 등 Error도 실패로 격리(V-06)
+            return Result.fail("EXCEPTION:" + e.getClass().getSimpleName());
         }
```
</details>

<details>
<summary>패치 3 — WatermarkPayload: 키 길이 검증(V-09)</summary>

```diff
--- a/src/main/java/io/github/juwonlee/kurbypdf/WatermarkPayload.java
+++ b/src/main/java/io/github/juwonlee/kurbypdf/WatermarkPayload.java
@@
     public static byte[] buildPayload(Map<String, String> claimsIn, byte[] hmacKey, byte[] aesKey) throws Exception {
+        if (hmacKey == null || hmacKey.length < 32)
+            throw new IllegalArgumentException("hmacKey must be >= 32 bytes");
+        if (aesKey == null || (aesKey.length != 16 && aesKey.length != 24 && aesKey.length != 32))
+            throw new IllegalArgumentException("aesKey must be 16/24/32 bytes");
```
</details>

**재검증 결과 (패치 적용 사본에서 동일 PoC 실행):**

| 시나리오 | 패치 전 | 패치 후 |
| --- | --- | --- |
| S0 정상 삽입·검증 | `valid=true` | `valid=true` (유지) |
| 원본 테스트(`KurbyPdfTest.testWatermarkPdf`) | 통과 | **통과 유지 (JUnit 1 tests successful)** |
| S4 가짜 워터마크 끼워넣기(V-01) | `valid=false reason=EXCEPTION:AEADBadTagException` | **`valid=true claims={uid=alice}` (진짜 워터마크를 찾아냄)** |
| S8 압축 폭탄(V-06) | `OutOfMemoryError`로 프로세스 종료 | **`valid=false reason=WATERMARK_NOT_FOUND`, 프로세스 생존** |
| S7 1바이트 HMAC 키(V-09) | 삽입 성공 | **`IllegalArgumentException`으로 거부** |

> 2차 검토에서 **1차 패치(createInputStream 복사 루프에만 상한)를 실제로 적용·실행해 보니 S8이 여전히 OOM**이었습니다. PDFBox가 스트림을 돌려주기 전에 전부 해제하기 때문입니다. 위 패치는 이를 바로잡아 `createRawInputStream` + 상한 `Inflater`로 직접 해제하도록 고친 **재검증 완료본**입니다.

> V-02/V-03/V-04/V-05(문서 바인딩·비대칭 서명)는 설계 변경이 필요해 이번 diff에는 포함하지 않았습니다. §3의 각 조치 방안과 §5 우선순위에 방향을 제시했습니다.

---

## 7. 2차 검토 결과

1차 작성 후 분리된 검토 절차에서 보고서와 PoC·패치를 재확인하고 아래를 반영했습니다.

| # | 검토 지적 | 반영 |
| --- | --- | --- |
| 1 | V-06의 `OutOfMemoryError`가 `catch (Exception)`에 잡힌다고 단정하면 틀림 — `Error`는 `Exception`이 아님 | §3 V-06·§6 패치 2에서 "`catch`로 잡히지 않고 밖으로 던져진다", "`Throwable`로 넓힘"으로 정정·검증 |
| 1-b | **1차 패치(복사 루프 상한)를 적용해도 S8이 여전히 OOM** — PDFBox가 createInputStream에서 선(先)해제함 | 패치를 `createRawInputStream` + 상한 `Inflater` 직접 해제로 교체하고, 256MiB 힙에서 폭탄이 막히는 것을 재실행으로 확인 |
| 2 | S4가 "진짜 워터마크가 분명히 있는데" 실패함을 보여야 설득력 있음 | PoC에 `before/after` 출력 추가해 before=`valid=true` 확인 |
| 3 | jackson 권고 12건을 그대로 "취약"으로 적으면 과장 — 폴리모픽 미사용이라 대부분 직접 악용 불가 | V-12에 "악용 가능성" 단락을 넣어 실제 노출 수준을 구분 |
| 4 | 패치가 원본 정상 동작(`KurbyPdfTest`)을 깨지 않는지 확인 필요 | 패치 사본에서 원본 테스트 통과 재확인, §6 표에 명시 |
| 5 | 통계와 본문 ID 개수 일치 여부 | Critical1/High3/Medium4/Low3/Info2 = 13건, §1 표와 §3 항목 수 일치 확인 |
| 6 | 의존성 버전·커밋 해시 등 사실관계 | 분석 커밋 `74d3aed`, PDFBox 2.0.30/Jackson 2.17.1을 `build.gradle.kts`와 대조 확인 |

**검토 결론:** High 이상 항목(V-01, V-02~V-04, V-05)은 모두 재현 또는 코드 근거로 뒷받침됩니다. §6 패치는 검증 경로 결함(V-01/V-06/V-08~V-11)을 실제로 막으면서 정상 동작을 유지함을 재검증했습니다. 설계축 결함(문서 바인딩·비대칭 전환)은 후속 과제로 명확히 분리했습니다.

---

## 부록 A. 재현 환경

- JDK: Temurin 17 (`--release 8`로 대상의 Java 8 타깃과 동일하게 컴파일)
- 의존성(Maven Central, SHA-1 대조): `pdfbox-2.0.30`, `fontbox-2.0.30`, `commons-logging-1.2`, `jackson-databind/core/annotations-2.17.1`
- 입력: 대상 저장소의 `src/test/resources/input/sample.pdf`
- 테스트 키: HMAC=`0x11`×32, AES=`0x22`×32 (원본 `KurbyPdfTest`와 동일)
- 의존성 권고: OSV.dev API 조회(2026-11 기준)
