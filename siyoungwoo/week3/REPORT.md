# KurbyPdf 보안 취약점 보고서

| 항목 | 내용 |
| --- | --- |
| 분석 대상 | https://github.com/juwonlee-dev/KurbyPdf |
| 분석 기준 커밋 | `74d3aedeea9204694a8bc1e04e75edaa75add94d` (2025-09-22, `feat: Add README`) |
| 분석 범위 | 저장소 전체 18개 파일 (main 소스 9개, 테스트 1개, 빌드 설정, README) |
| 분석 일자 | 2026-11-23 |
| 작성 | 우시영 (Claude Code 사용) |
| 검토 상태 | 2차 검토 완료, 지적 사항 반영본 (6장 참조) |
| 근거 과제 | study-ai Issue #46 (3주차) 2번 문항 |

---

## 1. 통계 (요약 페이지)

### 1.1 위험도별 탐지 건수

| 위험도 | 건수 | 비율 | 분포 | 해당 항목 |
| --- | ---: | ---: | --- | --- |
| Critical | 0 | 0.0% | | 없음 |
| High | 1 | 8.3% | █ | V-01 |
| Medium | 3 | 25.0% | ███ | V-02, V-03, V-04 |
| Low | 3 | 25.0% | ███ | V-05, V-06, V-07 |
| Info | 5 | 41.7% | █████ | V-08, V-09, V-10, V-11, V-12 |
| **합계** | **12** | 100.0% | | |

### 1.2 유형별 탐지 건수

| 유형 | 건수 | 항목 |
| --- | ---: | --- |
| 워터마크 설계·검증 로직 | 3 | V-01, V-02, V-03 |
| 입력 처리·가용성 | 1 | V-04 |
| 암호·키·PDF 보호 설정 | 4 | V-05, V-06, V-09, V-12 |
| 의존성·빌드·배포 | 2 | V-07, V-08 |
| 테스트·오류 처리·문서 | 2 | V-10, V-11 |

### 1.3 검증 상태별 건수

| 검증 상태 | 건수 | 항목 |
| --- | ---: | --- |
| PoC 실행으로 재현 | 7 | V-01, V-02, V-03, V-04, V-05, V-06, V-11 |
| 공개 취약점 DB 조회로 확인 | 1 | V-07 |
| 코드·저장소 확인 (실행 재현 없음) | 4 | V-08, V-09, V-10, V-12 |

V-11은 여러 세부 항목 중 예외 유형과 `KeyUtil` 동작만 실행으로 확인했다.

### 1.4 전체 목록

| ID | 위험도 | 제목 | 주요 위치 |
| --- | --- | --- | --- |
| V-01 | High | 워터마크가 문서에 결합되지 않아 다른 문서로 이식 가능 | `WatermarkPayload.java:27-31` |
| V-02 | Medium | 고정 식별자 때문에 수령자가 키 없이 워터마크를 찾아 제거 가능 | `PdfForensicEmbedder.java:16-17, 64` |
| V-03 | Medium | 첫 번째 워터마크만 검증하여 오귀속·검증 방해 가능 | `PdfWatermarkInspector.java:31-34, 64-66` |
| V-04 | Medium | 입력 크기 제한이 없어 압축 폭탄으로 메모리 고갈 | `PdfWatermarkInspector.java:56, 83` |
| V-05 | Low | PDF 보호 설정 미흡 | `PdfProtector.java:9-11`, `KurbyPdf.java:21, 35-40` |
| V-06 | Low | 키 길이·키 분리 검증 부재 | `KurbyPdf.java:24-25` |
| V-07 | Low | 알려진 취약점이 있는 Jackson 2.17.1 사용 및 전이 노출 | `build.gradle.kts:27-28` |
| V-08 | Info | 빌드·배포 무결성 통제 부재 | 저장소 구성, `README.md:25-40` |
| V-09 | Info | 예측 가능한 난수로 삽입 위치 결정 | `PdfForensicEmbedder.java:23, 40` |
| V-10 | Info | 테스트 코드의 암호 출력과 고정 키 | `KurbyPdfTest.java:24-30, 80-81` |
| V-11 | Info | 오류 처리 불일치와 README·실제 API 불일치 | `PdfVerificationUtil.java:24-29, 53-55` |
| V-12 | Info | 암호 운용상 보완점 | `WatermarkPayload.java:30-31, 51-55` |

---

## 2. 분석 개요

### 2.1 대상 요약

KurbyPdf는 PDF에 보이지 않는 추적용 워터마크를 넣고 검증하는 Java 8 라이브러리다. 동작은 다음과 같다.

1. `WatermarkPayload.buildPayload`가 `{v, claims, ts, nonce}`를 JSON으로 만들고 HMAC-SHA256 서명을 붙인 뒤 AES-GCM으로 암호화한다.
2. `PdfForensicEmbedder.embed`가 그 바이트를 스트림 객체 하나로 만들고, 페이지마다 1×1 Form XObject 3개의 사전에 `/_k1` 키로 연결한다.
3. `PdfProtector`가 사용자 암호가 있을 때만 AES-256 PDF 암호화를 적용한다.
4. `PdfVerificationUtil.verify*`가 `PdfWatermarkInspector`로 `/_k1` 스트림을 찾아 복호화하고 서명을 확인한다.

네트워크, 파일 시스템, 명령 실행, 역직렬화 대상 클래스 지정 같은 기능은 없다. 따라서 공격 표면은 (a) 워터마크 자체의 설계, (b) 외부에서 들어온 PDF 바이트 처리, (c) 키와 암호 취급, (d) 의존성과 빌드로 좁혀진다.

### 2.2 위협 모델

| 행위자 | 가진 것 | 목표 |
| --- | --- | --- |
| 수령자(유출자) | 본인에게 배포된 PDF, 그 열람 암호 | 추적을 피해 유출, 또는 타인에게 책임 전가 |
| 외부 제출자 | 검증·워터마크 기능에 임의 PDF를 넣을 수 있는 경로 | 서비스 장애 유발 |
| 라이브러리 사용 개발자 | README, 공개 API | (악의 없음) 오용으로 인한 보호 누락 |

HMAC 키와 AES 키는 배포 서버만 가진다고 가정한다. V-01, V-02, V-03(b), V-04의 공격 단계는 **키 없이** 수행했다(결과 확인용 검증 호출만 정상 키 사용). V-03(a), V-05, V-06은 키를 가진 운영자·호출자의 동작에서 생기는 문제다.

### 2.3 위험도 판정 기준

