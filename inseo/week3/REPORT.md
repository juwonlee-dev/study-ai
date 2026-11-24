# KurbyPdf 보안 취약점 분석 보고서

## 1. 요약 및 통계

- 분석 대상: https://github.com/juwonlee-dev/KurbyPdf
- 대상 커밋 SHA: `74d3aedeea9204694a8bc1e04e75edaa75add94d` (2025-09-22, `feat: Add README`, 기본 브랜치 HEAD)
- 분석일: 2026-11-23
- 분석 방식: 로컬 복제본에 대한 정적 코드 분석과 로컬 PoC 실행 (외부 서비스 대상 테스트 없음)

### 위험도별 확인 항목 (V 항목)

| 위험도 | 건수 | 항목 |
|--------|------|------|
| Critical | 0 | - |
| High | 2 | V-01, V-02 |
| Medium | 2 | V-03, V-04 |
| Low | 2 | V-05, V-06 |
| Info | 2 | V-07, V-08 |
| 합계 | 8 | |

### 별도 집계 (취약점으로 확정하지 않은 항목)

| 구분 | 건수 | 항목 |
|------|------|------|
| 잠재적 위험 (Low) | 1 | P-01 |
| 정보성 (Info) | 2 | P-02, P-03 |

위 두 표의 건수는 상세 항목 수와 일치한다 (4장의 확인된 항목 8건, 5장의 잠재적 위험 1건과 정보성 2건). V-07, V-08은 2차 검토에서 Low에서 Info로 조정했다 (6장).

## 2. 분석 대상과 범위

KurbyPdf는 PDFBox로 PDF에 숨김 워터마크(AES-GCM 암호화 + HMAC-SHA256 서명)를 삽입하고 검증하는 Java 8 라이브러리다. 독립 실행 서버가 아닌 라이브러리이므로 네트워크 공격 표면은 없고, 라이브러리를 사용하는 애플리케이션이 넘기는 입력(PDF 바이트, 키, 클레임, 암호)이 입력 경로다.

- 소스: `src/main/java/io/github/juwonlee/kurbypdf/` 하위 9개 파일, 테스트 1개, `build.gradle.kts`, `README.md`
- 주요 의존성: `pdfbox 2.0.30`, `jackson-databind 2.17.1` (`build.gradle.kts:27-28`)
- 분석 환경: Windows, JDK 17 (`--release 8`로 컴파일), 분석 디렉터리는 study-ai 저장소 밖(`C:\Users\USER\orca\analysis`)
- 분석 대상 저장소에는 변경, 푸시, PR을 하지 않았다.

### 분석 방법

1. 전체 소스 판독 후 입력 경로 추적 (PDF 바이트, 키, 클레임, 암호가 위험 지점에 도달하는지 확인)
2. 의존성 알려진 취약점 조회 (`gh api /advisories`, GitHub Advisory DB)
3. 의존성 jar를 Maven Central에서 받아 `javac`로 컴파일하고 PoC를 로컬에서 실행해 재현
4. 별도 에이전트에 의한 2차 검토 (6장)
5. 보고서 확정 전 최종 검증 (줄번호 재대조, V-01/P-01 추가 확인, 6.5절)

이 보고서의 모든 조치 방안은 실제 패치 적용이나 테스트를 거치지 않은 제안이다 (7장).

## 3. 위험도 분류 기준

이 프로젝트는 서버가 아니라 워터마크 라이브러리이므로, 프로젝트가 주장하는 보안 목적(위변조 검출, 유출 추적, 문서 보호)에 대한 영향을 기준으로 삼았다.

| 등급 | 기준 |
|------|------|
| Critical | 권한 없는 입력으로 원격 코드 실행, 키 노출 등 라이브러리 보안 목적이 전면 붕괴 |
| High | 실행으로 재현되었고, 별도 권한 없이 조작 가능한 입력으로 보안 목적(귀속 무결성, 가용성)이 심각하게 훼손 |
| Medium | 재현되었으나 공격자에게 일정한 전제(문서 수신, 설정 오용)가 필요하거나 영향이 제한적 |
| Low | 방어적 코딩 미흡, 영향이 작거나 오용 가능성 위주 |
| Info | 보안 영향 없이 개선이 바람직한 사항 |

항목별 검증 상태는 "실행 재현"(PoC로 결과 확인)과 "코드 판독"(소스로만 확인, 미실행)으로 구분해 적었다. 실행 재현은 다시 작성자 직접 재현과 2차 검토 에이전트 재현으로 나누어 7장에 정리했다.

### V 항목과 P 항목의 구분 기준

- V 항목(4장, "확인된 취약점"): 이 저장소의 코드나 설정에서 보안 목적(귀속 무결성, 가용성, 문서 보호)을 훼손하거나 방어가 부족한 동작을 PoC 실행 또는 소스 판독으로 직접 확인한 것. 등급은 Critical부터 Info까지 모두 가능하다.
- P 항목(5장, "잠재적 위험과 정보성"): 취약점으로 확정하지 못한 위험(P-01: 도달 가능성을 항목별로 검증하지 못한 의존성 권고) 또는 보안 영향 없이 빌드/문서를 개선하는 사항(P-02, P-03).
- V-07, V-08을 Info로 둔 이유: 두 항목은 코드에서 동작을 확인했으므로 V 항목이다. 그러나 V-07은 어느 경우에도 `_k1`이 리소스에서 직접 열거되므로(V-03) 위치 예측 가능성이 실질 영향을 더하지 않고, V-08은 테스트 코드에 한정되어 라이브러리 사용 경로에 영향이 없다. 따라서 "보안 영향 없이 개선이 바람직한 사항"(Info)으로 분류했다.

## 4. 상세 결과

### V-01. High: 워터마크 서명이 문서 내용에 결속되지 않아 다른 문서로 이식 가능

