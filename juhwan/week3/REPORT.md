# KurbyPdf 보안 취약점 분석 보고서

## 1. 위험도별 탐지 통계

| 위험도 | 기준 (CVSS 3.1 기본 점수) | 탐지 수 | 취약점 ID |
|---|---|---:|---|
| Critical | 9.0 – 10.0 | 0 | – |
| High | 7.0 – 8.9 | 1 | KP-01 |
| Medium | 4.0 – 6.9 | 1 | KP-02 |
| Low | 0.1 – 3.9 | 3 | KP-03, KP-04, KP-05 [^kp05] |
| Info | 점수 없음 (보안 약점·개선 권고) | 2 | KP-06, KP-07 |
| **합계** | | **7** | |

[^kp05]: KP-05는 현재 코드 경로에서 도달 불가한 의존성 권고라 CVSS를 산정하지 않았다. 업스트림 최고 위험도(HIGH)와 배포 경로(`api` 전이·fat JAR relocate 은닉)를 고려해 Low로 분류했다.

| ID | 위험도 | 제목 | 위치 | 로컬 PoC |
|---|---|---|---|---|
| KP-01 | High (7.5) | 검증 경로에서 외부 PDF로 무제한 메모리/스택 사용(DoS) | `PdfWatermarkInspector.java:46,56,80-94` | 재현됨 |
| KP-02 | Medium (5.9) | 워터마크가 문서 내용과 묶이지 않아 이식·변조를 못 잡음 | `WatermarkPayload.java:27-31` | 재현됨 |
| KP-03 | Low (3.3) | 워터마크를 쉽게 찾아 제거하거나 검증을 깨뜨릴 수 있음 | `PdfWatermarkInspector.java:51-71` | 재현됨 |
| KP-04 | Low (2.2) | 키 길이·키 분리를 검증하지 않음 | `KurbyPdf.java:24-25` | 재현됨 |
| KP-05 | Low (CVSS 미산정) | 알려진 취약점이 있는 jackson 2.17.1 사용, fat JAR에 relocate로 숨겨 배포 | `build.gradle.kts:28,64` | 해당 없음 |
| KP-06 | Info | PDF 권한을 넓게 허용하고, 사용자 암호만 있으면 보호를 해제할 수 있음 | `PdfProtector.java:9-16` | 재현됨 |
| KP-07 | Info | 테스트 코드가 PDF 암호를 표준 출력에 기록 | `KurbyPdfTest.java:80-81` | 코드 확인 |

> 검증: 위 표의 합계 7 = 본문 `### KP-` 항목 수 7.

## 2. 분석 개요

| 항목 | 내용 |
|---|---|
| 대상 | https://github.com/juwonlee-dev/KurbyPdf (Java 라이브러리, PDF 숨김 워터마크 삽입·검증) |
| 분석 커밋 | `74d3aedeea9204694a8bc1e04e75edaa75add94d` (2025-09-22, "feat: Add README", 전체 커밋 4개) |
| clone 위치 | 저장소 밖 임시 디렉토리 `mktemp -d` → `/var/folders/lk/1mm7j3815g120x8z7skfzz4c0000gn/T/tmp.nsgGxU8OtN/KurbyPdf` |
| 범위 | `src/main/java` 9개 파일(557줄), `src/test`, `build.gradle.kts`, README |
| 의존성(실제 버전) | `pdfbox 2.0.30`(→ `fontbox 2.0.30`, `commons-logging 1.2`), `jackson-databind 2.17.1`(→ `jackson-core/annotations 2.17.1`), 빌드 플러그인 `shadow 8.1.1` |
| 방법 | 전체 소스를 정독하며 입력 → 처리 → 위험 지점(sink) 호출 경로 추적, OSV(api.osv.dev)로 정확한 버전 조회, 로컬 PoC |
| 로컬 실행 환경 | Corretto JDK 17.0.8.1, `javac --release 8`. 저장소에 `gradle/wrapper/`가 없어 `./gradlew`를 실행할 수 없음. 그래서 Maven Central의 같은 버전 jar로 직접 컴파일함 |
| 작업 규칙 | `juhwan/CLAUDE.md`(Task1)를 먼저 읽고 그 규칙을 따름: 저장소 밖에 clone, SHA 기록, 외부 게시 금지, 원격 공격 금지(로컬 PoC만), 호출 경로를 추적한 것만 보고, 확인하지 못한 내용은 "확인 필요"로 표시, 행 번호는 `cat -n`으로 다시 확인 |

**전제(가정):** KurbyPdf는 라이브러리입니다. 그래서 위험도는 README가 설명하는 사용 형태를 기준으로 매겼습니다. 서버가 유출된 PDF나 외부에서 제출한 PDF를 받아 `PdfVerificationUtil.verify*`로 유출자를 확인하는 형태입니다. 호출자가 신뢰할 수 있는 PDF만 다룬다면 KP-01의 위험도는 내려갑니다.

## 3. 취약점 상세

### KP-01 검증 경로에서 외부 PDF로 무제한 메모리/스택 사용 (DoS)

- **위험도:** High, CVSS 3.1 `AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H` = **7.5** (CWE-409, CWE-400, CWE-674)
  - 근거: 키나 암호 없이 1MB짜리 PDF 하나로 검증 서버의 힙(또는 스택)을 소진시킬 수 있습니다. 앞의 "전제"가 적용됩니다.
