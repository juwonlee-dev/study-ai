# KurbyPdf 보안 취약점 분석 보고서

- 분석 대상: [juwonlee-dev/KurbyPdf](https://github.com/juwonlee-dev/KurbyPdf) (commit `74d3aed`, `master`)
- 과제: [study-ai #46 3주차](https://github.com/juwonlee-dev/study-ai/issues/46) 과제 2
- 작성: Claude Code (`bohye/CLAUDE.md` 지침 적용) · 작성일 2026-11-23 · 2차 검토 반영본

## 1. 위험도별 탐지 통계

| 위험도 | 건수 | 취약점 ID |
|---|---:|---|
| 🔴 Critical | 0 | - |
| 🟠 High | 2 | KP-01, KP-03 |
| 🟡 Medium | 2 | KP-02, KP-04 |
| 🔵 Low | 6 | KP-05, KP-06, KP-07, KP-08, KP-11, KP-12 |
| ⚪ Info | 2 | KP-09, KP-10 |
| **합계** | **12** | |

> 집계에서 제외한 관찰 사항(실행 확인이 필요한 추정 포함)은 [6절](#6-기타-관찰-사항-집계-제외)에 따로 적었다.

### 위험도 기준

| 위험도 | 기준 |
|---|---|
| Critical | 인증 없이 원격 코드 실행·키 유출 등 즉시 전면 침해 |
| High | 라이브러리 핵심 보안 목적(유출 추적·위변조 검출)을 직접 무력화 |
| Medium | 특정 조건에서 보안 기능 우회, 서비스 거부 |
| Low | 오용 시 위험이 커지는 약점, 보호의 조용한 누락, 방어 심층화 부족 |
| Info | 직접적 취약점은 아니나 확인·개선이 필요한 사항 |

### 요약 목록

| ID | 위험도 | 제목 | 위치 |
|---|---|---|---|
| KP-01 | High | 워터마크가 문서에 바인딩되지 않아 다른 PDF로 이식(누명 씌우기) 가능 | `WatermarkPayload.java:27-31`, `PdfWatermarkInspector.java:96-138`, `PdfVerificationUtil.java:40-52` |
| KP-02 | Medium | 첫 번째 워터마크만 신뢰하고, 손상된 스트림 1개로 전체 검증이 중단됨 | `PdfVerificationUtil.java:40`, `PdfWatermarkInspector.java:31-34, 51-71, 97-107` |
| KP-03 | High | 고정 식별자·공유 스트림으로 워터마크 탐지·일괄 제거가 쉬움 | `PdfForensicEmbedder.java:16-17, 23, 40, 43-64, 80-86` |
| KP-04 | Medium | 신뢰할 수 없는 PDF 검증 시 메모리 고갈(DoS) 가능 | `PdfWatermarkInspector.java:46, 80-94` |
| KP-05 | Low | 사용자 암호가 없으면 Owner 암호가 무시되고 암호화 없이 저장됨 | `KurbyPdf.java:34-41` |
| KP-06 | Low | 키 길이·키 분리·입력 검증 부재 | `KurbyPdf.java:24-25`, `WatermarkPayload.java:37, 55`, `PdfVerificationUtil.java:26-27, 36` |
| KP-07 | Low | PDF 권한 제한이 최소한이고 우회 가능하며 열람 암호 강도 검증 없음 | `PdfProtector.java:9-16`, `KurbyPdf.java:35` |
| KP-08 | Low | 테스트 코드의 고정 키 사용 및 비밀번호 평문 출력 | `KurbyPdfTest.java:24-30, 46-47, 80-82` |
| KP-09 | Info | 의존성 버전 보안 점검 필요 | `build.gradle.kts:3, 27-28` |
| KP-10 | Info | README와 실제 코드 불일치로 인한 오용 가능성 | `README.md:66, 69, 73, 92, 96` |
| KP-11 | Low | 대칭키 구조로 부인 방지 불가(검증자가 워터마크 위조 가능) | `WatermarkPayload.java:36-56`, `PdfVerificationUtil.java:32` |
| KP-12 | Low | 페이지가 0개인 PDF에서 워터마크 없이 성공 반환 | `PdfForensicEmbedder.java:43-54`, `KurbyPdf.java:31, 45` |

## 2. 분석 범위와 방법

- 범위: `src/main/java` 9개 파일, `src/test/java` 1개 파일, `build.gradle.kts`, `README.md`
- 방법: 소스코드 전수 정적 리뷰(수동). 데이터 흐름(삽입 → 저장 → 추출 → 검증)과 위협 모델 기준으로 검토했다. 이후 독립 검토자가 2차 검토를 했다(5절).
- 위협 모델: 라이브러리 목적은 "배포 PDF 유출 추적·위변조 검출"이다. 공격자는 열람 암호를 아는 정상 수신자(내부자)이며, HMAC/AES 키는 모른다고 가정한다. 검증 서버는 출처를 알 수 없는 유출 PDF를 입력으로 받는다.
- 제외: 분석 대상 코드의 빌드·실행, 동작하는 익스플로잇 작성은 하지 않았다. 아래 공격 시나리오는 코드 근거 기반 분석이며 실행으로 확인하지 않았다.

## 3. 취약점 상세

### KP-01 [High] 워터마크가 문서에 바인딩되지 않아 다른 PDF로 이식 가능

- 위치: `WatermarkPayload.java:27-31`, `PdfWatermarkInspector.java:96-138`, `PdfVerificationUtil.java:40-52`
- 근거: 서명 대상 `body`는 `v`, `claims`, `ts`, `nonce`만 포함한다. 문서 내용·문서 ID 등 해당 PDF를 특정하는 값이 없다. 검증 측도 블롭 자체의 GCM 태그와 HMAC만 확인하며 블롭이 어떤 문서에 들어 있는지는 보지 않는다. `ts`·`nonce`를 발급 기록과 대조하지도 않는다.
- 전제: 다른 수신자 B에게 배포된 사본(문서 종류는 무관)과 그 열람 암호가 필요하다. 사용자 암호가 적용되면 `_k1` 스트림도 PDF 암호화되기 때문이다(`PdfProtector.java:16`). B의 사본이 무암호이거나 수신자 간 암호가 같다면 전제는 더 쉬워진다.
- 공격 시나리오: B의 사본에서 복호화한 `_k1` 블롭을 사용자 A가 유출하려는 PDF의 워터마크와 바꿔 넣는다. 블롭은 원본 그대로이므로 GCM·HMAC 검증을 통과하고 `valid=true, uid=B`가 나온다.
- 영향: 유출자 추적 결과를 조작해 무고한 사용자에게 책임을 돌릴 수 있다. 핵심 목적인 "불법 유출 추적"의 신뢰성이 무너진다.
- 조치 방안:
  1. 삽입 시 문서를 특정하는 값을 만들어 `body`에 넣고 서명한다. 예: 원본 PDF의 SHA-256, 또는 삽입 시 생성해 트레일러 `/ID`에 기록한 값. 검증 시 같은 값을 다시 추출·계산해 비교한다.
  2. 발급 시 `nonce → (uid, fileId, 문서 해시)`를 서버 원장에 기록하고, 검증 시 블롭 내용과 대조한다.
  3. `verifyDetailed` 결과에 "문서 바인딩 검증 여부"를 별도 필드로 반환한다.

### KP-02 [Medium] 첫 번째 워터마크만 신뢰하고, 손상된 스트림 1개로 전체 검증이 중단됨

- 위치: `PdfVerificationUtil.java:40`, `PdfWatermarkInspector.java:31-34, 51-71, 97-107`
- 근거:
  - `verifyDetailed`는 `extractFirst`로 페이지 순회 중 처음 발견한 블롭 하나만 판정한다.
  - 블롭이 손상되면 다음 세 곳에서 예외가 난다.
    - 13바이트 미만일 때 `IllegalArgumentException`(97-98행)
    - GCM 태그가 맞지 않을 때 `AEADBadTagException`(105행)
    - JSON이 깨졌을 때 파싱 예외(107행)
  - `extractAll`(51-71행)은 이 예외를 잡지 않는다. 따라서 손상된 `_k1` 스트림이 하나만 있어도 정상 워터마크를 확인하지 못하고 `EXCEPTION:*`으로 끝난다.
- 공격 시나리오:
  - 회피: 1페이지에 임의 바이트로 된 `_k1` 폼 XObject를 추가하면, 원래 워터마크가 남아 있어도 검증이 실패한다.
  - 위장: KP-01의 전제를 갖춘 공격자가 이식 블롭을 1페이지 앞쪽에 추가한다. 원래 워터마크를 지우지 않아도 판정 결과가 바뀐다.
- 영향: 추적 실패 또는 잘못된 추적 결과. KP-01·KP-03을 증폭하는 요소다.
- 조치 방안:
  1. 블롭별 복호화·검증을 `try/catch`로 감싸 실패 항목은 "무효"로 기록하고 순회를 계속한다.
  2. `extractAll` 결과 전체로 판정한다. 유효 워터마크끼리 `claims`가 다르거나 무효 블롭이 섞여 있으면 `CONFLICT`/`TAMPERED` 같은 별도 사유로 반환한다.

### KP-03 [High] 고정 식별자·공유 스트림으로 워터마크 탐지·일괄 제거가 쉬움

- 위치: `PdfForensicEmbedder.java:16-17, 23, 40, 43-64, 80-86`
- 근거:
  - 모든 문서가 고정 딕셔너리 키 `/_k1`, `/_k1v`를 쓴다.
  - 블롭 스트림은 문서당 하나만 만들고(43행), 모든 폼 XObject가 같은 객체를 참조한다(64행). 이 객체 하나만 없애면 모든 복제본이 무력화된다.
  - 1×1 BBox, 0×0 클리핑 영역(82-83행)이라는 특징도 매번 같다.
  - 위치 난수는 `new Random(System.currentTimeMillis())`(23, 40행)로 만들어 예측 가능하다. 다만 키 이름만으로도 바로 찾을 수 있다.
- 공격 시나리오: 수신자는 자기 사본과 열람 암호만 있으면 된다. 다른 전제는 필요 없다. 이 수신자가 PDF 편집 도구로 `/_k1` 키를 가진 XObject를 지우거나 `_k1` 값을 제거하고 저장하면, 검증 결과는 `WATERMARK_NOT_FOUND`가 된다.
- 영향: 워터마크가 제거됐다는 사실은 드러나지만 유출자는 특정할 수 없다. 핵심 목적인 유출 추적이 내부자에게 손쉽게 무력화된다. 전제 조건이 KP-01보다 적어 실현성은 오히려 높으므로 High로 분류했다.
- 조치 방안:
  1. 키 이름을 문서마다 다르게(키 파생 등) 하거나 일반 메타데이터처럼 보이게 한다.
  2. 복제본마다 독립 스트림과 다른 IV를 쓴다. 현재는 `KurbyPdf.java:28`에서 페이로드를 한 번만 만들어 `PdfForensicEmbedder.java:43`에서 공유한다. 따라서 `buildPayload`를 복제본 수만큼 호출하도록 구조를 바꿔야 한다.
  3. 위치 난수는 `SecureRandom`으로 생성한다.
  4. 구조 기반 워터마크만으로는 제거를 막을 수 없다. 필요하면 콘텐츠 레벨(가시·비가시 이미지·텍스트) 워터마크를 병행하고 README에 한계를 명시한다.
  5. 삽입 위치를 다양화한다면 검증 측도 중첩 Form XObject까지 탐색하도록 함께 고친다(`PdfWatermarkInspector.java:51-60`).

### KP-04 [Medium] 신뢰할 수 없는 PDF 검증 시 메모리 고갈(DoS) 가능

- 위치: `PdfWatermarkInspector.java:46, 80-94`
- 근거:
  - `PDDocument.load(bin[, password])`를 기본 메모리 설정으로 호출하며 상한이 없다.
  - `streamToBytes`는 `_k1` 스트림을 필터(예: FlateDecode)로 디코딩한 결과를 크기 제한 없이 메모리에 읽는다.
  - 위협 모델상 검증 입력은 출처를 알 수 없는 PDF다.
- 공격 시나리오: 작은 압축 데이터가 수 GB로 풀리는 `_k1` 스트림(압축 폭탄)이나, 페이지·XObject가 매우 많은 PDF를 검증 API에 제출한다.
- 영향: 검증 서버 JVM이 `OutOfMemoryError`를 내거나 CPU가 고갈되어 서비스가 거부된다.
- 조치 방안:
  1. `streamToBytes`에 최대 길이를 두고 초과 시 중단한다(**필수**). 기준은 정상 블롭 크기의 수 배, 수십 KB 수준이다. 아래 2의 `MemoryUsageSetting`은 이 `ByteArrayOutputStream`에는 적용되지 않는다.
  2. `PDDocument.load(..., MemoryUsageSetting.setupMainMemoryOnly(max))` 또는 `setupMixed(maxMain, maxStorage)`로 총량을 제한한다. `setupMixed(maxMain)`만 쓰면 초과분이 임시 파일로 넘어갈 뿐 총량은 제한되지 않는다.
  3. 입력이 이미 `byte[]`이므로 크기 상한은 호출 측 API 경계에서 검사한다. 검사할 페이지·XObject 수와 처리 시간에도 상한을 둔다.

### KP-05 [Low] 사용자 암호가 없으면 Owner 암호가 무시되고 암호화 없이 저장됨

- 위치: `KurbyPdf.java:34-41`
- 근거: 암호화는 `userPassword`가 비어 있지 않을 때만 적용된다. 호출자가 `userPassword=null`(또는 `""`)에 `ownerPassword="..."`를 주어 "열람은 자유, 권한은 제한"을 의도해도 경고 없이 암호화·권한 설정이 생략된다. 반환되는 `ownerPassword`도 `null`이다.
- 영향: 호출자는 보호가 적용됐다고 착각할 수 있다. 다만 누락되는 것은 KP-07에서 다루는 우회 가능한 권한 제한뿐이고, 열람 기밀성은 원래 의도대로 없다. 그래서 Low로 분류했다.
- 조치 방안(권장 순):
  1. 이 조합을 `IllegalArgumentException`으로 거부해 호출자가 의도를 명확히 하게 한다.
  2. `WatermarkResult`에 암호화 적용 여부를 반환한다.
  3. 또는 `PdfProtector.applyUserPassword(doc, "", ownerPwd)`로 권한 보호를 적용한다. 단, KP-07 때문에 실효성은 제한적이다.

### KP-06 [Low] 키 길이·키 분리·입력 검증 부재

- 위치: `KurbyPdf.java:24-25`, `WatermarkPayload.java:37, 55`, `PdfVerificationUtil.java:26-27, 36`
- 근거:
  - Base64 디코딩한 키를 길이 검증 없이 쓴다. HMAC 키는 1바이트여도 허용되고, AES 키는 JCE가 16/24/32바이트만 받을 뿐 32바이트를 강제하지 않는다. 두 키가 같아도 막지 않는다.
  - 키 입력이 잘못되면 명확한 오류 대신 다음 예외가 그대로 전파된다.
    - 키가 null이면 `NullPointerException`
    - Base64 형식이 아니면 `IllegalArgumentException`
    - 빈 키면 `SecretKeySpec`에서 예외
- 영향: 블롭은 AES-GCM 인증을 먼저 거친 뒤에 HMAC을 검사한다(105행 → 130-136행). 따라서 HMAC 키만 약하면 바로 위조되지는 않는다. 위조 위험은 AES 키까지 저엔트로피이거나 두 키가 같아 키 분리가 깨질 때 생긴다. 이때 어느 정도로 위험한지는 키 엔트로피에 따라 달라지며, 이는 추정이다.
- 조치 방안: 삽입·검증 진입점에서 다음을 강제한다.
  - HMAC 키 ≥ 32바이트, AES 키 = 32바이트
  - 두 키가 같으면 거부하고, null·형식 오류는 명시적 예외나 `MISSING_KEYS`로 처리
  - 마스터 키 하나에서 HKDF로 용도별 키를 파생하는 방안도 좋다. 단, Java 8 표준 라이브러리에는 HKDF가 없어 직접 구현하거나 BouncyCastle 등을 써야 한다.

### KP-07 [Low] PDF 권한 제한이 최소한이고 우회 가능하며 열람 암호 강도 검증 없음

- 위치: `PdfProtector.java:9-16`, `KurbyPdf.java:35`
- 근거:
  - `new AccessPermission()`(9행)은 기본값이 모든 권한 허용이다. 10행은 인쇄를 명시적으로 허용하고, 실제로 제한하는 것은 `setCanExtractContent(false)`(11행) 하나뿐이다. 수정·페이지 조립·양식 입력 등은 모두 허용된다.
  - 권한 비트는 PDF 표준상 뷰어가 지키는 권고 사항이다. 사용자 암호로 열 수 있는 문서는 일부 도구에서 권한이 무시된다.
  - `userPassword`의 길이·복잡도 검증이 없다.
- 영향: 복사 방지가 쉽게 우회되고 문서 수정(KP-03의 워터마크 제거 포함)도 막지 않는다. 약한 열람 암호는 오프라인 무차별 대입에 노출된다.
- 조치 방안:
  1. `setCanModify(false)`, `setCanAssembleDocument(false)`, `setCanFillInForm(false)` 등 필요한 제한을 명시적으로 설정한다.
  2. 권한 제한의 한계를 README·Javadoc에 명시한다.
  3. 열람 암호 최소 길이 정책을 옵션으로 제공한다.

### KP-08 [Low] 테스트 코드의 고정 키 사용 및 비밀번호 평문 출력

- 위치: `KurbyPdfTest.java:24-30, 46-47, 80-82`
- 근거: HMAC/AES 키를 `0x11`, `0x22`로 채운 고정값으로 쓴다. 생성된 Owner 암호, 사용자 암호, claims를 표준출력에 출력하고, 결과 PDF를 `build/test-out`에 남긴다.
- 영향: 운영 코드에 그대로 복사되면 키가 공개값이 된다. CI 로그에 비밀번호가 남는다. 테스트 한정이므로 Low로 분류했다.
- 조치 방안: 테스트 키는 `SecureRandom`으로 생성한다. 비밀번호 출력은 제거하거나 마스킹한다. 산출물은 JUnit `@TempDir`에 만든다.

### KP-09 [Info] 의존성 버전 보안 점검 필요

- 위치: `build.gradle.kts:27-28` (`pdfbox:2.0.30`, `jackson-databind:2.17.1`), `build.gradle.kts:3` (shadow 플러그인)
- 근거: 키가 없는 공격자의 입력을 직접 파싱하는 의존성은 PDFBox다. Jackson은 GCM 인증을 통과한 평문만 파싱한다(`PdfWatermarkInspector.java:105-107`). 이번 분석에서는 취약점 DB를 조회하지 않았으므로 두 버전에 알려진 CVE가 있는지는 **확인하지 못했다**. `com.github.johnrengelman.shadow` 플러그인은 `com.gradleup.shadow`로 이관된 것으로 알려져 있다(추정, 확인 필요).
- 조치 방안: OWASP Dependency-Check나 GitHub Dependabot으로 정기 점검하고 각 계열의 최신 패치 버전으로 올린다. `api` 대신 `implementation`을 써서 사용자 프로젝트로 전이되는 범위를 줄이는 것도 검토한다.

### KP-10 [Info] README와 실제 코드 불일치로 인한 오용 가능성

- 위치: `README.md:66, 69, 73, 92, 96`
- 근거:
  - 클래스명: README의 `PdfVerification`(66, 69, 92행)은 실제로 `util.PdfVerificationUtil`이다.
  - 메서드명: `getTimestamp()`(73행)는 실제로 `getTimestampMillis()`다.
  - 파일 위치: `KeyUtil`(96행)은 실제로 `util/` 아래에 있다.
  - 키 생성·보관 방법 안내가 없다.
  - 코드 주석 불일치(README 외): `KurbyPdf.java:31` 주석은 "페이지당 2개"라고 적었지만, 실제 기본값은 3개다(`PdfForensicEmbedder.java:20, 23`).
- 영향: 사용자가 예제를 임의로 고치다가 약한 키나 잘못된 검증 로직을 쓸 수 있다.
- 조치 방안: README 예제를 실제 API에 맞춘다. `SecureRandom` 기반 키 생성 예시와 키 관리 주의사항을 추가한다. 주석을 실제 기본값에 맞춘다.

### KP-11 [Low] 대칭키 구조로 부인 방지 불가

- 위치: `WatermarkPayload.java:36-56`, `PdfVerificationUtil.java:32`
- 근거: 삽입과 검증이 같은 HMAC 키와 AES 키를 쓴다. 따라서 검증 서버나 키 보관자는 임의의 `uid`로 유효한 워터마크를 만들 수 있다. AES-GCM이 이미 무결성을 제공하므로 HMAC은 같은 키 보관자에 대해 추가 보증을 주지 않는다.
- 영향: 키 보관 시스템이 침해되거나 운영자가 악의적이면 사용자에게 누명을 씌울 수 있다. 워터마크를 내부자 징계·분쟁의 증거로 쓸 때 증명력이 약하다. 영향의 크기는 운영 환경에 따라 다르다(추정).
- 조치 방안: 서명에 비대칭키(예: Ed25519, ECDSA)를 쓴다. 서명 키는 발급 서버만 갖고 검증 측은 공개키만 갖는다. 발급 원장(KP-01 조치 2)도 함께 운영해 감사 추적을 남긴다.

### KP-12 [Low] 페이지가 0개인 PDF에서 워터마크 없이 성공 반환

- 위치: `PdfForensicEmbedder.java:43-54`, `KurbyPdf.java:31, 45`
- 근거: 페이로드 스트림을 만든 뒤 `doc.getPages()`를 순회하며 참조를 삽입한다. 페이지가 없으면 아무 것도 참조하지 않는다. 그래도 `watermark()`는 예외 없이 결과를 반환한다. 참조되지 않은 스트림이 저장 결과에 남는지는 PDFBox 동작에 따라 다르고, 남더라도 검증기는 페이지 리소스만 보므로 찾지 못한다(추정).
- 영향: 호출자는 워터마크가 들어갔다고 믿지만 추적 정보가 없는 문서가 배포된다.
- 조치 방안: 삽입한 복제본 수를 세어 0이면 예외를 던진다. 삽입 직후 `extractFirst`로 자체 검증하는 옵션도 제공한다.

## 4. 양호 사항

- 페이로드 암호화에 AES-GCM(96비트 랜덤 IV, 128비트 태그)을 쓰고 IV를 `SecureRandom`으로 생성한다(`WatermarkPayload.java:50-56`).
- 서명을 상수 시간 비교 `MessageDigest.isEqual`로 비교한다(`PdfWatermarkInspector.java:136`).
- Owner 암호를 자동 생성할 때 `SecureRandom` 기반 32자(87종 문자, 약 200비트)를 쓴다(`KeyUtil.java:6, 13-38`).
- PDF 암호화에 AES-256을 쓴다(`PdfProtector.java:14-15`).

## 5. 2차 검토

### 절차

1. **1차:** 작성자(Claude Code 메인 세션)가 전체 소스를 정적 리뷰하고 초안(10건)을 작성했다.
2. **2차:** 별도 컨텍스트의 독립 검토 에이전트가 소스 전체를 다시 읽고 초안과 대조했다. 검토자는 읽기 전용으로 작업했고 빌드·실행은 하지 않았다. 다음 다섯 가지를 확인했다.
   - 오탐 여부
   - 라인 근거
   - 위험도 적정성
   - 누락 취약점
   - 조치안 타당성과 통계 일치
3. **재확인:** 작성자가 검토 지적 중 사실 확인이 가능한 항목을 저장소에서 직접 재확인한 뒤 반영했다. 확인한 항목은 다음과 같다.
   - 의존성 선언 라인
   - README 문구
   - 분석 대상 브랜치명
   - `AccessPermission` 기본값

### 검토 결과와 반영 내역

| 구분 | 검토 지적 | 반영 |
|---|---|---|
| 판정 | KP-01~05, KP-08은 CONFIRMED이고, KP-06·07·09·10은 PARTIAL(근거·라인 일부 오류)이다. REJECTED는 없다. | 아래와 같이 수정했다. |
| 위험도 | KP-03은 전제 없이 핵심 목적을 무력화하므로 High 기준에 해당한다. | Medium → **High**로 올렸다. |
| 위험도 | KP-05에서 누락되는 것은 우회 가능한 권한 제한뿐이다. | Medium → **Low**로 내렸다. |
| 전제 | KP-01은 다른 수신자의 사본과 열람 암호가 필요하다. | "전제" 항목을 추가했다. |
| 근거 오류 | KP-06에서 GCM이 HMAC보다 먼저 검증되므로 "약한 HMAC 키만으로 위조"는 성립하지 않는다. | 영향 서술을 고치고 입력 검증 부재를 통합했다. |
| 근거 보완 | KP-07에서 실제로 제한하는 권한은 하나뿐이다. | 근거와 조치를 보완했다. |
| 라인 오류 | KP-09의 의존성 위치는 25-26행이 아니라 27-28행이다. 신뢰할 수 없는 입력의 파서는 Jackson이 아니라 PDFBox다. | 수정했다. |
| 근거 오류 | KP-10에서 README에 "페이지당 2개" 문구가 없다(코드 주석에만 있다). `getTimestamp()` 불일치가 누락됐다. | 수정·추가했다. |
| 조치 보정 | KP-04에서 `setupMixed(maxMain)`은 총량 제한이 아니고, `streamToBytes` 길이 상한이 필수다. | 수정했다. |
| 조치 보정 | KP-03의 IV 분리는 구조 변경이 필요하다. KP-05는 거부나 반환값 방식을 우선해야 한다. HKDF는 Java 8 표준에 없다. | 수정했다. |
| 누락 | 대칭키 구조라 부인 방지가 불가하다. | **KP-11**(Low)로 신규 등록했다. |
| 누락 | 페이지가 0개인 PDF가 성공을 반환한다. | **KP-12**(Low)로 신규 등록했다. |
| 일관성 | 요약 목록과 상세 섹션의 위치 표기가 다르고, 분석 대상 브랜치가 `main`이 아니라 `master`다. | 수정했다. |

- **통계 변화:** 반영 후 통계는 초안 High 1 / Medium 4 / Low 3 / Info 2(합계 10)에서 High 2 / Medium 2 / Low 6 / Info 2(합계 12)로 바뀌었다.
- **재대조:** 1절 통계표, 요약 목록, 3절 상세 제목의 위험도를 다시 대조해 서로 일치함을 확인했다.

## 6. 기타 관찰 사항 (집계 제외)

실행 확인이 필요하거나 보안 영향이 작아 통계에서 제외한 항목이다.

- **[추정]** 입력 PDF가 이미 암호화된 경우의 처리가 불명확하다. `KurbyPdf.java:21`은 암호 없이 `load`한다. 이때 userPassword를 주지 않으면, 암호화 사전이 남은 상태로 `save`(44행)하다 예외가 날 수 있다. 실행으로 확인하지 않았다.
- `KeyUtil.randomOwnerPassword(len)`(`KeyUtil.java:17-27`)은 `len`을 검증하지 않는다. `len < 4`이면 4자가 생성되고, 음수이면 예외가 난다.
- 검증기는 페이지 리소스의 XObject만 탐색한다(`PdfWatermarkInspector.java:51-60`). 현재 삽입 구조에서는 문제가 없지만, KP-03 조치와 함께 보완해야 한다.