- 위치: `WatermarkPayload.java:21-62`, `PdfWatermarkInspector.java:96-139`, `PdfVerificationUtil.java:40-52`
- 원인: HMAC은 `v`, `claims`, `ts`, `nonce`만 서명한다 (`WatermarkPayload.java:27-38`). 문서 해시, 페이지 수 등 문서 식별 정보가 서명 범위에 없고, 검증기는 문서 내용을 확인하지 않는다. 또 `ts`와 `nonce`는 검증 시 유효기간이나 중복 여부를 검사하지 않는다.
- 발생 조건: 공격자가 피해자(예: alice)의 워터마크 PDF 사본을 확보해야 한다 (유출되었거나 공유받은 경우). 사본만 있으면 되고 키는 필요 없다. 워터마크 블롭은 암호문 그대로 복사하면 되기 때문이다.
- 영향: 공격자가 자신이 유출할 문서에 alice의 워터마크 블롭을 이식하면 검증기가 `valid=true`, `claims={uid=alice}`를 반환한다. 유출 추적 결과가 무고한 사용자를 지목하게 된다. 특히 alice가 받은 적 없는 전혀 다른 문서에 이식해도 alice가 지목된다.
- 검증 결과 (실행 재현, 작성자 직접 재현):
  1. 같은 원본 사본 간 이식: 같은 `sample.pdf`에서 만든 alice용 PDF의 `_k1` 스트림 원본 바이트를 bob용 PDF의 `_k1` 스트림에 덮어쓴 뒤 `PdfVerificationUtil.verifyDetailed`를 호출하자 `valid=true`, `claims={uid=alice}`가 나왔다.
  2. 다른 원본 문서로 이식 (최종 검증에서 추가 실행): `sample.pdf`(2페이지)와 무관한 빈 1페이지 PDF에 bob용 워터마크를 넣고, 그 `_k1` 스트림을 alice의 블롭으로 덮어쓰자 `valid=true`, `claims={uid=alice}`가 나왔다.
  3. 사본 간 식별 정보 확인 (최종 검증에서 추가 실행): 같은 원본에서 만든 alice용과 bob용 PDF는 암호 설정 여부와 무관하게 `/ID`와 페이지 수(2)가 동일했다.
- 위험도 재검토: High를 유지하되 경계 사례로 기록한다. 근거는 다음과 같다.
  - 3장 High 기준(실행 재현, 키 불필요, 귀속 무결성 훼손)은 충족한다. 이식은 결정적으로 동작하고(위 1, 2) 영향은 무고한 사용자 지목이다. V-03(제거)은 추적 불능에 그치지만 V-01은 오귀속이라 영향이 더 크다.
  - 반면 Medium 기준의 "일정한 전제"에 해당하는 요소도 있다. 피해자의 사본을 확보해야 한다. 같은 원본의 사본 사이에서는 기반 콘텐츠가 같으므로(위 3) 이식의 결과가 피해자의 사본을 그대로 유출하는 것과 외형상 구분되지 않는다. 이 경우의 추가 위험은 작다.
  - 이식이 고유한 추가 위험을 만드는 경우는 피해자가 받은 적 없는 다른 문서에 붙이는 것이다(위 2). 이 경우만 아래 조치 1(지문)로 막을 수 있다. 앞으로 애플리케이션이 서버 측 발급 장부(조치 2)로 이를 대조한다면 실질 등급은 Medium으로 낮아질 수 있다.
- 조치 방안 (모두 제안이며 적용 및 테스트하지 않음):
  1. 문서 지문을 서명 범위에 넣는다. `WatermarkPayload.buildPayload`가 지문을 받아 `body`에 포함해 서명하고, 검증 시 같은 방식으로 재계산해 비교한다. 지문은 삽입기가 덧붙이는 그리기 연산(`PdfForensicEmbedder.java:59, 80-86`, `AppendMode.APPEND`)의 영향을 받지 않아야 한다. 검증 시점의 문서는 이미 워터마크 연산이 포함되어 있어 "삽입 전 페이지 콘텐츠 해시"는 재계산할 수 없으므로, 삽입 연산을 제외하는 계산 규칙을 따로 정의해야 한다.
     - 이 방식의 효과는 서로 다른 원본 문서 사이의 이식 방지로 한정된다.
     - 같은 원본에서 발급된 수신자별 PDF 사이의 이식은 막지 못한다. 위 3처럼 `/ID`와 페이지 수가 모든 사본에서 같고 기반 콘텐츠도 같아서, 이 값들을 서명에 넣어도 사본마다 달라지지 않는다. 그리고 `/ID`와 페이지 수는 공격자가 임의로 맞출 수 있는 값이다. 원본 콘텐츠 해시를 쓰면 정당한 재저장과 편집도 검증에 실패한다.
  2. 서버 측 발급 장부로 검증한다. 발급 시 `fileId`, `nonce`, 수신자, 원본 문서 식별자(원본 해시 등)를 장부에 기록한다. 검증 시 검증기가 반환하는 `claims`와 `nonce`를 장부와 대조하여 (a) 장부에 없는 `nonce`, (b) 해당 `fileId`의 원본과 다른 문서에 붙은 워터마크, (c) 이미 폐기된 발급을 거부한다. 이 방식은 위 2(다른 원본으로 이식)를 막는 데 유효하다. 같은 원본 사본 간 이식은 장부로도 막을 수 없다. 장부에서 alice에게 발급된 `nonce`가 alice의 사본에서 나온 것인지, 이식된 것인지 구분할 정보가 없기 때문이다.
  3. 삽입 시점 `ts`로 유효기간을 두고, 호출자가 `nonce`/`fileId` 중복을 장부에서 검사할 수 있도록 검증 결과에 값을 노출한다 (이미 `getNonce()`가 있음).
  4. 지문을 AES-GCM의 AAD에도 넣어 암호문 단계에서 결속할 수 있다. 다만 이 변경은 기존에 발급된 PDF를 검증할 수 없게 만들므로, 페이로드 버전 필드 `v`로 분기해 구버전(`v=1`) 검증을 유지해야 한다.
- 기술적 한계: 파일 전체를 통제할 수 있는 공격자(수신자가 PDF를 마음대로 편집할 수 있음)에게는 파일 내부에 저장되는 어떤 서명이나 지문도 근본적인 방어가 되지 못한다. 공격자는 지문 입력값(`/ID`, 페이지 수, 콘텐츠)을 피해자 사본과 똑같이 맞춰 다시 쓰거나, 피해자 사본 자체를 편집해 유출할 수 있다. 서명이 보장하는 것은 "워터마크 내용이 키 소유자에 의해 발급되었다"는 점이지 "이 문서 파일이 그 수신자에게 발급되었다"는 점이 아니다. 따라서 조치 1은 오귀속의 비용을 높일 뿐이고, 근본 신뢰의 기준은 서버 측 장부(조치 2)에 있다.
- 변형 (코드 판독, 미실행): `verifyDetailed`는 첫 워터마크만 판정하므로(`PdfVerificationUtil.java:40-52`) 여러 문서의 페이지를 섞은 문서도 첫 워터마크만 유효하면 통과할 수 있다. 같은 계열의 문제로 위 지문 결속과 함께 다룬다.

### V-02. High: 워터마크 스트림을 크기 제한 없이 해제하여 메모리 고갈(OutOfMemoryError)