- **같은 근본 원인의 세 가지 sink(2차 검토로 (b)·(c) 추가):** 검증 경로는 외부 PDF를 상한 없는 기본 `MemoryUsageSetting`으로 로드하고(`:46`), 페이지의 모든 XObject를 먼저 객체화한 뒤(`:56`) Form XObject의 `/_k1`을 읽습니다(`:59-64`). 세 지점 모두 입력 크기와 중첩 깊이에 상한이 없습니다. 공통 조치는 `:46`의 `MemoryUsageSetting` 상한을 **필수**로 거는 것입니다(디스크 스크래치 상한으로 힙 폭주를 막음).
- **위치:**
  - (a) `PdfWatermarkInspector.java:80-94`: `streamToBytes()`가 `/_k1` 스트림을 상한 없이 `ByteArrayOutputStream`으로 읽음(압축은 그 앞 `:83` `createInputStream()`에서 풀림).
  - (b) `PdfWatermarkInspector.java:56`: `res.getXObject(name)`. `instanceof PDFormXObject` 검사(`:57`)보다 **먼저** 모든 XObject를 객체화하므로, `/Filter [/FlateDecode /JPXDecode]` Image XObject는 `PDImageXObject` 생성자에서 전체가 디코딩됨. `_k1`도 필요 없음.
  - (c) `PDDocument.load`의 PDF 파서(`:46`): 깊게 중첩된 배열/딕셔너리는 재귀 파싱(`BaseParser.parseCOSArray`)에서 `StackOverflowError`를 냄.
  - `PdfWatermarkInspector.java:46`: `PDDocument.load(bin[, password])`. 기본 `MemoryUsageSetting`(메인 메모리만 쓰고 상한 없음).
  - `PdfVerificationUtil.java:53`: `catch (Exception e)`만 있어서 `OutOfMemoryError`·`StackOverflowError`가 호출자까지 그대로 전파됩니다.
  - `KurbyPdf.java:21`: 삽입 경로도 같은 방식으로 상한 없이 로드합니다(외부 업로드 PDF에 워터마크를 넣는 서비스일 때).
- **설명:** 호출 경로는 `verify()` → `verifyDetailed():40` → `extractFirst():32` → `extractAll():46,56,64` 순서입니다. (a)에서 `COSStream.createInputStream()`은 `/FlateDecode` 필터를 풀면서 읽는데, 정상 삽입기는 필터 없이 기록합니다(`PdfForensicEmbedder.java:47` `createOutputStream()`). 따라서 필터가 붙은 `_k1`은 위조이지만 검사기가 걸러내지 않습니다. (b)는 `_k1`과 무관하게 모든 이미지 XObject를 디코딩하므로 `streamToBytes()` 필터 검사로는 막지 못합니다. (c)는 파서 단계라 어떤 스트림 검사보다도 앞섭니다. 세 경로 모두 AES-GCM 복호화(`:105`)보다 먼저 일어나므로 키가 없어도 공격할 수 있습니다.
- **재현 (로컬):**
  - (a) `/_k1` Flate 폭탄: 빈 PDF의 Form XObject `/_k1`에 `/Filter /FlateDecode` 스트림(0x00 1GiB → deflate 9)을 붙임. 결과 **1,044,783바이트**.
  - (b) Image XObject 폭탄: 1×1 DeviceGray 이미지 `/Filter [/FlateDecode /JPXDecode]`에 0x00 1GiB → deflate 9. 결과 약 1,044,370바이트. `_k1` 없음.
  - (c) 깊은 중첩: 페이지 객체에 `[`를 10만 번 중첩한 배열. 결과 약 200KB.
  ```text
  (a) java -Xmx256m ... verify bomb.pdf      → OutOfMemoryError (java.io.ByteArrayOutputStream.toByteArray)
                                                 at PdfWatermarkInspector.streamToBytes:90 → extractAll:64
      java -Xmx4g  ... verify bomb.pdf        → OutOfMemoryError (최대 RSS 2,493,775,872 B)
  (b) java -Xmx256m ... verify imgbomb.pdf    → OutOfMemoryError
                                                 at ...PDImageXObject.<init> → PDResources.getXObject
                                                 at PdfWatermarkInspector.extractAll:56
  (c) java ... verify deep.pdf                → StackOverflowError (깊이 9743)
                                                 at BaseParser.parseCOSArray → PDDocument.load
                                                 at PdfWatermarkInspector.extractAll:46
  ```
  - 공격 시나리오: "유출 문서 신고·검증" 업로드 창구에 (a)/(b)/(c) 중 하나를 반복해 올리면 검증 서버 JVM이 OOM 또는 StackOverflow로 쓰러집니다. `verify()`는 boolean만 반환한다고 문서화되어 있어 호출자가 `Error`까지 대비하기도 어렵습니다.
