# KurbyPdf 보안 취약점 보고서

- **과제**: Issue #46 (3주차) 2번 — 오픈소스 프로젝트의 취약점 찾아보기
- **분석 대상**: https://github.com/juwonlee-dev/KurbyPdf
- **분석 기준 커밋**: `74d3aedeea9204694a8bc1e04e75edaa75add94d` (2025-09-22, `feat: Add README`)
- **분석 일자**: 2026-11-23
- **분석 방법**: 저장소 전체 소스를 정적 분석하고, 라이브러리를 **로컬 Java 8(1.8.0_261)에서 실제로 빌드·실행**해 일부 동작을 확인했다. 의존성 취약점은 GitHub Advisory Database와 Maven Central 메타데이터를 2026-11-23에 조회했다.
- **적용한 지침**: 1번 과제의 `gunsang/CLAUDE.md`

> **읽는 법**: 각 항목의 "확인 방법"에 그 근거를 어떻게 얻었는지 적었다.
> - `소스`: KurbyPdf 소스를 읽어 확인한 사실.
> - `실행 확인`: 로컬 Java 8에서 라이브러리를 돌려 재현한 사실. 사용한 입력과 출력을 함께 적었다.
> - `PDFBox 소스`: PDFBox 2.0.30 태그 소스를 읽어 확인한 사실(라이브러리를 그 경로로 실행하지는 않음).
> - `Advisory DB`: GitHub Advisory Database 조회 결과.
> 빌드·실행은 정상 입력에 대해서만 했고, 공격 입력을 만들어 돌린 PoC는 없다. 공격 시나리오는 소스에서 도출한 것이다.

---

## 1. 통계 요약

### 1.1 위험도별 탐지 건수

| 위험도 | 건수 | 항목 |
|---|---:|---|
| Critical | 0 | — |
| High | 2 | V-01, V-02 |
| Medium | 3 | V-03, V-06, V-07 |
| Low | 3 | V-04, V-05, V-08 |
| Info (개선 권고) | 5 | I-01 ~ I-05 |
| **합계** | **13** | 취약점 8건 + 개선 권고 5건 |

### 1.2 피해 대상별 분포

취약점이 "누구에게 피해를 주는가"로 나눈 분포다. 정의는 2장에 있다.

| 피해 대상 | High | Medium | Low | Info | 합계 |
|---|---:|---:|---:|---:|---:|
| 문서를 보호하려는 배포자 (보안 기능 무력화) | 2 | 1 | 2 | 3 | 8 |
| 라이브러리를 실행하는 서버 (가용성) | 0 | 1 | 0 | 1 | 2 |
| 라이브러리를 의존성으로 쓰는 프로젝트 (전이) | 0 | 1 | 1 | 1 | 3 |
| **합계** | **2** | **3** | **3** | **5** | **13** |

Critical(키 없이 RCE·키 유출·서명 위조)은 없다. High 2건은 모두 "이 라이브러리를 썼는데도 유출자 추적·위변조 검출이라는 핵심 기능이 성립하지 않는" 문제다.

### 1.3 전체 목록

| ID | 위험도 | 제목 | 주 위치 |
|---|---|---|---|
| V-01 | High | 워터마크가 문서 내용과 묶이지 않아 이식·변조를 잡지 못함 | `WatermarkPayload.java:27-31` |
| V-02 | High | 키 없이 워터마크를 찾아 제거할 수 있음 | `PdfForensicEmbedder.java:16, 62-64` |
| V-03 | Medium | 검증 PDF 처리 시 메모리 상한이 없어 서비스 중단 가능 | `PdfWatermarkInspector.java:46, 83` |
| V-06 | Medium | 첫 번째 워터마크만 신뢰하고 오류·불일치를 구분하지 않음 | `PdfWatermarkInspector.java:31-33, 62-66` |
| V-07 | Medium | jackson 2.17.1의 알려진 취약점이 소비자에게 전이됨 | `build.gradle.kts:28` |
| V-04 | Low | 암호화가 선택이고 권한 대부분이 열려 있음 | `KurbyPdf.java:35`, `PdfProtector.java:9-11` |
| V-05 | Low | 키 길이·형식 검증 없음 | `KurbyPdf.java:24-25` |
| V-08 | Low | Fat JAR 재배치와 파일 직접 설치로 취약 의존성이 고착됨 | `build.gradle.kts:59-64`, `README.md:27` |
| I-01 | Info | 삽입 위치 난수가 예측 가능 | `PdfForensicEmbedder.java:23, 40` |
| I-02 | Info | 테스트 코드가 비밀번호를 표준 출력에 기록 | `KurbyPdfTest.java:78-82` |
| I-03 | Info | AES-GCM 운용 한계(AAD·키 식별자·IV 수명) | `WatermarkPayload.java:51-56` |
| I-04 | Info | PDFBox 2.0.30은 CVE는 없으나 구버전, wrapper 파일 누락 | `build.gradle.kts:27` |
| I-05 | Info | 이미 암호화된 입력 PDF 처리 방침 없음 | `KurbyPdf.java:21, 35, 44` |