- 위치: `PdfWatermarkInspector.java:80-94` (특히 `83`, `87-89`), `PdfVerificationUtil.java:53-55`
- 원인: `streamToBytes`가 `createInputStream()`(83행)을 호출하면 PDFBox 2.0.30은 필터 디코드 결과 전체를 문서의 scratch 버퍼에 먼저 기록한 뒤 스트림을 돌려준다 (`COSStream.java:175`, `COSInputStream.java:86-87`). 이 scratch는 `load`에 넘긴 `MemoryUsageSetting`으로 만들어지며(`PDDocument.java:1228-1232`), KurbyPdf는 상한 없는 `setupMainMemoryOnly()`를 쓰는 `load(bin)`·`load(bin, password)`를 호출한다 (`PdfWatermarkInspector.java:46`, `PDDocument.java:1133, 1169`). 따라서 `_k1` 스트림에 FlateDecode 필터가 지정된 PDF를 만들면 작은 파일이 83행에서 이미 큰 메모리를 차지하고, 87-89행이 읽은 데이터를 `ByteArrayOutputStream`에 한 번 더 복사한다. 메모리 소비가 시작되는 곳(83행)과 `OutOfMemoryError`가 실제로 나는 곳은 구분해야 한다. 해제 크기와 힙의 비율에 따라 88행의 복사 중에 나는 경우를 스택트레이스로 확인했고, 해제 크기가 힙보다 훨씬 큰 경우의 발생 지점은 스택트레이스가 비어 확인하지 못했다. `verifyDetailed`는 `Exception`만 잡으므로 `OutOfMemoryError`는 호출자까지 전파된다.
- 발생 조건: 검증 대상 PDF를 공격자가 제공할 수 있는 경우 (유출 의심 문서를 받아 검증하는 서비스 등). 키 없이 가능하다. 복호화(`decryptAndVerify`)보다 앞단에서 발생한다.
- 영향: 검증 프로세스의 메모리 고갈과 서비스 중단(가용성).
- 검증 결과 (실행 재현): 약 453KB의 PDF(압축 스트림이 해제 시 400MB)를 `-Xmx128m`으로 `verifyDetailed`에 넣자 `OutOfMemoryError`가 발생해 프로세스가 비정상 종료되었다. 기본 힙 크기에서는 더 큰 해제 크기가 필요하며, 압축률상 PDF 크기는 수 MB 수준에 그친다 (미실행, 추정).
- 조치 방안:
  1. `createInputStream()`(83행)을 호출하기 전에 `COSStream.getLength()`와 `/Filter` 존재 여부를 확인하고, 필터가 있는 `_k1` 스트림은 거부한다 (삽입기는 필터 없이 저장함, `PdfForensicEmbedder.java:43-51`). 읽기 루프(87-89행)에 상한(예: 64KB)만 두는 방식은 기본 설정에서 디코드가 83행에서 이미 끝난 뒤라 고갈을 막지 못하며, 필터 없는 스트림의 복사 크기를 제한하는 보조 수단에 그친다 (PDFBox 단독 실행: 해제 100MB 스트림에서 읽기 전에 힙이 약 98MB 늘었다).
  2. `verifyDetailed`에서 `OutOfMemoryError`를 잡지 말고(복구 불가), 대신 입력 크기 상한(PDF 바이트 수, 페이지 수)을 호출 전에 적용한다. 다만 이 공격의 PDF는 약 453KB여서(위 검증 결과) 수 MB 단위의 PDF 크기 상한은 통과하므로, 이 조치만으로는 V-02를 막지 못하고 해제 크기를 제한하는 조치 1, 3과 함께 써야 한다.
  3. `PdfWatermarkInspector.java:46`의 `load(bin)`·`load(bin, password)`는 상한 없는 `setupMainMemoryOnly()`를 쓴다 (`PDDocument.java:1133, 1169`). 여기에 상한 있는 설정(`MemoryUsageSetting.setupMainMemoryOnly(상한)`)을 넘기면, 필터 디코드 결과 전체를 문서의 scratch에 먼저 쓰는 PDFBox 2.0.30의 동작(`COSStream.java:175`, `COSInputStream.java:86-87`) 때문에 상한을 넘는 순간 `IOException("Maximum allowed scratch file memory exceeded.")`이 나고(`ScratchFile.java:176`) `PdfVerificationUtil.java:53`에서 `Result.fail`이 된다. 이 상한은 모든 `OutOfMemoryError`를 막는 장치가 아니다. 상한은 `_k1` 하나가 아니라 입력 PDF 사본(`PDDocument.java:1231`)과 파싱된 스트림 전체에 걸리므로 허용할 PDF 크기보다 넉넉하게 잡아야 하고, 87-89행이 디코드 결과를 힙에 한 번 더 복사하므로 가용 힙보다는 충분히 작게 잡아야 한다. 상한 없이 저장 위치만 옮기는 설정(`setupTempFileOnly()` 등)은 이 복사 때문에 해결책이 아니다 (이 마지막 부분은 소스 판독이며 실행하지 않았다). 조치 1의 `/Filter` 검사와 함께 쓴다. 해제 100MB 스트림에 상한 50MB를 준 PDFBox 직접 호출은 `createInputStream()`에서 `IOException`으로 거부했고 상한 150MB는 통과했다 (Claude Code 에이전트 실행, JDK 17). 이는 PDFBox 단독 검증이며, KurbyPdf의 `load`에 상한을 넘기도록 실제로 패치한 뒤의 동작은 확인하지 않았다 (미실행).

### V-03. Medium: 워터마크를 키 없이 제거할 수 있고 삽입 위치가 식별 가능 (디코이 삽입 변형 포함)

- 위치: `PdfForensicEmbedder.java:16, 64`, `PdfWatermarkInspector.java:55-60`
- 원인: 워터마크는 Form XObject 딕셔너리의 고정 키 `_k1`에 평문 위치로 저장된다. 키 이름이 고정이고 페이지 리소스에서 쉽게 열거된다. 서명과 암호화는 변조를 탐지하지만 삭제는 탐지하지 못한다 (워터마크가 없으면 `WATERMARK_NOT_FOUND`일 뿐, 삽입 여부를 증명할 수 없다).
- 발생 조건: 문서 수신자(user 암호 보유)가 PDFBox 등으로 문서를 열어 `_k1` 항목을 삭제하고 보안을 제거한 뒤 저장한다. PDFBox는 권한 비트를 라이브러리 차원에서 강제하지 않는다.
- 영향: 수신자가 워터마크를 제거한 사본을 유출해도 검증기가 `WATERMARK_NOT_FOUND`만 반환해 추적이 불가능하다. README는 "위변조 방지"를 장점으로 내세우므로 사용자가 제거 불가능한 것으로 오해할 수 있다 (README의 주의사항은 "강력한 DRM 대체 수단은 아니다"라고만 안내).
- 검증 결과 (실행 재현): user 암호로 연 문서에서 모든 `_k1` 항목을 제거하고 `setAllSecurityToBeRemoved(true)`로 저장한 뒤 검증하자 `valid=false`, `reason=WATERMARK_NOT_FOUND`가 나왔다.
- 조치 방안:
  1. 워터마크 제거가 완전히 막힐 수 없음을 README에 명시한다 (현재 소스 기준 가장 직접적인 조치).
  2. 키 이름을 문서별 무작위 이름으로 바꾸거나, 워터마크를 콘텐츠 스트림(페이지 콘텐츠의 가시/비가시 마커)이나 XMP 메타데이터 등 여러 계층에 중복 삽입해 제거 비용을 높인다.
  3. 워터마크 삭제는 통제 불가이므로, 호출자가 배포 시점에 문서 ID와 수신자 매핑을 서버 측 DB에 별도 기록하도록 권고한다.
