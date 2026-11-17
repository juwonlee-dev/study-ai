# KurbyPdf 보안 취약점 분석 보고서

## 1. 탐지 결과 통계

| 위험도 | 기준 | 탐지 건수 |
| --- | --- | :---: |
| 🟥 치명 (Critical) | 인증 없이 원격 코드 실행, 키·원문 대량 유출처럼 즉시 전면 피해 | **0** |
| 🟧 높음 (High) | 라이브러리의 핵심 보안 기능(위변조 검출·추적)이 키 없이 무력화됨 | **2** |
| 🟨 중간 (Medium) | 조건(사용자 암호 보유, 검증 키 보유, 신뢰할 수 없는 입력 등)이 필요하지만 보안 목적을 훼손하거나 서비스 장애를 일으킴 | **6** |
| 🟩 낮음 (Low) | 오용 가능성을 높이거나 방어를 약화하지만 단독 피해는 제한적 | **3** |
| ⬜ 정보 (Info) | 직접적인 취약점은 아니지만 개선이 필요한 구성·문서 | **3** |
| **합계** | | **14** |

| ID | 위험도 | 취약점 | 재현 | 조치 검증 |
| --- | --- | --- | :---: | :---: |
| H-1 | 높음 | 워터마크가 문서 내용에 묶이지 않아 위변조를 검출하지 못함 | ✅ | 부분 차단 |
| H-2 | 높음 | 워터마크를 다른 PDF로 옮겨도 유효하게 검증됨 | ✅ | 부분 차단 |
| M-1 | 중간 | 대칭키 서명이라 검증 측이 임의 사용자 워터마크를 위조할 수 있음 | ✅ | 설계 변경 필요 |
| M-2 | 중간 | 가짜 워터마크 하나로 검증 전체가 실패함 | ✅ | ✅ 차단 |
| M-3 | 중간 | 고정 마커(`/_k1`)로 워터마크를 쉽게 찾아 제거할 수 있음 | ✅ | 완화만 가능 |
| M-4 | 중간 | 사용자 암호 보유자에게 수정·조립·주석 권한을 허용함 | ✅ | ✅ 차단 |
| M-5 | 중간 | 압축 폭탄 PDF로 검증·삽입 시 자원 고갈(OOM) | ✅ | ✅ 차단(상한 내 비용 남음) |
| M-6 | 중간 | 알려진 취약점이 있는 Jackson 2.17.1 사용(Fat JAR에 내장) | 조회 | 버전 상향 |
| L-1 | 낮음 | HMAC·AES 키 길이와 null 여부를 검증하지 않음 | ✅ | ✅ 차단 |
| L-2 | 낮음 | 워터마크 위치를 예측 가능한 난수(`java.util.Random` + 현재 시각)로 정함 | 코드 | 코드 수정 |
| L-3 | 낮음 | 사용자 암호를 주지 않으면 소유자 암호·권한 보호 없이 저장됨 | ✅ | ✅ 차단 |
| I-1 | 정보 | 테스트 코드의 고정 키와 소유자 암호 콘솔 출력 | 코드 | - |
| I-2 | 정보 | Gradle Wrapper 파일 누락, 이관된 Shadow 플러그인 ID 사용 | 코드 | - |
| I-3 | 정보 | README의 보안 기능 설명과 API가 실제 코드와 다름 | 코드 | - |

> **재현** ✅: PoC로 실제 동작을 확인함 · 조회: 취약점 DB 조회 · 코드: 소스 정적 분석으로 확인함
>
> **조치 검증** ✅: 6장의 조치 코드를 적용한 사본에서 같은 PoC가 막히는 것을 확인함 · 부분 차단: 일부 시나리오만 막힘(한계는 각 항목에 적음)

---

## 2. 분석 개요