- **조치 방안:**
  1. `:46`의 `MemoryUsageSetting` 상한을 **필수**로 적용합니다(힙 폭주 (a)(b)를 함께 막는 1차 방어). 로컬에서 Image 폭탄 (b)는 상한을 걸자 `IOException: Maximum allowed scratch file memory exceeded.`로 **948ms** 만에 거부됐습니다.
  2. `streamToBytes()`의 필터·크기 검사는 `/_k1` 전용 보조 방어로 둡니다(필터 붙은 `_k1`을 위조로 거부). (a) 폭탄 PDF는 이 패치 적용 후 `-Xmx256m`에서 **163ms** 만에 `EXCEPTION:IOException`으로 거부되고 정상 워터마크 검증은 계속 `valid=true`였습니다.
  3. (c) 파서 스택 소진: pdfbox를 **2.0.37**로 올리면 막힙니다. 같은 `deep.pdf`가 2.0.30에서는 `StackOverflowError`, 2.0.37에서는 `EXCEPTION:IOException`으로 거부됨을 로컬에서 확인했습니다(중첩 한도 추가). `verifyDetailed()` 시작부의 입력 크기 상한(예: `pdfBytes.length > 50MB` → `Result.fail("PDF_TOO_LARGE")`)으로 부분 완화됩니다.
  ```java
  // PdfWatermarkInspector.java
  import org.apache.pdfbox.io.MemoryUsageSetting;

  private static final int MAX_WM_BYTES = 64 * 1024; // 정상 페이로드는 수백 바이트

  // :46 교체 — 메인 메모리 32MB, 전체 256MB 상한 (필수)
  MemoryUsageSetting mem = MemoryUsageSetting.setupMixed(32L * 1024 * 1024, 256L * 1024 * 1024);
  doc = PDDocument.load(bin, password == null ? "" : password, mem);

  // :80-94 교체
  private static byte[] streamToBytes(COSStream s) throws IOException {
      // 삽입기는 필터 없이 기록하므로(PdfForensicEmbedder.java:47) 필터가 붙은 _k1은 위조로 간주
      if (s.getFilters() != null) throw new IOException("unexpected filter on watermark stream");
      if (s.getLength() > MAX_WM_BYTES) throw new IOException("watermark stream too large");
      try (InputStream in = s.createInputStream()) {
          ByteArrayOutputStream bout = new ByteArrayOutputStream();
          byte[] buf = new byte[8192];
          int r;
          while ((r = in.read(buf)) != -1) {
              if (bout.size() + r > MAX_WM_BYTES) throw new IOException("watermark stream too large");
              bout.write(buf, 0, r);
          }
          return bout.toByteArray();
      }
  }
  ```
  - (b)를 더 확실히 막으려면 `:55-57`을 COS 수준 검사로 바꿔 이미지 XObject를 아예 객체화하지 않습니다: `res.getCOSObject().getCOSDictionary(COSName.XOBJECT)`에서 `/Subtype /Form`인 항목만 골라 `_k1`을 읽습니다.
  - `KurbyPdf.java:21`에도 같은 `MemoryUsageSetting`을 적용합니다. 상한은 문서 1건 기준이므로, 호출자 쪽에서 동시 검증 수도 제한하도록 한 줄 권고를 README에 둡니다.

### KP-02 워터마크가 문서 내용과 묶이지 않아 이식·변조를 못 잡음

- **위험도:** Medium, CVSS 3.1 `AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N` = **5.9** (CWE-345, CWE-347)
  - 근거: 피해자 명의로 워터마크가 들어간 PDF를 하나 손에 넣어야 하므로 AC:H입니다. 대신 검증 결과(누가 유출했는가)를 완전히 바꿔 놓을 수 있으므로 I:H입니다.
- **위치:**
  - `WatermarkPayload.java:27-31`: 서명 대상이 `v, claims, ts, nonce`뿐입니다. 문서 해시나 페이지 정보가 없습니다.
  - `PdfWatermarkInspector.java:122-136`: 검증도 같은 4개 필드만 다시 계산합니다.
  - `PdfVerificationUtil.java:45-52`: 서명만 맞으면 `Result.ok`를 반환합니다.
  - README "삽입된 워터마크의 존재 여부, 무결성, 위변조 여부 확인 가능", "AES-GCM + HMAC-SHA256 적용, 위변조 방지"
- **설명:** `_k1` 스트림은 그 자체로 완결된 암호문(IV‖CT)입니다. 그래서 키가 없어도 원시 바이트를 그대로 다른 PDF에 복사할 수 있습니다. 검증기는 이 스트림이 원래 어느 문서에 들어 있었는지 확인하지 않습니다. `nonce`는 기록되지만 발급 이력과 대조하지 않으므로 재사용도 막지 못합니다. 결국 README의 "위변조 확인"은 워터마크 페이로드에만 해당하고, 문서 본문은 보호하지 않습니다.
- **재현 (로컬):**
  ```text
  [B-0] alice 원본                         -> valid=true claims={uid=alice}
  [B-1] 다른 문서에 alice 워터마크 이식        -> valid=true claims={uid=alice}   ← 키 없이 _k1 원시 바이트만 복사
  [B-2] alice 문서 본문 변조 후               -> valid=true claims={uid=alice}   ← "TAMPERED: amount = 999,999" 추가
  ```
  - 공격 시나리오 1 (오귀속): 실제 유출자 bob이 유출할 문서에서 자기 워터마크를 지우고(KP-03), alice 문서의 `_k1`을 붙여 넣습니다. 검증 결과는 "alice가 유출"이 됩니다.
  - 공격 시나리오 2 (변조 미탐지): 받은 계약서 본문을 고쳐도 `verify()`는 `true`를 반환합니다. "정상 문서"라는 근거로 오용될 수 있습니다.