---

## 2. 분석 기준

### 2.1 위협 모델

- 라이브러리 사용자는 PDF를 배포하는 서버 측이고, HMAC 키와 AES 키는 서버만 보유한다(README.md:106-108의 "불법 유출 추적" 사용례).
- 주 공격자는 **정당한 수령인(유출자)**이다. 자기 워터마크가 든 PDF와 그 사용자 비밀번호를 갖고 있지만 서버의 HMAC/AES 키는 모른다.
- 검증(`PdfVerificationUtil`)에 들어오는 PDF는 유출본, 즉 신뢰할 수 없는 입력이다.

### 2.2 위험도 기준

CVSS를 그대로 쓰지 않고, 이 라이브러리가 README.md:8-15에서 약속한 보안 목표(워터마크 삽입·추적, 무결성·위변조 확인, PDF 암호 보호)에 미치는 영향으로 판정했다.

| 위험도 | 기준 |
|---|---|
| Critical | 키·비밀번호 없이 RCE, 키 유출, 임의 서명 위조가 가능 |
| High | 키 없이 핵심 보안 목표(유출자 추적, 위변조 검출)를 무력화하거나 잘못된 결론을 유도 |
| Medium | 특정 조건에서 가용성 침해 또는 보안 기능 약화. 알려진 취약점이 있는 의존성이 소비자에게 전이되는 경우 포함 |
| Low | 단독 악용이 어렵거나 영향이 제한적인 약점, 오용을 유발하는 설계 |
| Info | 현재 코드에서 악용 경로를 확인하지 못했으나 개선을 권고하는 사항 |

---

## 3. High

### V-01 [High] 워터마크가 문서 내용과 묶이지 않음 — 이식·변조 미탐지

**위치**
- `WatermarkPayload.java:27-31` — HMAC 대상(`body`)이 `v`, `claims`, `ts`, `nonce` 네 필드뿐이다.
- `KurbyPdf.java:28` — `buildPayload(claims, hmacKey, aesKey)` 호출에 입력 PDF에서 파생한 값이 들어가지 않는다.
- `PdfWatermarkInspector.java:121-128` — 검증도 같은 네 필드만 재구성해 HMAC를 맞춘다.
- `README.md:15` — "무결성, 위변조 여부 확인 가능"이라고 설명한다.

**내용 (확인 방법: 소스)**
서명 대상 어디에도 "이 페이로드가 어느 문서에 붙었는지"를 나타내는 값(문서 해시·ID)이 없다. 그래서 암호문 스트림 하나는 어떤 PDF에 붙여도 그대로 유효하다. 검증의 `valid`는 페이로드 자체의 무결성만 보증할 뿐 문서의 무결성과는 무관하다.

**공격 시나리오**
- *이식(누명)*: 공격자가 동료 명의로 워터마킹된 아무 PDF와 그 사용자 비밀번호를 받아, 자신이 유출할 문서의 `/_k1` 스트림을 그 동료의 것으로 바꾼다. 검증하면 동료의 클레임으로 `valid=true`가 나온다. 서버 키는 필요 없다.
- *내용 변조 미탐지*: 워터마킹된 PDF 본문(금액·조항 등)을 고쳐도 `/_k1` 스트림이 남아 있으면 검증은 `true`다.

**영향**
추적 결과가 엉뚱한 사람을 가리킬 수 있어 워터마크의 증거 가치가 사라진다. 사용자가 `verify()==true`를 "문서가 변조되지 않았다"로 해석하면 잘못된 판단을 하게 된다.

**조치 방안 (현재 코드 기준)**
1. 페이로드에 원본 식별값을 넣는다. `KurbyPdf.java:28`에서 `SHA-256(inputPdf)`를 계산해 `buildPayload`에 넘기고, `WatermarkPayload.java:27-31`의 `body`에 `doc` 필드로 추가해 HMAC 대상에 포함시킨다.
   ```java
   // KurbyPdf.java (import java.security.MessageDigest)
   byte[] docHash = MessageDigest.getInstance("SHA-256").digest(inputPdf);
   byte[] payload = WatermarkPayload.buildPayload(claims, docHash, hmacKey, aesKey);
   ```
2. 검증 측(`PdfWatermarkInspector.java:121-128`)의 body 재구성에도 `doc`를 같은 순서로 넣어야 서명이 맞는다. 페이로드 형식이 바뀌므로 `WatermarkPayload.java:28`의 `v`를 2로 올리고, 기존 v1 페이로드를 거부할지 "문서 바인딩 없음"으로 표시할지 정한다.
3. `PdfVerificationUtil.verifyDetailed`에 "기대 원본 해시"를 받는 오버로드를 추가해 불일치 시 `Result.fail("DOCUMENT_MISMATCH")`를 반환한다.
4. 위 조치는 **다른 문서로의 이식**만 막는다. 본문 변조까지 검출하려면 PDF 전자서명(PDFBox `PDSignature`)을 별도로 적용해야 한다. `README.md:15`의 문구도 "페이로드 무결성 확인"으로 바로잡는다.

---

