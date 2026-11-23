# KurbyPdf 보안 취약점 보고서

- 과제: Issue #46 (3주차) 2번 "오픈소스 프로젝트의 취약점 찾아보기"
- 분석 대상: https://github.com/juwonlee-dev/KurbyPdf
- **분석 기준 커밋: `74d3aedeea9204694a8bc1e04e75edaa75add94d`** (2025-09-22, `feat: Add README`)
- 분석 일자: 2026-11-20
- 분석 방법: 저장소를 클론하지 않고 `gh api`로 위 커밋의 전체 파일(바이너리 `sample.pdf`와 Gradle 실행 스크립트 `gradlew`, `gradlew.bat` 제외 15개)을 읽어 정적 분석. 의존성은 GitHub Advisory Database(`gh api advisories`)와 Maven Central 메타데이터를 2026-11-20에 조회.
- 검토 절차: 초안 작성 후, 초안을 쓰지 않은 별도 에이전트가 원본 코드·PDFBox 2.0.30 소스·Jackson 2.17.1 소스·Advisory DB와 항목별로 대조했다. 바뀐 내용은 8장에 기록했다.
- 한계: **KurbyPdf 코드를 빌드·실행하지 않았다.** 모든 공격 시나리오는 소스 대조로 도출한 것이며 PoC로 재현하지 않았다. 직접 확인한 사실과 추정은 본문에서 구분해 적는다. 본문에서 "PDFBox 소스 확인", "Jackson 소스 확인"이라고 적은 것은 2차 검토에서 해당 태그의 소스를 읽어 확인한 것이다.

---

## 1. 통계 요약

이 보고서는 탐지 항목을 **"누가 어떤 피해를 입는가"**에 따라 세 유형으로 나눈다(정의는 2.1).

- **유형 A — 보안 기능 미달**: KurbyPdf가 약속한 보호(유출자 추적, 위변조 검출, PDF 암호 보호)가 제대로 작동하지 않는다.
- **유형 B — 실행 서버 공격**: KurbyPdf를 설치해 돌리는 서버가 KurbyPdf를 통해 공격받는다.
- **유형 C — 의존성 전이**: KurbyPdf가 함께 들여오는 다른 라이브러리 때문에, KurbyPdf를 가져다 쓰는 프로젝트가 위험해진다.

### 1.1 위험도별 탐지 건수

| 위험도 | 건수 | 항목 |
|---|---:|---|
| Critical | 0 | - |
| High | 2 | V-01, V-02 |
| Medium | 3 | V-03, V-04, V-05 |
| Low | 3 | V-06, V-07, V-08 |
| Info (개선 권고) | 5 | I-01, I-02, I-03, I-04, I-05 |
| **합계** | **13** | 취약점 8건 + 개선 권고 5건 |

### 1.2 유형 × 위험도 건수

| 유형 | Critical | High | Medium | Low | Info | 합계 |
|---|---:|---:|---:|---:|---:|---:|
| A. 보안 기능 미달 | 0 | 2 | 1 | 2 | 3 | 8 |
| B. 실행 서버 공격 | 0 | 0 | 1 | 0 | 1 | 2 |
| C. 의존성 전이 | 0 | 0 | 1 | 1 | 1 | 3 |
| **합계** | **0** | **2** | **3** | **3** | **5** | **13** |

High 2건은 모두 유형 A다. "설치하면 서버가 장악된다" 수준의 항목(Critical)은 없고, 서버가 직접 공격받는 유형 B의 취약점은 서비스 중단(DoS) 1건이다.

### 1.3 전체 항목 목록

| 유형 | ID | 위험도 | 제목 | 주 위치 |
|---|---|---|---|---|
| A | V-01 | High | 워터마크가 문서 내용에 바인딩되지 않음 (이식·내용 변조 미탐지) | `WatermarkPayload.java:27-38` |
| A | V-02 | High | 워터마크를 키 없이 식별·제거 가능 | `PdfForensicEmbedder.java:16-17, 43, 64` |
| A | V-04 | Medium | 검증이 첫 번째 워터마크만 신뢰하고 불일치·오류를 구분하지 않음 | `PdfWatermarkInspector.java:31-34, 62-66` |
| A | V-06 | Low | PDF 암호화가 선택 사항이고 권한 설정이 대부분 허용 상태 | `KurbyPdf.java:35`, `PdfProtector.java:9-11` |
| A | V-07 | Low | 키 길이·형식 검증 없음 | `KurbyPdf.java:24-25`, `WatermarkPayload.java:37, 55` |
| A | I-01 | Info | 삽입 위치 난수가 예측 가능 (`java.util.Random` + 시간 시드) | `PdfForensicEmbedder.java:23, 40` |
| A | I-02 | Info | 테스트 코드가 비밀번호를 표준 출력에 기록 | `KurbyPdfTest.java:80-81` |
| A | I-03 | Info | AES-GCM 운용 한계 (키 수명·AAD·키 식별자) | `WatermarkPayload.java:51-56` |
| B | V-03 | Medium | 검증 대상 PDF 처리 시 메모리 사용량 무제한 (DoS) | `PdfWatermarkInspector.java:46, 83` |
| B | I-05 | Info | 이미 암호화된 입력 PDF의 처리 방침이 없음 | `KurbyPdf.java:21, 35, 44` |
| C | V-05 | Medium | jackson-databind 2.17.1 / jackson-core 2.17.1의 알려진 취약점 | `build.gradle.kts:28` |
| C | V-08 | Low | Fat JAR 재배치와 system-scope 설치 안내로 취약 의존성이 고착됨 | `build.gradle.kts:59-64`, `README.md:27, 37-38` |
| C | I-04 | Info | PDFBox 2.0.30은 알려진 CVE는 없으나 구버전, Gradle wrapper 파일 누락 | `build.gradle.kts:27` |

항목 ID는 초안과 2차 검토 기록(8장)에서 쓴 번호를 그대로 유지했다. 그래서 유형별로 묶은 본문에서는 번호가 순서대로 나오지 않는다.

---

## 2. 분류 기준

### 2.1 유형 기준

| 유형 | 정의 | 피해를 입는 쪽 | 피해의 모습 |
|---|---|---|---|
| A. 보안 기능 미달 | KurbyPdf가 제공한다고 밝힌 보안 기능이 공격자에 의해 무력화되거나 잘못된 결과를 낸다 | 워터마크로 문서를 보호하려는 배포자 | 유출자를 찾지 못함, 엉뚱한 사람을 지목함, 기대한 암호 보호가 적용되지 않음 |
| B. 실행 서버 공격 | 공격자가 만든 입력을 KurbyPdf가 처리하는 과정에서 그 프로세스·서버가 피해를 입는다 | KurbyPdf를 설치해 실행하는 서버 | 서비스 중단, 처리 실패 |
| C. 의존성 전이 | KurbyPdf 자체 코드가 아니라 함께 배포되는 외부 라이브러리와 배포 방식에서 오는 위험 | KurbyPdf를 의존성으로 추가한 프로젝트 | 알려진 취약점이 있는 라이브러리가 딸려 들어오고 교체하기 어려움 |

워터마킹된 PDF를 받아 보는 최종 수령인의 기기에 영향을 주는 항목은 없다.

### 2.2 위험도 기준

CVSS 점수를 그대로 쓰지 않고, 이 라이브러리의 보안 목표(README.md:8-15의 "워터마크 삽입·추적", "무결성·위변조 여부 확인", "PDF 암호 보호")에 미치는 영향으로 판정했다.

| 위험도 | 기준 |
|---|---|
| Critical | 키·비밀번호 없이 원격 코드 실행, 키 유출, 임의 서명 위조가 가능 |
| High | 키 없이 라이브러리의 핵심 보안 목표(유출자 추적, 위변조 검출)를 무력화하거나 잘못된 결론을 유도 |
| Medium | 특정 조건(검증 서비스로 노출, 다른 약점과 결합 등)에서 가용성 침해 또는 보안 기능 약화. 알려진 취약점이 있는 의존성이 소비자에게 전이되는 경우 포함 |
| Low | 단독 악용이 어렵거나 영향이 제한적인 약점, 오용을 유발하는 API 설계 |
| Info | 현재 코드에서 악용 경로를 확인하지 못했지만 개선을 권고하는 사항 |