- 변형 (V-03에 포함): 디코이 `_k1` 삽입 (2차 검토 에이전트가 실행 재현, 작성자는 직접 재실행하지 않음). 페이지 리소스에 임의 바이트의 `_k1` 스트림을 가진 Form XObject를 추가하면 정상 워터마크가 남아 있어도 검증이 `valid=false`, `reason=EXCEPTION:AEADBadTagException`으로 실패한다. 원인은 `extractAll`이 모든 `_k1`을 복호화하다 첫 예외에서 전체를 중단하는 구조다 (`PdfWatermarkInspector.java:55-67`, `PdfVerificationUtil.java:53-54`). 수신자뿐 아니라 PDF를 가진 누구나 키 없이 수행할 수 있다.
  - 별도 항목이 아니라 V-03에 포함하고 Medium을 유지한 근거: 검증이 거짓으로 통과하는 우회가 아니라 실패하는 방향(fail-closed)이다. 같은 전제(PDF를 가진 자)에서 워터마크 제거로도 같은 결과(추적 불능)를 얻으므로 공격자에게 새로운 능력을 주지 않는다. 또한 사유가 `WATERMARK_NOT_FOUND`가 아닌 `EXCEPTION:AEADBadTagException`으로 구분되어 변조 흔적이 남는다 (두 PoC 결과가 서로 다른 `reason`을 반환한 것으로 확인). 키 없이 조작 가능하다는 점은 3장 High 기준에 해당하지만, 심각한 훼손(오귀속 등)이 없어 단독 상향 근거로 보지 않았다.
  - 조치 제안 (적용 및 테스트하지 않음). 복호화 실패 블롭을 무조건 무시하고 유효한 워터마크 하나로 성공 처리하면 새로운 우회가 생길 수 있다. 예를 들어 V-01의 이식 블롭이 정상 블롭과 함께 있을 때 어느 쪽이 먼저 오느냐로 귀속이 정해진다 (`PdfWatermarkInspector.java:31-34`의 `extractFirst`는 첫 레코드를 반환). 따라서 다음과 같이 제안한다.
    1. 유효한 모든 워터마크를 검사한다. 서로 다른 `claims`가 있으면 `CONFLICT`(충돌) 상태로 처리하고 성공으로 보지 않는다.
    2. `_k1` 블롭이 존재하지만 전부 복호화에 실패한 경우는 `WATERMARK_NOT_FOUND`와 구분되는 별도 사유(예: `WATERMARK_UNDECRYPTABLE`)로 반환한다. 키 오류와 전면 변조가 성공이나 미탐으로 오인되지 않게 한다.
    3. 복호화에 실패한 블롭의 건수를 검증 결과(`Result`)에 포함해 호출자가 변조 시도를 로깅할 수 있게 한다.
- 한계: 페이지 래스터화 후 재인쇄 같은 우회 방법은 이 라이브러리 설계로 막을 수 없고 범위 밖이다.

### V-04. Medium: 소유자 암호 검증 부재와 과도하게 열린 권한 설정

- 위치: `KurbyPdf.java:33-41`, `PdfProtector.java:8-17`
- 원인:
  1. 호출자가 지정한 `ownerPassword`가 `userPassword`와 같은지 검사하지 않는다 (`KurbyPdf.java:36-40`).
  2. 새 `AccessPermission()`은 모든 권한이 허용된 상태이며 (PDFBox 2.0.30 `AccessPermission.java:52, 70-72`, 기본값 `~3`), 코드는 기본값과 같은 `setCanPrint(true)`와 기본값을 바꾸는 `setCanExtractContent(false)`만 호출해 실질적으로 내용 추출만 막는다 (`PdfProtector.java:9-11`). 수정, 조립, 주석, 양식 입력, 접근성 추출이 모두 허용된다.
  3. `userPassword`가 없으면 암호화와 권한 설정 자체가 적용되지 않고 소유자 암호도 생성되지 않는다 (`KurbyPdf.java:35`). README는 "Owner 암호는 자동 랜덤 생성 가능"이라고만 적어 이 조건을 알리지 않는다.
- 영향: 소유자 암호와 사용자 암호를 같게 지정하면 열람자가 곧 소유자가 되어 모든 권한을 가진다. 그렇지 않더라도 수정, 조립이 허용되어 보호 효과가 낮다. PDF 권한 비트는 뷰어가 지키는 자율 규약이므로 그 자체로도 강한 통제가 아니다.
- 검증 결과 (실행 재현): `userPassword == ownerPassword == "same"`으로 만든 PDF를 user 암호로 열었을 때 `isOwnerPermission=true`였다. 일반 사용자 암호 PDF의 권한은 `print=true modify=true extract=false assemble=true annotMod=true fillForm=true`였다.
- 조치 방안:
  1. `KurbyPdf.watermark`에서 `ownerPassword.equals(userPassword)`이면 `IllegalArgumentException`을 던진다.
  2. `PdfProtector`에서 `setCanModify(false)`, `setCanAssembleDocument(false)`, `setCanModifyAnnotations(false)`, `setCanFillInForm(false)` 등 필요한 비트를 명시적으로 닫는다. 정책은 `WatermarkRequest`에서 선택 가능하게 둘 수 있다.
  3. README에 `userPassword`가 없을 때는 암호화가 적용되지 않는다는 점을 명시한다.

### V-05. Low: HMAC 키 길이/강도 검증 부재

- 위치: `KurbyPdf.java:24-25`, `WatermarkPayload.java:36-37`
- 원인: 키를 Base64 디코딩해 그대로 사용하며 길이를 검사하지 않는다. AES 키는 JCE가 길이를 검사해 거부하지만, HMAC 키는 비어 있지만 않으면 1바이트 키도 받아들인다.
- 영향: 호출자 실수로 약한 HMAC 키가 사용되면 서명 위조가 쉬워진다. 단, 키는 호출자 소유이며 공격자 제어 입력이 아니다.
- 검증 결과 (실행 재현): HMAC 키 1바이트는 정상 삽입되었고, AES 키 3바이트는 `InvalidKeyException`, 빈 HMAC 키는 `IllegalArgumentException: Empty key`가 났다.
- 조치 방안: HMAC 키는 32바이트 이상, AES 키는 16/24/32바이트인지 `KurbyPdf.watermark`와 검증 경로 진입부에서 검사하고, 오류 메시지에 키 값을 넣지 않는다. 암호화와 서명에 같은 키를 쓰지 않도록 README에 명시한다.