### V-02 [High] 키 없이 워터마크를 찾아 제거 가능

**위치**
- `PdfForensicEmbedder.java:16-17` — 고정 키 이름 `/_k1`, `/_k1v`.
- `PdfForensicEmbedder.java:43` — 페이로드 스트림은 문서당 하나만 만든다.
- `PdfForensicEmbedder.java:62-64` — 페이지마다 만드는 Form XObject는 모두 그 스트림을 참조하고 BBox가 1×1로 같다.
- `PdfWatermarkInspector.java:55-60` — 검증 자신이 페이지 리소스를 순회하며 `/_k1`을 가진 XObject를 찾는다. 공격자도 같은 방법을 쓰면 된다.

**내용 (확인 방법: 소스 + PDFBox 소스)**
워터마크는 Form XObject 딕셔너리의 비표준 키에 달린 스트림으로만 존재한다. 키 이름이 코드에 공개돼 있고, 몰라도 원본에 없던 1×1 Form XObject는 눈에 띈다. 사용자 비밀번호로 연 문서는 권한 플래그와 무관하게 수정·재저장할 수 있다(PDFBox `PDDocument.setAllSecurityToBeRemoved()`는 권한을 검사하지 않음 — `PDDocument.java:1702-1705`). 사용자 비밀번호는 선택이라(V-04) 비밀번호 없이 배포된 사본에는 이 장벽조차 없다.

**공격 시나리오**
유출자가 자기 사본을 열어 모든 페이지에서 `/_k1` 키를 가진 XObject를 지우고 다시 저장한다. 이후 검증 결과는 `WATERMARK_NOT_FOUND`(`PdfVerificationUtil.java:43`)다. 인쇄 후 스캔, "PDF로 인쇄", 포맷 변환으로도 워터마크는 사라진다.

**영향**
유출자가 추적을 회피할 수 있어 주 사용례(README.md:106-108)가 성립하지 않는다. README.md:111-112가 "강력한 DRM 대체 수단은 아니다"라고 밝히지만, 제거가 코드 몇 줄 수준이라는 점은 드러나 있지 않다.

**조치 방안 (현재 코드 기준)**
구조 기반 비가시 워터마크는 원리상 완전한 제거 방지가 불가능하다. 제거 비용을 올리는 방향만 제시한다.
1. `PdfForensicEmbedder.java:16-17`의 고정 키 대신 문서마다 HMAC 키에서 파생한 이름을 쓰거나, 정상 객체처럼 보이는 위치(콘텐츠 스트림·폰트·이미지)에 분산한다.
2. `PdfForensicEmbedder.java:43`에서 사본마다 독립 스트림(다른 IV로 재암호화)을 만들어 참조 하나를 지워도 남게 한다(1번과 함께 적용해야 의미가 있다).
3. 렌더링 결과에 남는 채널(글자 간격·좌표 미세 변조)을 병행하면 인쇄·변환에도 일부 살아남는다.
4. `PdfProtector.java:9-11`에서 수정 권한을 끈다(V-04). 강제력은 없지만 일반 뷰어 편집은 막는다.
5. README에 "수령인이 구조 편집으로 제거 가능"을 명시한다.

---

## 4. Medium

### V-03 [Medium] 검증 PDF 처리 시 메모리 상한 없음 (DoS) — 라이브러리 실행 서버

**위치**
- `PdfWatermarkInspector.java:46`, `KurbyPdf.java:21` — `PDDocument.load(InputStream[, password])`를 메모리 설정 없이 호출한다.
- `PdfWatermarkInspector.java:83` — `s.createInputStream()`으로 `/_k1` 스트림을 디코드한다.
- `PdfWatermarkInspector.java:84-90` — 디코드 결과를 상한 없는 `ByteArrayOutputStream`에 다시 복사한다.
- `PdfVerificationUtil.java:53` — `catch (Exception e)`만 있어 `OutOfMemoryError`는 잡히지 않는다.
- `PdfVerificationUtil.java:33`, `KurbyPdf.java:14` — 입력 PDF 크기 상한이 없다.

**내용 (확인 방법: 소스 + PDFBox 소스)**
- `PDDocument.load(InputStream)`은 `MemoryUsageSetting.setupMainMemoryOnly()`를 쓰고(`PDDocument.java:1131-1133`), 이 설정은 상한이 없다(`MemoryUsageSetting.java:98-101`).
- `COSStream.createInputStream()`은 지연 디코드가 아니라 반환 전에 필터 체인 전체를 디코드해 scratch 버퍼(위 설정에서는 무제한 메인 메모리)에 쓴다(`COSInputStream.java:62-108`). 메모리 소진은 읽기 루프(`:84-90`)가 아니라 `createInputStream()`(`:83`)에서 먼저 일어난다.
- 스트림을 읽는 시점(`:64`)은 복호화(`:65`)보다 앞이므로 **AES 키가 없어도** 여기에 도달한다.