### 2.3 위협 모델 (가정)

- 라이브러리 사용자는 PDF를 배포하는 서버 측 애플리케이션이며, HMAC 키와 AES 키는 서버만 보유한다.
- **주 공격자는 정당한 수령인(유출자)이다.** 자신의 워터마크가 들어간 PDF와 그 사용자 비밀번호를 갖고 있다. README.md:106-108의 사용 사례(불법 유출 추적)가 근거다.
- 검증(`PdfVerificationUtil`)에 들어오는 PDF는 유출본, 즉 **신뢰할 수 없는 입력**이다.

---

## 3. 유형 A — 보안 기능이 약속한 보호를 제공하지 못함

KurbyPdf는 그 자체가 보안 도구다. 이 유형은 "도구를 썼는데 기대한 보호가 되지 않는" 문제를 모았다. 서버가 침해되는 것은 아니고, 피해는 **유출자를 찾지 못하거나, 엉뚱한 사람을 지목하거나, 걸었다고 생각한 암호 보호가 적용되지 않는** 형태로 나타난다. 공격자는 주로 워터마킹된 PDF를 정당하게 받은 수령인이며, V-01·V-02·V-04는 암호 키 없이 가능하다.

| ID | 위험도 | 한 줄 요약 |
|---|---|---|
| V-01 | High | 워터마크를 다른 문서에 옮겨 붙여도 검증이 통과한다. 본문을 고쳐도 탐지하지 못한다. |
| V-02 | High | 수령인이 일반 PDF 도구로 워터마크를 찾아 지울 수 있다. |
| V-04 | Medium | 워터마크가 여러 개면 첫 번째 것만 믿어서 결과를 조작하거나 검증을 방해할 수 있다. |
| V-06 | Low | 비밀번호를 주는 방식에 따라 암호 보호가 조용히 빠지고, 권한도 대부분 열려 있다. |
| V-07 | Low | 약한 키를 넣어도 그대로 받아들인다. |

### V-01 [High] 워터마크가 문서 내용에 바인딩되지 않음

**위치**
- `src/main/java/io/github/juwonlee/kurbypdf/WatermarkPayload.java:27-38` — HMAC 대상(`bodyJson`)이 `v`, `claims`, `ts`, `nonce` 네 필드뿐이다.
- `src/main/java/io/github/juwonlee/kurbypdf/KurbyPdf.java:28` — `buildPayload(claims, hmacKey, aesKey)` 호출에 `inputPdf`에서 파생한 값이 전달되지 않는다.
- `src/main/java/io/github/juwonlee/kurbypdf/PdfWatermarkInspector.java:122-136` — 검증도 같은 네 필드만 재계산한다.
- `README.md:15` — "삽입된 워터마크의 존재 여부, 무결성, **위변조 여부** 확인 가능"이라고 설명한다.

**원인 (확인한 사실)**
페이로드에는 그것이 삽입된 문서를 식별하는 값(해시, 문서 ID 등)이 없다. 따라서 암호문 덩어리(`/_k1` 스트림)는 어떤 PDF에 붙여도 그대로 유효하다.

**공격 시나리오**
1. *이식(누명 씌우기)*: 공격자 A가 동료 B에게서 B 명의로 워터마킹된 아무 PDF(문서 Y)와 그 비밀번호를 받는다. A는 자신이 유출할 문서 X에서 자기 워터마크 스트림을 B의 것으로 바꾼다(PDFBox로 `/_k1` 항목 교체). 유출된 X를 검증하면 `valid=true`, `claims.uid = B`가 나온다. 키는 필요 없다.
2. *내용 변조 미탐지*: 워터마킹된 PDF의 본문(금액, 조항 등)을 수정해도 `/_k1` 스트림이 남아 있으면 `PdfVerificationUtil.verify()`는 `true`를 돌려준다.

**영향**
- 추적 결과가 엉뚱한 사람을 가리킬 수 있어 워터마크의 증거 가치가 없어진다.
- README가 말하는 "위변조 여부 확인"은 **페이로드 자체**의 무결성일 뿐 문서의 무결성이 아니다. 사용자가 `verify() == true`를 "문서가 변조되지 않았다"로 해석하면 잘못된 판단을 하게 된다.

**조치 방안**
1. 페이로드에 원본 식별값을 넣는다. `KurbyPdf.java:28`에서 `SHA-256(inputPdf)`를 계산해 `buildPayload`에 넘기고, `WatermarkPayload.java:27-31`의 `body`에 `doc` 필드로 추가한다(HMAC 대상에 포함됨).
   ```java
   // KurbyPdf.java (import java.security.MessageDigest 추가)
   byte[] docHash = MessageDigest.getInstance("SHA-256").digest(inputPdf);
   byte[] payload = WatermarkPayload.buildPayload(claims, docHash, hmacKey, aesKey);
   ```
   검증 측도 함께 바꿔야 서명이 맞는다. `PdfWatermarkInspector.java:122-126`의 body 재구성에 `doc` 필드를 같은 순서로 넣는다. 페이로드 형식이 달라지므로 `v`를 2로 올리고(`WatermarkPayload.java:28`), 기존 v1 페이로드를 거부할지 "문서 바인딩 없음"으로 표시해 허용할지 정해 둔다.
2. `PdfVerificationUtil.verifyDetailed`에 "기대하는 원본 해시"를 받는 오버로드를 추가하고, 불일치 시 `Result.fail("DOCUMENT_MISMATCH")`를 반환한다. `DecodedWatermark`(`PdfWatermarkInspector.java:141-157`)와 `Result`에 `doc` 값을 노출해 호출자가 원본 저장소와 대조할 수 있게 한다.
3. 위 조치는 **다른 문서로의 이식**만 막는다. 같은 문서의 타인 사본을 입수한 경우와 본문 변조 검출은 막지 못한다. 본문 변조 검출이 필요하면 PDF 전자서명(PDFBox `PDSignature`)을 별도로 적용해야 한다.
4. `README.md:15`의 문구를 "워터마크 페이로드의 무결성 확인"으로 고친다.

---

### V-02 [High] 워터마크를 키 없이 식별·제거 가능

**위치**
- `PdfForensicEmbedder.java:16-17` — 고정된 딕셔너리 키 이름 `/_k1`, `/_k1v`.
- `PdfForensicEmbedder.java:43` — 페이로드 스트림은 문서당 **하나만** 생성된다.
- `PdfForensicEmbedder.java:62-64` — 페이지마다 만드는 Form XObject는 모두 그 하나의 스트림을 참조하고, BBox가 1×1로 동일하다.
- `PdfProtector.java:9-11` — 수정 관련 권한을 막지 않는다(V-06 참고).

**원인 (확인한 사실)**
워터마크는 Form XObject 딕셔너리의 비표준 키에 달린 스트림으로만 존재한다. 페이지 리소스를 순회하며 `/_k1` 키를 가진 XObject를 찾으면 되고, 이는 이 라이브러리의 `PdfWatermarkInspector.java:51-60`이 하는 일과 같다. "페이지당 3개 삽입"(`PdfForensicEmbedder.java:23`)은 참조가 3개일 뿐 데이터는 1개다.

**공격 시나리오**
유출자는 자기 사본을 사용자 비밀번호로 연 뒤, 모든 페이지의 XObject 중 `/_k1` 키를 가진 것을 지우거나 키만 제거하고 다시 저장한다. 라이브러리가 공개돼 있어 키 이름을 알 수 있고, 키 이름을 몰라도 원본에 없는 1×1 Form XObject는 쉽게 눈에 띈다. 이후 검증 결과는 `WATERMARK_NOT_FOUND`(`PdfVerificationUtil.java:43`)다.