- **조치 방안:** 삽입 전에 원본 콘텐츠 스트림의 다이제스트를 서명 대상 claims에 넣고, 검증 시 다시 계산해 비교합니다. **단, 2차 검토에서 이 다이제스트만으로는 본문 변조(시나리오 2)를 완전히 막지 못함이 확인되었습니다. 아래 조치는 "이식 탐지"(시나리오 1: 다른 문서로 `_k1` 복사)에 한정해 유효하며, 변조 탐지는 뒤의 발급 기록 대조로 보완해야 합니다.**
  - 한계 (2차 검토): 검증 시 `ContentDigest.of(doc, true)`는 페이지의 **마지막 콘텐츠 스트림을 내용 확인 없이 제외**합니다. 공격자가 그 마지막 스트림을 `q … /Fm0 Do Q` + 보이는 변조 텍스트로 바꾸면 나머지 스트림 다이제스트는 그대로라 통과합니다. 또 다이제스트 대상이 콘텐츠 스트림뿐이라, 이름으로 참조되는 이미지·폰트 XObject 데이터와 `/Annots`(FreeText 주석·양식 값)는 바꿔도 탐지하지 못합니다.
  - 아래 `ContentDigest` 계산 자체는 로컬에서 확인했습니다(이식·변조 모두 값이 달라짐). 하지만 위 한계 때문에 "본문 변조 전면 차단"으로 주장하지 않습니다.
  ```java
  // 신규: ContentDigest.java — 페이지별 콘텐츠 스트림(디코딩 후) SHA-256
  static String of(PDDocument doc, boolean excludeLast) throws IOException, NoSuchAlgorithmException {
      MessageDigest md = MessageDigest.getInstance("SHA-256");
      for (PDPage page : doc.getPages()) {
          List<COSStream> streams = new ArrayList<>();
          COSBase c = page.getCOSObject().getDictionaryObject(COSName.CONTENTS);
          if (c instanceof COSStream) streams.add((COSStream) c);
          else if (c instanceof COSArray) for (COSBase b : (COSArray) c) {
              COSBase o = b instanceof COSObject ? ((COSObject) b).getObject() : b;
              if (o instanceof COSStream) streams.add((COSStream) o);
          }
          int n = excludeLast && !streams.isEmpty() ? streams.size() - 1 : streams.size(); // 마지막 = 워터마크 스트림
          for (int i = 0; i < n; i++) try (InputStream in = streams.get(i).createInputStream()) {
              byte[] buf = new byte[8192]; int r; while ((r = in.read(buf)) != -1) md.update(buf, 0, r);
          }
          md.update((byte) 0x1E); // 페이지 구분
      }
      return Base64.getEncoder().encodeToString(md.digest());
  }

  // KurbyPdf.java:26-28 — 호출자 Map을 바꾸지 않도록 복사 후 바인딩 값 추가
  Map<String, String> claims = new HashMap<>(req.getClaims());
  claims.put("_cd", ContentDigest.of(doc, false));
  byte[] payload = WatermarkPayload.buildPayload(claims, hmacKey, aesKey);

  // PdfForensicEmbedder.java:59 — resetContext=true는 맨 앞에 "q" 스트림을 끼워 넣어 원본 스트림 배열을 바꾸므로 false로 변경
  //   (각 복제본은 이미 :80/:86에서 save/restoreGraphicsState로 감싸져 있음)
  new PDPageContentStream(doc, page, PDPageContentStream.AppendMode.APPEND, true, false)

  // PdfWatermarkInspector.extractAll() — 문서 로드 직후 한 번 계산하고, :136 판정에 결합
  String cd = ContentDigest.of(doc, true);
  boolean valid = MessageDigest.isEqual(expect, got) && cd.equals(claims.get("_cd"));
  ```
  - 이 패치를 적용하면 `_cd`가 없는 기존 문서는 `valid=false`가 됩니다. 호환이 필요하면 `Result`에 `contentBound` 플래그를 따로 두는 편이 낫습니다. `extractAll()`에서 계산한 `cd`를 `:136` 판정에 쓰려면 `decryptAndVerify(...)`(`:96`) 시그니처에 `cd`를 넘기도록 바꿔야 하므로, 위 한 줄은 그대로 적용되지 않고 시그니처 수정이 함께 필요합니다.
  - **변조 탐지(권장): 발급 기록 대조.** 발급 시 `nonce → (수신자, fileId, SHA-256(출력 PDF 바이트))`를 서버에 저장합니다. 검증 시 제출된 PDF 바이트 해시를 이 기록과 비교해, 다르면 "워터마크는 유효하나 문서가 발급본과 다름"으로 보고합니다. 이렇게 하면 마지막 스트림·리소스·주석 변조까지 모두 잡히고, 재사용(동일 nonce 재제출)도 함께 탐지됩니다.
  - README의 "위변조 방지" 문구는 "워터마크 페이로드 위변조 방지"로 범위를 좁혀 고칩니다(문서 본문 무결성은 발급 기록 대조로 보장).

### KP-03 워터마크를 쉽게 찾아 제거하거나 검증을 깨뜨릴 수 있음