| 위험도 | 기준 |
| --- | --- |
| Critical | 인증·키 없이 원격 코드 실행, 키 유출, 임의 클레임 위조처럼 전면적 침해가 가능 |
| High | 공격자가 키 없이 라이브러리의 핵심 보안 목표(추적 결과의 신뢰성)를 **거짓 양성**으로 깨뜨릴 수 있음 |
| Medium | 핵심 기능을 무력화하거나 가용성을 해치지만, 결과가 실패로 드러나거나 공격자가 유도하기 어려운 전제 조건이 필요 |
| Low | 단독 악용은 어렵고 설정·운용 조건에 따라 위험이 생김 |
| Info | 직접적 보안 영향은 확인되지 않았으나 개선이 권장됨 |

### 2.4 분석 방법과 환경

- 정적 분석: 기준 커밋의 모든 파일을 줄 단위로 읽었다. 줄 번호는 모두 기준 커밋 기준이다.
- 동적 재현: main 소스를 수정 없이 컴파일하고 별도 PoC 클래스로 호출했다.
  - JDK 1.8.0_261, PDFBox 2.0.30, Jackson 2.17.1 (대상의 `build.gradle.kts`와 같은 버전, Maven Central SHA-1 일치 확인)
  - 입력은 대상 저장소의 `src/test/resources/input/sample.pdf` (2쪽, 42,373바이트)
  - 키는 대상 테스트와 같은 32바이트 고정 값
- 의존성: 2026-11-23에 OSV(`https://api.osv.dev/v1/query`)를 버전 지정으로 조회했다.
- 2차 검토: 작성 맥락을 공유하지 않은 독립 검토자가 소스를 먼저 읽고 보고서와 대조했다(6장).
- 한계: 저장소에 Gradle Wrapper 파일이 없어(V-08) `gradlew test`는 실행하지 못했다. 대상의 JUnit 테스트 자체는 실행하지 않았다. 조치 방안의 코드는 별도 표시가 없는 한 대상에 적용해 실행해 본 것이 아니다.

---

## 3. 취약점 상세

### V-01. 워터마크가 문서에 결합되지 않아 다른 문서로 이식 가능 — High

**위치**
- `WatermarkPayload.java:27-31` 서명·암호화되는 본문이 `v`, `claims`, `ts`, `nonce`뿐이다.
- `PdfWatermarkInspector.java:122-136` 검증도 이 네 값의 HMAC만 확인한다.
- `PdfVerificationUtil.java:40-52` 서명이 맞으면 `valid=true`를 반환한다.

**설명**
워터마크 페이로드에 "어느 문서에 넣은 것인지"를 나타내는 값이 없다. 암호문은 그 자체로 완결된 토큰이라서, 한 PDF의 `/_k1` 스트림 바이트를 그대로 다른 PDF에 옮겨도 복호화와 서명 검증이 모두 통과한다. 옮기는 데에는 HMAC 키도 AES 키도 필요 없다. PDF가 암호화되어 있어도 수령자는 열람 암호를 알고 있으므로 스트림을 꺼낼 수 있다.

**영향**
- 공격자는 피해자에게 배포된 PDF 하나(와 그 열람 암호)만 확보하면, **임의의 다른 PDF**에 "피해자에게 배포됨"이라는 유효한 워터마크를 붙일 수 있다.
- 검증 결과가 실패가 아니라 `valid=true`로 나오므로 유출 책임이 엉뚱한 사람에게 귀속된다. README가 내세우는 "무결성, 위변조 여부 확인"이 성립하지 않는다.
- 같은 문서를 받은 두 사람 사이의 교체(아래 C)는 피해자 배포본을 그대로 유출하는 것과 결과가 같다. 추가 위험은 **다른 문서로의 이식**(아래 B)에 있다.

**재현** (PoC 실제 출력)
```
A(정상 배포본)      : valid=true reason=null claims={uid=victim}
키 없이 추출한 blob  : 164 bytes
B(이식 전)           : valid=false reason=WATERMARK_NOT_FOUND claims={}
B(이식 후, 다른 문서): valid=true reason=null claims={uid=victim}
C(공격자 배포본)     : valid=true reason=null claims={uid=attacker}
C(교체 후)           : valid=true reason=null claims={uid=victim}
```
B는 내용이 전혀 다른 빈 A4 한 쪽짜리 PDF다. blob 길이는 nonce 자릿수에 따라 163~164바이트로 달라진다.

**조치 방안**
1. (단기, 코드 변경 최소) 발급 기록을 둔다. 발급 시 `nonce → (수령자, 문서 식별자, 최종 배포 파일의 SHA-256, 발급 시각)`을 서버에 저장하고, 검증 결과의 `nonce`를 이 기록과 대조한 뒤에만 귀속을 확정한다. `nonce`는 이미 결과로 반환된다(`PdfVerificationUtil.java:48-52`). README의 검증 절차에 이 대조를 필수 단계로 적는다.
2. (형식 변경) 페이로드 버전을 `v=2`로 올리고 서명 본문에 문서 결합 값 `doc`을 넣는다.
   ```java
   // WatermarkPayload.buildPayload(claims, docDigest, hmacKey, aesKey) — 27-31행 본문
   body.put("v", 2);
   body.put("doc", Base64.getEncoder().encodeToString(docDigest));
   ```
   - 검증 측은 `PdfWatermarkInspector.java:122-126`의 본문 재구성에 `doc`을 추가하고, 대상 PDF에서 같은 방식으로 다시 계산한 값과 비교한다. 다르면 `DOCUMENT_MISMATCH`로 실패시키되 클레임은 결과에 담아 돌려준다(진본 워터마크가 다른 문서에서 발견된 것 자체가 단서다).
   - `doc`을 GCM의 AAD로도 넣으면 불일치 시 복호화가 `AEADBadTagException`으로 끝나 클레임을 꺼낼 수 없다. AAD는 쓰지 않고 본문 값 비교만 쓴다.
   - 다이제스트 설계 요건: (i) 삽입 **전** 문서에서 계산한다. (ii) 페이지 콘텐츠 스트림만이 아니라 페이지 리소스(이미지·폰트)의 디코드된 스트림까지 포함한다. 콘텐츠만 해시하면 스캔본처럼 콘텐츠가 이미지 호출 한 줄인 문서들이 같은 값을 갖는다. (iii) 삽입은 `AppendMode.APPEND, true, true`(`PdfForensicEmbedder.java:59`)로 페이지 `/Contents`를 `[q 스트림, 원본…, Q + 워터마크 스트림]`으로 바꾸므로, 검증 측이 워터마크가 덧붙인 스트림과 폼을 식별해 제외할 수 있도록 삽입 방식에 식별 규칙을 함께 정의해야 한다. 재워터마크(V-03)가 허용되면 이 규칙이 깨지므로 V-03 조치 3(기존 워터마크가 있으면 거부)이 전제다.
3. 내용 결합만으로는 같은 문서를 받은 수령자끼리의 교체를 막을 수 없다. 이 경우는 1의 발급 기록 대조가 유일한 통제다.
4. 조치 전까지는 README에 "`valid=true`는 워터마크가 진본이라는 뜻이지, 이 문서에 발급되었다는 뜻이 아니다"를 명시하고, 호출자가 `fileId` 클레임을 문서 실체와 직접 대조하도록 안내한다.