- PDFBox 소스 확인(실행 미확인): 사용자 비밀번호로 연 문서는 권한 플래그와 무관하게 수정해 다시 저장할 수 있다. PDFBox 2.0.30의 `PDDocument.setAllSecurityToBeRemoved()`(`PDDocument.java:1702-1705`)는 권한을 검사하지 않고, 저장 경로(`COSWriter.java:1372-1380`)에도 `AccessPermission` 검사가 없다.
- 사용자 비밀번호는 선택 사항이라(`KurbyPdf.java:35`) 비밀번호 없이 배포된 사본에는 이 장벽도 없다.
- 인쇄 후 스캔, "PDF로 인쇄", 다른 포맷으로 변환해도 워터마크는 사라진다.

**영향**
유출자가 추적을 피할 수 있다. 라이브러리의 주 사용 사례(README.md:106-108)가 성립하지 않는다. README.md:111-112가 "강력한 DRM 대체 수단은 아니다"라고 밝히고 있지만, 제거 난이도가 코드 몇 줄 수준이라는 점은 드러나 있지 않다.

**조치 방안**
구조 기반의 비가시 워터마크는 원리상 완전한 제거 방지가 불가능하다. 다음은 제거 비용을 올리는 방안이다.
1. 식별 가능한 고정 표식을 없앤다. `PdfForensicEmbedder.java:16-17`의 고정 키 대신 문서마다 HMAC 키에서 파생한 이름을 쓰거나, 비표준 키 대신 정상 객체처럼 보이는 위치(콘텐츠 스트림 내 표시 콘텐츠, 폰트·이미지 스트림 등)에 분산한다.
2. `PdfForensicEmbedder.java:43`에서 스트림을 한 번만 만들지 말고 사본마다 독립 스트림(서로 다른 IV로 재암호화)을 만들어 참조 하나를 지워도 나머지가 남게 한다. 단, 모든 사본이 같은 키 이름으로 식별되는 한 한꺼번에 지워지므로 1번과 함께 적용해야 의미가 있다.
3. 구조 외 채널을 병행한다. 예: 글자 간격·좌표 미세 변조처럼 렌더링 결과에 남는 워터마크. 인쇄·변환에도 일부 살아남는다.
4. `PdfProtector.java:9-11`에서 수정 권한을 명시적으로 끈다(V-06). 강제력은 없지만 일반 뷰어에서의 편집은 막는다.
5. README에 "수령인이 구조 편집 도구로 제거할 수 있음"을 명시한다.

---

### V-04 [Medium] 검증이 첫 번째 워터마크만 신뢰하고 불일치·오류를 구분하지 않음

**위치**
- `PdfWatermarkInspector.java:31-34` — `extractFirst`는 `extractAll` 결과의 0번만 반환한다.
- `PdfVerificationUtil.java:40-52` — `verifyDetailed`는 `extractFirst`만 사용한다.
- `PdfWatermarkInspector.java:62-66` — 스트림 하나의 복호화가 실패하면 예외가 그대로 던져져 나머지 스트림은 검사하지 않는다.
- `PdfWatermarkInspector.java:138` — 서명이 틀려도 `claims`가 담긴 `DecodedWatermark`를 반환한다.

**원인 (확인한 사실)**
한 문서에 서로 다른 워터마크 스트림이 여러 개 있어도 이상으로 취급하지 않고, 순회 순서상 첫 번째 것의 결과가 곧 검증 결과가 된다.

**공격 시나리오**
1. *끼워 넣기*: V-01의 이식 공격에서 자기 워터마크를 지울 필요 없이, 타인의 유효한 `/_k1` 스트림을 가진 XObject를 첫 페이지 리소스의 앞쪽에 추가하면 된다. 검증은 타인의 클레임으로 `valid=true`를 반환한다. PDFBox 소스 확인: `PDResources.getXObjectNames()`는 딕셔너리의 `keySet()`을 그대로 반환하고(`PDResources.java:537-540, 597-605`), `COSDictionary`의 내부 맵(`SmallMap`, 항목이 많아지면 `LinkedHashMap` — `COSDictionary.java:50, 219-222`)은 두 경우 모두 삽입 순서로 순회한다(`SmallMap.java:277-290`). 즉 순서는 PDF를 만든 쪽이 정한다.
2. *검증 방해*: 임의 바이트로 된 `/_k1` 스트림을 앞쪽에 추가하면 뒤에 유효한 워터마크가 있어도 검증이 예외로 끝난다. 예외 종류는 스트림 길이에 따라 다르다. 같은 복호화 코드(`:97-105`)를 로컬 Java 17.0.12에서 실행해 확인한 결과, 12바이트 이하는 `:97-98`에서 `IllegalArgumentException`, 13~27바이트는 `c.doFinal`(`:105`)에서 `java.security.ProviderException`, 28바이트 이상은 `javax.crypto.AEADBadTagException`이었다. 세 경우 모두 `PdfVerificationUtil.java:53`에서 잡혀 `EXCEPTION:<클래스명>`이 된다. Java 8에서는 실행하지 않았다.
3. *재워터마킹*: 이미 워터마킹된 PDF를 다시 `KurbyPdf.watermark`에 넣으면 스트림이 둘이 되고, 위 순회 순서에 따라 이전 워터마크의 클레임이 검증 결과로 나온다. 1차 출력이 암호화되지 않은 경우에만 성립한다. `KurbyPdf.java:21`이 비밀번호 없이 로드하므로 사용자 비밀번호가 걸린 출력을 다시 넣으면 로드 단계에서 실패한다.
4. *API 오용*: `extractFirst`/`extractAll`은 public이다. 호출자가 `isSignatureValid()`를 확인하지 않으면 서명이 틀린 클레임을 신뢰하게 된다.

**영향**
잘못된 귀속(V-01 악화) 또는 유효한 워터마크가 남아 있는데도 검증 실패. 단, 공격자는 이미 V-02로 워터마크를 지울 수 있으므로 추가 영향은 "더 은밀하게 결과를 조작할 수 있다"는 정도다.

**조치 방안**
1. `PdfWatermarkInspector.java:62-66`에서 스트림별 복호화 실패를 예외로 던지지 말고 기록한 뒤 계속 순회한다. 잡을 예외에 `java.security.ProviderException`을 포함해야 한다. 이 예외는 `RuntimeException`이라 `GeneralSecurityException`만 잡으면 13~27바이트 스트림(시나리오 2)에서 빠져나간다.
2. `PdfVerificationUtil.java:40`을 `extractAll` 기반으로 바꾸고 다음 규칙을 적용한다.
   - 유효한 워터마크가 0개: `WATERMARK_NOT_FOUND` 또는 `INVALID_SIGNATURE`
   - 유효한 워터마크들의 클레임·nonce가 모두 같음: 성공
   - 서로 다른 유효 워터마크가 2개 이상이거나 복호화 실패 스트림이 섞여 있음: `Result.fail("MULTIPLE_WATERMARKS")` 등 별도 사유로 실패 처리하고 전체 목록을 노출

   이 규칙에서도 시나리오 2(검증 방해)는 사유 코드만 달라질 뿐 실패로 끝난다. 다만 유효한 워터마크의 클레임이 목록으로 함께 나오므로 조사자가 "조작 흔적이 있는 문서"로 판단할 근거가 남는다.
3. `KurbyPdf.java:31` 앞에서 입력 문서에 이미 `/_k1`이 있는지 검사해 거부하거나 기존 것을 제거한다.
4. `PdfWatermarkInspector.java:138`은 서명이 유효하지 않으면 클레임을 비워서 반환한다.

---

### V-06 [Low] PDF 암호화가 선택 사항이고 권한 설정이 대부분 허용 상태

**위치**
- `KurbyPdf.java:35` — `userPassword`가 null/빈 문자열이면 암호화 블록 전체를 건너뛴다. 이때 `ownerPassword`를 줬더라도 무시된다.
- `PdfProtector.java:9-11` — `new AccessPermission()` 뒤 `setCanPrint(true)`, `setCanExtractContent(false)`만 설정한다.
- `KurbyPdf.java:35`, `WatermarkRequest.java:10-11` — 비밀번호 강도 검증이 없다.

