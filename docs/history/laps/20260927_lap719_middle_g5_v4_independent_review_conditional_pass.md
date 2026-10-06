# 2026-09-27 | lap 719 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, 중간(middle, 진단·계획·확인). 게임 코드 hands-on 수정 없음.
- 가설 / 사용자 관찰: lap717(v4 반전게이트 구현+회귀)·lap718(공격 N=5)의 middle 요청 (a)~(d)를 독립 검수한다.
  (a) v4 게이트 opcode 집합이 lap676 원문과 일치하는가, (b) 반전 게이트가 lap676의 22개 호출부에서 20기 초과
  선택 시 안전한가, (c) monkeypatch 재사용 결과가 유효한 재검증인가, (d) 공격 N 추가가 필요한가.
- 예상 PASS / FAIL 조건: raw·바이트·정적 xref로 (a)~(d)가 모두 lap717/718 주장과 모순 없으면 2단 조건부 PASS,
  제품 동작을 바꾸는 모순이 있으면 FAIL/HOLD.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 문서만 — 이 기록, `docs/STATUS.md`,
  `docs/feedback/INBOX.md`, `docs/feedback/APPROVALS.md`(한도 초과 265줄 → 종결 계보 압축, 원문
  `docs/history/20260927_approvals_lap719_precompaction.md` SHA256 `5e1862fe…96e36fa`), `loop/ESCALATE_SOL`(lap719 섹션 추가).
  제품 코드·EXE·도구 0 변경. 검수 대상 파일 SHA256: `patches/selection/g5_selection_cap50_v4.py`
  `3e3fdfff…4f7e064`, `test_g5_selection_cap50_v4.py` `ccfa9e5a…a31f507`. 커밋 없음(uncommitted).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 재해시 일치(읽기만). v4 후보를 원본에서 독립
  재빌드 → `0e472792410ddc87eb5eee9809c99761da61d8afa23e73638db0fae5e10f9cbb`(lap717/718 값과 일치, 임시 사본 삭제).
  런타임 실행 없음(기존 raw 재파싱).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `PYTHONPATH=. .venv/bin/python -m patches.selection.g5_selection_cap50_v4 <원본> /tmp/lap719/v4.exe` → SHA 위 값.
  - capstone 역어셈블: `0x4AE550: jmp 0x4E4D50`(jmp이므로 cave 진입 시 `[esp+8]`=2번째 인자), 게이트
    `cmp 0x52/0x56/0x19b je body; <0x19d→count; ≤0x1a1→body; <0x1ae→count; ≤0x1bc→body; else count`,
    body `0x4E4E63`, cave 끝 `0x4E4F67` < 한도 `0x4E5000`.
  - `pytest -q patches/selection/test_g5_selection_cap50_v4.py patches/selection/test_g5_selection_cap50_v3.py
    tests/test_g5_command_packer_xrefs.py` → **9 passed**(10.44s).
  - lap676 도구 재실행 `tools/g5_command_packer_xrefs.py --exe <원본>` → 공유 temp
    `20260927_lap719_middle_g5_v4_review/g5_command_packer_xrefs_rerun.json` SHA256
    `0bd3259c7f4b3628577111e6823f1161d3370938577788047e631519e0b3eac9`.
  - 원본 `.text` 선형 스캔: `word [0x892ffe]` 쓰기 18곳, 원본 파일 전체에서 `0x004AE550` 절대주소 바이트 참조 0건.
  - raw 재파싱: `temp/Syw2plus_patch/20260927_lap717_v4_shp/{original1,candidate1..3}`,
    `20260927_lap717_v4_regression/{fullcoverage,moveattack,roundtrip}_candidate1`,
    `20260927_lap718_v4_attack_n5/candidate2..5`, 대조 `20260926_lap688_g5_repeat/{original,candidate}-1..5`.