---

### V-02. 고정 식별자 때문에 수령자가 키 없이 워터마크를 찾아 제거 가능 — Medium

**위치**
- `PdfForensicEmbedder.java:16-17` 식별자가 `_k1`, `_k1v`로 고정되어 있다.
- `PdfForensicEmbedder.java:43-51, 64` 페이로드는 스트림 객체 하나이고 모든 폼이 그것을 참조한다.
- `PdfForensicEmbedder.java:62-63, 82-85` 1×1 폼을 크기 0 클리핑으로 그리는 동일한 패턴이 반복된다.
- `KurbyPdf.java:35-41` PDF 암호화는 선택 사항이다.

**설명**
워터마크는 PDF 객체 구조에만 존재하고, 모든 배포본에서 같은 이름(`/_k1`)을 쓴다. 암호화하지 않은 배포본은 파일 바이트에서 문자열 검색만으로 위치가 드러난다. 암호화한 배포본도 수령자는 열람 암호로 문서를 열 수 있고, PDF 권한 플래그는 뷰어가 자발적으로 지키는 값이므로 라이브러리로 열어 `/_k1` 항목을 지운 뒤 암호 없이 다시 저장할 수 있다. 페이지당 3개씩 넣어도 실체는 스트림 하나라서 중복 삽입이 내성을 높이지 못한다.

**영향**
유출자가 추적 정보를 지운 사본을 만들 수 있다. 결과는 `WATERMARK_NOT_FOUND`로 드러나므로 거짓 귀속은 아니지만, "불법 유출 추적"이라는 사용 목적은 달성되지 않는다. 결과가 실패로 드러나고 README도 DRM 대체가 아니라고 밝히고 있어 Medium으로 판정했다.

**재현** (PoC 실제 출력)
```
배포본          : valid=true reason=null claims={uid=leaker}
열람암호 권한   : owner=false modify=true assemble=true annot=true fillForm=true extract=false print=true
제거한 _k1 참조 : 6
제거 후(무암호) : valid=false reason=WATERMARK_NOT_FOUND claims={}
제거 후 암호화  : false, pages=2
```
무암호 배포본에서는 원시 바이트에 `/_k1 `이 6회, `/_k1v`가 1회 그대로 나타났다.

**조치 방안**
구조 기반 워터마크의 제거를 완전히 막을 수는 없다. 비용을 올리는 방향으로 조치한다.
1. 고정 이름을 없앤다. 사전 키를 문서마다 무작위 이름으로 만들고, `PdfWatermarkInspector`는 이름으로 찾는 대신 폼 사전의 스트림 값들을 차례로 AES-GCM 복호화해 인증에 성공한 것만 워터마크로 인정한다(GCM 태그가 식별자 역할을 한다). `_k1v`처럼 읽지 않는 표식(`PdfForensicEmbedder.java:44`)은 제거한다. 단, 후보 스트림을 여럿 읽게 되므로 V-04 조치 1의 사전 검사(원시 길이 상한, 필터 거부)가 먼저 적용되어 있어야 한다.
2. 삽입 채널을 하나 더 둔다. 스트림 하나를 공유하지 말고 사본마다 다른 IV로 암호화한 별도 객체를 만들고, 콘텐츠 수준 채널(예: 보이지 않는 텍스트 렌더링 모드의 문자열)을 병행한다.
3. 발급 기록(V-01 조치 1)을 남겨 워터마크가 지워진 사본도 다른 단서로 좁힐 수 있게 한다.
4. README 주의사항에 "수령자는 워터마크를 제거할 수 있으며 `WATERMARK_NOT_FOUND`는 변조 신호로 다뤄야 한다"를 추가한다.

---

### V-03. 첫 번째 워터마크만 검증하여 오귀속·검증 방해 가능 — Medium

**위치**
- `PdfWatermarkInspector.java:31-34` `extractFirst`가 목록의 0번만 돌려준다.
- `PdfWatermarkInspector.java:64-66` 스트림 하나라도 복호화에 실패하면 예외가 루프 전체를 중단시킨다.
- `PdfVerificationUtil.java:40` 검증이 `extractFirst`만 사용한다.
- `KurbyPdf.java:31` 삽입 전에 기존 워터마크 존재 여부를 확인하지 않는다.

**설명**
문서에 워터마크가 여러 개 있을 때 어느 것이 맞는지 판단하는 규칙이 없다. 검증은 페이지·XObject 순서상 가장 먼저 발견된 것 하나만 보고 결론을 낸다. 그 결과 두 가지 문제가 생긴다.

- (a) 이미 워터마크가 있는 PDF에 다시 워터마크를 넣으면 옛 워터마크가 남고, 검증은 **옛 수령자**를 돌려준다.
- (b) 진짜 워터마크 앞에 복호화되지 않는 `/_k1` 스트림을 끼워 넣으면, 뒤에 유효한 워터마크가 있어도 검증 전체가 예외로 끝난다.

**영향**
- (a) 배포본이 다시 시스템에 올라가 재배포되는 흐름(예: A가 받은 파일을 업로드, B에게 배포)에서 B가 유출해도 A로 판정된다. 결과가 `valid=true`인 오귀속이지만, 재배포라는 운영 흐름이 전제이고 공격자가 이를 유도해 얻는 이득이 뚜렷하지 않아 High가 아닌 Medium으로 판정했다.
- (b) 유출자가 워터마크를 지우지 않고도 검증을 실패시킬 수 있다. V-01의 이식과 결합하면 이식한 워터마크를 맨 앞에 두어 원래 워터마크를 가릴 수 있다.

**재현** (PoC 실제 출력)
```
1차 배포(user-1)        : valid=true reason=null claims={uid=user-1}
재워터마크(user-2) 검증 : valid=true reason=null claims={uid=user-1}
extractAll 개수         : 2

쓰레기 _k1 선행 삽입 후 : valid=false reason=EXCEPTION:AEADBadTagException claims={}
```

**조치 방안**
1. `PdfVerificationUtil.verifyDetailed`(40행)가 `extractAll`을 쓰도록 바꾸고 판정 규칙을 정한다. 유효한 워터마크가 하나도 없으면 실패, 유효한 워터마크들의 `nonce`가 서로 다르면 `CONFLICTING_WATERMARKS`로 실패시키고 발견된 클레임 전체를 결과에 담는다.
2. `PdfWatermarkInspector.extractAll`의 64-66행을 스트림 단위 `try/catch`로 감싸 한 스트림의 실패가 나머지 탐색을 막지 않게 한다. 실패 건수는 결과에 포함한다.
   ```java
   try {
       out.add(decryptAndVerify(streamToBytes(stream), hmacKey, aesKey));
   } catch (GeneralSecurityException | IOException | IllegalArgumentException e) {
       undecodable++; // 결과에 포함해 변조 신호로 노출
   }
   ```