**공격 시나리오**
공격자가 작은 PDF(수 MB 이하)를 만들어, 첫 페이지 리소스에 `/_k1`을 가진 Form XObject를 두고 그 스트림을 FlateDecode로 압축한 대량의 0바이트로 채운다. 디코드 결과가 검증 서버 힙을 넘으면 `OutOfMemoryError`가 나고, 이는 `Exception`이 아니라 `verifyDetailed` 밖으로 전파된다. (같은 필터를 여러 번 겹쳐 압축비를 키우는 방법은 PDFBox가 거부한다 — `COSInputStream.java:71-78`이 `HashSet`으로 **동일 필터의 중복**을 막는다. 서로 다른 필터를 체인하는 것은 막지 않지만, 단일 FlateDecode 폭탄만으로도 공격은 성립한다.)

**영향**
검증을 서비스로 노출한 애플리케이션의 가용성 침해. 같은 JVM의 다른 요청도 영향을 받는다. 삽입 경로(`KurbyPdf.watermark`)도 입력 크기 검사 없이 같은 설정으로 로드하지만(`:14, 21`), 삽입 경로에서 이 폭탄이 재현되는지는 확인하지 못했다.

**조치 방안 (현재 코드 기준)**
1. `PDDocument.load` 호출(`PdfWatermarkInspector.java:46`, `KurbyPdf.java:21`)에 상한 있는 메모리 설정을 넘긴다(주 방어). `load(InputStream, String, MemoryUsageSetting)` 오버로드가 2.0.30에 있다(`PDDocument.java:1204`).
   ```java
   // import org.apache.pdfbox.io.MemoryUsageSetting;
   private static final long MAX_PDF_MEMORY = 256L * 1024 * 1024; // 호출자 조정 가능
   doc = PDDocument.load(bin, password == null ? "" : password,
           MemoryUsageSetting.setupMainMemoryOnly(MAX_PDF_MEMORY));
   ```
   상한을 넘으면 `IOException`이 나 `PdfVerificationUtil.java:53`에서 잡힌다. `setupMixed(long)` 1인자 형태는 임시 파일이 무제한이라(`MemoryUsageSetting.java:145-148`) 2인자 형태를 쓴다.
2. 보조로 `PdfWatermarkInspector.java:84-90` 읽기 루프에 상한을 둔다(이것만으로는 `:83` 디코드를 막지 못한다). 서로 다른 `/_k1` 스트림 개수에도 상한을 둔다.
3. `PdfVerificationUtil.java:33`, `KurbyPdf.java:14`에 입력 PDF 최대 크기 검사를 추가한다.
4. 검증을 별도 프로세스/제한된 힙에서 돌리도록 README에 안내한다.

---

### V-06 [Medium] 첫 번째 워터마크만 신뢰하고 오류·불일치를 구분하지 않음

**위치**
- `PdfWatermarkInspector.java:31-33` — `extractFirst`가 `extractAll`의 0번만 반환한다.
- `PdfVerificationUtil.java:40` — `verifyDetailed`가 `extractFirst`만 쓴다.
- `PdfWatermarkInspector.java:62-66` — 스트림 하나의 복호화가 실패하면 예외가 그대로 던져져 나머지를 검사하지 않는다.
- `PdfWatermarkInspector.java:138` — 서명이 틀려도 `claims`가 담긴 `DecodedWatermark`를 반환한다.

**내용 (확인 방법: 소스 + 실행 확인)**
한 문서에 서로 다른 워터마크가 여러 개 있어도 이상으로 보지 않고, 순회 순서상 첫 번째 결과가 곧 검증 결과가 된다. 실행 확인: 같은 복호화 코드(`:96-105`)를 Java 1.8.0_261에서 블롭 길이별로 돌리면 — 12바이트는 `IllegalArgumentException`(`:97-98`), 13·20·27바이트는 `AEADBadTagException`("Input too short - need tag"), 28·64바이트는 `AEADBadTagException`("Tag mismatch!")이었다. 어떤 경우든 예외가 `extractAll`을 중단시킨다.

**공격 시나리오**
- *끼워 넣기*: 타인의 유효한 `/_k1` 스트림을 첫 페이지 리소스 앞쪽에 추가하면 검증이 타인의 클레임으로 `valid=true`를 낸다(V-01 이식의 변형). 순회 순서는 PDF 작성자가 정한다.
- *검증 방해*: 임의 바이트의 `/_k1`을 앞쪽에 추가하면 뒤에 유효한 워터마크가 있어도 복호화 예외로 검증이 끝난다.
- *API 오용*: `extractFirst`/`extractAll`은 public이다. 호출자가 `isSignatureValid()`를 확인하지 않으면 서명이 틀린 클레임을 신뢰하게 된다(`:138`).

**영향**
잘못된 귀속(V-01 악화) 또는 유효한 워터마크가 있는데도 검증 실패. 공격자는 이미 V-02로 워터마크를 지울 수 있으므로 추가 영향은 "더 은밀하게 결과를 조작"하는 정도다.

