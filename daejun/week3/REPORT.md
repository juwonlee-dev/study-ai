# KurbyPdf 보안 취약점 분석 보고서

| 항목 | 내용 |
|---|---|
| 분석 대상 | [juwonlee-dev/KurbyPdf](https://github.com/juwonlee-dev/KurbyPdf) (`main`, 커밋 `74d3aed`) |
| 대상 성격 | PDF 숨김 워터마크 삽입·검증 Java 라이브러리 (Java 8, PDFBox 2.0.30, Jackson 2.17.1) |
| 분석 범위 | `src/main` 9개 파일, `src/test` 1개 파일, `build.gradle.kts`, `gradle.properties`, `settings.gradle.kts`, `README.md` (저장소 전체 18개 파일) |
| 분석 방법 | 전체 소스 수동 리뷰 → PoC 코드로 실제 재현 → 조치 코드 적용 후 동일 PoC 재실행 → OSV DB로 의존성 CVE 조회 |
| 분석 일자 | 2026-11-14 |
| 분석 도구 | Claude Code (Claude Opus 5.5), JDK 17 (`--release 8` 컴파일) |

---

## 1. 위험도별 통계

| 위험도 | 건수 | 해당 항목 |
|:---:|:---:|---|
| 🔴 Critical | 0 | - |
| 🟠 High | 1 | V-01 |
| 🟡 Medium | 2 | V-02, V-03 |
| 🔵 Low | 4 | V-04, V-05, V-06, V-07 |
| ⚪ Info | 3 | V-08, V-09, V-10 |
| **합계** | **10** | 2차 검토에서 오탐 6건 제외 (7장 참고) |

### 위험도 판정 기준

| 위험도 | 기준 (악용 난이도 × 영향 범위) |
|---|---|
| Critical | 특별한 조건 없이 악용되고 키 유출·원격 코드 실행 등 시스템 전체가 위험해짐 |
| High | 악용이 쉽고(일반 PDF 편집 수준), 라이브러리의 핵심 보안 기능이 **잘못된 '정상' 결과**를 내 신뢰가 무너짐 |
| Medium | 악용이 쉬우나 영향이 가용성 저하, 또는 **탐지할 수 있는 실패**(워터마크 없음 등)에 그침 |
| Low | 악용에 추가 조건(키 유출, 잘못된 호출 등)이 필요하거나 영향이 제한적임 |
| Info | 직접 위협은 없으나 보안 수준 향상을 위한 개선 권고 |

### 취약점 목록

| ID | 위험도 | 유형 | 제목 | 위치 | 재현 |
|---|---|---|---|---|---|
| V-01 | High | 무결성 검증 | 워터마크가 문서 내용과 연결되지 않아 변조·이식 문서도 검증 통과 | `WatermarkPayload.java:27-38`, `PdfVerificationUtil.java:32-56` | ✅ |
| V-02 | Medium | 자원 고갈(DoS) | 압축 폭탄 PDF 검증 시 메모리 고갈 | `PdfWatermarkInspector.java:46, 80-94` | ✅ |
| V-03 | Medium | 보호 기능 우회 | 고정된 키 이름과 단일 공유 스트림 때문에 워터마크를 쉽게 제거 | `PdfForensicEmbedder.java:16, 43-64` | ✅ |
| V-04 | Low | 에러 처리 | 위조 스트림 1개만 있어도 정상 워터마크 검증 전체가 실패 | `PdfWatermarkInspector.java:62-66` | ✅ |
| V-05 | Low | 접근 통제 | PDF 권한이 과하고 암호 조합을 검증하지 않음 | `PdfProtector.java:9-13`, `KurbyPdf.java:35-41` | ✅ |
| V-06 | Low | 취약한 구성요소 | 알려진 CVE가 있는 Jackson 2.17.1을 `api`로 노출 | `build.gradle.kts:28` | OSV 조회 |
| V-07 | Low | 입력값 검증 / 암호화 | 키 길이·키 분리를 검증하지 않고 예외가 그대로 전파됨 | `KurbyPdf.java:24-25`, `PdfVerificationUtil.java:26-27` | ✅ |
| V-08 | Info | 중요정보 노출 | 테스트 코드가 비밀번호를 표준출력에 기록하고 키를 하드코딩함 | `KurbyPdfTest.java:24-29, 80-82` | 코드 확인 |
| V-09 | Info | 암호화(난수) | 워터마크 위치에 예측 가능한 난수를 사용 | `PdfForensicEmbedder.java:23, 40` | 코드 확인 |
| V-10 | Info | 공급망 / 빌드 | Gradle Wrapper가 누락되었고 의존성 무결성을 검증하지 않음 | `build.gradle.kts`, `.gitignore:3`, `README.md:25-40` | 코드 확인 |

---

## 2. 분석 대상 구조와 공격 표면

```
KurbyPdf.watermark(pdf, req)            ← 발급 측 (서버가 소유한 PDF)
 ├─ WatermarkPayload.buildPayload       claims+ts+nonce → HMAC-SHA256 → AES-256-GCM
 ├─ PdfForensicEmbedder.embed           /_k1 키로 FormXObject에 payload 스트림 부착
 └─ PdfProtector.applyUserPassword      PDF 표준 암호화(AES-256)
PdfVerificationUtil.verify(pdf, ...)    ← 검증 측 (유출본·업로드 파일 = 신뢰할 수 없는 입력)
 └─ PdfWatermarkInspector.extractAll    PDF 파싱 → /_k1 스트림 디코드 → 복호화 → HMAC 비교
```

- 라이브러리 형태라서 인증·세션·URL 같은 웹 계층은 없습니다. 주요 공격 표면은 **검증 대상 PDF(외부 입력)** 와 **워터마크된 PDF를 받은 수신자**입니다.
- 공격자 모델: (A1) 워터마크된 PDF를 정상적으로 받은 수신자, (A2) 검증 API에 임의 PDF를 업로드하는 외부인. 두 공격자 모두 HMAC/AES 키는 모른다고 가정합니다.

---

## 3. 취약점 상세

### V-01. 워터마크가 문서 내용과 연결되지 않아 변조·이식 문서도 검증 통과 — 🟠 High

| 항목 | 내용 |
|---|---|
| 위치 | `WatermarkPayload.java:27-38` (서명 대상), `PdfVerificationUtil.java:32-56` (검증 로직), `README.md:15, 100` (기능 설명) |
| 공격자 | A1 (워터마크된 PDF 수신자) |
| 악용 난이도 | 쉬움: 일반 PDF 편집기, 또는 PDFBox 코드 20줄 수준 |

**설명**
HMAC 서명 대상은 `v, claims, ts, nonce` 네 값뿐입니다(`WatermarkPayload.java:27-38`). 문서 본문, 페이지 수, 파일 해시 등 **문서를 식별하는 값이 전혀 포함되지 않습니다.** 검증(`PdfVerificationUtil.verifyDetailed`)도 payload 서명만 확인합니다. 그런데도 README는 "삽입된 워터마크의 존재 여부, 무결성, 위변조 여부 확인 가능"(`README.md:15`)이라고 설명하고 있습니다.

**입력 → 취약 지점 경로**
수신자가 PDF 본문을 수정하거나 `_k1` 스트림을 다른 PDF로 옮김 → `verifyDetailed()` → `extractFirst()` → `decryptAndVerify()`가 payload만 검증 → `valid=true`.

**재현 결과 (PoC)**
```
[tamper(edit page 1 text)] valid=true reason=null claims={uid=victim-001}   ← 1페이지에 "TAMPERED CONTENT" 추가
[transplant(new doc)]      valid=true reason=null claims={uid=victim-001}   ← 전혀 다른 1페이지 문서에 _k1 이식
```

**영향**
- 변조된 문서(예: 시험지, 내부 보고서)가 "정상·무결" 판정을 받습니다.
- 피해자(`uid=victim-001`)의 워터마크를 공격자가 만든 문서에 이식하면, 그 문서의 **유출자로 피해자가 지목됩니다**(누명 씌우기).

**조치 방안** (검증 완료)
발급 시 출력 PDF의 SHA-256을 계산해 `fileId`/`nonce`와 함께 서버에 저장하고, 검증할 때 비교합니다. 기존 API는 유지하고 오버로드만 추가합니다.

```java
// WatermarkResult.java
private final byte[] sha256;
public WatermarkResult(byte[] pdfBytes, String ownerPassword) {
    this.pdfBytes = pdfBytes;
    this.ownerPassword = ownerPassword;
    try {
        this.sha256 = MessageDigest.getInstance("SHA-256").digest(pdfBytes);
    } catch (NoSuchAlgorithmException e) { throw new IllegalStateException(e); }
}
/** 발급 문서 해시. fileId/nonce와 함께 서버에 저장해 검증 시 사용 */
public byte[] getSha256() { return sha256.clone(); }

// PdfVerificationUtil.java
public static Result verifyDetailed(byte[] pdfBytes, String userPassword,
                                    byte[] hmacKey, byte[] aesKey, byte[] expectedSha256) {
    Result r = verifyDetailed(pdfBytes, userPassword, hmacKey, aesKey);
    if (!r.isValid()) return r;
    if (expectedSha256 == null) return Result.fail("MISSING_EXPECTED_HASH");
    try {
        byte[] actual = MessageDigest.getInstance("SHA-256").digest(pdfBytes);
        if (!MessageDigest.isEqual(actual, expectedSha256)) return Result.fail("DOCUMENT_MODIFIED");
    } catch (NoSuchAlgorithmException e) {
        return Result.fail("EXCEPTION:" + e.getClass().getSimpleName());
    }
    return r;
}
```
- 조치 후 재현: `[fix-hash untouched] valid=true`, `[fix-hash tampered] valid=false reason=DOCUMENT_MODIFIED`
- 이식된 문서도 해시가 다르므로 같은 방식으로 차단됩니다.
- 서버 저장소가 없는 환경이라면 PDFBox `PDSignature` 기반 전자서명(PAdES)으로 문서 자체에 무결성을 부여하는 방법을 권장합니다.
- README의 "위변조 여부 확인" 문구를 "**claims 위변조 확인**(문서 본문 무결성은 해시 비교 오버로드 사용 시에만 보장)"으로 고쳐 기능 범위를 명확히 해야 합니다.

---

### V-02. 압축 폭탄 PDF 검증 시 메모리 고갈 (DoS) — 🟡 Medium

| 항목 | 내용 |
|---|---|
| 위치 | `PdfWatermarkInspector.java:46` (메모리 제한 없는 로드), `PdfWatermarkInspector.java:80-94` (스트림 전체를 크기 제한 없이 읽음), `PdfVerificationUtil.java:53` (`Exception`만 catch) |
| 공격자 | A2 (검증 API에 PDF를 업로드하는 외부인) |
| 악용 난이도 | 쉬움: 키 없이 1MB PDF 하나로 가능 |

**설명**
`PDDocument.load(bin)`는 기본 설정(메모리 무제한)으로 동작합니다. `streamToBytes()`는 `/_k1` 스트림을 디코드한 결과 전체를 `ByteArrayOutputStream`에 크기 제한 없이 쌓습니다. 이 스트림에 `/Filter /FlateDecode` 압축 폭탄을 넣으면, 복호화·HMAC 검증보다 **먼저** 메모리가 고갈됩니다. 이때 발생하는 `OutOfMemoryError`는 `Error` 계열이라 `verifyDetailed()`의 `catch (Exception e)`에 잡히지 않고 호출자 스레드까지 전파됩니다.

**입력 → 취약 지점 경로**
업로드 PDF → `verify()` → `extractAll()` → `PDDocument.load()`(:46) → `/_k1` 발견(:59-60) → `streamToBytes()`(:64, :87-89)에서 1GiB 디코딩 → OOM.

**재현 결과 (PoC)**
```
[bomb] malicious pdf size = 1089273 bytes                      ← 약 1MB, 디코딩하면 1GiB
-Xmx512m / -Xmx2g : java.lang.OutOfMemoryError: Java heap space  ← verifyDetailed 밖으로 전파
```

**조치 방안** (검증 완료)
```java
// PdfWatermarkInspector.java
private static final int  MAX_PAYLOAD_BYTES = 64 * 1024;          // 정상 payload는 수백 바이트
private static final long MAX_MEMORY_BYTES  = 64L * 1024 * 1024;  // PDF 파싱 메모리 상한 (JVM 힙보다 충분히 작게)

// :46
doc = PDDocument.load(bin, password != null ? password : "",
        MemoryUsageSetting.setupMainMemoryOnly(MAX_MEMORY_BYTES));

// streamToBytes() 반복문 안
if (bout.size() + r > MAX_PAYLOAD_BYTES) throw new IOException("watermark payload too large");
```
- 조치 후 재현(`-Xmx256m`): 폭탄 스트림은 건너뛰고 정상 워터마크를 검증합니다. `valid=true`
- `MAX_MEMORY_BYTES`는 반드시 JVM 힙보다 작아야 합니다. 2차 검토에서 256MB 상한·256MB 힙 조합은 OOM이 그대로 발생해 64MB로 조정했습니다(7장 참고).
- 호출 측(웹 서버)에서도 업로드 크기를 제한하고, 검증 작업을 별도 스레드 풀과 타임아웃으로 격리하기를 권장합니다.

---

### V-03. 고정된 키 이름과 단일 공유 스트림 때문에 워터마크를 쉽게 제거 — 🟡 Medium

| 항목 | 내용 |
|---|---|
| 위치 | `PdfForensicEmbedder.java:16` (`WM_KEY = "_k1"` 상수), `:43-51` (payload 스트림 1개만 생성), `:62-64` (모든 복제본이 같은 스트림 참조) |
| 공격자 | A1 |
| 악용 난이도 | 쉬움: 공개 소스에서 키 이름을 확인하고 딕셔너리 키 하나만 삭제하면 됨 |

**설명**
워터마크 위치를 표시하는 키 이름이 모든 문서에서 같은 상수 `/_k1`이고 오픈소스로 공개되어 있습니다. 주석에는 "페이지당 다중 삽입"이라고 되어 있지만, 실제로는 **하나의 COSStream 객체를 여러 FormXObject가 참조할 뿐**이라 중복 저장 효과가 없습니다. 0×0 클리핑 영역에 그려지므로(`:80-86`) 화면에 보이는 흔적도 없습니다.

**재현 결과 (PoC)**
```
[strip(_k1 removed)] valid=false reason=WATERMARK_NOT_FOUND   ← 모든 FormXObject에서 /_k1 키만 삭제
```

**영향**
유출 추적이라는 라이브러리 본래 목적을 무력화할 수 있습니다. 다만 결과가 "워터마크 없음"으로 **탐지 가능한 실패**이므로 V-01(잘못된 '정상' 판정)보다 한 단계 낮은 Medium으로 판정했습니다.

**조치 방안**
```java
// 1) 키 이름을 비밀키에서 파생해 문서·배포처마다 다르게 → 상수 검색으로 찾을 수 없게
static COSName deriveKeyName(byte[] hmacKey) throws Exception {
    Mac mac = Mac.getInstance("HmacSHA256");
    mac.init(new SecretKeySpec(hmacKey, "HmacSHA256"));
    byte[] h = mac.doFinal("kurbypdf/wm-key-name/v1".getBytes(StandardCharsets.US_ASCII));
    StringBuilder sb = new StringBuilder("_");
    for (int i = 0; i < 4; i++) sb.append(String.format("%02x", h[i]));
    return COSName.getPDFName(sb.toString());
}
// embed(doc, payload, hmacKey) 오버로드를 추가해 사용하고, Inspector도 같은 함수로 키를 찾음

// 2) 복제본마다 별도 COSStream 생성 (루프 안에서 createCOSStream)
```
- 완전한 제거 방지는 원리적으로 불가능합니다. 남는 위험을 줄이려면 본문 콘텐츠 스트림에 섞인 비가시 텍스트·미세 패턴 같은 **보조 워터마크**와 서버 측 다운로드 로그를 함께 쓰는 방식을 README에 안내하기를 권장합니다.
- 키 이름 파생은 기존 문서와 호환되지 않으므로 검증할 때 `_k1`과 파생 키를 모두 조회하는 이행 기간이 필요합니다.

---

### V-04. 위조 스트림 1개만 있어도 정상 워터마크 검증 전체가 실패 — 🔵 Low

| 항목 | 내용 |
|---|---|
| 위치 | `PdfWatermarkInspector.java:62-66` (스트림별 예외 처리 없음), `:33` (`extractFirst`가 첫 항목만 반환), `PdfVerificationUtil.java:40` |
| 공격자 | A1 |

**설명**
`extractAll()`은 발견한 `/_k1` 스트림마다 `decryptAndVerify()`를 호출하는데, 하나라도 복호화에 실패(`AEADBadTagException`)하면 **반복문 전체가 중단**됩니다. 또 `extractFirst()`는 서명 유효 여부와 관계없이 첫 항목을 반환하므로, 앞쪽에 무효 항목이 있으면 뒤의 정상 워터마크는 확인되지 않습니다.

**재현 결과 (PoC)**
```
[bogus(_k1 junk added)] valid=false reason=EXCEPTION:AEADBadTagException   ← 정상 워터마크가 그대로 있는데도 실패
```

**조치 방안** (검증 완료)
```java
// PdfWatermarkInspector.extractAll() :62-66
try {
    byte[] enc = streamToBytes(stream);
    out.add(decryptAndVerify(enc, hmacKey, aesKey));
} catch (GeneralSecurityException | IOException | IllegalArgumentException e) {
    // 위조·손상된 후보는 건너뛰고 나머지 워터마크 검사를 계속한다
}

// PdfVerificationUtil.verifyDetailed() :40 → 서명이 유효한 첫 항목을 선택
List<PdfWatermarkInspector.DecodedWatermark> all = PdfWatermarkInspector.extractAll(pdfBytes, hmacKey, aesKey, userPassword);
if (all.isEmpty()) return Result.fail("WATERMARK_NOT_FOUND");
PdfWatermarkInspector.DecodedWatermark dw = null;
for (PdfWatermarkInspector.DecodedWatermark c : all) { if (c.isSignatureValid()) { dw = c; break; } }
if (dw == null) return Result.fail("INVALID_SIGNATURE");
```
- 조치 후 재현: `[bogus(_k1 junk added)] valid=true claims={uid=victim-001}`
- 잘못된 비밀번호는 `PDDocument.load` 단계에서 예외가 나므로 기존처럼 실패합니다(`EXCEPTION:InvalidPasswordException`, 회귀 확인).

---

### V-05. PDF 권한이 과하고 암호 조합을 검증하지 않음 — 🔵 Low

| 항목 | 내용 |
|---|---|
| 위치 | `PdfProtector.java:9-11` (권한 설정), `:13` (owner/user 비교 없음), `KurbyPdf.java:35-41` (owner 암호만 지정한 경우) |

**설명**
1. `new AccessPermission()`은 **모든 권한을 허용한 상태로 생성**되는데, 코드는 추출 금지만 설정합니다. 그래서 수정·페이지 조립·주석 수정 권한이 그대로 열려 있어 V-01, V-03 공격을 PDF 편집기에서 바로 할 수 있습니다.
2. `ownerPassword == userPassword`이면 PDFBox는 owner 암호 일치를 먼저 확인하므로, 열람용 암호를 아는 수신자가 **소유자 권한(모든 제한 해제)** 을 얻습니다.
3. `userPassword` 없이 `ownerPassword`만 넘기면 암호화를 아무 알림 없이 건너뛰어, 호출자가 의도한 보호가 적용되지 않습니다(fail-open).

**재현 결과 (PoC)**
```
[perm owner==user] isOwnerPermission=true canExtract=true
[perm default]     canModify=true canAssemble=true canModifyAnnotations=true canExtract=false
[perm owner only]  isEncrypted=false returnedOwnerPwd=null
```
PDF 권한은 표준상 뷰어가 준수하는 **권고 성격**의 통제여서 영향이 제한적이므로 Low로 판정했습니다.

**조치 방안** (검증 완료)
```java
// PdfProtector.applyUserPassword()
if (ownerPassword == null || ownerPassword.isEmpty() || ownerPassword.equals(userPassword)) {
    throw new IllegalArgumentException("ownerPassword must be non-empty and differ from userPassword");
}
AccessPermission ap = new AccessPermission();
ap.setCanPrint(true);
ap.setCanExtractContent(false);
ap.setCanExtractForAccessibility(true);   // 접근성(스크린리더)은 유지
ap.setCanModify(false);
ap.setCanAssembleDocument(false);
ap.setCanModifyAnnotations(false);
ap.setCanFillInForm(false);
ap.setReadOnly();

// KurbyPdf.watermark() — owner 암호만 지정한 경우 명시적으로 거부
if ((req.getUserPassword() == null || req.getUserPassword().isEmpty())
        && req.getOwnerPassword() != null && !req.getOwnerPassword().isEmpty()) {
    throw new IllegalArgumentException("ownerPassword requires userPassword");
}
```
- 조치 후 재현: 세 경우 모두 거부되거나 `canModify=false canAssemble=false canModifyAnnotations=false`.
- 양식 입력이 필요한 PDF를 다루는 서비스라면 `setCanFillInForm`을 옵션으로 열어 둘 수 있습니다.

---

### V-06. 알려진 CVE가 있는 Jackson 2.17.1을 `api`로 노출 — 🔵 Low

| 항목 | 내용 |
|---|---|
| 위치 | `build.gradle.kts:28` (`api("com.fasterxml.jackson.core:jackson-databind:2.17.1")`) |
| 확인 방법 | OSV(api.osv.dev) 조회 (2026-11-14 기준) |

**설명**
| 패키지 | 권고 수 | 주요 항목 | 최소 수정 버전 (2.18 라인) |
|---|---|---|---|
| jackson-databind 2.17.1 | 12건 (High 5) | CVE-2026-54512 (PolymorphicTypeValidator 우회), CVE-2026-91777 (forward-reference 2차 시간 DoS) 등 | 2.18.11 |
| jackson-core 2.17.1 | 4건 (High 3) | CVE-2026-89407 (NumberInput ReDoS), CVE-2026-89425 등 | 2.18.11 |
| pdfbox / fontbox 2.0.30 | 0건 | - | (최신 2.0.37) |

**도달 가능성 검토**
라이브러리 코드는 `readTree()`와 `writeValueAsBytes()`만 사용하고, Default Typing이나 다형성 역직렬화는 쓰지 않습니다. `readTree()` 입력은 AES-GCM 인증을 통과한 복호문뿐이라 **키 없는 공격자는 Jackson에 임의 JSON을 넣을 수 없습니다.** 하지만 `api` 구성 때문에 취약 버전이 **라이브러리 사용자 프로젝트의 컴파일 클래스패스로 전이**되고, shadow JAR는 relocate된 상태로 고정 번들되어 사용자가 직접 패치할 수도 없습니다. 그래서 Low로 판정했습니다.

**조치 방안**
```kotlin
dependencies {
    api("org.apache.pdfbox:pdfbox:2.0.37")                                    // 공개 API(PDDocument) 노출 → api 유지
    implementation("com.fasterxml.jackson.core:jackson-databind:2.18.11")   // 내부 구현에만 사용 → implementation
}
```
- Jackson 2.18.x와 PDFBox 2.0.x는 모두 Java 8을 지원하므로 `options.release.set(8)` 설정과 호환됩니다. Maven Central에서 두 버전이 존재하는 것도 확인했습니다.
- Jackson 타입이 공개 API 시그니처에 없음을 확인했으므로 `implementation`으로 바꿔도 사용자 코드에는 영향이 없습니다.

---

### V-07. 키 길이·키 분리를 검증하지 않고 예외가 그대로 전파됨 — 🔵 Low

| 항목 | 내용 |
|---|---|
| 위치 | `KurbyPdf.java:24-25` (키 디코드 후 검증 없음), `PdfVerificationUtil.java:26-27` (Base64 예외 미처리) |

**설명**
- HMAC 키는 1바이트여도 허용되고, HMAC 키와 AES 키가 같아도 허용됩니다(키 분리 원칙 위반).
- `verifyBase64()`는 boolean을 반환한다고 문서화되어 있지만, 잘못된 Base64가 들어오면 `IllegalArgumentException`을 던집니다. 호출 측에서 예외 처리를 빠뜨리면 요청이 500 에러 등으로 중단될 수 있습니다.
- 위조하려면 AES-256-GCM 키도 필요하므로 약한 HMAC 키만으로는 직접 악용되지 않습니다. 그래서 Low로 판정했습니다.

**재현 결과 (PoC)**
```
[weakkey] 1-byte HMAC key accepted, verify=true
[weakkey] hmacKey==aesKey accepted, verify=true
[weakkey] verifyBase64 threw instead of returning false: java.lang.IllegalArgumentException: Illegal base64 character 21
```

**조치 방안** (검증 완료)
```java
// KurbyPdf.watermark() — 키 디코드 직후
if (hmacKey.length < 32) throw new IllegalArgumentException("hmacKey must be >= 32 bytes");
if (aesKey.length != 32) throw new IllegalArgumentException("aesKey must be 32 bytes (AES-256)");
if (MessageDigest.isEqual(hmacKey, aesKey)) throw new IllegalArgumentException("hmacKey and aesKey must differ");

// PdfVerificationUtil.verifyBase64()
try {
    byte[] hmac = Base64.getDecoder().decode(hmacKeyBase64);
    byte[] aes  = Base64.getDecoder().decode(aesKeyBase64);
    return verify(pdfBytes, userPassword, hmac, aes);
} catch (IllegalArgumentException e) {
    return false;
}
```
- 조치 후 재현: 1바이트 키는 `hmacKey must be >= 32 bytes`로 거부됩니다. 기존 테스트 키(각 32바이트, 서로 다름)는 그대로 통과합니다.

---

### V-08. 테스트 코드가 비밀번호를 표준출력에 기록하고 키를 하드코딩함 — ⚪ Info

- 위치: `KurbyPdfTest.java:24-29` (고정 키 `0x11`·`0x22`), `:80-82` (`ownerPwd`, `userPwd`, `claims` 출력), `:46-76` (암호화 결과 PDF를 `build/test-out`에 저장)
- 테스트 코드라 운영 영향은 없습니다. 다만 이 코드가 사용 예시로 복사되면 owner 암호가 CI 로그 등에 남을 수 있습니다.
- 조치: `System.out.println("ownerPwd=" + ownerPwd)` 줄을 삭제하거나 `assertNotNull(ownerPwd)`로 바꾸고, README 예시에 "owner 암호·키는 로그에 남기지 말 것"을 명시합니다.

### V-09. 워터마크 위치에 예측 가능한 난수를 사용 — ⚪ Info

- 위치: `PdfForensicEmbedder.java:23` (`System.currentTimeMillis()` 시드), `:40` (`java.util.Random`)
- 주석은 무작위 위치가 "보통 더 안전"하다고 설명하지만, 시드가 발급 시각이라 위치를 예측할 수 있습니다. 현재 구조에서는 V-03처럼 키 이름으로 바로 찾을 수 있으므로 추가 위험은 없습니다.
- 조치: 기본 `embed()`에서 `new SecureRandom().nextLong()`으로 시드를 만듭니다. 재현성이 필요할 때만 공개 오버로드로 시드를 넘기도록 유지합니다.

### V-10. Gradle Wrapper가 누락되었고 의존성 무결성을 검증하지 않음 — ⚪ Info

- `gradlew`는 커밋되어 있지만 `gradle/wrapper/gradle-wrapper.jar`와 `gradle-wrapper.properties`가 없어 Wrapper 빌드가 불가능합니다. 개발자가 임의 버전의 Gradle을 쓰게 되어 빌드 재현성이 떨어집니다.
- `gradle/verification-metadata.xml`(의존성 체크섬 검증)이 없습니다.
- README의 설치 안내(`README.md:25-40`)는 JAR 파일을 수동으로 복사하는 `system` scope 방식이라 배포본 무결성을 확인할 수단(체크섬·서명)이 없습니다.
- 조치: `gradle wrapper --gradle-version <버전>`으로 Wrapper 파일을 생성해 커밋하고, `distributionSha256Sum`을 설정합니다. `./gradlew --write-verification-metadata sha256 build`로 검증 메타데이터를 생성하고, 릴리스 JAR의 SHA-256을 README에 게시합니다.

---

## 4. 유형별 점검 결과 (누락 점검)

| 점검 유형 | 결과 | 비고 |
|---|---|---|
| 인젝션 (JSON / PDF 구조) | 해당 없음 | 사용자 claims는 Jackson으로 직렬화(이스케이프)됩니다. 생성되는 PDF 객체는 PDFBox API로 만들어지며 문자열 결합이 없습니다. |
| 인증 / 인가 | V-05 | PDF 암호·권한 설정 |
| 세션 관리 | 해당 없음 | 상태가 없는 라이브러리입니다. 세션·토큰을 다루지 않습니다. |
| 중요정보 노출 | V-08 | 운영 코드에는 로깅이 없습니다. `DecodedWatermark`·`Result`에 키는 포함되지 않습니다. |
| 암호화 | V-01, V-07, V-09 | AES-256-GCM(96bit 랜덤 IV, 128bit 태그)과 HMAC 상수 시간 비교는 적절합니다. |
| 파일 업로드 / 다운로드 | V-02 | 외부 PDF를 파싱할 때 자원 제한이 없습니다. 파일 시스템 경로는 다루지 않습니다(테스트 제외). |
| 에러 처리 | V-02, V-04, V-07 | 실패 사유로 예외 클래스명만 노출하므로 정보 노출은 없습니다. |
| 로깅 | 해당 없음 | 운영 코드에 로깅이 없어 감사 로그는 호출 측 책임입니다(README 안내 권장). |
| 의존성 / 공급망 | V-06, V-10 | |
| 동일 패턴 전수 검색 | 반영 완료 | 운영 코드의 `PDDocument.load` 2곳(`KurbyPdf.java:21`, `PdfWatermarkInspector.java:46`)을 확인했습니다. 발급 측(:21)은 서버 소유 PDF를 처리하는 경로라 V-02 범위에서 제외하고 동일 조치를 권고합니다. `Base64.getDecoder().decode` 5곳 중 4곳(`KurbyPdf.java:24-25`, `PdfVerificationUtil.java:26-27`)은 V-07에 포함하고, `PdfWatermarkInspector.java:135`는 상위 `catch`(`PdfVerificationUtil.java:53`)에서 처리되어 제외했습니다. `catch (Exception ignore)`는 close 호출에만 쓰여 문제가 없습니다. |

---

## 5. 조치 우선순위

| 순위 | ID | 이유 |
|---|---|---|
| 1 | V-01 | 잘못된 "정상" 판정은 유출자 오인·변조 문서 신뢰로 이어집니다. 오버로드 추가만으로 호환성을 유지하며 조치할 수 있습니다. |
| 2 | V-02, V-04 | 검증 API를 외부에 공개할 때 바로 필요합니다. 수정 범위가 `PdfWatermarkInspector` 한 파일에 집중되어 있습니다. |
| 3 | V-06, V-05, V-07 | 의존성 버전업과 입력 검증으로 짧은 시간에 조치할 수 있습니다. |
| 4 | V-03 | 키 파생 방식은 기존 문서와 호환되지 않으므로 이행 계획과 함께 진행해야 합니다. |
| 5 | V-08 ~ V-10 | 개발·배포 위생 개선 항목입니다. |

---

## 6. 재현·검증 환경

- 원본 소스와 조치 소스를 각각 `javac --release 8`로 컴파일하고, PDFBox 2.0.30 / Jackson 2.17.1 JAR(Maven Central)을 클래스패스에 넣었습니다.
- PoC 시나리오: `tamper`, `transplant`, `strip`, `bogus`, `bomb`, `perm`, `weakkey` (취약점 재현) / `fix-hash`, `regress` (조치 검증·회귀 확인)
- 회귀 확인: 기존 `KurbyPdfTest`와 같은 흐름(사용자 암호 `testpw123!` + owner 암호 자동 생성)이 조치 후에도 `valid=true`이고, 잘못된 암호는 계속 실패합니다.

---

## 7. 2차 검토 결과

### 7.1 검토 범위

| 검토 항목 | 수행 내용 | 결과 |
|---|---|---|
| 오탐 검증 | 10개 항목 모두 파일·라인을 다시 열어 확인했습니다. 6개 항목(V-01~V-05, V-07)은 PoC로 입력부터 취약 지점까지 실제 동작을 재현했습니다. 1차 후보 중 상위 방어로 차단되는 6건을 제외했습니다. | 확정 10건 / 제외 6건 |
| 누락 점검 | 저장소 18개 파일(설정·README·테스트 포함)을 모두 읽었는지 대조하고, 4장 유형별 점검과 동일 패턴 전수 검색을 수행했습니다. | V-06 추가 |
| 위험도 재평가 | "잘못된 정상 판정(High) vs 탐지 가능한 실패(Medium)" 기준으로 일관성을 점검했습니다. | 2건 조정 |
| 조치 방안 검증 | 조치 코드를 원본 사본에 적용해 Java 8 타깃으로 컴파일하고, 같은 PoC와 회귀 시나리오를 실행했습니다. | 1건 수정 |
| 정합성 확인 | 1장 통계(High 1 / Medium 2 / Low 4 / Info 3 = 10)와 3장 상세 항목 수, ID 순서, 파일 경로·라인 번호를 대조했습니다. | 일치 |

### 7.2 변경 내역

| 항목 | 변경 내용 | 사유 |
|---|---|---|
| V-01 | 1차의 "본문 변조 검증 통과"와 "워터마크 이식" 2건을 1건으로 **병합** | 근본 원인(문서와 연결되지 않은 서명)과 조치(해시 비교)가 같습니다. |
| V-03 / V-04 | 1차의 "워터마크 무력화" 1건을 제거(V-03)와 검증 방해(V-04)로 **분리** | 원인 코드(`Embedder` vs `Inspector:62-66`)와 조치가 다르고, V-04는 조치 코드로 완전히 해소됩니다. |
| V-02 | 조치 코드의 `MAX_MEMORY_BYTES`를 256MB에서 **64MB로 수정**하고 "힙보다 작게" 주의 문구 추가 | 재검증 중 상한 256MB·힙 256MB 조합에서 OOM이 여전히 발생했습니다. 64MB로 바꾼 뒤 `-Xmx256m`에서 정상 처리되는 것을 확인했습니다. |
| V-06 | **추가** (Low) | 1차 분석에는 의존성 점검이 빠져 있었습니다. OSV 조회 결과 Jackson 2.17.1에서 16건의 권고를 확인했습니다. |
| V-07 | 위험도 **Medium → Low** | 위조하려면 AES-256-GCM 키도 필요해, 약한 HMAC 키만으로는 직접 악용되지 않습니다. |
| V-09 | 위험도 **Low → Info** | V-03의 고정 키 이름으로 워터마크를 바로 찾을 수 있어 위치 예측에 따른 추가 위험이 없습니다. |
| 제외① Jackson 역직렬화 RCE | **오탐 제외** | Default Typing을 쓰지 않고(`readTree`만 사용), 입력이 GCM 인증을 통과해야 해서 키 없는 공격자는 도달할 수 없습니다. |
| 제외② HMAC 재직렬화 정규화 불일치로 서명 위조 | **오탐 제외** | 재직렬화한 body에 HMAC을 계산하지만, 그 원천 JSON이 GCM으로 인증되므로 키 없이 조작할 수 없습니다. |
| 제외③ HMAC 비교 타이밍 공격 | **오탐 제외** | `MessageDigest.isEqual`(상수 시간 비교)을 이미 사용합니다(`PdfWatermarkInspector.java:136`). |
| 제외④ GCM IV 재사용 | **오탐 제외** | `SecureRandom` 96bit IV를 매번 새로 생성합니다(`WatermarkPayload.java:51-52`). 같은 키로 2^32회 미만 사용하면 충돌 위험은 무시할 수준입니다. |
| 제외⑤ 실패 사유를 통한 정보 노출 | **오탐 제외** | `EXCEPTION:` 뒤에 예외 클래스명만 반환하고 메시지·스택은 노출하지 않습니다(`PdfVerificationUtil.java:54`). |
| 제외⑥ `KeyUtil.randomOwnerPassword(len)`의 len<4 처리 | **제외** (보안 영향 없음) | 공개 호출 경로는 기본값 32만 사용하고(`KurbyPdf.java:38`), len<4이면 오히려 4자로 보정됩니다. 생성 강도는 약 206bit(87종 문자 × 32자)로 충분합니다. |