3. `KurbyPdf.watermark`(31행 앞)에서 기존 `/_k1` 항목을 검사해, 있으면 거부하거나 제거 후 삽입하도록 요청 옵션을 둔다. 기본값은 거부가 안전하다.

---

### V-04. 입력 크기 제한이 없어 압축 폭탄으로 메모리 고갈 — Medium

**위치**
- `PdfWatermarkInspector.java:83` `s.createInputStream()`. PDFBox 2.0.x는 이 호출 시점에 스트림의 필터 전체를 내부 버퍼로 풀어 놓는다.
- `PdfWatermarkInspector.java:56` `res.getXObject(name)`이 워터마크와 무관한 것까지 페이지의 모든 XObject를 객체화한다. 이미지 XObject는 생성자에서 스트림을 디코드한다.
- `PdfWatermarkInspector.java:46`, `KurbyPdf.java:21` `PDDocument.load`를 메모리 설정 없이 호출한다(PDFBox 2.x 기본값은 주 메모리 무제한).
- `PdfVerificationUtil.java:53-55` `catch (Exception)`은 `OutOfMemoryError`를 잡지 못한다.
- `PdfForensicEmbedder.java:54-89` 페이지 수에 상한이 없다.

**설명**
검증 기능의 입력은 성격상 외부에서 회수한 PDF다. 검사기는 스트림의 원시 길이나 필터를 확인하지 않고 디코드를 시작한다. 경로는 두 가지다.

- (a) `/_k1`에 FlateDecode 필터가 걸린 큰 스트림을 달아 둔다. 정상 페이로드는 필터 없는 약 164바이트인데도 83행에서 전체가 풀린다. 87-89행의 읽기 루프에 도달하기 전에 고갈된다.
- (b) `/_k1`이 전혀 없는 PDF도 가능하다. 디코드 필터가 걸린 큰 이미지 XObject를 페이지 리소스에 두면 56행에서 풀린다.

**영향**
약 1MB짜리 PDF 하나로 검증 프로세스의 힙을 소진시킬 수 있다. `verifyDetailed`는 실패 사유를 돌려주는 대신 `OutOfMemoryError`를 호출자에게 던지므로, 검증을 서버에서 수행하면 같은 JVM의 다른 요청까지 영향을 받는다. 임의 PDF를 넣을 수 있는 경로가 필요하므로 Medium으로 판정했다.

**재현** (PoC 실제 출력, 검증 측 `-Xmx256m`)
```
(a) 폭탄 PDF 크기: 1044407 bytes (압축 해제 시 1024 MiB)
    maxHeap=245MiB, input=1044407 bytes
    verifyDetailed가 던진 예외: java.lang.OutOfMemoryError: Java heap space
      at org.apache.pdfbox.filter.FlateFilter.decompress(FlateFilter.java:104)
      at org.apache.pdfbox.cos.COSInputStream.create(COSInputStream.java:87)
      at org.apache.pdfbox.cos.COSStream.createInputStream(COSStream.java:175)
      at io.github.juwonlee.kurbypdf.PdfWatermarkInspector.streamToBytes(PdfWatermarkInspector.java:83)

(b) input=1044333 bytes, '_k1' 포함=false, maxHeap=245MiB
    java.lang.OutOfMemoryError: Java heap space
      at org.apache.pdfbox.cos.COSStream.createInputStream(COSStream.java:175)
      at org.apache.pdfbox.pdmodel.graphics.image.PDImageXObject.<init>(PDImageXObject.java:148)
```
스택은 관련 프레임만 발췌했다. 힙을 256MB로 제한한 조건의 결과이며, 더 큰 힙에서의 한계값은 측정하지 않았다. (b)의 입력 파일은 2차 검토자가 만든 것을 작성자가 다시 실행해 확인했다.

**조치 방안**
1. 디코드 **전에** 걸러낸다. `PdfWatermarkInspector.java:64` 앞에서 원시 길이와 필터를 검사한다. 정상 페이로드는 필터 없이 기록된다(`PdfForensicEmbedder.java:47`).
   ```java
   private static final int MAX_WM_BYTES = 64 * 1024;
   ...
   if (stream.getLength() > MAX_WM_BYTES || stream.getItem(COSName.FILTER) != null) {
       undecodable++;      // V-03 조치 2의 실패 집계에 포함
       continue;
   }
   ```
   87-89행 읽기 루프에 상한을 두는 것만으로는 막지 못한다(83행에서 이미 고갈된다. 2차 검토에서 실행으로 확인).
2. 55-58행에서 `res.getXObject(name)`으로 모든 XObject를 객체화하지 않는다. 리소스의 `/XObject` COS 사전을 직접 순회해 `/Subtype`이 `/Form`이고 `/_k1` 항목을 가진 것만 본다. 이미지 XObject는 건드리지 않는다.
3. 두 곳의 `PDDocument.load`에 메모리 한도를 지정한다.
   ```java
   MemoryUsageSetting mem = MemoryUsageSetting.setupMainMemoryOnly(64L << 20); // 요청당 64MB
   doc = PDDocument.load(bin, password == null ? "" : password, mem);
   ```
   2차 검토에서 `setupMixed(64MB, 512MB)`를 (a) 입력에 적용하면 OOM 대신 `IOException: Maximum allowed scratch file memory exceeded`로 끝나는 것을 실행으로 확인했다. 다만 임시 파일을 쓰는 설정은 동시 요청 시 부담이 디스크로 옮겨가므로 주 메모리 한도 방식을 권한다.
4. 공개 API 진입점(`KurbyPdf.watermark`, `PdfVerificationUtil.verifyDetailed`)에서 입력 바이트 길이와 페이지 수 상한을 검사하고, 한도는 요청 객체로 조정할 수 있게 한다.
5. 2차 방어로 `verifyDetailed`의 53행에서 `OutOfMemoryError`와 `StackOverflowError`를 `RESOURCE_LIMIT` 실패로 바꿔 돌려준다. 이것만으로는 충분하지 않다.

---

### V-05. PDF 보호 설정 미흡 — Low

**위치**
- `PdfProtector.java:9-11` `new AccessPermission()`은 모든 권한 허용이 기본이고, 코드가 끄는 것은 내용 추출 하나다.
- `KurbyPdf.java:35` 사용자 암호가 비어 있으면 보호 블록 전체를 건너뛴다.
- `KurbyPdf.java:36-40` 소유자 암호가 사용자 암호와 같아도 막지 않는다.
- `KurbyPdf.java:21, 40, 44` 입력 PDF가 이미 암호화되어 있는지 확인하지 않는다.

