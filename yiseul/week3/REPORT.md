# KurbyPdf 보안 취약점 보고서

- 대상: https://github.com/juwonlee-dev/KurbyPdf (커밋 `74d3aed feat: Add README`, 기준일 2026-11-24)
- 범위: `src/main`, `src/test`, `build.gradle.kts`, README (Java 소스 9개, 약 630줄)
- 방법: 소스 전수 정적 분석 + OSV(api.osv.dev) 의존성 조회 + 커밋 이력 시크릿 검색. 작업 지침은 `yiseul/CLAUDE.md`를 사용했다.
- **한계: 아래 모든 항목은 코드 읽기 기반이며 실제로 실행해 재현하지 못했다.** 재현용 PoC 실행은 실행 환경의 권한 거부로 수행하지 못했다. 각 항목의 "검증 상태"에 이를 표기했고, PoC 설계는 7장에 남겼다.

## 1. 요약 통계

| 위험도 | 건수 | 항목 |
|---|---|---|
| Critical | 0 | - |
| High | 0 | - |
| Medium | 4 | M-1, M-2, M-3, M-4 |
| Low | 6 | L-1 ~ L-6 |
| Info | 4 | I-1 ~ I-4 |
| 합계 | 14 | |

위험도 기준: Critical = 인증 없이 원격 코드 실행 또는 핵심 비밀 노출 / High = 핵심 보안 목적 직접 무력화 또는 외부 입력만으로 서비스 중단 / Medium = 특정 조건에서 보안 목적 훼손 / Low = 방어 심화·견고성 / Info = 참고.

핵심 판단: 이 라이브러리는 서버에서 임의 입력을 받는 코드 경로가 거의 없고(입력은 PDF 바이트와 호출자가 준 키), 암호 프리미티브 사용(AES-GCM, HMAC-SHA256, SecureRandom, 상수시간 비교)은 올바르다. 문제는 암호 구현이 아니라 **워터마크가 문서에 결합되지 않는 설계, 검증 시 자원 제한 부재, 보호 옵션이 조용히 꺼지는 동작**이다.

## 2. 취약점 상세

### M-1. 워터마크가 문서 내용에 결합되지 않아 다른 PDF로 이식 가능 (Medium)
- 위치: `WatermarkPayload.java:28-46`, `PdfWatermarkInspector.java:107-136`
- 근거: HMAC 서명 대상은 `v, claims, ts, nonce`뿐이며 PDF 내용 해시나 문서 ID가 없다. 키를 모르는 사람은 위조할 수 없지만, 유효한 `_k1` 페이로드 바이트를 그대로 복사해 다른 PDF에 `PdfForensicEmbedder.embed`(public)로 넣으면 검증이 통과한다.
- 영향: 유출 추적 시 "이 문서는 사용자 A에게 배포된 것"이라는 결론을 다른 문서에 대해서도 만들 수 있다. 책임 추적의 증거 가치가 떨어진다. 공격자는 자기 사본 하나(사용자 비밀번호 보유)만 있으면 된다.
- 조치: 페이지 콘텐츠(또는 원본 PDF 해시) 다이제스트를 claims와 함께 HMAC 대상에 포함하고, 검증 시 다시 계산해 비교한다. 최소한 `fileId` 클레임을 필수화하고 검증 API가 기대 `fileId`를 인자로 받아 대조하게 한다. `ts`로 유효 기간을 선택적으로 검사한다.
- 검증 상태: 코드 경로 확인함, 미재현.

### M-2. 검증 경로에 입력 크기·압축 해제 제한이 없음 (자원 고갈, Medium)
- 위치: `PdfWatermarkInspector.java:46`(`PDDocument.load`, 메모리 설정 없음), `:83-92`(`createInputStream` 후 무제한 `ByteArrayOutputStream`), `KurbyPdf.java:21`, `PdfVerificationUtil.java:53`(`catch (Exception)`)
- 근거: 검증 대상은 유출된 외부 PDF다. `_k1` 스트림에 `FlateDecode`를 걸면 `createInputStream()`이 해제된 바이트를 모두 읽어 메모리에 올린다. 수 KB의 PDF가 수 GB로 풀릴 수 있다. `OutOfMemoryError`는 `Exception`이 아니므로 `verifyDetailed`의 `catch (Exception)`에 잡히지 않고 호출자까지 전파된다. 페이지 수·객체 수 제한도 없다.
- 영향: 검증 기능을 외부에 노출한 서비스에서 작은 파일로 JVM을 OOM으로 만들 수 있다(서비스 거부).
- 조치: `PDDocument.load(bytes, password, null, null, MemoryUsageSetting.setupMixed(...))`로 임시파일 모드와 상한을 지정한다. `streamToBytes`에서 읽는 총량을 상한(예: 페이로드는 정상 크기가 수백 바이트이므로 4KB)으로 제한하고 초과하면 즉시 실패시킨다. 입력 PDF 최대 크기와 페이지 수 상한을 둔다.
- 검증 상태: 코드 경로 확인함, 미재현. PDFBox가 필터를 해제하는 동작은 문서 기준이다.