**원인**
- 확인한 사실: 소유자 비밀번호만 지정한 요청은 경고 없이 평문 PDF를 반환하고 `WatermarkResult.getOwnerPassword()`는 null이다.
- PDFBox 소스 확인: `AccessPermission()` 기본 생성자는 모든 권한을 허용한 상태로 시작한다(`AccessPermission.java:52, 70-72`). 따라서 수정·주석·페이지 조립·양식 입력 권한이 열려 있다.
- PDFBox 소스 확인: 키 길이 256 설정(`PdfProtector.java:14`)은 리비전 6(AES-256)을 쓴다(`StandardSecurityHandler.java:104-116`). 암호화 알고리즘 자체는 문제가 없고, 남는 약점은 비밀번호 강도와 권한 설정이다.
- 확인한 사실: 사용자 비밀번호와 소유자 비밀번호에 같은 값을 줘도 막지 않는다(`KurbyPdf.java:36-40`). 이 경우 수령인이 소유자 권한을 갖는다.

**공격 시나리오**
호출자가 "소유자 비밀번호만 걸어 편집을 막겠다"는 의도로 `userPassword=null, ownerPassword="..."`를 넘기면 아무 보호 없는 PDF가 배포된다. 암호화된 경우에도 일반 PDF 편집기에서 수정이 허용돼 V-02의 제거 작업이 쉬워진다.

**영향**
호출자가 기대한 보호가 적용되지 않는다. 권한 플래그 자체가 강제력이 없으므로 영향은 제한적이다.

**조치 방안**
1. `KurbyPdf.java:35`의 조건을 "userPassword 또는 ownerPassword 중 하나라도 있으면 보호 적용"으로 바꾼다. 소유자 비밀번호만 있을 때는 사용자 비밀번호를 빈 문자열로 둔다.
2. `PdfProtector.java:9-11`에서 필요한 권한만 켜는 방식으로 바꾼다.
   ```java
   ap.setCanModify(false);
   ap.setCanModifyAnnotations(false);
   ap.setCanAssembleDocument(false);
   ap.setCanFillInForm(false);
   ```
   `setCanExtractForAccessibility(false)`도 있지만 화면 낭독기 사용을 막을 수 있어 필요할 때만 켠다.
3. 사용자 비밀번호 최소 길이를 검사하거나, 최소한 README에 약한 비밀번호는 오프라인 대입 공격에 취약하다는 점을 적는다. 사용자 비밀번호와 소유자 비밀번호가 같으면 거부한다.

---

### V-07 [Low] 키 길이·형식 검증 없음

**위치**
- `KurbyPdf.java:24-25` — Base64 디코드만 하고 길이를 확인하지 않는다. `getHmacKeyBase64()`가 null이면 `NullPointerException`이다.
- `WatermarkPayload.java:37` — HMAC 키 길이 제한 없음. 1바이트 키도 허용되고 빈 키만 `IllegalArgumentException`으로 거부된다(2차 검토에서 Java 17로 실행 확인, 대상 런타임인 Java 8에서는 미확인).
- `WatermarkPayload.java:55` — AES 키 길이는 JCE가 16/24/32바이트만 받아 주므로 여기서만 간접 검증된다(같은 방법으로 확인).
- `PdfVerificationUtil.java:36` — null 여부만 검사한다.
- `PdfVerificationUtil.java:26-27` — `verifyBase64`는 try 블록 밖에서 디코드하므로, 잘못된 Base64가 들어오면 다른 검증 메서드와 달리 `Result`/`false`가 아니라 예외가 그대로 나온다.

**공격 시나리오**
직접적인 외부 공격 경로는 아니다. 호출자가 짧은 문자열(예: 비밀번호 같은 값)을 HMAC 키로 넘겨도 조용히 동작하므로, AES 키가 함께 유출된 상황에서 HMAC 키를 오프라인 전수 조사할 수 있게 된다. 두 키에 같은 값을 써도 막지 않는다.

**영향**
약한 키가 운영에 들어갈 수 있다. 검증 없이 던져지는 예외(`NullPointerException`, `IllegalArgumentException`, `InvalidKeyException`)로 원인 파악도 어렵다.

**조치 방안**
`KurbyPdf.java:24-25` 직후에 검사를 추가한다. `PdfVerificationUtil.java:36`에는 같은 조건을 넣되, 이 메서드는 예외 대신 `Result.fail`을 돌려주는 계약(`:33-38`)이므로 `Result.fail("WEAK_KEY")`로 반환한다. `verifyBase64`(`:26-27`)의 디코드는 try로 감싸 `false`를 반환한다.
```java
// KurbyPdf.java
if (hmacKey.length < 32) throw new IllegalArgumentException("hmacKey must be >= 32 bytes");
if (aesKey.length != 16 && aesKey.length != 32) throw new IllegalArgumentException("aesKey must be 16 or 32 bytes");
if (MessageDigest.isEqual(hmacKey, aesKey)) throw new IllegalArgumentException("hmacKey and aesKey must differ");
```
null·잘못된 Base64는 `IllegalArgumentException`으로 통일한다. `KeyUtil`에 32바이트 키 생성 헬퍼를 추가해 README 예제에서 쓰게 하는 것도 방법이다.

---

## 4. 유형 B — 라이브러리를 실행하는 서버가 공격받음

이 유형은 KurbyPdf를 설치한 서버가 **KurbyPdf를 통해** 피해를 입는 문제다. 검증 기능은 출처를 알 수 없는 유출본 PDF를 입력으로 받으므로, 공격자가 조작한 파일을 넣을 수 있다. 확인된 피해 범위는 서비스 중단(DoS)까지이며, 코드 실행이나 정보 탈취로 이어지는 경로는 찾지 못했다.

| ID | 위험도 | 한 줄 요약 |
|---|---|---|
| V-03 | Medium | 조작된 작은 PDF 하나로 검증 서버의 메모리를 고갈시킬 수 있다. |

### V-03 [Medium] 검증 대상 PDF 처리 시 메모리 사용량 무제한 (DoS)

**위치**
- `PdfWatermarkInspector.java:46`, `KurbyPdf.java:21` — `PDDocument.load(InputStream[, password])`를 메모리 설정 없이 호출한다.
- `PdfWatermarkInspector.java:83` — `s.createInputStream()`으로 `/_k1` 스트림을 디코드한다.
- `PdfWatermarkInspector.java:84-90` — 디코드 결과를 상한 없이 `ByteArrayOutputStream`에 한 번 더 복사한다.
- `PdfWatermarkInspector.java:48-67` — 서로 다른 `/_k1` 스트림의 개수에도 제한이 없다.
- `PdfVerificationUtil.java:53` — `catch (Exception e)`만 있어 `OutOfMemoryError`는 잡히지 않는다.
- `PdfVerificationUtil.java:33`은 null과 빈 배열만, `KurbyPdf.java:14`는 null만 검사한다. 입력 크기 상한은 없다.

**원인**
- 확인한 사실: 스트림을 읽는 시점(`:64`)은 복호화(`:65`)보다 앞이므로 키가 없어도 도달한다. 정상 페이로드는 클레임 JSON 크기(수백 바이트)인데 읽는 크기에는 제한이 없다.
- PDFBox 소스 확인: `PDDocument.load(InputStream)`은 `MemoryUsageSetting.setupMainMemoryOnly()`를 쓰고(`PDDocument.java:1131-1133, 1166-1169`), 이 설정은 상한이 없다(`MemoryUsageSetting.java:98-101`).
- PDFBox 소스 확인: `COSStream.createInputStream()`은 지연 디코드가 아니다. `COSInputStream.create()`(`COSInputStream.java:62-108`)가 반환 전에 필터 체인 전체를 디코드해 scratch 버퍼(위 설정에서는 무제한 메인 메모리)에 쓴다. 따라서 메모리 소진은 `PdfWatermarkInspector.java:83`에서 먼저 일어나고, `:87-89`의 읽기 루프는 그 뒤의 2차 복사다.