**설명**
- (a) 열람 암호로 연 사용자에게 수정, 페이지 조립, 주석, 양식 입력 권한이 그대로 허용된다.
- (b) 요청에 소유자 암호만 넣고 사용자 암호를 비우면 암호화가 전혀 적용되지 않고, 결과의 `ownerPassword`도 `null`이다. 호출자는 "소유자 암호로 권한만 제한"했다고 생각할 수 있지만 실제 결과물은 무보호 PDF다. 예외나 경고가 없다.
- (c) 소유자 암호와 사용자 암호를 같은 값으로 주면 수령자가 열람 암호만으로 소유자 권한을 얻어 11행의 추출 제한이 무력화된다.
- (d) 원 소유자가 권한을 제한해 둔(열람 암호 없는) PDF를 입력하면, 사용자 암호를 지정하지 않은 호출은 저장 단계에서 `IllegalStateException`으로 실패하고, 지정한 호출은 원래 제한을 경고 없이 새 정책으로 교체한다.

**영향**
정책을 지키는 뷰어에서도 문서 수정이 허용된다. (b), (c), (d)는 조용한 보호 누락·완화라 호출자가 알아차리기 어렵다. PDF 권한 플래그 자체가 강제력이 약한 통제이고 호출자의 입력이 전제이므로 Low로 판정했다.

**재현** (PoC 실제 출력)
```
(a) 열람암호 권한   : owner=false modify=true assemble=true annot=true fillForm=true extract=false print=true
(b) ownerPassword만 지정: encrypted=false, 반환 ownerPassword=null
    userPassword=""     : encrypted=false
(c) user==owner: owner=true extract=true
    user!=owner: owner=false extract=false
(d) 입력: encrypted=true print=false modify=false
    암호 미지정: IllegalStateException: PDF contains an encryption dictionary, please remove it with setAllSecurityToBeRemoved() or set a protection policy with protect()
    암호 지정 : 성공, print=true modify=true
```

**조치 방안**
1. `PdfProtector.java:9-11`에서 필요한 권한만 남긴다. 접근성용 추출 권한은 스크린리더 사용을 막게 되므로 끄지 않는다.
   ```java
   ap.setCanModify(false);
   ap.setCanAssembleDocument(false);
   ap.setCanModifyAnnotations(false);
   ap.setCanFillInForm(false);
   ```
2. `KurbyPdf.java:35`의 조건을 "사용자 암호 또는 소유자 암호가 있으면 보호 적용"으로 바꾼다. 소유자 암호만 있으면 사용자 암호를 빈 문자열로 두고 권한 제한을 적용한다. 이 경우 누구나 문서를 열 수 있고 권한 플래그만 남는다는 한계를 Javadoc에 적는다.
3. 같은 위치에서 `ownerPwd.equals(req.getUserPassword())`이면 `IllegalArgumentException`으로 거부한다.
4. `KurbyPdf.java:21` 뒤에서 `doc.isEncrypted()`이면 명시적으로 거부하거나, 기존 권한을 읽어 새 정책에 승계한다. 기본값은 거부가 안전하다.
5. 암호가 둘 다 없을 때 무보호로 저장된다는 점을 `WatermarkRequest` Javadoc과 README에 적는다.

---

### V-06. 키 길이·키 분리 검증 부재 — Low

**위치**
- `KurbyPdf.java:24-25` Base64 디코드 결과를 검사 없이 사용한다.
- `WatermarkPayload.java:37, 55` 받은 바이트로 곧바로 키 객체를 만든다.

**설명**
HMAC 키는 1바이트여도 받아들이고, AES 키는 JCE가 허용하는 16/24/32바이트면 내용과 무관하게 통과한다. 두 키에 같은 값을 넣어도 막지 않는다. 약한 키로 발급된 워터마크는 정상 발급과 구분되지 않는다.

**영향**
호출자의 설정 실수(짧은 키, 문자열 암호를 그대로 Base64한 값)가 그대로 운영에 들어가면 서명 위조와 페이로드 복호화의 난도가 키 길이만큼 낮아진다. 호출자 실수가 전제이므로 Low다.

**재현** (PoC 실제 출력)
```
HMAC키 1바이트 + AES키 16바이트(all-zero): 삽입 성공, valid=true
```

**조치 방안**
1. 발급 경로에 검사를 넣는다. `KurbyPdf.java:25` 뒤뿐 아니라, public이라 직접 호출될 수 있는 `WatermarkPayload.buildPayload`(21행)에도 같은 검사를 둔다.
   ```java
   if (hmacKey.length < 32) throw new IllegalArgumentException("hmacKey must be >= 32 bytes");
   if (aesKey.length != 32) throw new IllegalArgumentException("aesKey must be 32 bytes");
   if (MessageDigest.isEqual(hmacKey, aesKey)) throw new IllegalArgumentException("hmacKey and aesKey must differ");
   ```
2. 검증 경로(`PdfVerificationUtil.verifyDetailed`, 38행 뒤)는 이미 발급된 워터마크를 계속 검증할 수 있도록 AES 16/24/32바이트를 허용하고, HMAC 키 최소 길이와 두 키의 동일 여부만 검사한다.
3. 키 생성 실수를 줄이기 위해 `KeyUtil`에 `SecureRandom` 기반 32바이트 키 생성 메서드를 추가하고 README 예제가 그것을 쓰게 한다.

---

### V-07. 알려진 취약점이 있는 Jackson 2.17.1 사용 및 전이 노출 — Low

**위치**
- `build.gradle.kts:27-28` `pdfbox:2.0.30`, `jackson-databind:2.17.1`을 `api` 범위로 선언한다.
- `build.gradle.kts:59-64` Fat JAR에서 두 라이브러리를 다른 패키지명으로 재배치한다.

**설명**
2026-11-23 OSV 조회 결과는 다음과 같다.

| 구성요소 | 버전 | 권고 건수 | 비고 |
| --- | --- | ---: | --- |
| `jackson-databind` | 2.17.1 | 12 | 아래 목록 |
| `jackson-core` (전이) | 2.17.1 | 4 | 아래 목록 |
| `pdfbox` | 2.0.30 | 0 | 2.0.x 최신은 2.0.37 |
| `fontbox` (전이) | 2.0.30 | 0 | |
| `commons-logging` (전이) | 1.2 | 0 | |

`jackson-databind` 2.17.1 (12건)