### M-3. 사용자 비밀번호가 비어 있으면 암호화가 조용히 생략됨 (Medium)
- 위치: `KurbyPdf.java:35-41`
- 근거: `userPassword`가 null 또는 빈 문자열이면 `PdfProtector`를 호출하지 않는다. 이때 호출자가 `ownerPassword`를 줘도 무시되고 `WatermarkResult.ownerPassword`는 null이다. 경고나 예외가 없다.
- 영향: 비밀번호 변수가 빈 값으로 들어오는 설정 실수(환경변수 누락 등)가 보호되지 않은 PDF 배포로 이어진다. README는 "PDF 암호 보호"를 기능으로 소개하고 있어 오해하기 쉽다.
- 조치: 암호화가 의도된 요청인지 구분하는 명시적 플래그를 두거나, `userPassword`가 빈 문자열("")이면 예외를 던진다(null만 "보호 안 함"으로 허용). 반환값에 `encrypted` 여부를 담아 호출자가 확인할 수 있게 한다. 비밀번호 최소 길이 검증도 추가한다.
- 검증 상태: 코드 경로 확인함, 미재현.

### M-4. 암호화 권한이 인쇄·복사 방지 외에는 모두 허용이고, 보호 모델이 워터마크 제거를 막지 못함 (Medium)
- 위치: `PdfProtector.java:9-16`
- 근거: `AccessPermission` 기본값에서 `setCanExtractContent(false)`만 바꾼다. 수정, 페이지 조립, 주석, 양식 입력은 허용 상태다. PDF 권한 비트는 표준 뷰어의 자율 준수에 의존하며, 사용자 비밀번호로 문서를 연 사람은 PDFBox 등으로 복호화 후 리소스를 수정해 `_k1`을 삭제하고 다시 저장할 수 있다(문서 구조상 가능한 동작이며 미재현).
- 영향: 추적 대상 사용자가 직접 워터마크를 제거한 사본을 만들 수 있다. 라이브러리가 "위변조 방지"를 장점으로 소개(README)하지만 실제로는 위변조 **검출**만 가능하고, 제거는 검출되지 않는다(검증 시 "워터마크 없음"이 될 뿐 누구의 사본인지 알 수 없다).
- 조치: 최소 권한 원칙으로 `setCanModify(false)`, `setCanAssembleDocument(false)`, `setCanModifyAnnotations(false)`, `setCanFillInForm(false)`를 명시한다. README에 "워터마크 제거는 막지 못하며, 제거 사실을 검출하려면 눈에 보이는 워터마크나 서버 측 배포 기록을 병행해야 한다"를 명시한다. 가능하면 `_k1` 외에 XMP 메타데이터나 콘텐츠 스트림 내 위치 등 서로 다른 위치에 중복 삽입한다.
- 검증 상태: 권한 설정 코드 확인함, 제거 시나리오 미재현.

### L-1. 숨김 위치가 고정 키(`_k1`)·고정 구조라 식별과 제거가 쉬움 (Low)
- 위치: `PdfForensicEmbedder.java:16-17`, `:35-88`
- 근거: 모든 문서에 같은 키 이름 `_k1`과 BBox 1x1 폼, 0x0 클리핑을 쓴다. 모든 사본이 같은 `payloadStream`을 공유해 한 곳만 지워도 복제본 의미가 없다. README가 강한 DRM이 아니라고 밝히고 있어 Low로 둔다.
- 조치: 키 이름을 키에서 파생해 문서마다 다르게 하거나, 페이지마다 별도 스트림에 별도 IV로 암호화한 복제본을 넣는다.
- 검증 상태: 코드 확인함.

