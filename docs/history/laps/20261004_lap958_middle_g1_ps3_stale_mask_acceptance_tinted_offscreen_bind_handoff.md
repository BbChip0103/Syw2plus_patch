# 2026-10-04 | lap 958 | G1 W70 lap957 PS3 stale mask 독립 수용 · tinted 화면 밖 origin 바인드 수리 인계

- 실제 provider/model/effort / 지정 역할: middle(Claude Code `claude-opus-5-5`, high, Fast OFF), 진단·계획·확인. 게임·하네스·source·test·DLL·validator 변경0, 새 게임 실행0, commit0. `loop/.lap_counter` 958 읽기만.
- 목표: lap957 stale mask 2개를 제품 helper 없이 재계산하고, "steady stale 약 75% = `rle_tinted` last-writer"의 의미를 판정해 다음 work를 확정/기각한다.
- 가설: (a) 마스크 합 == 헤더 == 레코드, 분류 표 재현. (b) tinted 픽셀 stale은 replay와 실제 buffer의 호출 단위 불일치(lap957 제안) 또는 compose 생략 때문이다.
- 예상 PASS / FAIL: 재계산 불일치 0이면 장치 수용, 아니면 FAIL. 원인은 source·원본 디스어셈블·같은 run PNG 세 근거가 일치할 때만 판정, 아니면 계측 work로 넘긴다.
- 변경 파일 / 커밋: 새 카드 `docs/work/active/G1_MIDDLE_W70_PS3_STALE_TINTED_OFFSCREEN_BIND_HANDOFF_LAP958.md`, 이 기록, STATUS. uncommitted.
- 원본 SHA / 후보 SHA / fixture: `Syw2plus/game.exe b56986e0…a8ac`·`save/save006.dat 616b7997…d064` read-only MATCH. lap957 source 5파일·stale_mask.bin 2개·raw 3개 SHA = lap957 기록(카드 §1). save006 비합성, 8 player records는 활성8인 부하증명 아님.
- 실행 명령 / 산출(공유 temp `20261004_lap958_middle_review/`, `.venv/bin/python`): `recalc_lap958.py`(`ba184bc27599aad5f7086ec8aa6129b3442353a4bd4653bbf052ece11fd27e00`) → `recalc_lap958.json`(`ba45cd931ed42947315544a3eeb6445b86a1121af6db037e7cd6605d609deb1c`); `geom_lap958.py`(`15e967313e1b600d7467b12680821a39e121377df968f590d0dbed190b818e95`) → `geom_lap958.json`(`021759a71cab526c6375f66f4cd8e57ea129ff1be1ad3beeb74fcdf443c9ce80`)·`stale_intersection_r1_lap958.png`(`8d3e9c7d82a3c43e20725294cd24609125963e5e3aa549087dc7f1846b2f4160`); `png_block_lap958.py`(`d37c98370bc46e69ebacca466c1d2a7a076af42b011660d78e0f8ac1faf661da`) → `png_block_lap958.json`(`1863aa3b529e58a21498492355a7471bb0f7ea5c16aa2e45c572957100c1fc78`). 원본 `objdump -D -b binary -m i386 --adjust-vma=0x400000 --start-address=0x466EA0 --stop-address=0x467060`(읽기 전용).
- 측정값 / 판정:
  - 장치: 93덤프 맵/헤더/레코드 **불일치 0** → lap957 stale mask **PASS(partial) 수용**. 분류 표(steady 75.45/14.43/8.40%, 초기 표, residual 겹침 2,441.1) 정확히 재현.
  - 새 사실: steady stale은 고정 집합(교집합 r1 41,861·r2 41,806 / 평균 42.8k).
  - `0x466EA0` = `dst = lut[src]`(0xFE skip), 목적지 읽기 없음, viewport `+0x4D0..+0x4DC` 자체 클립 → a≠b 가설 기각.
  - 원인 판정: `mirror_tinted_rle`는 clipped=FALSE라 origin이 화면 밖인 새 key는 identity frame을 영구 바인드하지 못해 compose 0 → expected가 terrain 값으로 남아 stale. 위치(위쪽 가장자리 건물 줄, 화면 안 건물은 일치)·렌더(stale 픽셀 2×2 비균일 0.0 vs 일치 0.237)·source 세 근거 일치. 위쪽 줄 stale 26,951px = 교집합의 64%.
  - lap957 제안(호출 단위 replay-vs-buffer 불일치 계측)은 **기각하고** 최소 수리로 대체: 화면 밖 origin일 때만 기존 clipped(원점 재생) 바인드 경로 사용. 실패 시 같은 lap에서 opt-in 분기 계수로 추적.
  - burst UNKNOWN 유지, 기준2 전체 미합격(PS3 경계·PS35·P6/P7 HD·D-2·사용자승인).
- 회귀 / 남은 위험: per-call 바인드 실패 사유는 직접 계측하지 않음(예측 P-1~P-3으로 반증 가능하게 둠). census 정렬은 다른 run 근사. 디스크 여유 18GiB(<20GiB) — 다음 실행 전 PROMPT 규칙대로 회수 필요.
- 다음 한 가지: work(Sonnet) 1 lap — 카드 §4 tinted 화면 밖 origin 바인드 수리 + fresh save006 scale2x pair(lap957 r1과 같은 stale-mask spec), P-1~P-3·안전·성능 공개.
