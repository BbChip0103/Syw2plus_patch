# G9 Windows 실행 거부 — 2026-10-10

## 사용자 실측 / 범위

일반 전달본 실행 성공, 자리고정 전달본 Windows에서 “현재 PC에서는 이 앱을 실행할 수 없습니다”. 이름만 바꾼 전달본이라는 사용자 확인. 기존 Linux/Wine 검증을 Windows 합격으로 취급하지 않는다. G1·원본·핀·과거 raw·기존 일반판 비접촉.

## 근거와 가설

- 공유폴더 `260921_temp/2613_G2_G6_G8_G9_자리고정.exe`는 2,004,992 bytes, SHA256 `a6d357102dec956f8caa407a2bcb1d56eb14409bc9a67ee17d0ca80a478c40bc`; 동결 r10과 byte-exact. 복사 손상 없음(사용자PC 파일 자체 SHA는 별도 미수집).
- r10: PEoffset0x40, sections95, section table end0x1010, SizeOfHeaders0x1200, first.text RVA0x1000/raw0x1200. 헤더 virtual span이 첫 코드 페이지로 침범한다.
- 일반 V8: SHA1e83466e…, sections94/tableend0xFE8/SizeOfHeaders0x1000/first.textRVA0x1000. 추가G9section이 부족한 헤더 공간을 확장한 경로에서 생긴 차이다.
- Microsoft PE 정의: SizeOfHeaders는 DOS/PE/section headers의 FileAlignment 정렬 크기이며 section RVA는 SectionAlignment에 정렬된다. [공식 형식](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format). 위 겹침은 확인된 구조 결함이고 사용자 Windows 거부와의 인과는 직접 Windows 재시험 전 유력 가설이다.

## 수정 / 종료 조건

기능 detour의 stack semantics 및 자리순서 로직은 유지하고 owned section 내 검증된 여유공간 사용으로 header 증가를 피한다. exactSHA/preimage·unsupportedversion·비중첩·byte-exact rollback 관련 회귀, 기존 사본/prefix/display/nativeABIguard로 최소 실제 실행, 한 번 독립 raw 검수. 전체Fast·장기실험/멀티를 반복 조건으로 추가하지 않는다. 새 후보/기존 실패판 보존; 승인 뒤 이전 전달판 archive, txt0. native Windows 합격은 사용자 재시험 전 미확인.

## 기계/독립 byte 확인

- r11 후보는 공유temp `20261010_g9_windows_header_fix/candidate/[ESL]Syw2plus 2613_G2_G6_G8_G9_자리고정.exe`, SHA256 `b612109b8cd9e313927871a5a35f28cc09b9c95f80626c938f4d42192cb00556`이다.
- pinnedV8 owned `.g8code+0x20`의15byte stub. 파일크기2,003,968B/section94/header0x1000/table끝0xFE8/SizeOfImage0x2F49000을 유지한다. 독립 검수에서 V8 대비27byte만 checksum·세G9site·stub 범위에 있고, 기존G8코드·나머지header/sectiondescriptor가 그대로임을 확인했다.
- 새판·역사r10 모두 rollback→exactV8. G9 실제후보바이트 ELF32/stack·원복 검사2passed100.59s, comboSHA/헤더불변 검사2passed156.25s. 새SHA는 이 명시적결함수리 때문에 변경한 것으로 과거raw/안전pin을 통과용으로 갱신한 것이 아니다.
- G2_G6_G8 일반판도 헤더/table범위·섹션수·raw/virtual nonoverlap·정렬·파일/image범위·실행EP 검사 오류0. 이는 검사한PE구조 범위의 결과이며 모든결함없음/무결점 보장은 아니다. 일반판 bytes/SHA 불변.
- make doctor tooling/original PASS; optionaldefaultmanifest 없음은 이번private runtime증거와 구분한다. 전체Fast/장기실험은 반복하지 않고 관련검사·최소actual경로만 수행한다.

## 종료 — 범위 한정 기술 수용 / 전달 (23:46 KST)

- native 최소실행: `sp_long_v89_20261010_234043` privatePE SHA b612…/PID2077500/ELF32+samePIDguard gate. 새입력 전PS9,60초PS3/tick714/33개체→120초PS3/tick1914/72개체 heartbeat로 실제진행 확인. raw main result의peak48과heartbeat72는 서로다른표본이다. ownedprefix 프로세스0/game_removed=true, PID없음. 첫2회는 adapter/evidence 폴더 누락으로 game전실패였으며 알려진출력폴더 최소생성 후 마지막1회만 실제실행했다. 추가trial0.
- 보조 `LIVE_FAILED`는 peak>1200 strict조건 미달이고 nested builderSHA39680…/g9_fixed_start=false는 상속generic메타데이터다. 실제candidate/gate/private manifest SHA b612…로 정체성을 확인했다. 실제start/짧은진행은 확인했지만 새로운G9 자리좌표행동·Windows native 실행은 미검증이다. 전체보조PASS/Windows 수용으로 승격하지 않는다.
- independent review는 `ACCEPT_SCOPED_TECHNICAL`, blocker0: `independent_review/review.md` SHA256 `a4b6b0fb46aa5ee4946f8ad855b3331d48aea18b7b5714308800b55498dffd56`, `review.json` SHA256 `ef5303e0ce3e396f8f8861a09495937f1eac2f3dc80b3d72a7b177fda05a4241`.
- source범위: `patches/esl2610/g9_fixed_start.py`, `test_g9_fixed_start.py`, `test_g2_combo_2610.py`. 독립작업자구현/컨펌 분리. root후속 Ruff3files PASS, py_compile3 PASS, mypy `--explicit-package-bases --follow-imports=silent` source1 PASS(첫mypy 명령의duplicate-module config 오류는 해당옵션으로 해결,코드변경0). 전체Fast 재실행0.
- 사용자지정명 두판을 `260921_temp/`에 exclusive복사·SHA MATCH, 대체된이전두판은 `archive/20261010_234622_2613_before_header_fix/`로 SHA보존 이동. audit `20261010_g9_windows_header_fix/delivery.json`. txt생성/커밋/원본deploy/G1수정0. README에 최신후보/판정경계와r10장기결과를 구분했다.