### V-06. Low: 입력 검증과 예외 처리가 일관되지 않음

- 위치: `KurbyPdf.java:24-25`, `PdfVerificationUtil.java:24-29`
- 원인: `WatermarkRequest`의 키 필드가 null이면 `Base64.getDecoder().decode(null)`에서 `NullPointerException`이 난다 (`KurbyPdf.java:13-16`의 검증은 `claims`만 확인). `verifyBase64`는 `verifyDetailed`의 try 바깥에서 디코딩하므로 잘못된 Base64 문자열이 `IllegalArgumentException`으로 전파되어, 다른 실패는 `Result.fail`로 반환하는 계약과 어긋난다.
- 영향: 호출자가 예외 처리를 누락하면 비정상 종료한다. 직접적인 기밀성 영향은 없다.
- 검증 결과 (실행 재현): null 키로 `watermark` 호출 시 `NullPointerException`, `verifyBase64(..., "!!!", "!!!")`는 `IllegalArgumentException`이 났다.
- 조치 방안: 진입부에서 키 null 검사 후 `IllegalArgumentException`을 명시적으로 던지고, `verifyBase64`의 디코딩을 `try`로 감싸 `Result.fail("INVALID_KEY")`를 반환한다.

### V-07. Info: 삽입 위치 난수 시드가 현재 시각

- 위치: `PdfForensicEmbedder.java:22-24`, `PdfForensicEmbedder.java:40`
- 원인: 기본 `embed`가 `System.currentTimeMillis()`를 시드로 `java.util.Random`을 만든다 (`SecureRandom` 아님).
- 영향: 삽입 시각을 알면 삽입 좌표를 재현할 수 있어 위치 무작위화가 은닉 수단으로서 의미가 약하다. 다만 V-03과 같이 위치와 무관하게 `_k1`은 리소스에서 직접 열거되므로 실질 영향은 작다.
- 검증 결과 (코드 판독, 미실행).
- 조치 방안: 위치 무작위화를 유지한다면 `SecureRandom`을 쓰되, 근본 대책은 V-03의 조치 방안이다.

### V-08. Info: 테스트 코드가 사용자/소유자 암호를 표준 출력에 기록

- 위치: `src/test/java/io/github/juwonlee/kurbypdf/KurbyPdfTest.java:80-81`
- 원인: 테스트가 `ownerPwd=`와 `userPwd=`를 콘솔에 출력하고, 결과 PDF를 `build/test-out`에 저장한다. 테스트용 고정 키(`0x11`/`0x22` 반복, `KurbyPdfTest.java:24-30`)는 의도된 테스트 값이다.
- 영향: 이 테스트 패턴이 복사되어 운영 로그에 암호가 남을 수 있다. 테스트 자체의 실제 영향은 작다.
- 검증 결과 (코드 판독, 미실행).
- 조치 방안: 암호 출력 줄을 제거하거나 마스킹한다.

## 5. 잠재적 위험과 정보성 항목 (취약점으로 확정하지 않음)

### P-01. Low (잠재적 위험): jackson-databind 2.17.1의 알려진 권고

- 근거: `gh api /advisories?ecosystem=maven&affects=com.fasterxml.jackson.core:jackson-databind@2.17.1`로 2026-11-23에 조회한 결과, 2.17.1에 영향을 주는 것으로 표시된 권고가 12건이며 수정 버전은 2.18.8 ~ 2.18.11 계열(및 2.21.x, 2.22.x)로 표시되었다. 이 조회는 GitHub Advisory DB 응답이다.
- 검증 범위 구분 (최종 검증):
  - 확인한 것: GHSA-wv8q-qhhj-9h54 하나. FasterXML/jackson-databind 저장소의 보안 권고 API에서 수정 버전 2.18.11과 취약 범위 `>= 2.0.0, <= 2.18.10`을 확인했다. 이 권고는 `@JsonTypeInfo(use = Id.NAME, defaultImpl = ...)` 사용 시 알 수 없는 타입 ID가 캐시에 쌓이는 문제로, KurbyPdf가 쓰지 않는 POJO 다형성 경로다. 또한 Maven Central 메타데이터에서 jackson-databind 2.18.11과 2.18.12가 실제 배포되어 있음을 확인했다.
  - 확인하지 못한 것: 나머지 11건의 권고 원문, 심각도, 수정 버전은 GitHub Advisory DB 응답 외의 근거로 확인하지 않았다. 따라서 "2.18.11 이상" 권고는 위 1건과 Maven Central 존재 확인에 근거한 것이며, 12건 전체에 대한 독립 검증이 아니다. 수정 버전 일부는 미검증 상태로 둔다.
- 도달 가능성: KurbyPdf는 `ObjectMapper`를 `Map`의 직렬화(`writeValueAsBytes`)와, AES-GCM으로 인증된 평문의 `readTree`에만 사용한다 (`WatermarkPayload.java:33,48`, `PdfWatermarkInspector.java:107`). 임의 POJO 바인딩, 다형성 타입 처리, `InetAddress`/`Path` 역직렬화가 없어 조회된 권고 대부분의 취약 경로에는 도달하지 않는 것으로 판단하나, 개별 권고별 도달성은 검증하지 않았다.
- 조치 방안: `build.gradle.kts:28`의 `jackson-databind`를 현재 지원되는 패치 버전(2.18.11 이상)으로 올린다. 2.18.11은 위에서 원문을 확인한 GHSA-wv8q-qhhj-9h54 1건의 수정 버전이며, 확인하지 못한 나머지 11건까지 해결한다는 의미가 아니다. 라이브러리 사용자에게 미치는 영향은 배포 방식에 따라 다르다 (아래는 `build.gradle.kts`와 `README.md`의 코드 판독이며, Gradle 빌드와 소비자 애플리케이션 실행으로 확인한 것은 아니다).
  - 일반 JAR(`build.gradle.kts:38-40`): 의존성 메타데이터(POM 또는 Gradle 모듈 메타데이터)가 제공되는 방식으로 소비하는 경우에 한해, 28행이 `api` 구성이므로 Jackson이 소비자의 컴파일 클래스패스로 전이되고 소비자가 Jackson 버전을 직접 올려 대응할 수 있다. 다만 이 저장소에는 `maven-publish` 같은 게시 설정이 없고 README는 `files("libs/kurbypdf.jar")`로 JAR를 복사해 쓰도록 안내한다 (`README.md:27`, `README.md:38`). 이 방식은 의존성 메타데이터가 전달되지 않으며, README는 어느 JAR를 가리키는지도 밝히지 않는다.
  - `all.jar`(`shadowJar`, `build.gradle.kts:42-48`, `63-64`): 런타임 의존성 전체를 JAR에 포함하고 Jackson 패키지를 `io.github.juwonlee.shadow.jackson`으로 재배치한다. Jackson 복사본이 JAR 안에 고정되므로 소비자가 애플리케이션의 Jackson 버전을 올려도 이 복사본은 갱신되지 않는다고 판단한다. 이 JAR를 직접 쓰는 사용자에게는 수정 버전으로 의존성을 올려 다시 빌드한 KurbyPdf JAR를 배포해야 한다.
  - 같은 이유로 PDFBox도 `build.gradle.kts:59-60`에서 재배치되어 `all.jar`에 포함되므로, 아래 PDFBox 항목의 버전 갱신도 `all.jar` 사용자에게는 재빌드가 필요하다.