**조치 방안 (현재 코드 기준)**
1. `PdfWatermarkInspector.java:62-66`에서 스트림별 복호화 실패를 던지지 말고 기록한 뒤 계속 순회한다. 잡을 예외는 특정 타입을 나열하기보다 `Exception`으로 받는 편이 안전하다 — 런타임마다 예외 종류가 다르고, 12바이트 이하의 `IllegalArgumentException`은 `RuntimeException`이라 `GeneralSecurityException`만 잡으면 빠져나간다(위 실행 확인).
2. `PdfVerificationUtil.java:40`을 `extractAll` 기반으로 바꾼다: 유효 0개면 실패, 유효한 것들의 클레임·nonce가 모두 같으면 성공, 서로 다른 유효 워터마크가 2개 이상이거나 복호화 실패가 섞이면 `Result.fail("MULTIPLE_WATERMARKS")`로 전체 목록과 함께 실패 처리한다.
3. `KurbyPdf.java:31` 앞에서 입력에 이미 `/_k1`이 있는지 검사해 거부하거나 제거한다.
4. `PdfWatermarkInspector.java:138`은 서명이 유효하지 않으면 클레임을 비워 반환한다.

---

### V-07 [Medium] jackson 2.17.1의 알려진 취약점이 소비자에게 전이됨

**위치**
- `build.gradle.kts:28` — `api("com.fasterxml.jackson.core:jackson-databind:2.17.1")`. jackson-core 2.17.1이 전이로 따라온다.
- `build.gradle.kts:64` — shadow JAR에 재배치되어 포함된다.

**확인한 사실 (확인 방법: Advisory DB, 2026-11-23 조회)**
`com.fasterxml.jackson.core:jackson-databind@2.17.1`에 해당하는 권고 12건, `jackson-core@2.17.1`에 4건, 합계 **16건**이 조회됐다(GitHub severity 라벨 기준 High 8건/Medium 8건, CVSS 점수 7.0 기준으로는 High 7건/Medium 9건 — jackson-core의 CVE-2026-68494·CVE-2026-18401은 라벨은 high/medium이나 CVSS 점수가 없다). 대표적으로 PolymorphicTypeValidator 우회(CVE-2026-54512/54513, High 8.1), forward-reference 2차 시간 복잡도(CVE-2026-91777, High 7.5), `NumberInput` ReDoS(CVE-2026-89407, High 7.5) 등이다. 2.18.11과 2.18.12에 해당하는 권고는 **0건**이다.

**도달 가능성 (확인 방법: 소스)**
- KurbyPdf의 Jackson 사용은 `OM.readTree(byte[])`(`PdfWatermarkInspector.java:107`)와 `OM.writeValueAsBytes(Map)`(`:128`, `WatermarkPayload.java:33, 48`)뿐이다. POJO 역직렬화, 다형성 타이핑, Jackson 어노테이션은 쓰지 않는다.
- `readTree`에 들어가는 바이트는 AES-GCM 복호화를 통과한 평문이다. **AES 키가 없는 공격자는 Jackson 파서에 임의 입력을 넣을 수 없다.** 따라서 위 16건 중 KurbyPdf 자체 코드 경로로 도달하는 것은 확인되지 않았다.

**영향**
KurbyPdf 자체 경로에는 악용 경로가 없다. 위험은 High 등급이 다수인 버전을 `api` 구성으로 소비자에게 전이시키고 fat JAR에 고정한다는 데 있다(V-08). 소비자가 그 jackson을 자기 코드에서 다형성 역직렬화 등에 쓰면 노출된다. 2.2 기준의 "의존성 전이"에 해당해 Medium으로 판정했다(자체 도달 경로가 없다는 점만 보면 Low로 볼 여지도 있다).

**조치 방안 (현재 코드 기준)**
1. `build.gradle.kts:28`을 위 권고가 모두 수정된 **2.18.11 이상**으로 올린다(2026-11-23 기준 2.18 최신은 2.18.12, 2.x 최신은 2.23.0). Jackson 2.x는 Java 8을 지원하므로 `release 8` 설정(`:19`)과 충돌하지 않는다.
2. 공개 API 시그니처에 Jackson 타입이 없으므로 `api` 대신 `implementation`으로 바꿔 전이를 끊는다.
3. 의존성 취약점을 자동으로 잡도록 CI에 의존성 스캐너(Dependabot, OWASP Dependency-Check 등)를 연결해 다음 구버전 고착을 막는다.

---

## 5. Low

### V-04 [Low] 암호화가 선택이고 권한 대부분이 열려 있음

**위치**
- `KurbyPdf.java:35` — `userPassword`가 null/빈 문자열이면 암호화 블록 전체를 건너뛴다. 이때 `ownerPassword`를 줬어도 무시된다.
- `PdfProtector.java:9-11` — `new AccessPermission()` 뒤 `setCanPrint(true)`, `setCanExtractContent(false)`만 설정한다.
- `KurbyPdf.java:36-40` — 사용자·소유자 비밀번호 동일 여부를 검사하지 않는다.

