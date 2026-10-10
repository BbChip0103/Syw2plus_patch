# ESL 2613 G9: fixed-map / procedural-map 자리 배정 경로

## 입력과 근거

- 공식 2613 SHA256: `818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724`.
- 동결 V89 r8 SHA256: `39680ebbb202ba79cca4c47ac3eeb73b5cc9e8dbbf75c99ba679d07b1422db51`.
- 독립 정적/원시 검수: 공유 temp `20261010_055310_esl2613_hwtrace_c0_independent/bounded_hwtrace_c0_verdict.json`, SHA256 `9f8933708198d92597f129222e20d79a6fed057fa8e43832c0c1b4eb49745b00`.
- 실제 선행 추적: `20261010_053214_esl2613_g9_hwbp_r1/`. PS7 이후 hardware breakpoint의 legacy G9 hit0이다. 실제 control event는 `d54=0`을 기록했다. 더 이른 실행 전체를 추적한 증거는 아니다.

아래는 **주소/조사 근거**다. 후속 독립 검수에서 r8의 절차 지도 자리 대응 결함은 확인했지만, 새 패치 지점/구현의 최종 승인은 아니다. 원본과 r8은 변경하지 않는다.

## State2 분기

`0x424D50` handler는 `0x424D55`에서 WORD `[0x632D54]`를 읽는다.

| 조건 | 경로 | 자리 배정 |
|---|---|---|
| `d54 == 1` | `0x424D5F → 0x41BC40 → 0x41BD5F` | `0x42FB50`, 기존 G9 site `0x42FBB1` |
| `d54 != 1` | `0x424D73 → 0x41B9B0` | 아래 절차 지도 경로 |

기존 source-fixture는 명시적으로 `d54=0`이다. 쉬운 fixed-map 경로만 검증해 절차 지도를 계약에서 제외하지 않는다. G9는 입력 시작좌표 목록과 자리 index의 고정 대응이며, 서로 다른 seed의 지형에서 같은 절대 XY를 요구하는 것은 아니다.

## 절차 지도의 정적 호출 경로

`0x41BAC3 → 0x436E60 → 0x436E86 → 0x4464F0 → 0x446ADA → 0x446BF0 → 0x4471B9 → 0x44F020`.

`0x44F020`은 순서 구성 `0x44F260`, `0x450DA0` 후 각 자리에서 `0x44F074 → 0x44F0A0`으로 index를 얻는다. `0x44F079`의 AX가 입력 pair 선택에 쓰이고, `0x44F085`부터 동적 출력으로 저장한다. 성공한 배정 결과는 `0x446AF6..0x446B07`에서 PlayerStruct의 시작좌표로 복사된다.

| VA | 동결 바이트 | 의미 |
|---|---|---|
| `0x44F020` | `8b442414` | 함수 진입 첫 명령 |
| `0x44F074` | `e827000000` | index 선택 함수 호출 |
| `0x44F079` | `0fbfd0` | `movsx edx, ax` |
| `0x44F082` | `8b04d3` | 입력 `[ebx + edx*8]` 읽기 |
| `0x44F085` | `8906` | 출력 `[esi]` 쓰기 |
| `0x44F096` | `5e` | epilogue 진입 |
| `0x446AEA` | `b858deb300` | 성공 배정 후 PlayerStruct copyback 시작 전 |

## Read-only runtime 계측 계약

- `0x44F020` 진입 cdecl: caller=`[ESP]`, countWORD=`[ESP+4]`, output pointer=`[ESP+0xC]`, input pointer=`[ESP+0x10]`. `[ESP+8]`/`[ESP+0x14]`는 보조 선택 입력이다. prologue 전 값을 보존한다.
- pair는 `(DWORD x, DWORD y)`다. 8쌍은64 B/16 DWORD이다. 실제 count/pointer를 확인하며 정적 `0xB42D38`을 동적 입력이라고 추측하지 않는다.
- `0x44F079`: AX=선택 index, EBX=input base, ESI=current output pair, EBP=remaining count. 관측 iteration=`entry_count-EBP`, ESI=`entry_output+iteration*8`을 검증한다.
- `0x44F096`: 보존한 entry pointer/count로 입력과 출력을 읽는다. epilogue의 현재 ESP를 caller라고 오인하지 않는다.
- `0x446AEA`: 성공 반환 뒤 temp output=`ESP+0x84`를 기록한다. PS3 최종 PlayerStruct start는 `0xB3DE58+0x338*index`, 목록은 `0xB42D38`/countWORD=`0xB42D78`다.
- 호출이 반복될 수 있으므로 invocation별 entry/site/exit와 실제 성공 copyback을 연결한다. 서로 다른 시점/호출의 배열을 합쳐 성공/실패를 만들지 않는다.
- 하드웨어 breakpoint만 사용한다. 원본/EXE 코드/레지스터/장부/selection을 쓰지 않는다. 실제 mapping이 계약과 어긋나는지 확인한 다음 별도 writer의 RED 회귀·새 복사본 패치·독립 검수가 필요하다.

## 실제 반례와 새 hook 조사 근거