- PDFBox: 같은 방식으로 조회한 `org.apache.pdfbox:pdfbox` 권고는 모두 2.0.24 이하에서 수정된 것이어서 2.0.30에는 해당 권고가 표시되지 않았다 (GitHub Advisory DB 응답 기준). 최종 검증에서 Maven Central 메타데이터로 2.0.30보다 새로운 2.0.x 릴리스(2.0.31 ~ 2.0.37)가 존재함을 확인했다. 따라서 2.0.30은 2.0.x 최신이 아니다. 이 후속 릴리스들이 보안 수정을 포함하는지는 확인하지 못했다. 이 DB에 없는 최근 권고 여부도 확인하지 못했다.

### P-02. Info: 빌드 재현성

- `gradlew`는 있으나 `gradle/wrapper/` 디렉터리가 저장소에 없어(`git ls-files gradle` 결과 0건) `./gradlew test`가 `ClassNotFoundException: org.gradle.wrapper.GradleWrapperMain`으로 실패했다 (실행 확인). 이 때문에 이번 분석에서는 Gradle 빌드와 테스트를 실행하지 못했고 `javac`로 직접 컴파일했다. 조치: `gradle-wrapper.jar`와 `gradle-wrapper.properties`를 커밋하고 가능하면 `distributionSha256Sum`을 지정한다.
- 의존성 잠금이나 검증 메타데이터(`gradle/verification-metadata.xml`)가 없다. 공급망 변조 방어를 원하면 도입을 검토한다.

### P-03. Info: 문서와 구현의 불일치

- `KurbyPdf.java:31` 주석은 "페이지당 2개"이지만 기본 `embed`는 3개를 삽입한다 (`PdfForensicEmbedder.java:20-23`).
- README의 `PdfVerification` 클래스는 실제로 `util.PdfVerificationUtil`이고, `KeyUtil`도 `util` 패키지에 있다. README 예제의 `result.getTimestamp()`도 실제 메서드는 `getTimestampMillis()`다. 보안 영향은 없으나 사용자가 잘못된 API를 가정할 수 있다.

## 6. 2차 검토

별도의 Claude Code 에이전트(general-purpose)에게 보고서와 소스만 주고 독립 검토를 맡겼다. 검토자는 줄번호를 소스와 대조하고 PoC를 재실행했으며 독자 PoC 1개를 추가했다. 아래는 검토 결과와 조치 내역이다.

### 6.1 재현 검증 결과

V-01 ~ V-06의 PoC는 모두 초안과 동일한 결과로 재현되었다. 인용한 파일:줄번호도 전부 맞았다. 통계 표의 건수와 상세 항목 수도 일치했다.

### 6.2 수정한 항목과 이유

| 항목 | 지적 | 조치 |
|------|------|------|
| V-01 조치 1 | 삽입기가 페이지 콘텐츠에 그리기 연산을 덧붙이므로(`PdfForensicEmbedder.java:59, 80-86`) "삽입 전 콘텐츠 해시"는 검증 시 재계산이 불가능하다 | 지문 후보를 문서 `/ID`, 페이지 수, 삽입 연산 제외 규칙으로 바꾸고 사유를 명시 (이 후보의 효과가 다른 원본으로의 이식 방지로 한정됨은 6.5절 최종 검증에서 확인되어 V-01에 반영) |
| V-01 조치 3 | AAD 변경은 기존 발급 PDF와 호환되지 않는다 | `v` 필드로 버전 분기 유지를 명시 |
| V-01 변형 | 첫 워터마크만 판정하므로 페이지를 섞은 문서가 통과할 수 있다 | 코드 판독 기반 변형으로 추가 (미실행 표기) |
| V-02 조치 3 | `MemoryUsageSetting`은 `streamToBytes`의 힙 사용을 막지 못한다 | 해결책이 아님을 명시하도록 정정 (소스 판독 기준, 미실행) |
| V-03 | 디코이 `_k1` 변형이 실제로 재현됨 (`valid=false`, `AEADBadTagException`), 키 없이 PDF 소지자 누구나 가능 | "미실행"을 "실행 재현"으로 갱신하고 영향 범위와 조치(실패 블롭 건너뛰기) 추가 |
| V-04 | "`setCanExtractContent(false)`만 호출"은 부정확 (`PdfProtector.java:10`에서 `setCanPrint(true)`도 호출) | 서술 정정, 등급 Medium 유지 |
| V-07, V-08 | 영향이 작고 3장 Info 기준("보안 영향 없이 개선이 바람직")에 가깝다 | Low에서 Info로 조정, 통계 표 반영 |
| P-01 | 권고 목록과 수정 버전이 독립 재검증되지 않음 | 미검증 표기를 명시 |
| P-03 | README 예제의 `getTimestamp()`가 실제로는 `getTimestampMillis()` | 항목에 추가 |
| 통계 문장 | "4장의 상세 항목 수와 일치"가 P 항목 위치(5장)와 어긋남 | 문장 수정 |

### 6.3 유지한 항목과 이유

- V-04는 owner==user 부분만 보면 Low에 가깝다는 의견이 있었으나, 권한 비트 과개방과 합쳐 3장의 Medium 기준(설정 오용 포함)에 부합해 Medium으로 유지했다.
- 검토자는 별도의 신규 취약점을 더 찾지 못했다고 보고했다. 이는 검토자가 읽은 범위의 결과이며 누락이 없다는 보증은 아니다.

### 6.4 2차 검토 시점의 한계