**내용 (확인 방법: 실행 확인)**
로컬 Java 8에서 라이브러리를 정상 호출해 확인했다.
- `userPassword=null, ownerPassword="OwnerOnly!"` → 결과 PDF `isEncrypted=false`, `result.getOwnerPassword()=null`. **소유자 비밀번호만 준 요청이 경고 없이 평문 PDF를 반환한다.**
- `userPassword="userpw"`로 암호화한 뒤 사용자 비밀번호로 열면 `canModify=true, canModifyAnnotations=true, canAssembleDocument=true, canFillInForm=true, canExtractContent=false, canPrint=true`. 즉 **수정·주석·조립·양식 권한이 모두 열려 있다**(`AccessPermission()` 기본값이 전부 허용 — `AccessPermission.java:70-72`).
- `userPassword="pw", ownerPassword="pw"`(동일)로 열면 `isOwnerPermission=true`. **수령인이 소유자 권한을 갖는다.**

**영향**
호출자가 "소유자 비밀번호로 편집을 막겠다"는 의도로 `userPassword=null`을 주면 아무 보호 없는 PDF가 배포된다. 암호화해도 수정 권한이 열려 있어 V-02의 제거 작업이 쉬워진다. 권한 플래그 자체는 강제력이 없어 영향은 제한적이다.

**조치 방안 (현재 코드 기준)**
1. `KurbyPdf.java:35`의 조건을 "userPassword 또는 ownerPassword 중 하나라도 있으면 보호 적용"으로 바꾼다. 소유자만 있을 때는 사용자 비밀번호를 빈 문자열로 둔다.
2. `PdfProtector.java:9-11`에서 필요한 권한만 켠다.
   ```java
   ap.setCanModify(false);
   ap.setCanModifyAnnotations(false);
   ap.setCanAssembleDocument(false);
   ap.setCanFillInForm(false);
   ```
   `setCanExtractForAccessibility(false)`는 화면 낭독기를 막을 수 있어 필요할 때만 켠다.
3. 사용자·소유자 비밀번호가 같으면 거부하고, 비밀번호 최소 길이를 검사하거나 README에 약한 비밀번호 위험을 적는다.

---

### V-05 [Low] 키 길이·형식 검증 없음

**위치**
- `KurbyPdf.java:24-25` — Base64 디코드만 하고 길이를 확인하지 않는다. `getHmacKeyBase64()`가 null이면 `NullPointerException`이다.
- `WatermarkPayload.java:37` — HMAC 키 길이 제한 없음.
- `PdfVerificationUtil.java:24-28` — `verifyBase64`가 try 밖에서 디코드해, 잘못된 Base64가 들어오면 다른 메서드와 달리 예외가 그대로 나온다.

**내용 (확인 방법: 실행 확인)**
Java 1.8.0_261에서 확인: HMAC 키는 1바이트도 허용되고 빈 키만 `IllegalArgumentException`("Empty key")이다. AES 키는 JCE가 16/24/32바이트만 받아 1·33바이트는 `InvalidKeyException`이다. 즉 HMAC는 사실상 길이 검증이 없다.

**영향**
약한 키가 운영에 들어갈 수 있다. 호출자가 짧은 문자열(비밀번호 등)을 HMAC 키로 넘겨도 조용히 동작하므로, AES 키가 함께 유출된 상황에서 HMAC 키를 오프라인 전수 조사할 수 있다. 검증 없이 던져지는 예외로 원인 파악도 어렵다.

**조치 방안 (현재 코드 기준)**
`KurbyPdf.java:24-25` 직후에 검사를 추가한다. null·잘못된 Base64는 `IllegalArgumentException`으로 통일하고, `PdfVerificationUtil.java:24-28`의 디코드는 try로 감싸 `false`를 반환한다.
```java
if (hmacKey.length < 32) throw new IllegalArgumentException("hmacKey must be >= 32 bytes");
if (aesKey.length != 16 && aesKey.length != 32) throw new IllegalArgumentException("aesKey must be 16 or 32 bytes");
if (MessageDigest.isEqual(hmacKey, aesKey)) throw new IllegalArgumentException("hmacKey and aesKey must differ");
```

---

### V-08 [Low] Fat JAR 재배치와 파일 직접 설치로 취약 의존성이 고착됨

**위치**
- `build.gradle.kts:59-64` — PDFBox, FontBox, Jackson을 `io.github.juwonlee.shadow.*`로 재배치한다.
- `README.md:27` — `implementation files("libs/kurbypdf.jar")`
- `README.md:37-38` — Maven `system` scope + `systemPath`

**내용 (확인 방법: 소스)**
README가 안내하는 설치는 JAR를 직접 복사하는 방식이라 의존성 메타데이터가 전달되지 않는다. 소비자는 fat JAR를 써야 하고, 그 안의 PDFBox/Jackson은 재배치된 패키지명으로 고정돼 버전을 올릴 수 없다. XmpBox 재배치 설정(`:61`)은 pdfbox 2.0.30 의존성에 없어 적용 대상이 없고, commons-logging은 재배치하지 않아 원래 이름으로 들어간다.

**영향**
V-07처럼 번들된 의존성에 취약점이 공개돼도, 패키지명 기반 스캐너가 재배치된 사본을 놓칠 수 있다. 소비자는 KurbyPdf가 새 JAR를 낼 때까지 취약 버전을 계속 쓴다. 직접 악용 가능한 결함은 아니다.