| 권고 ID | CVE | 2.18 계열 수정 버전 |
| --- | --- | --- |
| GHSA-3pjw-73gf-8qr5 | CVE-2026-59888 | 2.18.8 |
| GHSA-5gvw-p9qm-jgwh | CVE-2026-59889 | 2.18.9 |
| GHSA-5jmj-h7xm-6q6v | CVE-2026-54515 | 2.18.9 |
| GHSA-cxp5-3px4-pw24 | CVE-2026-91777 | 2.18.11 |
| GHSA-gx83-3vf8-gh7j | CVE-2026-83557 | 2.18.10 |
| GHSA-hgj6-7826-r7m5 | CVE-2026-54514 | 2.18.8 |
| GHSA-j3rv-43j4-c7qm | CVE-2026-54512 | 2.18.8 |
| GHSA-q4xh-88c3-wmh7 | CVE-2026-68497 | 2.18.10 |
| GHSA-rmj7-2vxq-3g9f | CVE-2026-54513 | 2.18.8 |
| GHSA-vvgp-rfg2-7rr6 | CVE-2026-77310 | 2.18.9 |
| GHSA-wjgm-6hv5-3cvf | CVE-2026-19032 | 2.18.10 |
| GHSA-wv8q-qhhj-9h54 | CVE-2026-91776 | 2.18.11 |

`jackson-core` 2.17.1 (4건)

| 권고 ID | CVE | 2.18 계열 수정 버전 |
| --- | --- | --- |
| GHSA-72hv-8253-57qq | CVE-2026-18401 | 2.18.6 |
| GHSA-7hhh-6rmp-j9qf | CVE-2026-89425 | 2.18.11 |
| GHSA-p6pp-m3f8-5c89 | CVE-2026-89407 | 2.18.11 |
| GHSA-r7wm-3cxj-wff9 | CVE-2026-68494 | 2.18.8 |

권고들의 수정 버전은 2.18.x, 2.21.x, 2.22.x, 3.x 계열에만 있다. 2.17 계열은 Maven Central 기준 2.17.3이 마지막 릴리스이고 수정 버전이 없다. 2.18 계열에서는 2.18.11이 위 16건의 수정 버전을 모두 포함한다(2.18.11과 PDFBox 2.0.37이 Maven Central에 존재함을 확인).

**영향**
- 라이브러리 자체의 도달 가능성은 낮다. Jackson은 `ObjectMapper.readTree`(`PdfWatermarkInspector.java:107`)와 `Map` 직렬화에만 쓰이고, 파싱 대상은 AES-GCM 인증을 통과한 평문뿐이다. 권고 대부분이 다루는 다형성 타입 검증, 애너테이션 기반 바인딩, 비동기 파서는 사용하지 않는다. 다만 개별 권고 단위의 도달 여부를 실행으로 검증하지는 않았다.
- `api` 범위라서 이 라이브러리를 쓰는 애플리케이션의 클래스패스에 취약 버전이 그대로 전달된다. 애플리케이션이 그 Jackson으로 외부 JSON을 바인딩하면 영향권에 들어간다.
- Fat JAR는 패키지를 재배치하므로 패키지명·좌표 기반 점검 도구가 내장된 Jackson을 놓칠 수 있다.

**조치 방안**
1. `build.gradle.kts:28`을 `jackson-databind:2.18.11` 이상으로 올린다. Java 8 대상 빌드가 유지되는지 빌드로 확인한다.
2. `build.gradle.kts:27`을 `pdfbox:2.0.37`로 올린다(권고는 없으나 유지보수 릴리스 반영).
3. Jackson 타입은 공개 API 시그니처에 나오지 않으므로 Jackson 의존성을 `api`에서 `implementation`으로 바꾼다. PDFBox는 public 메서드 `PdfForensicEmbedder.embed(PDDocument, …)`(22, 35행)와 `PdfProtector.applyUserPassword(PDDocument, …)`(8행)의 시그니처에 `PDDocument`가 나오므로, 이 두 클래스를 package-private으로 내린 뒤에만 `implementation`으로 바꿀 수 있다.
4. CI에 의존성 점검(OSV-Scanner 또는 OWASP Dependency-Check)을 추가하고, Fat JAR에는 내장 구성요소 목록(SBOM)을 함께 배포한다.

---

### V-08. 빌드·배포 무결성 통제 부재 — Info

**위치**
- 저장소 루트에 `gradlew`, `gradlew.bat`은 있으나 `gradle/wrapper/gradle-wrapper.jar`와 `gradle-wrapper.properties`가 커밋되어 있지 않다(추적 파일 18개 중 `gradle/` 경로 없음).
- `README.md:25-40` 설치 방법이 `libs/kurbypdf.jar` 파일을 직접 넣는 방식(Gradle `files(...)`, Maven `system` 범위)이다.
- `build.gradle.kts:3` Shadow 플러그인이 `com.github.johnrengelman.shadow` 8.1.1이다.

**설명**
- Wrapper 설정이 없어 저장소만으로는 빌드가 재현되지 않고, Gradle 배포판 버전과 체크섬(`distributionSha256Sum`)도 고정되지 않는다.
- 의존성 검증 메타데이터(`gradle/verification-metadata.xml`)나 잠금 파일이 없다.
- 사용자는 출처·체크섬·서명을 확인할 수단 없이 JAR 파일을 수동으로 받아 쓰게 된다. `system` 범위 의존성은 저장소 메타데이터 검증과 취약점 점검에서도 빠지기 쉽다.
- 해당 Shadow 플러그인 ID는 Gradle Plugin Portal 기준 2023-03의 8.1.1이 마지막 릴리스이고, 후속 릴리스는 `com.gradleup.shadow` ID로 나온다.

**영향**
빌드 도구나 배포 JAR가 바뀌어도 탐지할 수단이 없다. 직접 악용 경로는 확인되지 않아 Info로 판정했다.

**조치 방안**
1. `gradle wrapper --gradle-version <고정 버전> --distribution-type bin`으로 Wrapper를 생성해 커밋하고 `gradle-wrapper.properties`에 `distributionSha256Sum`을 넣는다.
2. `gradle --write-verification-metadata sha256 help`로 의존성 검증 메타데이터를 만들어 커밋한다.
3. 릴리스 JAR에 SHA-256 체크섬과 서명을 함께 게시하고, 가능하면 Maven Central 좌표로 배포해 README의 `system` 범위 안내를 대체한다.
4. Shadow 플러그인을 `com.gradleup.shadow`의 현재 릴리스로 옮긴다.

---

### V-09. 예측 가능한 난수로 삽입 위치 결정 — Info

**위치**: `PdfForensicEmbedder.java:23, 40`

**설명**: 삽입 좌표를 `new Random(System.currentTimeMillis())`로 정한다. Javadoc(32행)은 무작위 위치가 "보통 더 안전"하다고 하지만, 좌표는 콘텐츠 스트림에 평문으로 남고 워터마크는 `/_k1` 이름으로 찾을 수 있으므로(V-02) 위치 난수화는 은닉 효과가 없다. 시드는 발급 시각이라 그 근방 값으로 추측할 수 있다.

**조치 방안**: 은닉을 의도한다면 `SecureRandom`을 쓰되, 실질적 은닉은 V-02의 조치로 확보한다. 의도하지 않는다면 Javadoc의 "더 안전" 표현을 지운다.

---

### V-10. 테스트 코드의 암호 출력과 고정 키 — Info