- 2차 검토 에이전트는 네트워크 접근이 금지되어 P-01의 권고 조회와 P-02의 빌드 실패 메시지를 재확인하지 못했다. 이 한계는 2차 검토 시점의 것이며, P-01에 대해서는 이후 6.5절의 최종 검증에서 일부(GHSA-wv8q-qhhj-9h54와 Maven Central 버전 존재)를 확인했다. 나머지 권고는 여전히 미검증이다.
- 검토자도 V-02의 기본 힙 환경 재현은 하지 못했다 (초안과 동일하게 `-Xmx128m`에서만 확인).

### 6.5 최종 검증 이력

2차 검토 반영 후 확정 전에 작성자가 다시 문서 전체와 소스를 대조했다. 아래는 발견한 문제와 반영 결과이다. 앞의 2차 검토 기록(6.1 ~ 6.4)은 그대로 보존했다.

| 번호 | 발견한 문제 | 근거 | 반영 결과 |
|------|-------------|------|-----------|
| 1 | V-01 지문 방안이 같은 원본에서 발급된 사본 간 이식을 막지 못함 | 같은 원본의 alice용과 bob용 PDF가 `/ID`와 페이지 수가 동일함을 직접 실행으로 확인 | 효과를 다른 원본 문서로의 이식 방지로 한정, 피해자 사본 확보 전제, 서버 측 발급 장부 방안, 파일 전체를 통제하는 공격자의 한계 명시. 다른 원본으로의 이식을 직접 실행으로 확인(`valid=true`, `claims={uid=alice}`)하여 추가. High 유지, 경계 사례로 근거 기록 |
| 2 | V-03의 "유효한 것이 하나라도 있으면 성공" 방안이 새 우회를 만들 수 있음 | `extractFirst`가 첫 레코드를 반환 (`PdfWatermarkInspector.java:31-34`). 이식 블롭과 정상 블롭이 공존하면 순서에 따라 귀속이 갈림 | 모든 유효 워터마크를 검사해 claims가 다르면 `CONFLICT`, 전부 복호화 실패는 `NOT_FOUND`와 구분, 실패 건수 노출로 수정. 디코이 변형이 V-03에 포함됨과 Medium 유지 근거 명시 |
| 3 | V 항목과 P 항목의 구분 기준, V-07/V-08 Info 사유 부재 | Info가 두 표에 모두 있는데 기준이 없었음 | 3장에 구분 기준과 사유 추가. 통계(8건/3건) 불변 |
| 4 | 6.4의 P-01 설명이 최신 검증 결과와 불일치 | 최종 검증에서 GHSA-wv8q-qhhj-9h54와 Maven Central을 확인 | 6.4 정정, P-01에 확인 범위와 미검증 범위 구분, PDFBox 2.0.31 ~ 2.0.37 존재 반영 |
| 5 | 조치 방안이 미적용 제안임이 명시되지 않음, 검증 주체 구분 부재 | 어떤 패치도 적용하거나 테스트하지 않았음 | 2장과 7장에 명시, 7장에 검증 상태 표 추가 |
| 6 | 최종 검증 이력 부재 | - | 이 절 추가 |

최종 검증에서 재대조한 파일:줄번호(약 26개 범위)는 모두 소스와 일치했고 수정할 곳은 없었다.

### 6.6 PR 리뷰 반영 이력

PR #54에 대한 외부 리뷰의 제안을 소스와 대조해 판단한 결과이다. 1, 2번은 juhwanHeo(APPROVED), 3 ~ 5번은 juwonlee-dev(APPROVED)의 인라인 코멘트에 대한 것이다. 표의 줄번호는 수정 전 기준이다. 앞의 6.1 ~ 6.5는 그대로 보존했으며, 6.2의 V-02 조치 3 행은 이력이므로 고치지 않았다.

| 번호 | 리뷰 제안 | 판단 근거 | 반영 결과 |
|------|-----------|-----------|-----------|
| 1 | P-01 조치 방안의 Jackson 전이 설명에 배포 방식 조건 추가 (`REPORT.md:181`) | `build.gradle.kts:42-48, 63-64`의 `shadowJar`가 런타임 의존성을 포함하고 Jackson을 재배치함. `README.md:27, 38`은 JAR 파일 복사를 안내하고 게시 설정은 저장소에 없음. 코드 판독이며 빌드와 소비자 앱 실행은 하지 않음 | 수용. P-01 조치 방안을 일반 JAR, `all.jar`로 나누어 서술하고, 같은 구조가 PDFBox(`build.gradle.kts:59-60`)에도 해당함을 추가. 이후 최종 검증에서 "전이"가 메타데이터 제공 방식에 한정됨을 명시하고, 2.18.11이 미검증 11건까지 해결한다는 의미가 아님을 추가 |
| 2 | 1장 첫 표 제목을 "위험도별 확인 항목"으로 변경 (`REPORT.md:10`) | 3장에서 V-07, V-08은 V 항목이지만 보안 영향이 없는 Info로 분류하는데, 기존 제목 "(확인된 취약점)"은 8건 모두 보안 영향이 확인된 것으로 읽힐 수 있음 | 수용. 제목을 "위험도별 확인 항목 (V 항목)"으로 변경. 등급과 건수(8건)는 불변 |
| 3 | V-02 발생 위치와 원인이 PDFBox 소스와 다름 (`REPORT.md:97-98`) | `COSStream.java:175`, `COSInputStream.java:86-87`: `createInputStream()`이 필터 디코드 결과 전체를 문서 scratch에 먼저 쓴 뒤 반환. `PDDocument.java:1133, 1169, 1228-1232`: 상한 없는 `setupMainMemoryOnly()`로 scratch 생성. Claude Code 에이전트가 PDFBox 단독으로 실행한 결과, 해제 100MB 스트림의 `createInputStream()` 반환 직후(읽기 전) 힙이 약 98MB 늘었음. OOM 발생 지점은 힙/해제 크기가 128MB/100MB, 512MB/400MB, 1100MB/400MB일 때 `PdfWatermarkInspector.java:88`로 확인했고, 해제 크기가 힙보다 훨씬 큰 경우는 스택트레이스가 비어 미확인 | 수용. 위치에 83행을 추가하고 원인을 "83행의 디코드 선행 소비 + 87-89행의 추가 복사"로 정정. 메모리 소비 시작 지점과 OOM 발생 지점을 구분해 서술 |
| 4 | V-02 조치 1의 읽기 루프 상한과 조치 3의 `MemoryUsageSetting` 판단 (`REPORT.md:103, 105`) | 2차 검토(6.2)는 `MemoryUsageSetting`이 "저장 위치만 바꾼다"고 정정했으나 소스 판독만 했고 실행하지 않았다. 상한 있는 `setupMainMemoryOnly(상한)`은 `ScratchFile.java:176`에서 `IOException`을 내며, 실행에서 해제 100MB 스트림에 상한 50MB는 `createInputStream()`에서 거부, 150MB는 통과했다. 따라서 2차 검토의 정정은 상한 있는 설정에 대해서는 틀린 방향이었고, 상한 없이 저장 위치만 옮기는 설정에는 맞다(이 부분은 소스 판독이며 미실행). 읽기 루프 상한은 디코드가 끝난 뒤라 기본 설정에서 효과가 없음 | 수용. 조치 1을 디코드 전 `/Filter`와 길이 검사로 바꾸고 읽기 루프 상한은 보조 수단으로 한정. 조치 3을 상한 있는 `MemoryUsageSetting` 전달안으로 재작성하되 모든 OOM을 막지는 못하며 상한 설정 기준(허용 PDF 크기와 가용 힙)을 명시. 조치 2에 PDF 크기 상한만으로는 약 453KB 공격 PDF를 막지 못한다는 한계 추가. KurbyPdf를 실제로 패치한 뒤의 동작은 미실행 |
| 5 | V-04 권한 설명이 두 호출이 모두 기본값과 같은 것처럼 읽힘 (`REPORT.md:131`) | `AccessPermission.java:52, 70-72`: 기본값 `~3`으로 모든 권한 허용. `PdfProtector.java:10`의 `setCanPrint(true)`는 기본값과 같고 `PdfProtector.java:11`의 `setCanExtractContent(false)`만 기본값을 바꿈 | 수용. 문장을 "기본값을 바꾸는 `setCanExtractContent(false)`"로 정정하고 `AccessPermission` 기본값 근거 추가. 등급(Medium) 불변 |