| 항목 | 내용 |
| --- | --- |
| 대상 | [juwonlee-dev/KurbyPdf](https://github.com/juwonlee-dev/KurbyPdf) (`master`, 커밋 `74d3aed`) |
| 성격 | PDF에 숨김 워터마크(AES-GCM 암호화 + HMAC-SHA256 서명)를 넣고 검증하는 Java 8 라이브러리 |
| 범위 | `src/main/java` 전체(9개 파일), `src/test`, `build.gradle.kts`, `README.md` |
| 의존성 | `org.apache.pdfbox:pdfbox:2.0.30`, `com.fasterxml.jackson.core:jackson-databind:2.17.1` |
| 분석 일자 | 2026-11-17 |
| 도구 | Claude Code(Opus 5.5), JDK 1.8.0_261, PDFBox 2.0.30 등 실제 의존성 JAR(Maven Central SHA-1 대조), OSV.dev 취약점 DB |

### 분석 방법

1. 소스 전체를 읽고 README가 약속하는 보안 속성(숨김, 무결성, 위변조 검출, 암호 보호)을 위협 모델로 정리했다.
2. 공격자를 셋으로 나눠 각 보안 속성이 지켜지는지 확인했다.
   - **열람자**: 배포받은 PDF와 사용자 암호를 가진 사람. 유출 추적 대상이다.
   - **검증자**: 검증을 위해 HMAC·AES 키를 가진 쪽(서비스 서버, 협력사 등)
   - **외부 입력자**: 삽입·검증 API에 임의의 PDF를 올리는 사람
3. 후보마다 PoC를 작성하고, 원본 소스를 그대로 컴파일해 실행했다(5장).
4. 조치 코드를 원본 사본에 적용해 같은 PoC를 다시 실행하고, 정상 기능(원래 테스트 PDF의 삽입·검증)이 유지되는지 확인했다(6장).
5. 의존성 버전을 OSV.dev에서 조회했다.
6. 독립 에이전트가 보고서를 2차 검토했고, 지적사항을 반영해 조치 코드와 보고서를 고친 뒤 다시 검증했다(7장).

---

## 3. 취약점 상세

### H-1. 워터마크가 문서 내용에 묶이지 않아 위변조를 검출하지 못함 — 🟧 높음

- **위치**: `WatermarkPayload.java:27-38`, `PdfWatermarkInspector.java:96-139`
- **설명**: 서명 대상(`body`)은 `v`, `claims`, `ts`, `nonce`뿐이고 문서 내용은 전혀 포함되지 않는다. 검증도 워터마크 스트림 자체의 서명만 확인한다. 그래서 페이지 내용을 고치거나, 페이지를 추가·삭제하거나, 페이지를 잘라 내도(CropBox·Rotate 변경) 검증 결과가 바뀌지 않는다. README는 "삽입된 워터마크의 존재 여부, 무결성, **위변조 여부** 확인 가능"(README.md:15), "위변조 방지"(README.md:100)라고 안내한다. 사용자가 검증 성공을 "문서가 원본 그대로"로 오해하게 된다.
- **재현(키 없이 사용자 암호만 사용)**:
  ```
  [0]   baseline                         : valid=true  claims={uid=victim-001}
  [1]   텍스트·페이지 추가                 : valid=true  claims={uid=victim-001}
  [R1]  워터마크 스트림을 공격자 내용으로 교체 : valid=true  claims={uid=victim-001}
  [R1b] CropBox 10x10 + Rotate 90       : valid=true  claims={uid=victim-001}
  ```
- **영향**: 변조된 문서가 정상 원본으로 판정된다. 계약서·시험지처럼 내용 무결성이 중요한 용도에서 위험하다.
- **조치 방안**:
  1. (근본) 내용 무결성이 필요하면 워터마크와 별개로 PDF 전자서명(PAdES)을 쓴다. PDFBox의 `PDDocument.addSignature`와 BouncyCastle로 구현할 수 있다. **무결성은 이 방법으로만 보장된다.**
  2. (현재 구조 유지) 서명 대상에 문서 지문을 넣는다. 지문은 페이지 수, 각 페이지의 MediaBox·CropBox·Rotate, 콘텐츠 스트림을 SHA-256으로 해시한 값이고, `body.doc`에 넣는다. 검증할 때는 워터마크가 덧붙인 마지막 스트림을 빼고 같은 해시를 다시 계산한다. 이때 마지막 스트림이 워터마크 형식인지도 확인한다. 허용 연산자는 `q Q cm re W n h Do`뿐이고, `re`는 0×0만 허용한다. 그래야 마지막 스트림을 공격자 내용으로 바꾸는 변조(R1)도 걸러진다. 코드는 6장 조치 ①을 참고한다.
  3. README의 "위변조 여부 확인" 문구를 실제 보장 범위에 맞게 고친다.
- **조치 ②의 한계**:
  - 지문은 콘텐츠 스트림과 페이지 기하만 덮는다. 폰트·이미지 같은 리소스 교체, 주석·양식 필드 추가는 검출하지 못한다.
  - 콘텐츠 스트림을 다시 쓰는 최적화 도구를 거치면 정상 문서도 불일치로 판정될 수 있다.
  - 기존 버전으로 만든 PDF에는 `doc` 값이 없어 검증에 실패한다. 페이로드 버전(`v`)을 2로 올리고, `v=1` 문서는 "레거시(무결성 미보장)"로 따로 표시하는 이행 기간을 둔다.

### H-2. 워터마크를 다른 PDF로 옮겨도 유효하게 검증됨 — 🟧 높음

- **위치**: `PdfForensicEmbedder.java:22-23, 43-64`, `PdfWatermarkInspector.java:55-66`
- **설명**: H-1과 원인이 같다. 암호화된 페이로드는 어떤 문서에 붙어 있어도 복호화와 서명 검증을 통과한다. 열람자는 사용자 암호로 문서를 연 뒤 `/_k1` 스트림의 바이트를 꺼낼 수 있다. 그 바이트를 공개 메서드 `PdfForensicEmbedder.embed`로 다른 PDF에 넣거나, 자기 사본의 `/_k1` 값을 바꿔치기할 수 있다.
- **재현(키 없이)**:
  ```java
  byte[] raw = read(findWm(PDDocument.load(victimPdf, "userpw")));   // 동료 사본에서 페이로드 추출
  PDDocument other = PDDocument.load(blank("COMPLETELY DIFFERENT DOCUMENT"));
  PdfForensicEmbedder.embed(other, raw);                               // [2] 다른 문서에 이식
  ```
  ```
  [2]  다른 문서로 이식                       : valid=true  claims={uid=victim-001}
  [R2] 같은 원본의 내 사본에 동료 페이로드 교체 : valid=true  claims={uid=victim-001}
  ```
- **영향**: 유출자가 자신이 받은 문서의 워터마크를 동료의 워터마크로 바꿔 유출할 수 있다. 그러면 추적 결과가 무고한 사용자(`victim-001`)를 가리킨다. 유출 추적이라는 라이브러리의 목적(README.md:106-108)이 정면으로 무너진다.
- **조치 방안**:
  1. H-1의 조치 ②(문서 지문 바인딩)를 적용하면 **다른 문서로 옮긴 페이로드([2])는 검증에 실패한다**. 6장에서 확인했다.
  2. 하지만 **같은 원본을 받은 수신자끼리는 지문이 같아서 [R2]는 막을 수 없다**. 지문은 워터마크를 넣기 전 원본으로 계산하기 때문이다. 이 시나리오는 워터마크를 떼어 낼 수 있다는 점(M-3) 자체가 원인이다. 그래서 아래 보완책을 함께 쓴다.
     - 수신자마다 페이지 안에 눈에 보이는 추적 표식(클레임에서 만든 짧은 ID)을 콘텐츠 스트림에 함께 넣는다. 그러면 지문이 수신자마다 달라져 바꿔치기가 검출된다.
     - 서버에 `nonce`·`ts`와 발급 대상, 발급한 문서 파일의 해시를 기록해 두고, 회수한 문서와 대조한다.
  3. `PdfForensicEmbedder`, `WatermarkPayload`처럼 내부 구현 클래스는 `public`을 거두고 패키지 전용으로 바꿔, 진입점을 `KurbyPdf.watermark`로 한정한다.

### M-1. 대칭키 서명이라 검증 측이 임의 사용자 워터마크를 위조할 수 있음 — 🟨 중간

- **위치**: `WatermarkPayload.java:36-38, 54-56`, `PdfVerificationUtil.java:18-21`
- **설명**: 검증에 필요한 키(HMAC 키, AES 키)가 생성에 필요한 키와 같다. 검증을 맡은 모든 시스템과 사람이 원하는 `uid`를 넣은 "진짜" 워터마크를 만들 수 있다.
- **재현**:
  ```
  [5] 검증 키로 uid=innocent-user 생성 : valid=true  claims={uid=innocent-user}
  ```
- **영향**: 검증 기능을 협력사나 여러 서버에 배포하면 키 보유자가 늘어난다. 그중 한 곳만 유출돼도 누구에게든 유출 책임을 씌우는 워터마크를 만들 수 있다. 추적 결과를 증거로 쓸 때 부인 방지가 성립하지 않는다.
- **조치 방안**: 서명을 비대칭 방식으로 바꾼다. 서버만 개인키로 서명하고(`Signature.getInstance("SHA256withECDSA")`, Java 8 지원), 검증 측에는 공개키만 배포한다. AES-GCM 암호화는 클레임 기밀성용으로 남기되, 검증 결과는 서명 검증으로만 판단한다. 공개 API의 키 형식이 바뀌므로 메이저 버전으로 올려 배포한다. *이 조치는 설계 변경이라 이번 검증 범위에서는 코드를 적용하지 않았다.*

### M-2. 가짜 워터마크 하나로 검증 전체가 실패함 — 🟨 중간

- **위치**: `PdfWatermarkInspector.java:55-71, 103-105`, `PdfVerificationUtil.java:40, 53-55`
- **설명**: `extractAll`은 `/_k1`이 붙은 모든 Form XObject를 복호화한다. 그중 하나라도 `AEADBadTagException`을 던지면 예외가 그대로 올라와 정상 워터마크까지 버려진다. 열람자는 키 없이 아무 바이트나 담은 `/_k1` 스트림을 페이지 리소스에 추가하기만 하면 된다.
- **재현**:
  ```
  [4] 64바이트 가짜 /_k1 추가 : valid=false reason=EXCEPTION:AEADBadTagException
  ```
- **영향**: 정상 워터마크가 남아 있어도 "검증 실패"가 된다. 워터마크를 지우지 않고도 유출 추적을 피할 수 있다(안티 포렌식).
- **조치 방안**: 후보별로 복호화·파싱 예외(`GeneralSecurityException`, `IOException`, `IllegalArgumentException`)만 잡아 그 후보를 건너뛴다. 키 설정 오류는 후보 루프에 들어가기 전에 `verifyDetailed`에서 먼저 걸러 `INVALID_KEYS`로 돌려준다(L-1). 그래서 키 오류가 "가짜 후보"로 묻히지 않는다. 복호화에 성공한 후보는 서명·지문이 맞지 않아도 결과에 남긴다. `extractFirst`는 유효한 후보를 먼저 돌려주고, 없으면 무효 후보를 돌려준다. 그 결과 "워터마크 없음(`WATERMARK_NOT_FOUND`)"과 "변조·이식 탐지(`INVALID_SIGNATURE`)"가 구분된다. 코드는 6장 조치 ②를 참고한다.

### M-3. 고정 마커(`/_k1`)로 워터마크를 쉽게 찾아 제거할 수 있음 — 🟨 중간

- **위치**: `PdfForensicEmbedder.java:16-17, 62-64`, `PdfWatermarkInspector.java:24`
- **설명**: 모든 문서의 워터마크가 고정된 비표준 키 `/_k1`, `/_k1v`를 쓴다. 0×0 클리핑 영역의 Form XObject에 매달려 있어서, 사용자 암호로 문서를 연 사람이면 누구나 키 이름으로 찾아 지울 수 있다. README는 "눈에 보이지 않는 **안전한** 워터마크를 숨김"(README.md:9)이라고 설명한다.
- **재현(키 없이)**:
  ```
  [3] /_k1 키 제거 : valid=false reason=WATERMARK_NOT_FOUND
  ```
- **영향**: 추적용 워터마크가 몇 줄짜리 코드로 사라진다. H-2의 바꿔치기 공격도 이 성질 때문에 가능하다.
- **조치 방안**: 숨김 워터마크는 원리상 완전히 막을 수 없으므로 아래처럼 제거 비용을 높이고 탐지를 보완한다.
  1. 마커 이름을 문서마다 무작위로 정한다(예: 페이로드 해시에서 파생). 검증기는 모든 Form 딕셔너리의 스트림 값을 후보로 검사한다(M-2 조치로 가짜 후보는 안전하게 무시된다).
  2. M-4 조치로 수정 권한을 막아, 일반 편집 도구로 문서를 고치려면 소유자 암호가 필요하게 한다.
  3. 검증 결과 `WATERMARK_NOT_FOUND`를 "정상 아님"으로 다루는 운영 정책을 README에 명시한다. H-2 보완책처럼 눈에 보이는 추적 ID를 함께 넣는다.

### M-4. 사용자 암호 보유자에게 수정·조립·주석 권한을 허용함 — 🟨 중간

- **위치**: `PdfProtector.java:9-11`
- **설명**: `new AccessPermission()`은 모든 권한을 허용한 상태로 시작한다. 코드는 내용 추출만 막으므로 수정(`canModify`), 페이지 조립, 주석·양식 편집은 그대로 허용된다.
- **재현**:
  ```
  [6] 사용자 암호로 연 문서 : isOwner=false canModify=true canAssemble=true canModifyAnnotations=true canFillInForm=true canExtract=false canPrint=true
  ```
- **영향**: PDF 편집기에서 소유자 암호 없이 문서를 수정할 수 있어 H-1·M-3 공격이 더 쉬워진다.
- **조치 방안**: 수정·조립·주석·양식 권한을 끄고 `setReadOnly()`로 고정한다. 코드는 6장 조치 ③을 참고한다. PDF 권한은 호환 뷰어가 지키는 약속일 뿐이고 qpdf 같은 도구로 해제할 수 있다. 따라서 이 조치는 공격 비용을 높일 뿐 위변조 방지 수단이 아니라는 점을 README에 적는다.

### M-5. 압축 폭탄 PDF로 검증·삽입 시 자원 고갈(OOM) — 🟨 중간

- **위치**: `PdfWatermarkInspector.java:46, 80-94`, `KurbyPdf.java:21`, `PdfVerificationUtil.java:53-55`
- **설명**: 검증과 삽입 모두 외부에서 받은 PDF를 메모리 제한 없이 읽는다(`PDDocument.load`). 검증할 때 `/_k1` 스트림은 크기 제한 없이 끝까지 풀어서 메모리에 담는다. `verifyDetailed`는 `Exception`만 잡으므로 `OutOfMemoryError`가 호출자까지 그대로 전파된다.
- **재현**: 1 GiB의 0을 Flate로 압축한 스트림(PDF 약 1 MB)을 `/_k1`에 넣고 힙 256 MB로 검증했다.
  ```
  [7] 1 GiB 압축 폭탄(1,044,755 B) : THROWN java.lang.OutOfMemoryError: Java heap space
  ```
- **영향**: 업로드된 PDF에 워터마크를 넣거나 검증하는 서버라면, 1 MB 요청 하나로 JVM이 메모리 부족에 빠져 서비스가 중단될 수 있다.
- **조치 방안**:
  1. **디코딩 전에 거른다.** 정상 페이로드는 필터 없이 수백 바이트로 기록된다(`PdfForensicEmbedder.java:43-48`). 따라서 `/Filter`가 있거나 `/Length`가 64 KiB를 넘는 후보는 풀지 않고 버린다. PDFBox의 `COSStream.createInputStream()`은 필터 출력 전체를 먼저 디코딩하므로, 읽은 다음에 크기를 검사해서는 소용없다.
  2. **PDF 전체에 상한을 둔다.** 삽입과 검증 모두 `MemoryUsageSetting.setupMixed(16 MiB, 256 MiB)`로 메모리와 임시 파일 사용량의 상한을 건다. 상한값은 서비스가 다루는 PDF 크기에 맞게 정한다.
  3. 서비스 쪽에서도 업로드 크기와 처리 시간을 제한한다.
  - 코드는 6장 조치 ①·②를 참고한다.
- **조치 후 남는 비용**: 조치 ①의 지문 계산은 콘텐츠 스트림을 디코딩하므로, 콘텐츠 스트림에 넣은 압축 폭탄은 상한(256 MiB)에 닿을 때까지 디스크를 쓴다. 실측 결과 임시 파일은 약 186 MB까지 쓰였고, 1.5초 뒤 `IOException`으로 실패했다(5장 [B2]). OOM은 나지 않지만, 요청당 비용을 더 줄이려면 상한을 낮추거나 요청 동시성을 제한한다.

### M-6. 알려진 취약점이 있는 Jackson 2.17.1 사용(Fat JAR에 내장) — 🟨 중간

- **위치**: `build.gradle.kts:28, 42-64`
- **설명**: OSV.dev에서 조회한 결과, `jackson-databind 2.17.1`에 12건, `jackson-core 2.17.1`에 4건의 공개 권고가 있다. 그중 HIGH가 8건이다(예: GHSA-j3rv-43j4-c7qm, GHSA-rmj7-2vxq-3g9f, GHSA-cxp5-3px4-pw24, GHSA-p6pp-m3f8-5c89). 2.18 계열에서는 모두 2.18.11에서 수정됐다. `pdfbox 2.0.30`, `fontbox 2.0.30`, `commons-logging 1.2`는 조회 결과 권고가 없었다.
- **실제 도달 가능성**: KurbyPdf는 AES-GCM 복호화에 성공한 JSON만 `readTree`로 파싱하고 다형성 역직렬화를 쓰지 않는다. 키 없는 공격자가 이 라이브러리를 통해 취약 코드에 도달할 가능성은 낮다.
- **위험도를 중간으로 둔 이유**: README는 배포 방법으로 JAR 파일을 직접 참조하라고 안내한다(README.md:25-40). 그리고 `shadowJar`가 Jackson을 `io.github.juwonlee.shadow.jackson`으로 재배치해 JAR 안에 넣는다. 그래서 라이브러리 사용자가 자기 프로젝트의 의존성 관리로 버전을 올릴 수 없고, 고치려면 라이브러리를 새로 배포해야 한다. 앞으로 Maven 저장소에 POM과 함께 배포하면 `api(...)` 범위 때문에 취약 버전이 전이 의존성으로도 노출된다.
- **조치 방안**: Java 8과 호환되는 2.18.11 이상으로 올리고, BOM으로 core·databind·annotations 버전을 함께 고정한다. Jackson은 내부 구현에만 쓰이므로 `implementation`으로 바꾼다. 이후 새 버전을 배포한다.
  ```kotlin
  dependencies {
      api("org.apache.pdfbox:pdfbox:2.0.30")
      implementation(platform("com.fasterxml.jackson:jackson-bom:2.18.11"))
      implementation("com.fasterxml.jackson.core:jackson-databind")
  }
  ```
  CI에 OWASP Dependency-Check나 GitHub Dependabot을 붙여 같은 문제가 다시 쌓이지 않게 한다.

### L-1. HMAC·AES 키 길이와 null 여부를 검증하지 않음 — 🟩 낮음

- **위치**: `KurbyPdf.java:24-28`, `PdfVerificationUtil.java:24-38`
- **설명**: 삽입 쪽은 HMAC 키가 1바이트여도 그대로 쓴다. 키가 `null`이면 `Base64.getDecoder().decode(null)`에서 `NullPointerException`이 나는데, 어떤 입력이 잘못됐는지 알려 주지 않는다. 검증 쪽 `verifyBase64`는 Base64 디코딩이 `try` 밖에 있어서, `boolean`을 반환해야 할 API가 잘못된 키 문자열에 `IllegalArgumentException`을 던진다. `verifyDetailed`는 null만 확인하고 키 길이는 확인하지 않는다.
- **재현**:
  ```
  1바이트 HMAC 키 → 허용됨
  null HMAC 키   → NullPointerException
  ```
- **조치 방안**: 삽입·검증 양쪽에서 HMAC 키는 32바이트 이상, AES 키는 16·32바이트만 허용한다. null이나 형식 오류는 명확한 메시지(`keys must not be null`, `INVALID_KEYS`)로 거부한다. 키는 `SecureRandom`으로 만든 32바이트를 쓰라고 README에 적는다. 코드는 6장 조치 ④를 참고한다.

### L-2. 워터마크 위치를 예측 가능한 난수로 정함 — 🟩 낮음

- **위치**: `PdfForensicEmbedder.java:23, 40`
- **설명**: 위치 난수는 `new Random(System.currentTimeMillis())`로 만든다. 주석은 무작위 위치가 "보통 더 안전"하다고 하지만, 생성 시각을 알면 위치를 재현할 수 있다. 다만 M-3처럼 키 이름만으로도 찾을 수 있어서 단독 영향은 작다.
- **조치 방안**: 기본 `embed`에서는 `SecureRandom`을 쓰고, 재현성이 필요한 경우에만 시드를 받는 오버로드를 쓰도록 분리한다(이번 패치에는 넣지 않았다).
  ```java
  private static final SecureRandom POS_RND = new SecureRandom();
  public static void embed(PDDocument doc, byte[] encryptedPayload) throws Exception {
      embed(doc, encryptedPayload, 3, true, POS_RND.nextLong());
  }
  ```

### L-3. 사용자 암호를 주지 않으면 소유자 암호·권한 보호 없이 저장됨 — 🟩 낮음

- **위치**: `KurbyPdf.java:34-41`, `WatermarkRequest.java:10-11`
- **설명**: `userPassword`가 비어 있으면 `PdfProtector`를 호출하지 않는다. 문서는 암호화되지 않은 채 저장되고, 소유자 암호도 만들어지지 않는다. `WatermarkRequest`에 `optional`로 표시된 의도된 동작이다. 하지만 README의 "PDF 암호 보호" 설명과 달리 권한 제한까지 조용히 꺼지는 안전하지 않은 기본값이다. 이 상태에서는 워터마크 스트림이 평문으로 보여 M-3 제거가 더 쉬워진다.
- **재현**:
  ```
  [6b] 사용자 암호 없이 생성 : encrypted=false
  ```
- **조치 방안**: 사용자 암호가 없어도 빈 사용자 암호와 무작위 소유자 암호로 항상 보호를 적용한다. 빈 사용자 암호는 누구나 열 수 있으므로 기밀성은 없고, 권한 제한(M-4)과 스트림 암호화만 더해진다. 코드는 6장 조치 ③을 참고한다.
- **호환성 영향**: 조치 후에는 모든 출력이 AES-256으로 암호화되고, `canExtractContent=false`와 읽기 전용 권한이 항상 적용된다. `WatermarkResult.getOwnerPassword()`도 항상 null이 아닌 값을 반환한다. 이 동작 변경은 릴리스 노트에 적는다.

### I-1. 테스트 코드의 고정 키와 소유자 암호 콘솔 출력 — ⬜ 정보

- **위치**: `KurbyPdfTest.java:24-29, 80`
- **설명**: 테스트 키는 `0x11`, `0x22`로 채운 고정값이다. 생성된 소유자 암호는 표준 출력으로 찍힌다. 테스트 전용이지만 예제 코드를 그대로 옮겨 쓰면 운영 로그에 소유자 암호가 남는다.
- **조치 방안**: 테스트에서도 `SecureRandom`으로 키를 만들고, 소유자 암호는 출력하지 않고 `assertNotNull`로만 확인한다.

### I-2. Gradle Wrapper 파일 누락, 이관된 Shadow 플러그인 ID 사용 — ⬜ 정보

- **위치**: 저장소 루트, `build.gradle.kts:3`
- **설명**: `gradlew`는 있지만 `gradle/wrapper/gradle-wrapper.properties`와 `gradle-wrapper.jar`가 커밋되지 않았다. 그래서 Wrapper로 빌드할 수 없고, 빌드 환경마다 다른 Gradle 버전을 쓰게 된다. 배포본 무결성 검증(`distributionSha256Sum`)도 걸 수 없다. Shadow 플러그인은 `com.github.johnrengelman.shadow` 8.1.1을 쓰는데, 이 플러그인은 GradleUp으로 이관되어 `com.gradleup.shadow`로 배포되고 있다.
- **조치 방안**: `gradle wrapper --gradle-version <버전> --gradle-distribution-sha256-sum <해시>`로 Wrapper를 생성해 커밋한다. 플러그인 ID는 `com.gradleup.shadow` 최신 버전으로 바꾼다.

### I-3. README의 보안 기능 설명과 API가 실제 코드와 다름 — ⬜ 정보

- **위치**: `README.md:3, 9, 15, 31-40, 66-73, 92, 100, 111`, `KurbyPdf.java:31`, `PdfForensicEmbedder.java:20-23`
- **설명**:
  - README의 `PdfVerification.verify/verifyDetailed`는 존재하지 않는다. 실제 클래스는 `util.PdfVerificationUtil`이다. `result.getTimestamp()`도 없고, 실제 이름은 `getTimestampMillis()`이다.
  - 페이지당 워터마크 수가 주석에는 2개(`KurbyPdf.java:31`), 구현에는 3개다.
  - "안전한 워터마크"(README.md:3, 9), "위변조 여부 확인"(README.md:15), "위변조 검출 목적에 적합"(README.md:111)은 H-1·M-3 때문에 사실과 다르다.
  - Maven 예시는 `system` 스코프로 로컬 JAR를 참조해 의존성 검사 도구가 버전을 추적하지 못한다.
- **조치 방안**: API 이름과 숫자를 코드와 맞춘다. 보안 보장 범위(추적용 표식이며 무결성 보장이 아님, 제거 가능성)를 "주의사항"에 명시한다. 배포는 Maven Central 좌표로 안내한다.

---

## 4. 공격 시나리오 요약

| 시나리오 | 필요한 것 | 결과 | 관련 ID |
| --- | --- | --- | --- |
| 유출자가 자기 사본의 워터마크를 동료 것으로 바꿔 유출 | 자기 문서·동료 문서의 사용자 암호 | 동료가 유출자로 지목됨 | H-2, M-3 |
| 유출자가 가짜 `/_k1`을 덧붙여 유출 | 사용자 암호 | 검증 실패로 추적 불가 | M-2 |
| 내용을 고친 문서를 원본처럼 유통 | 사용자 암호 | 검증 성공 | H-1, M-4 |
| 검증 서버 운영자·협력사가 특정인을 모함 | 검증 키 | 임의 `uid`의 유효한 워터마크 생성 | M-1 |
| 삽입·검증 API에 1 MB PDF 업로드 | 없음 | JVM 메모리 고갈 | M-5 |

---

## 5. 재현 환경과 결과

- 원본 소스(`74d3aed`)를 JDK 1.8.0_261 `javac`로 컴파일했다.
- 의존성은 `build.gradle.kts`와 같은 버전의 JAR를 Maven Central에서 받아 SHA-1을 대조했다(pdfbox·fontbox 2.0.30, jackson-* 2.17.1, commons-logging 1.2).
- PoC는 저장소 밖 임시 폴더에서 실행했다. 피해자 문서는 `uid=victim-001`, 사용자 암호 `userpw`로 만들었다. 공격은 모두 HMAC·AES 키 없이 수행했다([5] 제외).
- [R1], [R1b], [R2], [B2]는 2차 검토 과정에서 추가한 시나리오다.

| 번호 | 시나리오 | 원본 결과 | 조치 후 |
| --- | --- | --- | --- |
| [0] | 정상 삽입 후 검증 | `valid=true` | `valid=true` ✅ 기능 유지 |
| [1] | 사용자 암호로 열어 텍스트·페이지 추가 | `valid=true` ❌ | `INVALID_SIGNATURE` ✅ |
| [R1] | 워터마크 그리기 스트림을 공격자 텍스트 스트림으로 교체 | `valid=true` ❌ | `INVALID_SIGNATURE` ✅ |
| [R1b] | CropBox를 10×10으로, Rotate를 90으로 변경 | `valid=true` ❌ | `INVALID_SIGNATURE` ✅ |
| [2] | 페이로드를 전혀 다른 PDF에 이식 | `valid=true` ❌ | `INVALID_SIGNATURE` ✅ |
| [R2] | 같은 원본을 받은 유출자 사본의 `/_k1`을 피해자 페이로드로 교체 | `valid=true` ❌ | `valid=true` ❌ (H-2 한계) |
| [3] | `/_k1` 키 제거 | `WATERMARK_NOT_FOUND` | `WATERMARK_NOT_FOUND` (M-3 완화 대상) |
| [4] | 64바이트 0으로 된 가짜 `/_k1` 추가 | `EXCEPTION:AEADBadTagException` ❌ | `valid=true` ✅ 정상 워터마크로 검증 |
| [5] | 검증 키로 `uid=innocent-user` 워터마크 생성 | `valid=true` ❌ | `valid=true` ❌ (M-1 설계 변경 필요) |
| [6] | 사용자 암호로 연 문서의 권한 | `canModify=true` 등 ❌ | `canModify=false` 등 ✅ |
| [6b] | 사용자 암호 없이 생성 | `encrypted=false` ❌ | `encrypted=true` ✅ |
| [7] | 1 GiB 압축 폭탄 `/_k1`, 힙 256 MB | `OutOfMemoryError` ❌ | `WATERMARK_NOT_FOUND`, 2 ms, 임시 파일 0 MB ✅ |
| [B2] | 1 GiB 압축 폭탄을 콘텐츠 스트림에 넣음, 힙 256 MB | `WATERMARK_NOT_FOUND`(콘텐츠를 읽지 않음) | `EXCEPTION:IOException`, 1.5 s, 임시 파일 약 186 MB (상한 내) |
| - | 원래 테스트 PDF(`sample.pdf`) 삽입·검증(암호 있음/없음) | `valid=true` | `valid=true` ✅ |
| - | 1바이트 HMAC 키 | 허용 ❌ | `hmacKey must be >= 32 bytes` ✅ |
| - | null HMAC 키 | `NullPointerException` ❌ | `keys must not be null` ✅ |

---

## 6. 조치 코드 (현재 소스 기준)

아래 조치 ①~④는 원본 사본에 그대로 적용해 컴파일하고, 5장의 "조치 후" 결과를 얻은 코드다. M-1(비대칭 서명), M-6(의존성 상향), L-2(위치 난수)는 설계·빌드 변경이라 이 패치에 넣지 않았다.

### 조치 ① 문서 지문 바인딩과 메모리 상한 (H-1, H-2, M-5)

새 파일 `src/main/java/io/github/juwonlee/kurbypdf/DocFingerprint.java`:

```java
package io.github.juwonlee.kurbypdf;

import org.apache.pdfbox.contentstream.operator.Operator;
import org.apache.pdfbox.cos.COSNumber;
import org.apache.pdfbox.pdfparser.PDFStreamParser;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.common.PDRectangle;
import org.apache.pdfbox.pdmodel.common.PDStream;

import java.io.InputStream;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;

final class DocFingerprint {
    static final String MISMATCH = "MISMATCH";
    /** 워터마크 스트림에 허용하는 연산자. 0x0 클리핑 안에서 Form을 그리는 것 외에는 아무것도 할 수 없다. */
    private static final Set<String> WM_OPS = new HashSet<String>(Arrays.asList("q", "Q", "cm", "re", "W", "n", "h", "Do"));

    private DocFingerprint() {}

    /**
     * 페이지 수, 각 페이지의 기하 정보(MediaBox/CropBox/Rotate)와 콘텐츠 스트림을 해시한다.
     * forVerify=true면 마지막 스트림을 워터마크 스트림으로 보고 제외하되, 워터마크 형식이 아니면 MISMATCH를 반환한다.
     */
    static String of(PDDocument doc, boolean forVerify) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        md.update(Integer.toString(doc.getNumberOfPages()).getBytes("UTF-8"));
        for (PDPage page : doc.getPages()) {
            md.update(("|" + box(page.getMediaBox()) + box(page.getCropBox()) + page.getRotation()).getBytes("UTF-8"));
            List<PDStream> streams = new ArrayList<PDStream>();
            for (Iterator<PDStream> it = page.getContentStreams(); it.hasNext(); ) streams.add(it.next());
            int n = streams.size();
            if (forVerify) {
                if (n == 0 || !isWatermarkStream(streams.get(n - 1))) return MISMATCH;
                n--;
            }
            for (int i = 0; i < n; i++) {
                try (InputStream in = streams.get(i).createInputStream()) {
                    byte[] buf = new byte[8192];
                    int r;
                    while ((r = in.read(buf)) != -1) md.update(buf, 0, r);
                }
            }
        }
        return Base64.getEncoder().encodeToString(md.digest());
    }

    private static String box(PDRectangle b) {
        return b.getLowerLeftX() + "," + b.getLowerLeftY() + "," + b.getUpperRightX() + "," + b.getUpperRightY() + ";";
    }

    private static boolean isWatermarkStream(PDStream s) throws Exception {
        PDFStreamParser parser = new PDFStreamParser(s.toByteArray());
        parser.parse();
        List<Object> operands = new ArrayList<Object>();
        for (Object token : parser.getTokens()) {
            if (!(token instanceof Operator)) { operands.add(token); continue; }
            String op = ((Operator) token).getName();
            if (!WM_OPS.contains(op)) return false;
            if (op.equals("re")) {
                for (Object o : operands) {
                    if (!(o instanceof COSNumber) || ((COSNumber) o).floatValue() != 0f) return false;
                }
            }
            operands.clear();
        }
        return true;
    }
}
```

`WatermarkPayload.java` — 서명 대상에 `doc` 추가:

```diff
-    public static byte[] buildPayload(Map<String, String> claimsIn, byte[] hmacKey, byte[] aesKey) throws Exception {
+    public static byte[] buildPayload(Map<String, String> claimsIn, byte[] hmacKey, byte[] aesKey, String docHash) throws Exception {
@@
         body.put("nonce", Long.toUnsignedString(RND.nextLong()));
+        body.put("doc", docHash);
@@
         wrap.put("nonce", body.get("nonce"));
+        wrap.put("doc", body.get("doc"));
```

`KurbyPdf.java` — 메모리 상한, 삽입 직전 지문 계산(키 검증은 조치 ④, 보호 적용은 조치 ③):

```diff
-            doc = PDDocument.load(bin);
+            doc = PDDocument.load(bin, "", org.apache.pdfbox.io.MemoryUsageSetting.setupMixed(16L << 20, 256L << 20));
@@
-            byte[] payload = WatermarkPayload.buildPayload(claims, hmacKey, aesKey);
+            byte[] payload = WatermarkPayload.buildPayload(claims, hmacKey, aesKey, DocFingerprint.of(doc, false));
```

`PdfForensicEmbedder.java` — 페이지에 콘텐츠 스트림이 정확히 하나만 덧붙도록 한다. `resetContext=true`이면 PDFBox가 페이지 앞에 `q` 스트림을 하나 더 넣어 지문이 달라진다. 워터마크는 0×0 영역으로 잘리므로 렌더링에는 영향이 없다.

```diff
-            try (PDPageContentStream cs = new PDPageContentStream(doc, page, PDPageContentStream.AppendMode.APPEND, true, true)) {
+            try (PDPageContentStream cs = new PDPageContentStream(doc, page, PDPageContentStream.AppendMode.APPEND, true, false)) {
```

`PdfWatermarkInspector.java` — 메모리 상한, 검증 시 지문 비교:

```diff
-            doc = (password != null && !password.isEmpty()) ? PDDocument.load(bin, password) : PDDocument.load(bin);
+            doc = PDDocument.load(bin, password == null ? "" : password,
+                    org.apache.pdfbox.io.MemoryUsageSetting.setupMixed(16L << 20, 256L << 20));
+            String docHash = DocFingerprint.of(doc, true);
@@
-    private static DecodedWatermark decryptAndVerify(byte[] blob, byte[] hmacKey, byte[] aesKey) throws Exception {
+    private static DecodedWatermark decryptAndVerify(byte[] blob, byte[] hmacKey, byte[] aesKey, String docHash) throws Exception {
@@
         body.put("nonce", root.path("nonce").asText(""));
+        body.put("doc", root.path("doc").asText(""));
@@
-        boolean valid = MessageDigest.isEqual(expect, got); // Arrays.equals(expect, got); // 타이밍 공격 방어
+        boolean valid = MessageDigest.isEqual(expect, got)
+                && MessageDigest.isEqual(docHash.getBytes("UTF-8"), root.path("doc").asText("").getBytes("UTF-8")); // Arrays.equals(expect, got); // 타이밍 공격 방어
```

### 조치 ② 후보 격리, 디코딩 전 필터링, 실패 사유 구분 (M-2, M-5)

`PdfWatermarkInspector.java`:

```diff
     private static final int IV_LEN = 12;
+    private static final int MAX_PAYLOAD = 64 * 1024;
@@ extractFirst
         List<DecodedWatermark> list = extractAll(pdf, hmacKey, aesKey, password);
-        return list.isEmpty() ? null : list.get(0);
+        for (DecodedWatermark w : list) if (w.isSignatureValid()) return w;   // 유효한 후보 우선
+        return list.isEmpty() ? null : list.get(0);                           // 없으면 무효 후보(→ INVALID_SIGNATURE)
@@ extractAll
                             if (!seen.contains(stream)) {
                                 seen.add(stream);
-                                byte[] enc = streamToBytes(stream);
-                                DecodedWatermark rec = decryptAndVerify(enc, hmacKey, aesKey);
-                                out.add(rec);
+                                // 정상 페이로드는 필터 없이 수백 바이트로 기록된다. 디코딩 전에 걸러 압축 폭탄을 막는다.
+                                if (stream.containsKey(COSName.FILTER) || stream.getLength() > MAX_PAYLOAD) continue;
+                                try {
+                                    byte[] enc = streamToBytes(stream);
+                                    out.add(decryptAndVerify(enc, hmacKey, aesKey, docHash));
+                                } catch (java.security.GeneralSecurityException | java.io.IOException | IllegalArgumentException bad) {
+                                    // 복호화·파싱이 안 되는 후보(가짜 워터마크)는 건너뛴다
+                                }
                             }
```

### 조치 ③ 권한 축소와 항상 보호 적용 (M-4, L-3)

`PdfProtector.java`:

```diff
         ap.setCanPrint(true);
         ap.setCanExtractContent(false);
+        ap.setCanModify(false);
+        ap.setCanAssembleDocument(false);
+        ap.setCanModifyAnnotations(false);
+        ap.setCanFillInForm(false);
+        ap.setReadOnly();
```

`KurbyPdf.java`:

```diff
-            String ownerPwd = null;
-            if (req.getUserPassword() != null && !req.getUserPassword().isEmpty()) {
-                ownerPwd = req.getOwnerPassword();
-                if (ownerPwd == null || ownerPwd.isEmpty()) {
-                    ownerPwd = KeyUtil.randomOwnerPassword();
-                }
-                PdfProtector.applyUserPassword(doc, req.getUserPassword(), ownerPwd);
-            }
+            String ownerPwd = req.getOwnerPassword();
+            if (ownerPwd == null || ownerPwd.isEmpty()) {
+                ownerPwd = KeyUtil.randomOwnerPassword();
+            }
+            String userPwd = req.getUserPassword() == null ? "" : req.getUserPassword();
+            PdfProtector.applyUserPassword(doc, userPwd, ownerPwd);
```

### 조치 ④ 삽입·검증 양쪽 키 검증 (L-1)

`KurbyPdf.java`:

```diff
+            if (req.getHmacKeyBase64() == null || req.getPayloadAesKeyBase64() == null)
+                throw new IllegalArgumentException("keys must not be null");
             byte[] hmacKey = Base64.getDecoder().decode(req.getHmacKeyBase64());
             byte[] aesKey  = Base64.getDecoder().decode(req.getPayloadAesKeyBase64());
             Map<String, String> claims = req.getClaims();
 
+            if (hmacKey.length < 32) throw new IllegalArgumentException("hmacKey must be >= 32 bytes");
+            if (aesKey.length != 16 && aesKey.length != 32) throw new IllegalArgumentException("aesKey must be 16 or 32 bytes");
```

`util/PdfVerificationUtil.java`:

```diff
         if (hmacKeyBase64 == null || aesKeyBase64 == null) return false;
-        byte[] hmac = Base64.getDecoder().decode(hmacKeyBase64);
-        byte[] aes  = Base64.getDecoder().decode(aesKeyBase64);
-        return verify(pdfBytes, userPassword, hmac, aes);
+        try {
+            byte[] hmac = Base64.getDecoder().decode(hmacKeyBase64);
+            byte[] aes  = Base64.getDecoder().decode(aesKeyBase64);
+            return verify(pdfBytes, userPassword, hmac, aes);
+        } catch (IllegalArgumentException e) {
+            return false;
+        }
@@ verifyDetailed
             return Result.fail("MISSING_KEYS");
         }
+        if (hmacKey.length < 32 || (aesKey.length != 16 && aesKey.length != 32)) {
+            return Result.fail("INVALID_KEYS");
+        }
```

---

## 7. 2차 검토

### 절차

| 항목 | 내용 |
| --- | --- |
| 검토자 | 1차 작성 세션과 분리된 독립 Claude Code 에이전트(Opus 5.5) |
| 일자 | 2026-11-17 |
| 방법 | 보고서의 모든 파일:라인 인용을 원본 소스와 대조했다. OSV.dev를 다시 조회했다. 원본과 조치본에서 PoC를 직접 다시 실행했다. 새 공격 시나리오(R1, R1b, R2, R3)도 작성해 실행했다. |
| 결론 | 라인 인용, 통계 합계, OSV 수치, 원본 재현 결과는 정확함. 다만 1차 초안의 조치 ①·②가 일부 시나리오를 막지 못해, H-1·H-2·M-5의 "✅ 차단" 표기가 과장이라는 지적을 받았다. |

### 지적사항과 반영 결과

| # | 분류 | 지적 | 반영 |
| --- | --- | --- | --- |
| 1 | 조치 오류 | 같은 원본을 받은 수신자끼리 페이로드를 바꾸면([R2]) 지문이 같아 통과함 | H-2를 "부분 차단"으로 낮추고 한계와 보완책(수신자별 표식, 발급 기록 대조)을 추가함. [R2]를 5장에 기록함 |
| 2 | 조치 오류 | 마지막 스트림을 무조건 제외해 스트림 교체([R1])와 CropBox·Rotate 변조([R1b])가 통과함 | 지문에 페이지 기하를 넣고, 마지막 스트림 연산자 화이트리스트를 추가함. 재실행 결과 둘 다 `INVALID_SIGNATURE`로 검출됨. 남는 한계는 H-1에 명시함 |
| 3 | 조치 오류 | 64 KiB 상한은 디코딩 후에 적용돼 압축 폭탄이 디스크 약 1 GB 소모로 바뀜. 지문 계산이 새 공격면이 됨 | 디코딩 전에 `/Filter`·`/Length`로 거르게 바꿈([7]: 2 ms, 임시 파일 0 MB). 저장 공간 상한(256 MiB)을 추가함. 콘텐츠 스트림 폭탄([B2])의 잔여 비용을 M-5에 명시함 |
| 4 | 조치 오류 | 모든 예외를 삼키고 무효 후보를 버려, 변조와 워터마크 없음이 구분되지 않음 | 예외 범위를 좁히고, 무효 후보는 남겨 `INVALID_SIGNATURE`를 돌려주도록 바꿈 |
| 5 | 누락 | 검증 쪽 키 검증이 없고, `verifyBase64`가 예외를 던짐 | L-1 위치와 조치 ④에 검증 쪽 코드를 추가함 |
| 6 | 누락 | 삽입 쪽(`KurbyPdf.java:21`)도 메모리 제한 없이 로드함 | M-5 위치와 조치 ①에 추가함 |
| 7 | 사실 오류 | M-6의 "전이 의존성 노출"은 현재 배포 방식(JAR 직접 참조)과 맞지 않음 | 현재는 Fat JAR 내장이 주 이유이고, 전이 노출은 저장소 배포 시의 위험으로 고침 |
| 8 | 표현 | 조치 코드에 import가 없어 그대로 붙이면 컴파일되지 않음 | `DocFingerprint` 전체 import를 포함함. `MemoryUsageSetting`은 실제 패치처럼 FQCN으로 맞춤 |
| 9 | 누락 | README:3, 73, 111의 불일치·과장 누락 | I-3에 추가함 |
| 10 | 과장 | "사용자 암호 없으면 미암호화"는 의도된 옵션이라 중간 등급 근거가 약함. 조치 ③의 호환성 영향이 빠짐 | L-3(낮음)으로 분리함. 통계를 중간 6·낮음 3·합계 14로 갱신함. 호환성 영향을 추가함 |
| 11 | 표현 | 7장이 비어 있음 | 이 절을 작성함 |
| 12 | 표현 | 1장 인용문 두 줄이 한 줄로 렌더링됨 | 두 줄 사이에 빈 인용 줄을 넣음 |

### 반영 후 재검증

보강한 조치 코드를 원본 사본에 다시 적용했다. 그 상태로 1차 PoC([0]~[7])와 2차 검토 PoC([R1], [R1b], [R2], [R3], [B2]), 원래 테스트 PDF를 모두 다시 실행했다. 결과는 5장 "조치 후" 열과 같다. 차단되지 않은 [R2], [3], [5]는 각각 H-2, M-3, M-1의 한계로 명시했다.