**위치**: `KurbyPdfTest.java:24-30, 46-47, 72-76, 80-81`

**설명**: 테스트가 소유자 암호와 사용자 암호를 표준 출력에 찍고(80-81행), `0x11`/`0x22`로 채운 고정 키를 쓰며, 암호화된 결과 PDF를 `build/test-out/`에 남긴다. 값 자체는 테스트용이지만, README의 예제가 실제 API와 맞지 않아(V-11) 이 테스트가 사실상의 사용 예제가 되므로 운영 코드로 복사되기 쉽다.

**조치 방안**: 암호 출력 두 줄을 지우고, 키는 테스트마다 `SecureRandom`으로 생성하며, 출력 파일은 JUnit `@TempDir`에 쓴다.

---

### V-11. 오류 처리 불일치와 README·실제 API 불일치 — Info

**위치**
- `KurbyPdf.java:24-25` 키가 `null`이면 `NullPointerException`이 난다(PoC 확인).
- `PdfVerificationUtil.java:24-29` `verifyBase64`는 잘못된 Base64에 `IllegalArgumentException`을 던진다(PoC 확인). 같은 클래스의 다른 경로는 `Result.fail`을 돌려준다.
- `PdfVerificationUtil.java:53-55` 실패 사유가 예외 클래스 이름뿐이다. 워터마크 변조와 잘못된 AES 키가 모두 `AEADBadTagException`으로 나와 구분되지 않는다.
- `PdfWatermarkInspector.java:138` public인 `extractFirst`/`extractAll`은 서명이 무효(`signatureValid=false`)여도 클레임을 그대로 담아 돌려준다.
- `KeyUtil.java:17-27` public인 `randomOwnerPassword(int)`가 인자를 검사하지 않는다. `len=2`는 4자를 돌려주고 `len=-1`은 `NegativeArraySizeException`이다(PoC 확인).
- `README.md:66, 69, 92` 문서의 `PdfVerification.verify(...)` 클래스는 소스에 없다. 실제는 `util.PdfVerificationUtil`이다.
- `KurbyPdf.java:31` 주석은 "페이지당 2개"인데 실제 기본값은 3개다(`PdfForensicEmbedder.java:23`).

**설명**: 검증 API가 어떤 입력에는 `false`를, 어떤 입력에는 예외를 내므로 호출 코드가 예외를 "검증 통과도 실패도 아님"으로 잘못 처리할 여지가 있다. 문서와 API가 달라 사용자가 내부 클래스(`PdfWatermarkInspector`)를 직접 호출하게 되면 `isSignatureValid()` 확인을 빠뜨리고 서명되지 않은 클레임을 신뢰할 수 있다.

**재현** (PoC 실제 출력)
```
hmacKey=null → java.lang.NullPointerException
verifyBase64(잘못된 Base64) → java.lang.IllegalArgumentException
randomOwnerPassword(2).length=4
randomOwnerPassword(-1) → NegativeArraySizeException
```

**조치 방안**
1. 공개 API의 실패 방식을 하나로 통일한다(검증은 항상 `Result.fail(코드)`, 삽입은 항상 `IllegalArgumentException`).
2. 실패 코드를 `WRONG_PASSWORD`, `TAMPERED_OR_WRONG_KEY`, `MALFORMED_PDF`처럼 의미 단위로 나눈다.
3. `DecodedWatermark`는 서명이 무효이면 클레임을 비워 돌려주거나, 검사기 클래스를 package-private으로 내려 `PdfVerificationUtil`만 공개한다.
4. `randomOwnerPassword(int)`는 최소 길이(예: 16) 미만이면 `IllegalArgumentException`을 던진다.
5. README 예제를 실제 클래스명으로 고친다.

---

### V-12. 암호 운용상 보완점 — Info

**위치**: `WatermarkPayload.java:30-31, 51-55`, `PdfWatermarkInspector.java:123-126`, `WatermarkRequest.java:6-11`

**설명**
- 무작위 96비트 IV를 장기 고정 키와 함께 쓴다. NIST SP 800-38D는 무작위 IV 사용 시 키 하나당 암호화 횟수를 2^32회 이하로 제한한다. 대량 발급 서비스에서는 키 교체 주기가 필요하다.
- `ts`와 `nonce`는 서명되지만 검증 때 유효 기간이나 재사용을 확인하지 않는다. `v` 값도 검사하지 않는다(123행은 값이 없으면 1로 간주).
- 키와 암호를 `String`으로 주고받아 사용 후 메모리에서 지울 수 없다.

**조치 방안**: 키 식별자(`kid`)를 본문에 넣어 키 교체를 지원하고, 문서별 키를 HKDF로 파생하는 방식을 검토한다. 검증 시 `v`를 확인해 지원하지 않는 버전은 거부한다. 키 입력에 `byte[]`/`char[]` 오버로드를 추가한다.

---

## 4. 양호 사항

분석 중 확인한 적절한 구현이다.

- 서명 비교에 상수 시간 비교(`MessageDigest.isEqual`)를 쓴다 (`PdfWatermarkInspector.java:136`).
- IV, nonce, 소유자 암호 생성에 `SecureRandom`을 쓴다 (`WatermarkPayload.java:15`, `KeyUtil.java:6`).
- 인증 암호화(AES-GCM, 128비트 태그)를 쓰고 IV를 매번 새로 만든다 (`WatermarkPayload.java:51-55`).
- PDF 암호화는 AES-256이다 (`PdfProtector.java:14-15`).
- 소유자 암호 자동 생성은 기본 32자이고 4개 문자군을 보장한다 (`KeyUtil.java:13-15, 17-39`). 길이 인자 검증 부재는 V-11에 적었다.
- main 소스에 하드코딩된 비밀값, 파일·네트워크·명령 실행, 다형성 역직렬화가 없다.

---

## 5. 조치 우선순위

| 순위 | 항목 | 이유 |
| ---: | --- | --- |
| 1 | V-01 | 거짓 양성으로 추적 결과의 신뢰가 깨진다. 발급 기록 대조(조치 1)는 즉시 적용할 수 있고, 형식 변경(조치 2)은 설계가 필요하다. |
| 2 | V-04 | 약 1MB 입력으로 검증 프로세스를 중단시킬 수 있다. 디코드 전 검사와 XObject 순회 방식 변경이 필요하다. |
| 3 | V-03 | 검증 로직 수정으로 해결되고, V-01 악용 경로 하나를 함께 줄인다. V-01 조치 2의 전제이기도 하다. |
| 4 | V-07, V-06, V-05 | 버전·검증·설정 변경. 호환성 영향이 작다. |
| 5 | V-02 | 근본 해결이 어려워 V-01의 형식 변경과 함께 설계한다. V-04 조치가 선행되어야 한다. |
| 6 | V-08 ~ V-12 | 빌드·문서·테스트 정비. |