**조치 방안 (현재 코드 기준)**
1. Maven Central 등에 thin JAR와 POM을 배포하고 README 설치 안내를 좌표 기반(`implementation("io.github.juwonlee:kurbypdf:1.0.0")`)으로 바꾼다.
2. fat JAR를 유지한다면 릴리스마다 번들된 의존성 버전을 명시하고, 보안 패치 시 즉시 재배포한다.

---

## 6. 개선 권고 (Info)

현재 코드에서 악용 경로를 확인하지 못했으나 개선을 권고하는 사항이다.

### I-01 [Info] 삽입 위치 난수가 예측 가능
- 위치: `PdfForensicEmbedder.java:23`(시드 `System.currentTimeMillis()`), `:40`(`new Random(seed)`), `:32`("보통 더 안전"이라는 주석).
- 내용(소스): `java.util.Random`은 암호학적 난수가 아니고 시드도 추측 가능하다. 다만 XObject는 페이지 리소스에서 그대로 열거되므로(V-02) 위치를 숨겨 얻는 보안 효과가 애초에 없다. 악용 경로가 없어 Info로 둔다.
- 권고: `:32` 주석에서 무작위 배치를 보안 수단처럼 설명하는 부분을 지운다(숨겨도 열거되므로 효과 없음). 삽입 위치에 난수가 필요하다면 `java.util.Random` 대신 `SecureRandom`으로 바꾼다.

### I-02 [Info] 테스트 코드가 비밀번호를 표준 출력에 기록
- 위치: `KurbyPdfTest.java:78-82`(`ownerPwd`, `userPwd` 출력), `:69`("필요시 별도 로깅" 주석).
- 내용(소스): 테스트 전용 값이라 직접 위험은 없으나, 이 테스트가 사실상 사용 예제라 비밀번호를 로그에 남기는 패턴이 운영 코드로 복사될 수 있다.
- 권고: 출력을 제거·마스킹하고, "소유자 비밀번호는 로그에 남기지 말 것" 주석으로 바꾼다.

### I-03 [Info] AES-GCM 운용 한계
- 위치: `WatermarkPayload.java:51-56`, `PdfWatermarkInspector.java:103-104`.
- 내용(소스): IV는 `SecureRandom` 12바이트로 호출마다 새로 만들어 구현 자체는 올바르다. 남는 한계는 — 무작위 IV 방식은 한 키의 암호화 횟수 한도(NIST SP 800-38D 기준 2^32회)가 있고, AAD를 안 써 버전·문서 식별자가 암호문에 묶이지 않으며(V-01 연관), 키 식별자가 없어 키 교체 후 구 키를 순서대로 시도해야 한다.
- 권고: 암호문 앞에 키 식별자(1~2바이트)를 붙이고 GCM의 AAD로 함께 인증해 문서·버전·키를 묶는다. 한 키의 암호화 한도와 교체 주기도 README에 적는다.

### I-04 [Info] PDFBox 2.0.30은 CVE는 없으나 구버전, Gradle wrapper 파일 누락
- 위치: `build.gradle.kts:27`, 저장소 트리.
- 내용(Advisory DB + 소스): `org.apache.pdfbox:pdfbox@2.0.30`, `fontbox@2.0.30`에 해당하는 권고는 0건이다(2026-11-23 조회). 다만 신뢰할 수 없는 PDF를 파싱하는 라이브러리라 파서 견고성 패치가 누적된 최신 버전이 안전하다(2.0 계열 최신 2.0.37). `.gitignore:3`이 `gradle-wrapper.jar`를 추적 예외로 뒀지만 실제로 커밋되지 않아, 빌드 Gradle 버전·체크섬이 고정되지 않는다.
- 권고: `build.gradle.kts:27`을 2.0.37로 올린다(3.x는 `PDDocument.load` 등 API가 바뀌어 코드 수정이 필요하다). wrapper 파일을 커밋하고 `distributionSha256Sum`을 지정한다.

### I-05 [Info] 이미 암호화된 입력 PDF 처리 방침 없음
- 위치: `KurbyPdf.java:21`(비밀번호 없이 로드), `:35`, `:44`.
- 내용(소스 + PDFBox 소스): 소유자 비밀번호만 걸린 입력은 `:21`에서 열리지만, 요청에 `userPassword`가 없으면 `protect()`가 호출되지 않은 채 `:44`에서 저장돼 PDFBox가 `IllegalStateException`을 던진다(`COSWriter.java:1388-1392`). 사용자 비밀번호가 걸린 입력은 `:21`에서 실패한다. 가용성·사용성 문제이고 보안 영향은 작아 Info로 둔다.
- 권고: `:21` 직후 `doc.isEncrypted()`를 검사해 명시적으로 거부하거나, 입력 비밀번호를 받는 방침을 정해 README에 적는다.

---

## 7. 취약점으로 분류하지 않은 확인 사항