### L-2. 검증 견고성: 불량 스트림 하나가 전체 검증을 실패시키고, 예외 클래스명이 결과에 노출됨 (Low)
- 위치: `PdfWatermarkInspector.java:62-66`, `:100-105`, `util/PdfVerificationUtil.java:53-54`
- 근거: `extractAll`은 `_k1`을 발견할 때마다 복호화하며 하나라도 GCM 태그 불일치(`AEADBadTagException`)를 내면 전체가 예외로 끝난다. 정상 복제본이 남아 있어도 `verify`는 `EXCEPTION:AEADBadTagException`으로 실패한다. 반환되는 사유 코드에 예외 클래스명이 들어가 내부 구현이 드러난다. 또 `extractFirst`는 첫 항목만 보고, 최상위 페이지 리소스의 XObject만 순회한다(폼 내부 중첩은 탐색하지 않음).
- 조치: 스트림별로 try/catch로 감싸 실패는 건너뛰고 유효한 것이 하나라도 있으면 성공 처리한다(정책 선택). 사유 코드는 고정 열거형(`DECRYPT_FAILED` 등)으로 바꾸고 상세는 로그에만 남긴다.
- 검증 상태: 코드 확인함, 미재현.

### L-3. 키·입력 유효성 검증 부족 (Low)
- 위치: `KurbyPdf.java:24-25`, `util/PdfVerificationUtil.java:26-27`, `WatermarkRequest.java`
- 근거: Base64 키가 null이면 NPE, 형식이 틀리면 `IllegalArgumentException`이 그대로 전파된다(특히 `verifyBase64`는 boolean 반환 메서드인데 잘못된 Base64에서 예외를 던진다). HMAC 키 길이 하한이 없어 1바이트 키도 받아들이고, HMAC 키와 AES 키에 같은 값을 줘도 막지 않는다.
- 조치: 키 길이를 검사한다(HMAC ≥ 32바이트, AES는 16/24/32바이트). 두 키가 같으면 거부한다. Base64 디코딩 실패는 명확한 예외로 변환한다.
- 검증 상태: 코드 확인함.

### L-4. jackson-databind 2.17.1에 알려진 취약점 12건, fat JAR에 포함되어 사용자가 교체 불가 (Low, 도달 가능성 낮음)
- 위치: `build.gradle.kts:25-26`(`api` 의존성), `:55-58`(relocate로 shading)
- 근거: OSV 조회 결과 2.17.1에 GHSA 12건(심각도 HIGH 4건: GHSA-cxp5-3px4-pw24, GHSA-j3rv-43j4-c7qm, GHSA-q4xh-88c3-wmh7, GHSA-rmj7-2vxq-3g9f 등)이 보고되어 있다. 다만 이 코드는 `ObjectMapper.writeValueAsBytes`(Map 직렬화)와 `readTree`만 사용하고 다형성 타입이나 빈 역직렬화를 쓰지 않으며, `readTree` 입력은 AES-GCM 인증을 통과한 데이터(키 보유자가 만든 것)뿐이다. 대부분 이 경로에서 도달하지 않는다고 판단해 Low로 둔다(각 CVE의 PoC를 돌려보지는 않았다).
- 영향: 취약점 스캐너가 이 라이브러리를 High로 표시할 수 있고, `shadowJar`로 relocate된 JAR을 쓰는 소비자는 Jackson만 따로 업그레이드할 수 없다.
- 조치: OSV가 제시한 수정 버전 중 2.18 라인이면 2.18.11 이상(2.21 라인이면 2.21.7 이상)으로 올린다. 배포 JAR 정책을 정해, 가능하면 shaded JAR 대신 일반 JAR + 의존성 선언을 기본으로 제공한다.
- 검증 상태: OSV 조회 완료, 도달성은 코드 기준 판단.

### L-5. 테스트가 비밀번호를 표준 출력에 남기고 결과 PDF를 디스크에 씀 (Low)
- 위치: `src/test/.../KurbyPdfTest.java:46-47`, `:72-76`, `:80-82`
- 근거: 소유자 비밀번호와 사용자 비밀번호를 `System.out`에 출력하고, 암호화된 PDF를 `build/test-out`에 저장한다. CI 로그나 아티팩트에 남을 수 있다. 테스트용 고정 키(`0x11`, `0x22`)는 주석으로 테스트 전용임이 표시되어 있다(Info 수준).
- 조치: 비밀번호 출력을 제거하고 단언(assert)만 유지한다. 출력 파일은 `@TempDir`를 쓴다.
- 검증 상태: 코드 확인함.