**공격 시나리오**
공격자가 작은 PDF(수 MB 이하)를 만든다. 첫 페이지 리소스에 `/_k1` 키를 가진 Form XObject를 두고, 그 스트림을 FlateDecode로 압축한 대량의 0 바이트로 채워 디코드 결과가 검증 서버의 힙 크기를 넘게 한다. 이 파일을 검증 기능(예: "유출 의심 파일 업로드" 엔드포인트)에 넣으면 디코드 도중 `OutOfMemoryError`가 발생한다. 이는 `Exception`이 아니므로 `verifyDetailed` 밖으로 전파된다. 같은 필터를 여러 번 겹쳐 압축비를 키우는 방법은 PDFBox가 거부한다(`COSInputStream.java:71-78`).

**영향**
검증 기능을 서비스로 노출한 애플리케이션의 가용성 침해. 같은 JVM의 다른 요청도 영향을 받는다. 워터마크 삽입 경로(`KurbyPdf.watermark`)도 입력 크기 검사 없이(`KurbyPdf.java:14`) 메모리 상한 없는 설정으로 로드한다(`:21`). 다만 위 압축 폭탄이 삽입 경로에서도 메모리 고갈을 일으키는지는 확인하지 못했다.

**조치 방안**
1. `PDDocument.load` 호출(`PdfWatermarkInspector.java:46`, `KurbyPdf.java:21`)에 상한이 있는 메모리 설정을 넘긴다. 이것이 주 방어다. `load(InputStream, String, MemoryUsageSetting)` 오버로드는 2.0.30에 있다(`PDDocument.java:1204`).
   ```java
   // import org.apache.pdfbox.io.MemoryUsageSetting;
   private static final long MAX_PDF_MEMORY = 256L * 1024 * 1024; // 호출자가 조정할 수 있게 한다
   ...
   doc = PDDocument.load(bin, password == null ? "" : password,
           MemoryUsageSetting.setupMainMemoryOnly(MAX_PDF_MEMORY));
   ```
   상한을 넘으면 `IOException`이 나고(`ScratchFile.java:176`), 이는 `PdfVerificationUtil.java:53`에서 잡혀 `Result.fail`이 된다. `setupMixed`를 쓸 경우 인자 1개짜리는 임시 파일 크기가 무제한이라(`MemoryUsageSetting.java:145-148`) 문제가 디스크로 옮겨갈 뿐이므로 `setupMixed(main, storage)` 2인자 형태를 쓴다.
2. 보조 방어로 `PdfWatermarkInspector.java:87-89`의 읽기 루프에 상한을 둔다. 이것만으로는 `:83`의 디코드를 막지 못한다.
   ```java
   private static final int MAX_PAYLOAD_LEN = 64 * 1024;
   ...
   while ((r = in.read(buf)) != -1) {
       if (bout.size() + r > MAX_PAYLOAD_LEN) throw new java.io.IOException("watermark payload too large");
       bout.write(buf, 0, r);
   }
   ```
   디코드 전에 스트림의 `/Length`(인코딩 길이)가 정상 페이로드 범위인지 먼저 검사하고, `PdfWatermarkInspector.java:48-67`에서 처리하는 서로 다른 `/_k1` 스트림 개수에도 상한을 둔다.
3. `PdfVerificationUtil.java:33`과 `KurbyPdf.java:14`에 입력 PDF 최대 크기 검사를 추가한다(상한은 호출자가 설정할 수 있게 한다).
4. 호출 애플리케이션 쪽에는 검증을 별도 프로세스/제한된 힙에서 돌리도록 README에 안내한다.

---

## 5. 유형 C — 함께 들어오는 의존성으로 위험이 전이됨

KurbyPdf는 PDFBox(PDF 처리)와 jackson(JSON 처리)을 가져다 쓰고, KurbyPdf를 설치하는 프로젝트에는 이 둘도 함께 들어간다. 이 유형은 KurbyPdf의 코드가 아니라 **딸려 들어오는 라이브러리의 알려진 취약점과, 그것을 교체하기 어렵게 만드는 배포 방식**을 다룬다. KurbyPdf 자체 코드 경로로는 해당 취약점에 도달하지 않으며(V-05 본문), 피해는 KurbyPdf를 의존성으로 추가한 프로젝트가 그 라이브러리의 다른 기능을 쓸 때 생긴다.

| ID | 위험도 | 한 줄 요약 |
|---|---|---|
| V-05 | Medium | jackson 2.17.1에 알려진 취약점 16건. 버전을 2.18.11 이상으로 올리면 해소된다. |
| V-08 | Low | 의존성을 JAR 안에 넣어 이름을 바꿔 배포하므로 사용하는 쪽에서 교체할 수 없다. |

PDFBox 2.0.30에는 해당 버전에 걸리는 알려진 취약점이 없었다(I-04).

### V-05 [Medium] jackson-databind 2.17.1 / jackson-core 2.17.1의 알려진 취약점

**위치**
- `build.gradle.kts:28` — `api("com.fasterxml.jackson.core:jackson-databind:2.17.1")`. jackson-core 2.17.1이 전이 의존성으로 따라온다.
- `build.gradle.kts:48, 64` — shadow JAR에 재배치되어 포함된다.

**확인한 사실 (GitHub Advisory DB, 2026-11-20 조회, 버전 2.17.1에 해당하는 권고)**

| 패키지 | CVE (GHSA) | 등급/CVSS | 요약 | 2.18.x 수정 버전 | KurbyPdf 코드에서의 도달 가능성 |
|---|---|---|---|---|---|
| databind | CVE-2026-54512 (GHSA-j3rv-43j4-c7qm) | High 8.1 | 제네릭 타입 파라미터를 통한 PolymorphicTypeValidator 우회 | 2.18.8 | 미해당: 다형성 타이핑 미사용 |
| databind | CVE-2026-54513 (GHSA-rmj7-2vxq-3g9f) | High 8.1 | BasicPolymorphicTypeValidator 배열 서브타입 허용목록 우회 | 2.18.8 | 미해당: 위와 같음 |
| databind | CVE-2026-91777 (GHSA-cxp5-3px4-pw24) | High 7.5 | forward-reference 완료 처리의 2차 시간 복잡도 | 2.18.11 | 미해당: `readTree` 경로는 객체 ID를 다루지 않음 (Jackson 소스 확인) |
| databind | CVE-2026-91776 (GHSA-wv8q-qhhj-9h54) | High 7.5 | 알 수 없는 raw type ID를 모두 보관 | 2.18.11 | 미해당: 다형성 타이핑 미사용 |
| databind | CVE-2026-68497 (GHSA-q4xh-88c3-wmh7) | High 7.5 | Duration/XMLGregorianCalendar 숫자 파싱 DoS | 2.18.10 | 미해당: 해당 타입 역직렬화 없음 |
| databind | CVE-2026-59889 (GHSA-5gvw-p9qm-jgwh) | Medium 6.5 | `@JsonUnwrapped` 컨테이너에서 `@JsonView` 우회 | 2.18.9 | 미해당: 어노테이션 미사용 |
| databind | CVE-2026-59888 (GHSA-3pjw-73gf-8qr5) | Medium 6.5 | Record + PropertyNamingStrategy에서 `@JsonIgnore` 우회 | 2.18.8 | 미해당 |
| databind | CVE-2026-83557 (GHSA-gx83-3vf8-gh7j) | Medium 5.6 | DefaultBaseTypeLimitingValidator 거부목록 누락 | 2.18.10 | 미해당 |
| databind | CVE-2026-54514 (GHSA-hgj6-7826-r7m5) | Medium 5.3 | InetSocketAddress 역직렬화 시 DNS 조회(SSRF) | 2.18.8 | 미해당 |
| databind | CVE-2026-77310 (GHSA-vvgp-rfg2-7rr6) | Medium 5.3 | CVE-2026-54514의 불완전 수정 (InetAddress) | 2.18.9 | 미해당 |
| databind | CVE-2026-54515 (GHSA-5jmj-h7xm-6q6v) | Medium 5.3 | 대소문자 무시 역직렬화에서 `@JsonIgnoreProperties` 우회 | 2.18.9 | 미해당 |
| databind | CVE-2026-19032 (GHSA-wjgm-6hv5-3cvf) | Medium 5.3 | Path 역직렬화의 스킴 허용목록 누락 | 2.18.10 | 미해당 |
| core | CVE-2026-89407 (GHSA-p6pp-m3f8-5c89) | High 7.5 | `NumberInput.looksLikeValidNumber()` 정규식 ReDoS | 2.18.11 | 미해당: 호출부가 문자열→실수 역직렬화기뿐이고 `readTree`·`asInt`·`asLong` 경로에 없음 (Jackson 소스 확인) |
| core | CVE-2026-89425 (GHSA-7hhh-6rmp-j9qf) | High 7.5 | `UTF8DataInputJsonParser` 오류 토큰 길이 무제한 | 2.18.11 | 미해당: `readTree(byte[])`는 이 파서를 만들지 않음 (Jackson 소스 확인) |
| core | CVE-2026-68494 (GHSA-r7wm-3cxj-wff9) | High (CVSS v4 8.7) | 비동기 파서 maxNumberLength 우회 | 2.18.8 | 미해당: 비동기 파서 미사용 (Jackson 소스 확인) |
| core | CVE-2026-18401 (GHSA-72hv-8253-57qq) | Medium (CVSS v4 6.9) | 비동기 파서 숫자 길이 제한 우회 | 2.18.6 | 미해당: 위와 같음 |