- **위험도:** Low, CVSS 3.1 `AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N` = **3.3** (CWE-693)
  - 근거: 열람 권한이 있는 정당한 수신자(PR:L)가 로컬에서 추적 기능을 무력화하는 공격입니다. README도 "강력한 DRM 대체 수단은 아님"이라고 적고 있어 Low로 매겼습니다.
- **위치:**
  - `PdfForensicEmbedder.java:16`: 고정된 키 이름 `/_k1`. 모든 문서가 같은 이름을 쓰므로 검색 한 번으로 찾을 수 있습니다.
  - `PdfWatermarkInspector.java:64-66`: 스트림 하나라도 복호화에 실패하면 예외가 루프 밖으로 전파되어 문서 전체 검증이 실패합니다.
  - `PdfWatermarkInspector.java:31-33`: 첫 번째 워터마크만 판정에 씁니다.
  - `PdfForensicEmbedder.java:23,40`: 위치 난수로 `new Random(System.currentTimeMillis())`를 씁니다. 예측할 수 있습니다.
- **설명:** 유출자는 사용자 암호로 문서를 연 뒤 `/_k1`을 가진 XObject를 지우면 추적을 피할 수 있습니다. 지우지 않더라도 쓰레기 `_k1` 스트림을 하나 앞에 끼워 넣으면, 정상 워터마크가 남아 있어도 검증이 실패합니다.
- **재현 (로컬):**
  ```text
  [C-0] bob 원본(사용자 암호 pw)                     -> valid=true  claims={uid=bob}
  [C-1] 20바이트 쓰레기 _k1 스트림 1개를 앞에 추가      -> valid=false reason=EXCEPTION:ProviderException
  [C-2] /_k1 Form XObject 제거                     -> valid=false reason=WATERMARK_NOT_FOUND
  ```
- **조치 방안:**
  ```java
  // PdfWatermarkInspector.java:64-66 — 스트림별 실패를 격리하고 계속 탐색
  // 2차 검토: C-1 PoC가 실제로 던지는 예외는 java.security.ProviderException(RuntimeException)이다.
  //          GCM 복호화 시 CT가 너무 짧으면 javax.crypto.ShortBufferException을 ProviderException으로 감싸 던지므로
  //          GeneralSecurityException 목록만으로는 잡히지 않는다 → ProviderException을 반드시 포함한다.
  try {
      out.add(decryptAndVerify(streamToBytes(stream), hmacKey, aesKey));
  } catch (GeneralSecurityException | java.security.ProviderException | IOException | IllegalArgumentException e) {
      continue; // 위조/손상 스트림은 무시
  }

  // PdfWatermarkInspector.java:31-33 — 첫 번째가 아니라 유효한 것을 선택
  for (DecodedWatermark d : list) if (d.isSignatureValid()) return d;
  return null;

  // PdfForensicEmbedder.java:40 — 위치 난수는 SecureRandom 사용 (시드 지정 오버로드는 테스트 전용으로 분리)
  Random rnd = new java.security.SecureRandom();
  ```
  - 키 이름은 비밀 키에서 유도합니다(예: `HMAC(hmacKey, "kurbypdf-name")` 앞 8바이트를 hex로). 이렇게 하면 `/_k1` 같은 고정 문자열 검색으로는 찾지 못합니다. 다만 구조 분석으로 찾아 지우는 것까지 막을 수는 없습니다. 추적이 중요하면 보이는 워터마크나 서버 측 배포 로그를 함께 쓰라고 README에 적습니다.
  - 유효한 워터마크가 둘 이상이고 claims가 서로 다르면(공격자가 이식한 유효 워터마크를 앞에 둔 경우) `Result.fail("CONFLICTING_WATERMARKS")`로 처리합니다. 이 분기 수정은 **미검증**입니다(패치를 적용해 실행하지 않음).

### KP-04 키 길이·키 분리를 검증하지 않음

- **위험도:** Low, CVSS 3.1 `AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:L/A:N` = **2.2** (CWE-326, CWE-1204 계열의 키 관리 약점)
  - 근거: 호출자가 키를 잘못 쓸 때만 문제가 됩니다. 또 위조하려면 AES-GCM 키도 필요하므로 영향은 제한적입니다.
- **위치:**
  - `KurbyPdf.java:24-25`: Base64 디코딩 결과를 검증 없이 사용합니다.
  - `WatermarkPayload.java:37,55`, `PdfWatermarkInspector.java:104,131`: 키를 그대로 `SecretKeySpec`에 넣습니다.
  - `PdfVerificationUtil.java:36`: null 여부만 검사합니다.
  - `PdfVerificationUtil.java:26-27`: `verifyBase64()`의 `Base64.getDecoder().decode()`가 `try` 밖에 있어, boolean을 반환한다고 문서화된 API가 잘못된 Base64 입력에 `IllegalArgumentException`을 던집니다(2차 검토 추가).
  - `KeyUtil`에는 키를 생성하는 함수가 없습니다. 암호 생성 함수만 있습니다.
- **설명:** HMAC 키가 1바이트여도 동작합니다. HMAC 키와 AES 키가 같아도 막지 않습니다. 잘못된 Base64는 `IllegalArgumentException`으로 그대로 터집니다. README 예제는 `hmacKey`, `aesKey`를 어디서 만드는지 설명하지 않아, 호출자가 약한 키를 쓰도록 방치합니다.
- **재현 (로컬):**
  ```text
  [D-1] 1바이트 HMAC 키(0x01)로 삽입/검증   -> valid=true
  [D-2] HMAC 키 == AES 키                -> valid=true
  ```
