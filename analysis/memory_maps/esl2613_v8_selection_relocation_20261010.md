# ESL 2613 V8: G2가 옮긴 선택 배열 — observer 주소 보정

## 핀 / 근거

- V8 r8 SHA256 `1e83466eab020818a6c0e9057508d71451af3ee1098af43ebefc20de8ab96e3d`.
- 공유 temp `20261010_034935_esl2613_g2_r8/reports/build_v8.json` SHA256 `fc80f322d2752e941deb90bc12a88daffcae9a753821779a489d66543aea78a0`.
- report `detail.g2.layer3.starts[".f2data"] = 0x2456400`.
- root와 work가 동결 V8의 실제 opcode/disassembly를 각각 읽었다. 이는 observer 읽기 주소의 근거이며 제품 변경은 아니다.

| 필드 | 공식 base | V8 G2 | 검증 |
|---|---|---|---|
| selection count DWORD | `0x899024` | `0x899024` | `.f2code` clear/read/write xrefs 유지 |
| selection entries DWORD[] | `0x1604004` | `0x2456404` | relocated `.f2data + 4` |
| Shift handler 순회 끝 | base list+400 B | `0x2456594` | 100개×4 B, exclusive end |

- `0x41DD48`: bytes `b804644502`, `mov eax, 0x2456404`.
- `0x41DD69`: bytes `3d94654502`, `cmp eax, 0x2456594`.
- `.f2data` relocation의 범위는 `0x2456400..0x2462D00`이다. 선택 배열은 이 범위 안에 있다. 선택 cap100 유지와 배열 주소 불변은 다른 주장이다. report의 `.f2data`는 원본 자료 블록의 의미 이름이다. 새 VA의 실제 PE storage는 zero-fill `.g2bss` 안의 relocated 영역이며, 같은 이름의 file-backed PE section이2456400에 있다고 해석하지 않는다.

## 실패 해석과 다음 계측

- 기존 G6 observer는 base용 `tools.esl2610_runtime.SELECTION_ENTRIES_VA=0x1604004`를 V8에도 사용했다. native handler는 다른 relocated 배열을 사용하므로 그 주소의0/sentinel을 실제 선택으로 해석하면 안 된다.
- 96개 fixture의 `isolated=0`, 다음3개 fixture에서의 `unit_row(slot0)` 예외는 이전 원시 그대로 보존한다. 이동/겹침/양자화는 가능한 부가 문제였지만 당시 결과만으로 원인이라고 확정할 수 없다. 선택 주소 보정을 먼저 검증한다.
- 새 observer는 pinned build report와 실제 candidate opcode를 대조해 읽기 주소를 바인딩한다. frozen source/base runtime 상수를 몰래 바꾸지 않는다.
- count/raw entries/read address를 UID 해석 전에 기록한다. slot0/범위 밖/UID·owner 불일치는 INVALID/TRANSIENT로 명시하고 성공 목록에서 걸러내지 않는다. count-before/raw/count-after의 제한된 재읽기로 변경 중 표본을 구분한다.
- UI 선택/Shift 추가/owner filter/명령은 새 실제 입력 결과로만 판단한다. 새 주소를 찾았다는 정적 사실 자체는 G6 런타임 PASS가 아니다.

## Shift native 분기·계측 근거

동일 pinned V8를 root가 다시 Capstone으로 `0x41DC40` 함수 경계부터 읽었다. 중간 명령 바이트를 새 시작점으로 삼지 않는다.

| VA | 바이트/의미 | read-only 용도 |
|---|---|---|
| `0x41DC40` | `81ec78020000`, native handler prologue | 실제 handler 진입 |
| `0x41DCC3` | `bd01000000`, EBP=1 | 아래 Shift 비교의 상수 |
| `0x41DD07` | `a1e038b900`, clicked UID=`[0xB938E0]` | 실제 hit UID/slot 해석 |
| `0x41DD1E` | `392d9839b900`, Shift flag=`[0xB93998]`와 EBP 비교 | 요청 key가 아닌 앱 내부 modifier 증거 |
| `0x41DD24` | `0f8585010000`, 값이1이 아니면 `0x41DEAF` | Shift-add route를 우회 |
| `0x41DD35` | `8b0dc43fb600`, local index=`[0xB63FC4]` | native owner 비교 |
| `0x3347000` | `3b7c2410`, EDI vs compacted count `[ESP+0x10]` | G6 cave 실제 count 검사 |
| `0x3347006` | `a1e038b900`, clicked UID reload | cave 종료 동작 |

- handler/Shift site의 `[ESP+0x10]`를 cave 이후의 compacted count라고 소급 해석하지 않는다. 기록은 site별로 구분한다.
- 빈 선택에서 A를 선택한 결과만으로 Shift flag1/분기 진입을 증명할 수 없다. B의 실제 clicked UID·Shift flag·local/owner·cave count와 입력 전후 선택을 연결해야 한다.
- `20261010_064329_g6_shift_instrumentation/` ELF32 run/ancestor-attach fixture는 세 명령 body의 nonzero/zero hit를 검증했지만 실제 game attempt는 메뉴에서 PointerRoot focus1/BadWindow로 중단돼 해당 native 계측에 도달하지 않았다. input0/제품 판정 없음이다. 원시 outer `gdb_exit_code=1`은 pre-GDB runner 코드이며 실제 GDB exit가 아니다.