- `20261010_061348_esl2613_proc_g9_independent/g9_procedural_independent_verdict.json` SHA256 `3e03abd028b1901f713c55cb7112b0c290fd7e632a4d9380fa4602ca35e825c3`: 실제 `0x44F020` 진입의64 B 입력과 PS3 입력이 같고,8개 owner의 출력 index는 `[1,5,7,0,2,4,3,6]`이다. chooser는 입력 pair buffer를 읽기만 하므로 입력 순서 변경으로 설명되지 않는다. r8의 G9 절차 지도 대응은 scoped FAIL이다.
- 실제 site/exit/copyback 세부 추적은 GDB command 오류로 누락됐으며 원시 그대로 보존한다. 특히 `ESP+0x84`는 temp 배열 주소이지 그 위치의 DWORD를 다시 pointer로 역참조하는 것이 아니다. 향후 계측은 실제 ELF32 mock에서 네 명령 body까지 실행해야 한다.
- 검토용 hook 범위는 `0x44F079`의6 B `0fbfd083c40c`, continuation=`0x44F07F`다. **06:42 KST 정적 재계산 정정:** 초기의 `entryESP−0x30`/`[ESP+0x34]` 해석은 잘못됐다. `0x44F079`는 caller가 helper의12 B 인자를 정리하기 전이므로 site ESP=`entryESP−0x3C`, countWORD=`[ESP+0x40]`다. locals32 B + saved EBP/ESI/EBX/EDI16 B + 아직 남은 helper 인자12 B다. 기존 `0x30`은 helper 인자를 빠뜨린 값이다. EBP는 remaining count이고 자리 ordinal은 count-EBP다. 동결 r9의 `[ESP+0x34]` 구현은 의미 검수 HOLD이며 실행하지 않는다. native `0x44F0A0` 호출과 RNG/보조 자료 상태는 유지해야 한다.
- 새 섹션/코드 위치는 writer가 정확한 PE 정렬/기존 섹션/overlay/nonoverlap 근거로 정한다. 이 주소표를 이유로 임의 cave를 사용하거나 기존 r8을 덮어쓰지 않는다. RED 회귀→별도 새 후보→원복/버전 거부/재빌드→fresh native identity와 독립 검수 전에는 수정 완료가 아니다.

## r10 수정과 독립 의미 수용 (07:19 KST 추가)

- 위 r9 HOLD는 이후 독립 실제 바이트 ELF32 반례로 **REJECT**됐다: `20261010_063711_esl2613_g9_r9_independent/verdict.json` SHA256 `a7759d6a4555baa568ae3485cffd8735ff49dbc0f4d08dd0f35fdec02c3a2710`. count1/poisoned scratch0에서 EDX−1이며 과거 해석·후보를 덮어쓰지 않는다.
- r10 SHA256 `a6d357102dec956f8caa407a2bcb1d56eb14409bc9a67ee17d0ca80a478c40bc`은 새 `.g9proc` VA `0x3349000`을 사용한다. hook `0x44F079`의 detour는 `e9829fef0290`, prefix는 `0fbf5424402bd583c40ce9706010fd`: countWORD `[ESP+0x40]`를 EDX에 읽고 EBP를 빼며, 기존12 B 인자를 정리한 뒤 `0x44F07F`로 복귀한다. 원래 helper CALL은 유지한다.
- fresh Sol source ACCEPT 정본 `20261010_070711_esl2613_g9_r10_independent/final/verdict.json` SHA256 `43fcafff2cd9add161fb06918437530964810a98508a911248fd82bdf4ee88f5`: 실제 candidate bytes ELF32 count0~8/negative guard/output/ABI/helper mock과 r9 RED→r10 GREEN, PE 보존/원복/재빌드 수용이다. 실제 helper/RNG·게임·멀티 증거로 확대하지 않는다.
- r10 후속 read-only index 관측은 **`0x44F07F`**에서 새 EDX와 helper 인자 정리가 끝난 ESP를 읽는다. 그 시점 ESP는 entryESP−0x30이며, hook 이전 `0x44F079`의 entryESP−0x3C와 혼동하지 않는다. entry `0x44F020`, exit `0x44F096`, 성공 copyback `0x446AEA`와 invocation별로 연결한다. root가 네 command body의 실제 ELF32 preflight와 실행 전후 hash를 요구했으며 실제 게임 결과는 아직 미정이다.

## r11 — Windows 헤더 겹침 수리 (2026-10-10 사용자 실측)

전달 r10은 Wine에서 실행됐지만 Windows에서 앱 실행을 거부했다. 전달본 SHA a6d357…는 동결 후보와 일치했다. `.g9proc` 추가로 section table 끝0x1010/SizeOfHeaders0x1200이 첫.text RVA0x1000에 침범했다. 헤더 구조 결함은 확인되었으며 Windows 거부의 인과/해소는 native Windows 재시험 전 미확인이다.

r11은 pinned V8 SHA1e83466e…의 owned `.g8code` 시작 VA0x3348000에서 +0x20, file offset0x1E9220에15byte stub을 넣는다. exact V8 SHA, zero preimage·raw/virtual range·기존22byte G8 본문 비중첩 확인 후 적용한다. prefix `0fbf5424402bd583c40ce9`의 `[ESP+0x40]` count 읽기·EBP감산·12byte stack정리는 동일하며 return displacement만 새배치에 맞춰진다. 세 기존G9 사이트만 같은로직으로 패치한다.

후보 SHA256 `b612109b8cd9e313927871a5a35f28cc09b9c95f80626c938f4d42192cb00556`, 2,003,968bytes,94sections/header0x1000/tableend0xFE8/first.textRVA0x1000/SizeOfImage0x2F49000. V8와 차이27bytes는 checksum·세G9site·stub만이며 section descriptors/파일길이/섹션원시포인터는 불변이다. 새r11과 역사r10의 rollback 모두 exactV8SHA1e83466e…로 복구된다. standalone pinnedofficialG9는 기존 compact+section 경로를 유지한다.

근거: 공유temp `20261010_g9_windows_header_fix/artifactreport.json`, `before_layout_audit.json`와 `independent_review/`. 별도G1·원본·안전핀/과거실패raw 변경0. nativeWindows 보장으로 쓰지 않는다.