CVSS는 Advisory DB에 실린 값이다. 표기가 없는 것은 v3, v3 점수가 없는 두 건만 v4 점수를 적었다.

**도달 가능성 판단 근거**
- 확인한 사실: KurbyPdf의 Jackson 사용은 `OM.readTree(byte[])`(`PdfWatermarkInspector.java:107`)와 `OM.writeValueAsBytes(Map)`(`PdfWatermarkInspector.java:128`, `WatermarkPayload.java:33, 48`)뿐이다. POJO 역직렬화, 다형성 타이핑, Jackson 어노테이션은 쓰지 않는다.
- 확인한 사실: `readTree`에 들어가는 바이트는 AES-GCM 복호화(`PdfWatermarkInspector.java:103-105`)를 통과한 평문이다. **AES 키가 없는 공격자는 Jackson 파서에 임의 입력을 넣을 수 없다.**
- Jackson 2.17.1 소스 확인:
  - `readTree(byte[])`(`ObjectMapper.java:3292-3295`)는 `JsonFactory.createParser(byte[])`를 거쳐 `UTF8StreamJsonParser` 또는 `ReaderBasedJsonParser`를 만든다(`JsonFactory.java:1304-1313, 1957-1961`). `UTF8DataInputJsonParser`(`:1984`)와 비동기 파서(`:1433, 1460`)는 다른 팩토리 메서드에서만 생성된다.
  - `NumberInput.looksLikeValidNumber()`의 호출부는 `NumberDeserializers.java:656, 759, 867, 1050`, `StdDeserializer.java:1068, 1086`뿐이다. `TextNode.asInt/asLong`은 `NumberInput.parseAsInt/parseAsLong`을 쓴다(`TextNode.java:126-133`).
  - `readTree` 경로에서 forward-reference 처리(`checkUnresolvedObjectId`) 호출은 주석 처리돼 있다(`ObjectMapper.java:4950`).

**공격 시나리오**
- KurbyPdf 내부: 위 16건 중 KurbyPdf 자체 코드 경로로 도달하는 것은 없다. AES 키가 유출돼 공격자가 임의 JSON을 넣을 수 있게 되더라도 마찬가지다.
- 소비자 애플리케이션: `api` 구성이라 jackson-databind 2.17.1이 소비자의 컴파일·런타임 클래스패스로 전이된다. 소비자가 더 높은 버전을 선언하지 않았고 다형성 역직렬화, 문자열→실수 역직렬화 등을 쓰고 있다면 위 CVE에 노출된다.

**영향**
KurbyPdf 자체 경로에서는 악용 경로가 없다. 위험은 High 등급 CVE가 다수 있는 버전을 `api`로 소비자에게 전이시키고 fat JAR에 고정해 배포한다는 데 있다(V-08). 2.2 기준의 "알려진 취약점이 있는 의존성이 소비자에게 전이되는 경우"에 해당해 Medium으로 판정했다. 자체 도달 경로가 없다는 점만 보면 Low로 볼 여지도 있다(8.3 참고).

**조치 방안**
1. `build.gradle.kts:28`을 위 표의 모든 권고가 수정된 **2.18.11 이상**으로 올린다. 2026-11-20 기준 Maven Central의 2.18 계열 최신은 2.18.12, 2.x 최신은 2.23.0이다. Jackson 2.x는 Java 8을 지원하므로 `build.gradle.kts:19`의 `release 8` 설정과 충돌하지 않는다(추정: 2.18 릴리스 노트로 확인하지는 않았다).
   ```kotlin
   api("com.fasterxml.jackson.core:jackson-databind:2.18.12")
   ```
2. 공개 API(`KurbyPdf`, `PdfVerificationUtil` 등)의 시그니처에 Jackson 타입이 없으므로 `api` 대신 `implementation`으로 바꿔 소비자에게 전이되지 않게 한다.
3. Dependabot 또는 OWASP Dependency-Check를 CI에 붙여 재발을 막는다.

---

### V-08 [Low] Fat JAR 재배치와 system-scope 설치 안내로 취약 의존성이 고착됨

**위치**
- `build.gradle.kts:59-64` — PDFBox, FontBox, Jackson을 `io.github.juwonlee.shadow.*`로 재배치한다. XmpBox 재배치 설정(`:61`)도 있지만 pdfbox 2.0.30의 의존성이 아니라 적용 대상이 없다. commons-logging은 재배치하지 않아(`:67` 주석 처리) 원래 패키지명으로 들어간다.
- `README.md:27` — `implementation files("libs/kurbypdf.jar")`
- `README.md:37-38` — Maven `system` scope + `systemPath`

**원인 (확인한 사실)**
README가 안내하는 설치 방식은 JAR 파일을 직접 복사해 넣는 것이다. 이 경우 의존성 메타데이터가 전달되지 않으므로 소비자는 fat JAR(`-all`)을 써야 하고, 그 안의 PDFBox/Jackson은 재배치된 패키지명으로 고정돼 소비자가 버전을 올릴 수 없다.

**공격 시나리오**
V-05처럼 번들된 의존성에 취약점이 공개돼도, 소비자 프로젝트의 의존성 관리(BOM, 버전 강제)나 패키지명 기반 스캐너는 재배치된 사본을 놓칠 수 있다(추정: 스캐너별 동작은 확인하지 않았다). 소비자는 KurbyPdf가 새 JAR를 배포할 때까지 취약 버전을 계속 쓰게 된다.

**영향**
의존성 취약점의 노출 기간이 길어진다. 직접 악용 가능한 결함은 아니다.

**조치 방안**
1. Maven Central 등 저장소에 일반(thin) JAR와 POM을 배포하고, README의 설치 안내를 좌표 기반(`implementation("io.github.juwonlee:kurbypdf:1.0.0")`)으로 바꾼다.
2. fat JAR를 유지한다면 릴리스마다 번들된 의존성 버전을 README나 릴리스 노트에 명시하고, 의존성 보안 패치 시 즉시 재배포한다.

---

## 6. 개선 권고 (Info)

현재 코드에서 악용 경로를 확인하지 못했지만 개선을 권고하는 사항이다. 제목에 해당 유형을 표시했다.