| 항목 | 근거 |
|---|---|
| HMAC 비교 타이밍 공격 | `PdfWatermarkInspector.java:136`이 `MessageDigest.isEqual`을 사용한다(소스). |
| IV·nonce·소유자 비밀번호 난수원 | `WatermarkPayload.java:15`, `KeyUtil.java:6` 모두 `SecureRandom`이다(소스). |
| 자동 생성 소유자 비밀번호 강도 | `KeyUtil.java:13-39`: 87종 문자 32자리. 실행 확인에서도 길이 32를 확인했다. |
| Jackson 역직렬화 가젯(RCE) | `readTree`로 `JsonNode`만 만들고 다형성 타이핑을 켜지 않는다(소스). |
| 코드/주석 불일치 | `KurbyPdf.java:31` 주석은 "페이지당 2개"지만 실제 기본값은 3이다(`PdfForensicEmbedder.java:22-23`). 보안 결함이 아니라 여기 기록만 한다. |

---

## 8. 2차 검토 기록

### 8.1 절차
- 검토자: 초안을 쓰지 않은 별도 에이전트. 보고서는 읽기만 하고 수정은 초안 작성자가 반영했다.
- 대조 대상: KurbyPdf `74d3aed` 소스, 로컬 Java 8 실행 결과, PDFBox 2.0.30 태그 소스, GitHub Advisory DB 재조회, Maven Central 메타데이터.
- 검토 항목: 인용 줄 번호, 원인 서술, 시나리오 성립 여부, 위험도, 조치 방안의 적용 가능성, 실행 확인 결과의 재현, 누락 취약점, 통계표 검산.

### 8.2 항목별 판정과 변경 내용

2차 검토에서 하드 에러 1건과 명확화 1건이 나왔고, 둘 다 반영했다. 나머지 항목은 검토자가 소스·실행·Advisory DB로 재대조해 초안과 일치함을 확인했다.

| 항목 | 판정 | 초안에서 바뀐 내용 |
|---|---|---|
| V-07 집계 | **수정** | "합계 16건(High 7 / Medium 9)"에서 집계 기준을 명시하지 않았다. GitHub severity 라벨 기준은 High 8 / Medium 8이고, 초안의 7/9는 CVSS 7.0 임계값 기준이었다. jackson-core의 CVE-2026-68494·CVE-2026-18401이 라벨은 high/medium이나 CVSS 점수가 없어 두 집계가 갈린다. 두 기준을 모두 적도록 고쳤다. 합계 16건과 결론은 그대로다. |
| V-03 시나리오 | **수정** | "필터를 여러 번 겹쳐 압축비를 키우는 방법은 PDFBox가 거부한다"가 `COSInputStream.java:71-78`을 잘못 일반화했다. 이 코드는 `HashSet`으로 **동일 필터의 중복**만 막고 서로 다른 필터 체인은 막지 않는다. 그렇게 한정하고, 단일 FlateDecode 폭탄만으로 공격이 성립한다는 점을 덧붙였다. |
| 인용 줄 번호 (V-01~V-08, I-01~I-05) | 확인 | 검토자가 `74d3aed` 소스와 표본 대조해 전부 일치. |
| 실행 확인 (V-04, V-05, V-06) | 확인 | 검토자가 로컬 Java 1.8.0_261에서 재현: 소유자 비번만 준 요청의 `isEncrypted=false`, 사용자 비번 문서의 권한 플래그, user==owner 허용, 복호화 길이별 예외, HMAC/AES 키 길이 동작이 초안과 모두 일치. |
| PDFBox 2.0.30 소스 인용 | 확인 | `PDDocument.java:1131-1133, 1204, 1702-1705`, `MemoryUsageSetting.java:98-101, 145-148`, `AccessPermission.java:70-72`, `COSWriter.java:1388-1392`, `COSInputStream.java:62-108` 모두 일치. |
| 의존성 권고 수치 | 확인 | jackson-databind@2.17.1 12건 + jackson-core@2.17.1 4건 = 16건, pdfbox/fontbox@2.0.30 0건, 2.18.11·2.18.12 0건 재조회 일치. |
| 통계표 (1.1, 1.2, 1.3) | 확인 | 합계 13건, 행·열 합, 본문 항목 수가 모두 정합. |
| 위험도 판정 | 확인 | 2.2 기준에 과대·과소 없음. V-04(Low)는 더 올릴 여지가 있으나 권한 플래그 비강제성·호출자 오용 전제를 감안해 Low 유지. |
| 누락 취약점 | 확인 | 소스 전수 검토에서 별도 취약점 없음. |

### 8.3 끝까지 확인하지 못한 것

- 모든 공격 시나리오의 실제 PoC 재현(공격 PDF를 만들어 돌리지는 않았다). 정상 입력 빌드·실행과 복호화 로직 재현까지만 했다.
- 삽입 경로(`KurbyPdf.watermark`)에서의 메모리 폭탄 재현(V-03 영향란에 미확인으로 명시).
- Advisory DB의 각 CVE 요약 설명 문구(ID·severity·CVSS 점수만 대조).
- Advisory DB 외 출처(NVD, OSV)와의 교차 대조.