### L-6. 빌드·공급망 위생 (Low)
- 위치: `build.gradle.kts:3`, 저장소 전체
- 근거: (1) `gradlew`는 있으나 `gradle/wrapper/*`가 커밋되어 있지 않다(`git ls-files`에 0건). 래퍼가 동작하지 않아 재현 가능한 빌드가 어렵다. (2) 의존성 잠금(lockfile)이나 `gradle/verification-metadata.xml`이 없다. (3) 플러그인 `com.github.johnrengelman.shadow` 8.1.1은 이관된(com.gradleup.shadow) 구버전이다. (4) README의 설치법이 로컬 JAR 복사이며 체크섬/서명이 없고, `SECURITY.md`(취약점 신고 창구)가 없다.
- 조치: wrapper JAR/properties를 커밋하고 `distributionSha256Sum`을 지정한다. `./gradlew dependencies --write-locks`와 의존성 검증을 도입한다. 릴리스에 체크섬을 제공하고 `SECURITY.md`를 추가한다.
- 검증 상태: 저장소 파일 목록으로 확인함.

### I-1. 예측 가능한 시드의 `java.util.Random` (Info)
- 위치: `PdfForensicEmbedder.java:23,40`
- 근거: 위치 시드가 `System.currentTimeMillis()`이고 `java.util.Random`을 쓴다. 위치는 비밀이 아니므로 직접적 영향은 없다. 주석의 "랜덤 위치가 보통 더 안전"은 근거가 약하다.
- 조치: 위치 무작위성이 필요하면 `SecureRandom`을 쓰거나, 의미 없으면 고정 배치로 단순화한다.

### I-2. AES-GCM 96비트 랜덤 IV를 장기 키로 대량 사용 (Info)
- 위치: `WatermarkPayload.java:51-56`
- 근거: 같은 AES 키로 약 2^32회를 넘겨 암호화하면 IV 충돌 확률이 무시할 수 없게 된다(NIST SP 800-38D 권고 한계). 문서 한 건당 1회 암호화하므로 일반 사용에서는 문제 없다.
- 조치: 키를 주기적으로 교체하고 키 ID(`kid`)를 페이로드에 넣어 구분한다.

### I-3. 문서와 코드 불일치 (Info)
- 위치: `README.md`(검증 예시 `PdfVerification`, 구조도), `KurbyPdf.java:31`
- 근거: README는 `PdfVerification.verify`를 쓰라고 하지만 실제 클래스는 `util.PdfVerificationUtil`이다. 구조도의 `KeyUtil`도 `util/` 하위다. `KurbyPdf.java:31` 주석은 "페이지당 2개"인데 실제 기본값은 3개다(`PdfForensicEmbedder.java:20,23`). 예시대로 코드를 쓰면 컴파일이 안 되고 사용자가 임의 대체 코드를 만들게 된다.
- 조치: README와 주석을 실제 API에 맞춘다.

### I-4. PDFBox 2.0.30은 구버전이나 알려진 취약점 조회 결과는 없음 (Info)
- 근거: OSV 조회에서 `org.apache.pdfbox:pdfbox:2.0.30`에 보고된 취약점은 없었다. 다만 2.0 라인에 더 새로운 패치 버전이 있으므로 정기적으로 올리는 것이 좋다(Maven Central 검색 응답이 일관되지 않아 최신 버전 번호는 확정하지 않았다).
- 조치: 2.0.x 최신 패치로 올리고 Dependabot/Renovate를 켠다. PDF 파서는 악성 입력 대상이 되기 쉬우므로 업데이트 주기를 짧게 가져간다.

## 3. 양호한 점
- `SecureRandom` 사용(`KeyUtil`, `WatermarkPayload`). Owner 비밀번호 32자, 문자군별 최소 1자 보장, 편향 없는 `nextInt` 사용.
- 서명 비교에 `MessageDigest.isEqual`(상수시간) 사용(`PdfWatermarkInspector.java:136`).
- AES-GCM + 랜덤 IV, 페이로드를 JSON 정렬 직렬화 후 HMAC(정규화 일관성 확보).
- PDF 암호화에 AES-256(`setEncryptionKeyLength(256)`, `setPreferAES(true)`) 지정.
- 커밋 이력 검색에서 하드코딩된 시크릿은 발견되지 않았다(키 이름 `_k1` 상수만 일치).