### I-01 [Info · 유형 A] 삽입 위치 난수가 예측 가능
- 위치: `PdfForensicEmbedder.java:23`(시드 `System.currentTimeMillis()`), `:40`(`new Random(seed)`), `:32`("보통 더 안전"이라는 주석).
- 내용: `java.util.Random`은 암호학적 난수가 아니고 시드도 추측 가능하다. 다만 XObject는 페이지 리소스에서 그대로 열거되므로(V-02) 위치를 숨겨서 얻는 보안 효과가 애초에 없다. 악용 경로가 없어 Info로 분류했다.
- 권고: 위치 무작위화가 보안 수단이라는 주석을 고치고, 난수가 필요하면 `SecureRandom`을 쓴다.

### I-02 [Info · 유형 A] 테스트 코드가 비밀번호를 표준 출력에 기록
- 위치: `KurbyPdfTest.java:80-81`(`ownerPwd`, `userPwd` 출력), `:69`("필요시 별도 로깅" 주석), `:24-30`(고정 테스트 키).
- 내용: 테스트 전용 값이라 직접적인 위험은 없다(`:23` 주석에 테스트용임이 명시됨). 다만 이 테스트가 사실상 사용 예제 역할을 하므로, 소유자 비밀번호를 로그에 남기는 패턴이 운영 코드로 복사될 수 있다.
- 권고: 출력문을 제거하거나 마스킹하고, 주석을 "소유자 비밀번호는 로그에 남기지 말고 안전한 저장소에 보관"으로 바꾼다.

### I-03 [Info · 유형 A] AES-GCM 운용 한계
- 위치: `WatermarkPayload.java:51-56`, `PdfWatermarkInspector.java:103-104`.
- 내용: IV는 `SecureRandom` 12바이트로 호출마다 새로 만들므로 구현 자체는 올바르다(확인). 남는 한계는 다음과 같다.
  - 무작위 IV 방식은 한 키로 암호화할 수 있는 횟수에 한도가 있다(NIST SP 800-38D 기준 2^32회). 대량 배포 환경에서 키를 교체하지 않으면 한도에 가까워진다.
  - AAD를 쓰지 않아 버전·문서 식별자가 암호문에 묶이지 않는다(V-01과 연관).
  - 암호문 밖에 키 식별자가 없어 키 교체 후에는 구 키를 순서대로 시도해야 한다. `/_k1v`(`PdfForensicEmbedder.java:44`)는 포맷 버전일 뿐이다.
- 권고: 페이로드 앞에 키 ID 1~2바이트를 두고 AAD로 포함한다. 키 교체 주기를 README에 안내한다.

### I-05 [Info · 유형 B] 이미 암호화된 입력 PDF의 처리 방침이 없음
- 위치: `KurbyPdf.java:21`(비밀번호 없이 로드), `:35`(사용자 비밀번호가 있을 때만 `protect`), `:44`(`doc.save`).
- 내용: 2차 검토에서 추가된 항목이다. 소유자 비밀번호만 걸린 PDF는 `:21`에서 열리지만, 요청에 `userPassword`가 없으면 `protect()`가 호출되지 않은 채 `:44`에서 저장하게 되고 PDFBox가 `IllegalStateException`을 던진다(PDFBox 소스 확인: `COSWriter.java:1388-1392`). 사용자 비밀번호가 걸린 입력은 `:21`에서 실패한다. 가용성·사용성 문제이고 보안 영향은 작아 Info로 분류했다.
- 권고: `:21` 직후 `doc.isEncrypted()`를 검사해 명시적인 예외로 거부하거나, 입력 비밀번호를 받아 처리하는 방침을 정해 README에 적는다.

### I-04 [Info · 유형 C] PDFBox 2.0.30은 알려진 CVE는 없으나 구버전, Gradle wrapper 파일 누락
- 위치: `build.gradle.kts:27`, 저장소 트리.
- 확인한 사실:
  - GitHub Advisory DB에서 `org.apache.pdfbox:pdfbox@2.0.30`, `org.apache.pdfbox:fontbox@2.0.30`, `commons-logging:commons-logging@1.2`(PDFBox 2.0.30 parent POM이 지정하는 버전)에 해당하는 권고는 0건이다(2026-11-20 조회). pdfbox 아티팩트의 기존 권고 8건(CVE-2016-2175, CVE-2018-8036, CVE-2018-11797, CVE-2019-0228, CVE-2021-27807, CVE-2021-27906, CVE-2021-31811, CVE-2021-31812)은 모두 2.0.24 이하 버전에서 수정됐다.
  - Maven Central 기준 2.0 계열 최신은 2.0.37, 전체 최신은 3.0.8이다.
  - PDFBox의 BouncyCastle 의존성은 `optional`이라 전이되지 않는다(2.0.30 POM 확인).
  - 커밋 트리에 `gradlew`, `gradlew.bat`은 있지만 `gradle/wrapper/gradle-wrapper.jar`와 `gradle-wrapper.properties`가 없다. `.gitignore:3`은 jar를 추적 대상으로 예외 처리해 두었는데 실제로는 커밋되지 않았다.
- 내용: 신뢰할 수 없는 PDF를 파싱하는 라이브러리이므로 파서의 견고성 수정이 누적된 최신 패치 버전을 쓰는 편이 안전하다. wrapper 설정이 없으면 빌드에 쓰이는 Gradle 버전과 배포본 체크섬이 고정되지 않는다.
- 권고: `build.gradle.kts:27`을 2.0.37로 올린다(3.x는 `PDDocument.load` 등 API가 바뀌어 코드 수정이 필요하다 — 추정). wrapper 파일을 커밋하고 `distributionSha256Sum`을 지정한다.

---

## 7. 취약점으로 분류하지 않은 확인 사항

분석 중 검토했으나 문제가 없다고 판단한 항목이다.

| 항목 | 근거 |
|---|---|
| HMAC 비교의 타이밍 공격 | `PdfWatermarkInspector.java:136`이 `MessageDigest.isEqual`을 사용한다. |
| IV·nonce·소유자 비밀번호 난수원 | `WatermarkPayload.java:15`, `KeyUtil.java:6` 모두 `SecureRandom`이다. |
| 자동 생성 소유자 비밀번호 강도 | `KeyUtil.java:13-39`: 87종 문자 32자리. 충분하다. |
| JSON 정규화 불일치를 이용한 서명 우회 | 검증 측이 재구성한 값(`PdfWatermarkInspector.java:110-126`)을 그대로 결과로 반환하므로 서명된 내용과 반환 내용이 어긋나지 않는다. 조작하려면 AES 키가 필요하다. |
| Jackson 역직렬화 가젯(RCE) | `readTree`로 `JsonNode`만 만들고 다형성 타이핑을 켜지 않는다(`PdfWatermarkInspector.java:23, 107`). |

---

## 8. 2차 검토 기록

### 8.1 절차

- 검토자: 초안을 쓰지 않은 별도 에이전트. 보고서 파일은 읽기만 하고 수정하지 않았으며, 수정은 검토 결과를 받아 초안 작성자가 반영했다.
- 대조 대상:
  - KurbyPdf 커밋 `74d3aed`의 15개 파일 전부 (`gh api`, 클론 없음)
  - PDFBox 태그 `2.0.30` 소스, Jackson `jackson-core-2.17.1` / `jackson-databind-2.17.1` 태그 소스
  - GitHub Advisory DB 재조회, Maven Central 메타데이터
  - JCE 키 길이 동작은 로컬 Java 17에서 실행
- 검토 항목: 인용 줄 번호, 원인 서술, 시나리오 성립 여부, 위험도, 조치 방안의 적용 가능성, 추정 표시 사실의 확정·반박, 누락 취약점, 통계표 검산.

### 8.2 항목별 판정과 변경 내용