- 측정값 / 판정:
  - **(a) PARTIAL — v4 코드는 lap676 문서 집합과 정확히 일치하나, lap676 문서 집합 자체가 raw와 다르다.**
    재실행 결과 22개 직접 호출부 중 21곳의 2번째 인자 즉치값은 `{0x52,0x56,0x1a0,0x1a1,0x1ae..0x1bc}`뿐이고
    `0x19b,0x19d,0x19e,0x19f`는 어느 호출부에도 없다(문서의 "각 호출에 즉치 정확히 하나"도 틀림 — 1번째·4번째
    인자에 0/1 즉치가 추가로 있으나 opcode 자리는 항상 2번째 인자). 22번째 `0x41F0A4`(및 `0x41F01D`의 jmp 진입)는
    즉치가 없고 2번째 인자가 **런타임 전역 `word [0x892ffe]`**다. 이 전역에 즉치로 쓰는 값은 3·4·0x20·0x25·0x4A·9이고
    나머지는 명령 버튼 테이블 `0x637A48`(16B 레코드, BSS라 정적값 없음)의 인덱스다. 즉 `0x41F0A4`는 lap676이
    말한 "비명령 호출부"가 아니라 **실제 유닛 명령 발행 호출부**다(v3 화이트리스트가 이동/공격에 효과가 있었고
    v4가 정지·홀드·순찰을 20→50으로 바꾼 사실과 일치). 여분 4값은 안전 위험이 아니라, 런타임 명령 인덱스가
    0x52·0x56·0x19b·0x19d~0x1a1·0x1ae~0x1bc 중 하나일 때 20기 상한이 남는 **범위 누락 위험**일 뿐이다(발생 여부 UNKNOWN).
  - **(b) CONFIRMED(안전).** 즉치 opcode 21곳은 전부 v4 집합 안이라 v4에서도 원본 본문으로 그대로 가며 v3·원본과
    동작이 같다. 원본 파일에 `0x4AE550` 함수 포인터 참조가 없어 데이터 경유 간접 호출자는 없다. v3→v4 동작 차이는
    `0x41F0A4` 명령 발행 호출부에서 명령 인덱스 ∉ {1,3,4,7,8,9} ∪ 집합이고 선택 >20일 때뿐이며, 이것이 의도한
    범위다. v4 docstring 42~55행의 "22곳이 이제 분할 경로를 탈 수 있다"는 위험 서술은 사실과 반대(해당 없음)라
    정정 대상이다.
  - **(c) CONFIRMED(유효).** 모든 후보 raw의 `provenance.private_exe_sha256`=`0e472792…`(정지/홀드/순찰 3회,
    fullcoverage, moveattack, roundtrip, 공격 N=5 4회), `source_unchanged=true`, cleanup 잔류 0. raw 표: 정지
    `0x1000002`·홀드 `0x1000027`·순찰 `0x1000023` 후보 50/50(버튼·단축키 모두), 원본 20/20, 지면 이동 50/50,
    ALT/Ctrl/Shift 전체 드래그 50, Shift 추가선택 4→7 유지. 도구 원문 무수정·모듈 전역만 교체이므로 유효한 재검증이다.
    부수: fullcoverage의 `source_exe`가 옛 경로 `Syw2plus_re/Syw2plus/syw2plus_original.exe`(동일 SHA, 읽기 전용).
  - **(d) CONFIRMED, 추가 N 불요 — 단 판정 지표 정정.** lap718은 lap689 middle이 자동교전 오염으로 불인정한
    `ever_command4`로 판단했다. lap689 인정 지표(클릭 직후 t=0 `pending==0x1000004` 동시 수)로 같은 raw를 다시 보면
    v4 5회 중 2회 **49/49**(run4·5), 나머지는 t=0.1 최대 14/22/18; v3 lap688 5회 중 2회 49/49, 나머지 18/12/23; 원본
    5회 중 2회 19/19, 나머지 7/11/8. 클릭 xy 일치 v4 4/5(49), v3 4/5, 원본 4/5. v4는 v3와 같은 표본 위상 패턴이며
    체계적 열화 신호 없음.
  - **종합: v4 2단 CONDITIONAL PASS(단일플레이, 측정한 명령 집합 한정).** 멀티 동기화 `UNKNOWN` 유지. 제품 G5
    최종 PASS·사용자 milestone 재승인은 선언하지 않는다(사용자 승인은 v3 `e5004764…` 대상이었다).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - **잔여 위험 R1(v3부터 존재, v4가 적용 범위를 넓힘):** 청크 경로는 선택 >20이면 항상 본문을 3회 호출하고
    `entries[20:40]`·`[40:50]`을 선택 수와 무관하게 넘긴다. 원본 본문은 20칸을 유효성 검사(`0x416F70`)로만 거른다.
    50기 선택 후 21~49기로 **선택을 줄였을 때** 꼬리 칸에 이전 핸들이 남으면 미선택 유닛도 명령을 받는다. 지금까지
    raw는 전부 "전체 50 선택 → 명령"이라 이 경우를 측정한 적이 없다.
  - 잔여 위험 R2: 런타임 명령 인덱스가 v4 비분할 집합과 겹치는 명령(미측정 명령 버튼)은 20 상한 유지 가능.
  - 독립 검수: 이 lap(middle). 사용자 승인: 없음(v4 후보 교체는 사용자/운영자 경계).
- 다음 한 가지: 마일스톤 경계로 `loop/ESCALATE_SOL` lap719 섹션에 승격. 운영자/사용자가 v4를 승인된 G5 후보로
  교체할지와 G1 재개를 판단한다. 판단 대기 중 비차단 work 1건(EXE 무변경): 기존 `tools/g5_stop_hold_patrol_v4_probe.py`
  절차로 50 선택 → 부분 드래그로 25기 재선택 → 정지 → `0x1000002` 수신이 정확히 선택 25기뿐인지(미선택 25기 불변)
  원본(20→10 재선택)과 paired 1회씩; 동시에 v4 docstring 42~55행 위험 서술과 lap676 memory map의 opcode 집합·
  `0x41F0A4` 분류를 정정. R1이 FAIL이면 같은 work가 청크 복사 수를 선택 수 기준으로 제한하는 v5를 만든다.