## 4. 조치 우선순위
1. M-2(자원 제한), M-3(빈 비밀번호 처리): 수정 범위가 작고 효과가 크다.
2. M-1(문서 결합), M-4(권한·README 정직화): 설계 변경이 필요하므로 버전 1.1 목표로 계획한다.
3. L-4(jackson 업그레이드), L-6(래퍼·잠금 파일): 빌드 설정 수정.
4. 나머지 Low/Info는 다음 정리 때 묶어서 처리한다.

## 5. 범위 밖/미실시
- 동적 재현(PoC 실행), 퍼징, 실제 PDF 뷰어별 권한 비트 준수 여부 테스트는 하지 않았다.
- 소비자 애플리케이션(서비스 코드)의 키 관리·저장 방식은 이 저장소에 없어 평가하지 못했다.

## 6. 2차 검토 결과
1차 작성 후 각 항목을 소스 줄 번호와 다시 대조했다.

| 항목 | 2차 검토 결과 |
|---|---|
| M-1 | `WatermarkPayload.java:28-46`에서 서명 대상에 문서 식별자가 없음을 재확인. 유지 |
| M-2 | `streamToBytes`와 `catch (Exception)` 줄을 재확인. 상한 없음. 유지(외부 입력 노출 여부에 따라 High 가능, 라이브러리 범위라 Medium) |
| M-3 | `KurbyPdf.java:35`의 조건을 재확인. 유지 |
| M-4 | 권한 설정이 `setCanPrint`, `setCanExtractContent`뿐임을 재확인. 제거 시나리오는 미재현이라 "가능한 구조"로 표현을 낮춤 |
| L-4 | 1차에서 High로 둘 뻔했으나 사용 API가 `writeValueAsBytes`/`readTree`뿐이고 입력이 AES-GCM 인증을 거친 뒤라 Low로 하향 |
| I-3 | README와 실제 클래스명(`PdfVerificationUtil`)을 대조해 확인 |

오탐으로 제외한 후보:
- "HMAC 후 암호화 순서가 잘못됨": GCM이 이미 인증을 제공하므로 중복일 뿐 취약점이 아니다.
- "서명 비교 타이밍 공격": `MessageDigest.isEqual` 사용으로 해당 없음.
- "소유자 비밀번호 생성 편향": `nextInt(bound)`와 Fisher-Yates 사용으로 편향 없음.
- "경로 조작/명령 실행": 파일 경로를 받는 코드가 없음(테스트 제외).

2차 검토에서 추가한 항목: `verifyBase64`의 예외 전파(L-3), 래퍼 파일 미커밋(L-6, `git ls-files`로 확인), `catch (Exception)`이 `Error`를 놓치는 점(M-2).

## 7. 재현 계획(미실시)
권한 문제로 실행하지 못했다. 허용되는 환경에서 다음을 확인하면 이 보고서의 "미재현" 항목을 모두 닫을 수 있다.
1. M-1: A 문서에서 `_k1` 스트림 바이트를 추출해 빈 PDF B에 `PdfForensicEmbedder.embed`로 삽입하고 `verifyDetailed`가 `valid=true`를 반환하는지 확인.
2. M-2: 256MiB 0 바이트를 Flate 압축한 스트림을 `_k1`에 넣고 `-Xmx128m`으로 `verifyDetailed` 실행, `OutOfMemoryError` 전파 여부 확인.
3. M-3: `userPassword=""`, `ownerPassword="x"`로 `watermark` 호출 후 `PDDocument.isEncrypted()`가 false인지 확인.
4. M-4: 사용자 비밀번호로 연 문서에서 `getCurrentAccessPermission().canModify()` 값을 읽고, `_k1` 폼 제거 후 저장해 검증이 `WATERMARK_NOT_FOUND`가 되는지 확인.
5. L-2: 첫 페이지에 쓰레기 `_k1` 스트림 폼을 앞에 추가하고 검증이 `EXCEPTION:AEADBadTagException`이 되는지 확인.