- **조치 방안:**
  ```java
  // KurbyPdf.watermark() 및 PdfVerificationUtil.verifyDetailed() 진입부에서 공통 호출
  static void checkKeys(byte[] hmacKey, byte[] aesKey) {
      if (hmacKey == null || hmacKey.length < 32) throw new IllegalArgumentException("hmacKey must be >= 32 bytes");
      if (aesKey == null || (aesKey.length != 16 && aesKey.length != 24 && aesKey.length != 32))
          throw new IllegalArgumentException("aesKey must be 16/24/32 bytes");
      if (MessageDigest.isEqual(hmacKey, aesKey)) throw new IllegalArgumentException("hmacKey and aesKey must differ");
  }

  // KeyUtil.java — 키 생성 함수 제공
  public static byte[] randomKey(int bytes) { byte[] k = new byte[bytes]; RND.nextBytes(k); return k; }
  ```
  - `checkKeys()`를 `verifyDetailed()`에서 throw로 쓰면 `Result` 기반 API 계약(`:32-56`)이 깨집니다. 검증 쪽에서는 throw 대신 `return Result.fail("INVALID_KEYS")`를 쓰고, throw는 `KurbyPdf.watermark()`에서만 합니다. 같은 맥락에서 `verifyBase64()`의 `decode()`도 `try` 안으로 옮겨 `IllegalArgumentException`을 `false`(또는 `Result.fail`)로 바꿉니다.

### KP-05 알려진 취약점이 있는 jackson 2.17.1 사용, fat JAR에 relocate로 숨겨 배포

- **위험도:** Low. CVSS는 해당 없음. KurbyPdf 코드 경로에서 도달할 수 없기 때문입니다. 업스트림 권고 중 최고 위험도는 HIGH입니다. (CWE-1395)
- **위치:**
  - `build.gradle.kts:28`: `api("com.fasterxml.jackson.core:jackson-databind:2.17.1")`
  - `build.gradle.kts:27`: `pdfbox:2.0.30`
  - `build.gradle.kts:59-64`: `shadowJar`가 pdfbox와 jackson을 `io.github.juwonlee.shadow.*`로 relocate합니다.
- **설명:** OSV에서 정확한 버전으로 조회한 결과입니다(2026-11-20).
  - `jackson-databind 2.17.1`: 12건 (예: GHSA-j3rv-43j4-c7qm/CVE-2026-54512 다형성 검증 우회 HIGH, GHSA-hgj6-7826-r7m5/CVE-2026-54514 `InetSocketAddress` 역직렬화 시 즉시 DNS 조회(SSRF), GHSA-wjgm-6hv5-3cvf/CVE-2026-19032 `Path` 역직렬화)
  - `jackson-core 2.17.1`: 4건 (예: GHSA-p6pp-m3f8-5c89/CVE-2026-89407 `NumberInput.looksLikeValidNumber` ReDoS, GHSA-7hhh-6rmp-j9qf/CVE-2026-89425 `DataInput` 파서)
  - `pdfbox/fontbox 2.0.30`, `commons-logging 1.2`, `jackson-annotations 2.17.1`, `shadow 8.1.1`: 0건
  - 2.18 계열에서 위 권고가 모두 고쳐진 버전은 `2.18.11`입니다(각 권고의 fixed 값 중 최댓값). Maven Central에는 `2.18.12`가 있습니다.
- **도달성 추적:** KurbyPdf가 jackson을 쓰는 곳은 `ObjectMapper.writeValueAsBytes(Map)`(`WatermarkPayload.java:33,48`, `PdfWatermarkInspector.java:128`)과 `ObjectMapper.readTree(byte[])`(`PdfWatermarkInspector.java:107`)뿐입니다.
  - `readTree`의 입력은 AES-GCM 복호화(`:105`)에 성공한 평문입니다. 즉 AES 키를 가진 사람만 이 입력을 만들 수 있습니다.
  - 코드에 `@JsonTypeInfo`, default typing, record, `Path`·`InetSocketAddress`·`Duration` 바인딩, async·`DataInput` 파서 사용이 없습니다.
  - ReDoS 권고(GHSA-p6pp-m3f8-5c89)의 `NumberInput.looksLikeValidNumber`는 **도달 불가로 확인**했습니다(2차 검토): `jackson-databind-2.17.1.jar` 안에서 이 메서드를 참조하는 클래스가 0개이고, `TextNode.asInt/asLong`은 `NumberInput.parseAsInt/parseAsLong`만 호출하며 그 안에서 `Integer.parseInt`/`Long.parseLong`/`parseDouble`만 부릅니다(`javap -c` 확인). 1차의 "확인 필요"를 해소합니다.
  - 따라서 현재 코드에서 외부 공격자가 이 권고들에 도달할 수는 없다고 판단했습니다.
  - 다만 `api(...)` 선언이라 이 버전이 소비자 프로젝트의 컴파일 클래스패스로 전이됩니다. 또 fat JAR은 패키지를 relocate하므로, 소비자의 SCA 도구가 `io.github.juwonlee.shadow.jackson` 안의 취약 버전을 찾아내지 못하고 소비자가 따로 올릴 수도 없습니다.