## 7. 분석의 한계와 미검증 사항

### 7.1 조치 방안의 상태

이 보고서의 모든 조치 방안(V-01 ~ V-08, P-01 ~ P-03)은 제안이다. 대상 소스에 패치를 적용하지 않았고, 제안한 변경(지문 서명, 장부 대조, 스트림 크기 상한, `CONFLICT` 처리 등)이 기존 발급 PDF와의 호환성이나 정상 검증에 미치는 영향을 테스트하지 않았다.

### 7.2 항목별 검증 상태

| 항목 | 검증 상태 | 재현 주체 |
|------|-----------|-----------|
| V-01 같은 원본 사본 간 이식 | 실행 재현 | 작성자 직접 재현, 2차 검토 에이전트도 같은 결과 재현 |
| V-01 다른 원본 문서로 이식, 사본 간 `/ID`와 페이지 수 동일 | 실행 재현 | 작성자 직접 재현 (최종 검증), 2차 검토 에이전트는 미재현 |
| V-01 페이지 혼합 변형 | 코드 판독 | 미실행 |
| V-02 메모리 고갈 (`-Xmx128m`) | 실행 재현 | 작성자 직접 재현, 2차 검토 에이전트도 같은 결과 재현 |
| V-02 기본 힙에서의 재현 가능성 | 추정 | 미실행 |
| V-02 디코드가 `createInputStream()`(83행)에서 선행됨, 상한 있는 `MemoryUsageSetting`의 `IOException` 거부 (PDFBox 단독 호출) | 소스 판독, 실행 재현 (JDK 17.0.17) | Claude Code 에이전트가 PR 리뷰 반영 시 실행. 작성자 직접 실행 아님 |
| V-02 OOM 발생 지점 (힙/해제 128MB/100MB, 512MB/400MB, 1100MB/400MB에서 `PdfWatermarkInspector.java:88`) | 실행 재현 (스택트레이스) | Claude Code 에이전트 실행. 해제 크기가 힙보다 훨씬 큰 경우(힙 128/256/300MB에 해제 400MB)는 스택트레이스가 비어 발생 지점 미확인 |
| V-02 조치 1, 3을 KurbyPdf에 실제 적용한 뒤의 동작, `setupTempFileOnly()` 등 상한 없는 설정의 동작 | 미실행 (후자는 소스 판독) | 대상 저장소를 수정하지 않았고 패치를 적용하지 않음 |
| V-03 워터마크 제거 | 실행 재현 | 작성자 직접 재현, 2차 검토 에이전트도 재현 |
| V-03 디코이 삽입 변형 | 실행 재현 | 2차 검토 에이전트만 재현. 작성자는 직접 재실행하지 않음 |
| V-04 owner==user, 권한 비트 | 실행 재현 | 작성자 직접 재현, 2차 검토 에이전트도 재현 |
| V-05 키 길이, V-06 null/Base64 | 실행 재현 | 작성자 직접 재현, 2차 검토 에이전트도 재현 |
| V-07, V-08 | 코드 판독 | 미실행 |
| P-01 권고 12건 | GHSA-wv8q-qhhj-9h54 1건과 Maven Central 버전 존재만 확인 | 작성자 (최종 검증). 나머지 11건은 미검증, 2차 검토 에이전트는 네트워크 불가로 미확인 |
| P-02 `./gradlew` 실패 | 실행 확인 | 작성자만. 2차 검토 에이전트는 `git ls-files gradle` 0건만 재확인 |
| 파일:줄번호 | 소스 직접 대조 | 작성자(최종 검증)와 2차 검토 에이전트가 각각 대조 |

위 표의 "추정"은 PoC나 소스로 확인하지 못한 판단을 뜻한다. 이 보고서에서 추정으로 남은 것은 V-02의 기본 힙 재현 가능성이다.

### 7.3 그 밖의 한계

- Gradle 빌드와 `src/test`의 JUnit 테스트(`KurbyPdfTest`)는 실행하지 못했다 (P-02: `gradle/wrapper/`가 저장소에 없어 `./gradlew`가 실패). PoC는 의존성 jar를 Maven Central에서 받아 직접 `javac`로 컴파일한 클래스로 실행했다. 테스트의 왕복 검증(워터마크 삽입 후 검증)과 같은 흐름은 PoC에서 확인했으나 JUnit 테스트 자체를 실행한 것은 아니다.
- 의존성 권고(P-01)는 GitHub Advisory DB 조회 결과이며 7.2에 적은 범위 밖의 권고 원문, 수정 버전, 도달성은 검증하지 않았다. PDFBox 2.0.31 ~ 2.0.37의 변경 내용도 확인하지 않았다.
- 다양한 PDF 뷰어(Acrobat 등)에서의 권한 비트 동작, 손상/악성 PDF에 대한 PDFBox 파서 자체의 취약점(퍼징)은 범위 밖이다.
- 암호화 구현(AES-GCM 12바이트 IV 무작위, 128비트 태그)은 표준 JCE 사용을 확인했으나 암호학적 증명이나 전문가 감사는 수행하지 않았다.