---

## 6. 2차 검토

### 6.1 절차

| 항목 | 내용 |
| --- | --- |
| 검토 일자 | 2026-11-23 |
| 검토자 | 보고서 작성 과정(대화, PoC 작성 맥락)을 공유받지 않은 별도 Claude Code 에이전트 |
| 방법 | 대상 소스를 먼저 읽어 자체 목록을 만든 뒤 보고서와 대조. 작성자의 PoC 재실행과 자체 실험 코드 추가 실행(JDK 1.8.0_261, PDFBox 2.0.30) |
| 검토 항목 | 근거 줄 번호, 오탐·과장, 위험도 보정, 조치 방안의 정확성, 누락, 통계 일관성 |
| 총평 | **수정 후 승인** |
| 후속 처리 | 작성자가 지적 사항을 다시 실행으로 확인한 뒤 본문에 반영 (아래 6.2) |

### 6.2 지적 사항과 반영 내역

| 번호 | 구분 | 지적 사항 | 작성자 확인 | 반영 |
| ---: | --- | --- | --- | --- |
| 1 | 오탐·과장 | V-04의 고갈 지점은 87-89행 읽기 루프가 아니라 83행 `createInputStream()`이다. | 스택 추적으로 재현 | V-04 위치·설명·재현 수정 |
| 2 | 조치 | V-04의 읽기 루프 상한은 폭탄을 막지 못한다. | 1과 같은 근거 | 조치 1을 디코드 전 원시 길이·필터 검사로 교체 |
| 3 | 누락 | `/_k1`이 없는 PDF도 이미지 XObject로 같은 고갈을 일으킨다(56행). | 검토자 입력으로 재실행해 재현 | V-04에 경로 (b)와 조치 2 추가 |
| 4 | 조치 | V-04의 `setupMixed`는 동작하지만 임시 파일 부담이 디스크로 옮겨간다. | 미재실행(검토자 실행 결과 인용) | 조치 3을 주 메모리 한도 방식으로 변경하고 출처 명시 |
| 5 | 조치 | V-01의 다이제스트 안은 그대로는 성립하지 않는다(삽입 스트림 식별 불가, 리소스 누락, AAD와 본문 비교의 충돌, 검증 측 변경·버전 상향 누락). | 코드 대조로 확인 | 조치를 발급 기록 대조(단기)와 형식 변경(설계 요건 명시)으로 재작성, AAD 제거 |
| 6 | 오탐·과장 | V-07 조치 3의 "공개 API에 PDFBox 타입이 없다"는 사실이 아니다. | `PdfForensicEmbedder.java:22, 35`, `PdfProtector.java:8` 확인 | Jackson만 `implementation`으로, PDFBox는 조건부로 수정 |
| 7 | 누락 | 소유자 암호와 사용자 암호가 같으면 열람 암호로 소유자 권한을 얻는다. | PoC 재현 | V-05 (c)와 조치 3 추가 |
| 8 | 누락 | 이미 암호화된 입력 PDF는 예외로 실패하거나 원 제한이 조용히 교체된다. | PoC 재현 | V-05 (d)와 조치 4 추가 |
| 9 | 누락 | `KeyUtil.randomOwnerPassword(int)` 인자 검증 부재. | PoC 재현 | V-11에 추가 |
| 10 | 누락 | 서명 무효 워터마크도 클레임을 반환한다. | 코드 확인 | V-11에 추가 |
| 11 | 위험도 | V-08의 판정 근거가 Info 기준 문장과 같다. | 기준 대조 | V-08을 Low에서 Info로 변경, 통계 갱신 |
| 12 | 위험도 | V-03 (a)는 `valid=true` 오귀속이라 High 기준과 겹친다. Medium 근거를 명시해야 한다. | 기준 대조 | V-03 영향에 근거 추가, 2.3 기준 문구 보완 |
| 13 | 조치 | V-05의 접근성 추출 차단은 정당한 기능을 훼손한다. | 동의 | 해당 줄 삭제 |
| 14 | 조치 | V-06의 AES 32바이트 강제는 기존 발급분 검증을 깨고, public 메서드로 우회된다. | 코드 확인 | 발급·검증 경로를 나눠 수정 |
| 15 | 조치 | V-02 조치 1의 HMAC 파생 이름은 무작위 이름과 차이가 없고, V-04 표면을 넓힌다. | 동의 | 무작위 이름으로 수정, V-04 선행 조건 명시 |
| 16 | 근거 | V-11 "변조와 입력 오류가 구분되지 않는다"는 부정확하다. | 코드 확인 | "변조와 잘못된 AES 키"로 수정 |
| 17 | 근거 | "모든 재현을 키 없이 수행"은 V-03(a), V-06에 해당하지 않는다. | PoC 코드 확인 | 2.2 문장 한정 |
| 18 | 근거 | V-01 blob 길이는 163~164바이트로 달라진다. | 원인(nonce 자릿수) 확인 | 재현 설명에 추가 |
| 19 | 근거 | 줄 번호 보정(V-06 "38행 뒤", `KeyUtil.java:13-15`), V-09의 시드 표현 완화. | 코드 확인 | 반영 |
| 20 | 근거 | V-07의 CVE 목록은 제3자가 확인할 수 있게 권고 ID를 병기해야 한다. | OSV 응답 원문 대조 | 권고 ID·수정 버전 표 추가 |
| 21 | 일관성 | V-11은 본문에 PoC 확인이 있는데 통계는 "재현 없음"이다. 비율 합계가 99%다. 목록과 본문 제목이 다르다. | 재계산 | 1.1, 1.3, 1.4 수정 |

검토자가 확인한 그 밖의 사항: 모든 `파일:줄` 인용에 내용이 틀린 것은 없었다. V-01, V-02, V-03, V-05, V-06의 PoC 출력은 재실행에서 같게 나왔다. 조치 방안에 쓴 `PDDocument.load(InputStream, String, MemoryUsageSetting)`, `MemoryUsageSetting` 설정 메서드, JDK 8 multi-catch는 대상 버전에 존재한다.

### 6.3 반영 후 남은 한계

- 수정한 조치 방안(V-04 조치 1·2, V-01 조치 2, V-05 조치 3·4)은 대상 코드에 적용해 실행해 보지 않았다. 적용 시 회귀 테스트가 필요하다.
- V-07은 권고 16건 각각의 도달 가능성을 실행으로 검증하지 않았다.
- V-04는 힙 256MB 조건에서만 측정했다.
- 2차 검토자도 작성자와 같은 계열의 AI 모델이다. 같은 유형의 누락을 공유할 수 있으므로 사람 리뷰어의 검토(PR 리뷰)를 대체하지 않는다.
- 반영 후 통계 재계산: 위험도별 0+1+3+3+5=12, 유형별 3+1+4+2+2=12, 검증 상태별 7+1+4=12.