- **조치 방안:**
  ```kotlin
  // build.gradle.kts:26-29
  dependencies {
      api("org.apache.pdfbox:pdfbox:2.0.37")                              // 2.0.x 최신 패치 (변경 내역 확인 필요)
      implementation(platform("com.fasterxml.jackson:jackson-bom:2.18.12")) // core/databind/annotations 동시 고정
      implementation("com.fasterxml.jackson.core:jackson-databind")        // 공개 API에 jackson 타입이 없으므로 api → implementation
      ...
  }
  ```
  - 배포 문서에 fat JAR에 들어 있는 라이브러리 버전을 적습니다. CI에는 OWASP Dependency-Check나 OSV-Scanner를 넣습니다.
  - Java 8 호환을 유지하려면 jackson 2.18.x를 권장합니다. 2.19 이후 계열의 Java 8 지원 여부는 **확인 필요**입니다.

### KP-06 PDF 권한을 넓게 허용하고, 사용자 암호만 있으면 보호를 해제할 수 있음

- **위험도:** Info (CWE-276). 약점이지만 PDF 표준 보안 처리기 자체의 한계에 가깝습니다.
- **위치:** `PdfProtector.java:9-16`, `KurbyPdf.java:35-41`
- **설명:**
  - `new AccessPermission()`은 기본적으로 모든 권한을 허용합니다(PDFBox 2.0.30 `AccessPermission` 기본값 = `~3`, 2차 검토에서 소스로 확인). 코드는 그중 `setCanExtractContent(false)`만 끕니다. 그래서 수정(`canModify`), 페이지 조립, 주석·양식 수정은 그대로 허용됩니다.
  - `userPassword`가 비어 있으면(`KurbyPdf.java:35`) `if` 블록 전체를 건너뛰므로 암호화·권한이 전혀 적용되지 않고, **호출자가 넘긴 `ownerPassword`까지 조용히 무시됩니다**(`:35-41`). "열람은 자유, 편집만 제한"(소유자 암호만 설정) 용도가 동작하지 않습니다. 이 경우 명시적 신호는 없고 `WatermarkResult.getOwnerPassword()`가 `null`이라는 간접 신호만 있습니다(`:34,45`) — 즉 **명시적 `encrypted` 플래그가 없는** 것이 문제입니다.
  - `ownerPassword == userPassword`인 경우도 막지 않습니다. 이 경우 사용자 암호로 열면 소유자 권한을 얻습니다.
  - KP-03 PoC에서는 사용자 암호로 연 문서에 `setAllSecurityToBeRemoved(true)`를 호출해 암호를 해제한 사본을 저장할 수 있었습니다(로컬에서 확인). 권한 비트는 강제력이 없는 권고일 뿐이라는 뜻입니다.
- **조치 방안:**
  ```java
  // PdfProtector.applyUserPassword()
  if (ownerPassword.equals(userPassword)) throw new IllegalArgumentException("owner password must differ from user password");
  AccessPermission ap = new AccessPermission();
  ap.setCanPrint(true);
  ap.setCanExtractContent(false);
  ap.setCanModify(false);
  ap.setCanAssemble(false);
  ap.setCanModifyAnnotations(false);
  ap.setCanFillInForm(false);
  ```
  - README에 "권한 비트는 협조적인 뷰어에서만 지켜짐"이라고 적습니다. `WatermarkResult`에 `encrypted` 여부도 함께 반환합니다.

### KP-07 테스트 코드가 PDF 암호를 표준 출력에 기록

- **위험도:** Info (CWE-532). 테스트 코드라서 운영 경로에는 영향이 없습니다.
- **위치:** `src/test/java/.../KurbyPdfTest.java:80-81`(`ownerPwd`, `userPwd` 출력), `:24-29`(고정 키 0x11/0x22)
- **설명:** CI 로그에 자동 생성된 소유자 암호가 남습니다. 이 코드를 사용 예제로 그대로 복사하면 운영 로그에도 남게 됩니다.
- **조치 방안:** `:80-81`의 `System.out.println`을 지우거나 `ownerPwd.length()`만 출력합니다. 고정 키 대신 `KeyUtil.randomKey(32)`(KP-04)를 씁니다.

## 4. 오탐으로 판단해 제외한 항목

- **AES-GCM IV 재사용:** 페이로드마다 `SecureRandom`으로 12바이트 IV를 새로 만듭니다(`WatermarkPayload.java:51-52`). 문제 없습니다.
- **HMAC 비교 타이밍 공격:** `MessageDigest.isEqual`을 사용합니다(`PdfWatermarkInspector.java:136`). JDK 6u17 이후 이 함수는 상수 시간으로 비교합니다.
- **소유자 암호 생성 강도:** `SecureRandom`과 87자 문자 집합에서 32자를 뽑습니다(`KeyUtil.java:6-27`). 약 206비트로 충분합니다.
- **Jackson 역직렬화 RCE:** default typing이나 다형성 역직렬화를 쓰지 않고, `readTree` 입력은 GCM으로 인증된 평문입니다(KP-05 도달성 추적 참고).
- **git 이력의 비밀정보:** 커밋 4개를 확인했습니다. 테스트용 고정 키(KP-07)와 테스트 암호 `testpw123!` 외에는 비밀정보가 없습니다.