| 항목 | 판정 | 초안에서 바뀐 내용 |
|---|---|---|
| V-01 | 확인 | 조치 방안 보완: 검증 측 body 재구성(`PdfWatermarkInspector.java:122-126`)에도 `doc` 필드 추가, `v`를 2로 올리고 v1 처리 방침 결정, `DecodedWatermark`에 `doc` 노출, 스니펫에 import 안내 추가. |
| V-02 | 확인 | "권한과 무관하게 재저장 가능"을 추정에서 PDFBox 소스 확인으로 변경(근거 줄 번호 추가, 실행 미확인 명시). 비밀번호 없이 배포된 사본에는 장벽이 없다는 점 추가. 조치 2는 조치 1과 함께여야 의미가 있다고 명시. |
| V-03 | **수정 필요** | (1) 원인 지점 정정: 메모리 소진은 읽기 루프(`:87-89`)가 아니라 `createInputStream()`(`:83`)에서 일어난다. PDFBox가 호출 시점에 스트림 전체를 디코드하기 때문이다. (2) 조치 방안 재작성: 초안의 1번(읽기 루프 상한)만으로는 막지 못하므로 보조 방어로 내리고, 상한 있는 `MemoryUsageSetting`을 주 방어로 올림. 초안이 제안한 1인자 `setupMixed`는 임시 파일이 무제한이라 2인자 형태로 정정. (3) 시나리오의 "수 KB PDF로 수 GB" 수치는 단일 FlateDecode 압축비로 불가능해 "수 MB 이하의 작은 PDF로 힙 크기를 넘는 디코드 결과"로 정정. (4) `KurbyPdf.java:14`는 null만 검사한다는 점 정정. (5) `/_k1` 스트림 개수 무제한 추가. (6) `PDDocument.load` 기본 메모리 설정을 추정에서 확인으로 변경. 주 위치를 `:46, 83`으로 변경. |
| V-04 | 확인 | 순회 순서를 추정에서 확인으로 변경. 초안은 내부 맵을 `LinkedHashMap`으로 가정했으나 실제는 `SmallMap`이며, 결론(삽입 순서)은 같다. 시나리오 2에 13바이트 미만일 때의 예외 종류 추가. 시나리오 3에 "1차 출력이 암호화되지 않은 경우에만 성립" 조건 추가. 조치 2의 한계(검증 방해는 여전히 실패로 끝남) 명시. |
| V-05 | 확인 | 표 16행의 CVE/GHSA/등급/CVSS/수정 버전이 재조회 결과와 전부 일치, 누락 없음. 도달 가능성 "미확인" 1건(CVE-2026-89407)과 "미해당(추정)" 4건을 Jackson 소스로 미해당 확정하고 근거 추가. 이에 따라 "AES 키 유출 시 파서 취약점을 시도할 수 있다"는 시나리오 문장을 "자체 경로로 도달하는 것은 없다"로 정정. CVSS v3 점수가 없던 2건에 v4 점수 추가. 2.18.11, 2.18.12에 해당하는 권고가 0건임을 재조회로 확인. |
| V-06 | 확인 | `AccessPermission()` 기본값을 추정에서 확인으로 변경. 암호화 리비전(6, AES-256) 사실 추가. 사용자·소유자 비밀번호 동일 허용 문제 추가. 스니펫에서 `setCanExtractForAccessibility(false)`를 접근성 부작용 때문에 선택 사항으로 분리. |
| V-07 | 확인 | 1바이트 HMAC 키 허용을 추정에서 실행 확인(Java 17)으로 변경. `verifyBase64`의 예외 누출 추가. `PdfVerificationUtil`에서는 예외 대신 `Result.fail`로 반환하도록 조치 방안 정정. |
| V-08 | 확인 | XmpBox 재배치 설정은 적용 대상이 없고 commons-logging은 재배치되지 않는다는 점으로 서술 정정. |
| I-01 ~ I-03 | 확인 | 변경 없음. |
| I-04 | 확인 | "2.0.24 미만에서 수정"을 "2.0.24 이하 버전에서 수정"으로 정정(CVE-2021-31811, 31812의 수정 버전이 2.0.24). |
| I-05 | 신규 | 검토자가 제안한 누락 항목을 Info로 추가. |
| 7장 표 | 확인 | 5행 모두 변경 없음. |
| 머리말 | 수정 | `gradlew*`를 바이너리라고 쓴 표현 정정. 검토 절차 문단 추가. |
| 1장 통계 | 수정 | I-05 추가로 Info 4→5, 합계 12→13. 분류표에서 I-03(AES-GCM 운용)을 "의존성·빌드"에서 "암호·키" 분류로 옮김(초안의 오분류). |

### 8.3 검토 의견 중 반영하지 않았거나 판단이 필요한 것

- **V-05의 위험도**: 검토자는 자체 경로 도달이 0건으로 확정됐으므로 Low 강등도 타당하다고 보았다. 2.2 기준에 "소비자 전이" 조항이 있어 Medium을 유지했다. Low로 본다면 1.1 표는 Medium 2건, Low 4건이 된다.
- **주석·문서와 코드 불일치**: `KurbyPdf.java:31` 주석("페이지당 2개")과 실제 기본값 3(`PdfForensicEmbedder.java:23`)의 차이, README(`:66, 69, 92`)가 존재하지 않는 `PdfVerification` 클래스를 안내하는 점을 검토자가 지적했다. 보안 결함이 아니어서 항목으로 싣지 않았다.

### 8.4 끝까지 확인하지 못한 것

- 모든 공격 시나리오의 실행 재현(빌드·PoC 없음).
- 사용자 비밀번호로 연 문서의 재저장 가능 여부(V-02): 소스 대조만 했다.
- JCE 키 길이 동작의 Java 8 런타임 확인(V-07): Java 17에서만 실행했다.
- Jackson 2.18.x의 Java 8 지원 여부(V-05 조치 방안).
- PDFBox 3.x의 API 변경 범위(I-04).
- 재배치된 fat JAR에 대한 스캐너별 탐지 동작(V-08).
- Advisory DB 외 출처(NVD, OSV, Apache 보안 공지)와의 교차 대조.

### 8.5 2차 검토 이후의 구성 변경

2차 검토를 반영한 뒤, 읽기 쉽도록 보고서 구성을 바꿨다. 이 변경은 별도 에이전트의 재검증을 다시 거치지 않았다.

- 탐지 항목을 피해 대상에 따라 유형 A(보안 기능 미달), B(실행 서버 공격), C(의존성 전이)로 나누고 2.1에 기준을 정의했다.
- 본문을 유형별 장(3~5장)으로 재배치하고 각 장 앞에 유형 설명과 요약표를 붙였다. 1.2의 분류표를 유형 × 위험도 표로 바꿨다.
- 이에 따라 장 번호가 바뀌었다(개선 권고 4→6장, 미분류 확인 사항 5→7장, 2차 검토 기록 6→8장). 8.2 표의 "분류표에서 I-03을 옮김"은 변경 전 1.2 표에 대한 기록이다.
- 각 항목의 ID, 위험도, 위치, 시나리오, 영향, 조치 방안 내용은 바꾸지 않았다.

### 8.6 PR 제출 후 자체 재검토에서 고친 내용 (2026-11-23)

다른 팀원의 보고서를 리뷰한 뒤 이 보고서를 다시 읽고, 틀렸거나 근거 없이 쓴 문장 두 곳을 고쳤다. 이 수정은 별도 에이전트의 재검증을 거치지 않았다.

| 항목 | 고치기 전 | 고친 내용 | 근거 |
|---|---|---|---|
| V-04 시나리오 2 | "13바이트 이상이면 `AEADBadTagException`" | 13~27바이트는 `ProviderException`, 28바이트 이상은 `AEADBadTagException`으로 정정. 조치 방안 1에 `ProviderException`을 잡아야 한다는 점 추가 | 같은 복호화 코드를 로컬 Java 17.0.12에서 길이별(12, 13, 20, 27, 28, 64바이트)로 실행. 8.2 표의 V-04 행에 적힌 "13바이트 미만일 때의 예외 종류 추가"는 2차 검토 지적을 실행 확인 없이 옮긴 것이었다 |
| V-03 영향 | 삽입 경로도 "같은 문제가 생긴다" | 삽입 경로에 입력 크기 검사와 메모리 상한이 없다는 사실만 남기고, 압축 폭탄이 이 경로에서 재현되는지는 확인하지 못했다고 명시 | `KurbyPdf.java:14, 21`. 삽입 경로에서의 재현은 소스로도 실행으로도 확인한 적이 없었다 |