## 5. 2차 검토

- **검토자:** 1차 작성 워커와 별개의 Orca Claude 워커(claude-opus, 독립 세션). 과제 조건상 2차 검토는 OpenAI Codex 모델에 맡기려 했으나, 보안 취약점 보고서가 OpenAI의 사이버보안 안전장치(cybersecurity safeguard)에 걸려 Codex 워커가 실행을 거부했습니다. 그래서 과제 조건("Claude Code를 메인으로 사용")에도 맞게 **별도 Claude 워커**가 수행했습니다.
- **일시:** 2026-11-20
- **방법:** 1차 clone을 재사용하지 않고 대상 저장소를 새 `mktemp -d`에 독립 clone(`74d3aed…`), 소스 전체를 `cat -n`으로 정독해 파일:행을 재확인, Maven Central POM으로 전이 의존성 버전 확인, OSV(api.osv.dev, 2026-11-20) 재조회, PDFBox 2.0.30 sources jar로 내부 동작 확인, 로컬 PoC(Corretto JDK 17, `javac --release 8`) 실행. 원격 공격과 외부 게시는 하지 않음.
- **결과 요약:** 오탐 없음. 새로운 독립 취약점 없음. 통계 표 합계(7) = 본문 `### KP-` 항목 수(7) 일치 재확인. KP-01~06에 대해 보강 사항이 도출되어 모두 반영함.

| ID | 2차 검토 판정 | 핵심 지적 | 반영 내역 |
|---|---|---|---|
| KP-01 | 수정 필요 | `getXObject()`(`:56`)에 두 번째 sink(Image XObject `[/FlateDecode /JPXDecode]` 폭탄, `_k1` 없이 `-Xmx256m`에서 OOM). 추가로 깊은 중첩 PDF가 파서에서 `StackOverflowError`. `MemoryUsageSetting` 상한만이 (a)(b)를 함께 막음 | **반영**: 위치에 `:46,56` 추가, sink 3종(a/b/c) 구분, `MemoryUsageSetting`을 필수 조치로 명시. (b)는 상한 적용 시 948ms에 거부·(c)는 pdfbox 2.0.37에서 거부됨을 로컬 확인해 추가 |
| KP-02 | 수정 필요 | 조치안 `ContentDigest`가 마지막 콘텐츠 스트림을 내용 확인 없이 제외하고 리소스·`/Annots`를 빼므로 본문 변조(시나리오 2)가 계속 통과. 시그니처도 그대로는 적용 불가 | **반영**: 조치 효과를 "이식 탐지"로 한정 명시, 한계 단락 추가, 변조 탐지는 발급 시 출력 PDF SHA-256 기록 대조로 보완, 시그니처 수정 필요 명시 |
| KP-03 | 수정 필요 | 조치 catch가 C-1 PoC가 실제로 던지는 `java.security.ProviderException`(RuntimeException)을 못 잡아 패치 후에도 C-1이 실패(로컬 재현) | **반영**: catch에 `ProviderException` 추가, 유효 워터마크 다중 시 `CONFLICTING_WATERMARKS` 처리(미검증 표시) 추가 |
| KP-04 | 확인(보완) | `verifyBase64()` 디코딩이 `try` 밖(`:26-27`)이라 boolean API가 예외를 던짐. 검증 경로에서 throw는 `Result` 계약 위반 | **반영**: 위치에 `PdfVerificationUtil.java:26-27` 추가, 검증 쪽은 `Result.fail("INVALID_KEYS")`·`decode()`를 `try` 안으로 권고 |
| KP-05 | 수정 필요(형식) | OSV 12/4건·CVE 번호 일치 재확인. `looksLikeValidNumber`는 databind 참조 0건으로 도달 불가 확인. 통계 표 Low 기준(CVSS 0.1–3.9)과 KP-05(점수 없음) 불일치 | **반영**: "확인 필요" → "도달 불가 확인", 통계 표에 CVSS 미산정 각주 추가, SSRF 용어를 "즉시 DNS 조회(SSRF)"로 보정 |
| KP-06 | 확인(보완) | `AccessPermission` 기본값 전부 허용을 소스로 확인. `userPassword`가 비면 `ownerPassword`도 조용히 무시됨. "결과에 표시 안 됨"은 과함(`getOwnerPassword()==null` 간접 신호 있음) | **반영**: `ownerPassword` 무시 설명 추가, 표현을 "명시적 `encrypted` 플래그 없음"으로 보정 |
| KP-07 | 확인 | `KurbyPdfTest.java:80-81`, `:24-29` 일치. 추가 지적 없음 | 변경 없음 |

- **미반영:** 없음. 2차 검토에서 제기된 모든 항목을 반영했습니다. KP-03의 `CONFLICTING_WATERMARKS` 분기와 KP-02의 시그니처 변경은 실제 패치를 적용해 실행하지 않았으므로 본문에 "미검증"으로 표시했습니다.
- **원본 검토 노트:** `week3-review.md`(2차 검토 워커 산출물)에 7건 항목별 판정·근거(파일:행)와 로컬 PoC 출력이 보관되어 있습니다(저장소에는 커밋하지 않음).
