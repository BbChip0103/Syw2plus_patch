# 2026-10-05 | lap 965 | G1 middle — lap963 H-E 반증 독립 검수 · H-E3(비클립 cache 바인드 폭 게이트) 인계

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high, Fast OFF / middle(진단·계획·확인). 게임 hands-on 수정 없음. `loop/.lap_counter` 965 읽기만.
- 선행 처리(lap964 승격): lap964 work가 남긴 `loop/ESCALATE_SOL`(958B, SHA256 `4176110e4a808bec1676a0d0e0b523e50d57b8620a1b60738ea9aea1a4bed9ff`)의 요청 두 가지를 처리했다. (a) 사용자 재개 의사는 INBOX 2026-10-05 00:39 항목("루프 재개하고 10분에 1번씩 진행상황 보고해…")으로 이미 기록돼 있다. (b) Opus middle 검수는 이 lap이 수행한다. 처리 후 파일을 지웠다. 원문 전문:
  > lap964 work(Claude Sonnet) 승격 요청 — 구현 근거 충돌/역할 불일치. 코드·게임·테스트 변경 0.
  > 1) docs/STATUS.md "다음 한 가지": 사용자 2026-10-05 00:20 지시로 lap963 후 중단(STOP 유지, 재개 전 lap964 시작 금지). 그러나 00:39 loop.sh --role=work가 기동했고 loop/STOP은 없다(사용자 명시 재개 기록은 문서에 없음).
  > 2) 문서상 재개 이후 다음 작업은 "Opus middle 1 lap": lap963 H-E 반증 독립 재계산 + H-E2 정의. work는 H-E2를 추측 구현할 수 없다.
  > 승격 작업자가 할 일: (a) 사용자 재개 의사 확인(INBOX에 기록) (b) 재개라면 Opus middle로 lap963 기록(docs/history/laps/20261005_lap963_work_g1_cache_replay_viewport_he_falsified.md)을 trace/mask 입력에서 독립 재계산하고 H-E2(cache→screen 전송/offset 가장자리 x>=760,y<480 미갱신)를 정의, `g1_mirror_replay_viewport` 유지/되돌림 결정 후 work에 인계.
- 가설 / 검수 대상: lap963 E-1 반증(가장자리 stale 3,512 불변)이 raw에서 재현되는지. 가장자리 stale의 실제 원인이 무엇인지(lap962 대안 H-E2 = 전송 offset 포함). `g1_mirror_replay_viewport`를 유지할지.
- 예상 PASS / FAIL: lap963 기록 수치가 독립 재계산과 불일치 0이면 반증 수용. 원인이 raw 기하·계수·현재 source 경로로 하나로 설명되면 FEASIBLE 인계, 설명되지 않으면 BLOCKED.
- 변경 파일(uncommitted, 문서만): 본 기록, `docs/work/active/G1_MIDDLE_W70_HE_FALSIFIED_UNCLIPPED_CACHE_BIND_GATE_LAP965.md`(인계 카드), `docs/STATUS.md`, `loop/ESCALATE_SOL` 삭제(원문은 위에 보존). 게임·source·test·DLL·validator 변경 0.
- 원본 SHA / fixture: 검수 source `g1_mirror2x.c 1ec6468d…4019`·`g1_mirror_frame.h e8210cc6…87d7`·`g1_mirror2x.h f7139abd…66c3`·`direct_draw_trace.c a929c02f…21ee`·`tests/test_g1_mirror2x.py e7d80f97…7b75`(직접 sha256sum, lap963 기록과 일치). 원본 EXE·save006은 안전검사로 확인(아래 검증). 비합성 save006, 활성8인 부하증명 아님.
- 실행: 새 게임 실행 0. 공유 temp `20261005_lap965_middle_review/`: `recalc_lap965.py`(`2d9a0cbc…76ad`)→`recalc_lap965.json`(`78aec654…c5c3`), `he3_geometry_lap965.py`(`0d4d40dd…2d6d`)→`he3_geometry_lap965.json`(`8b6dda84…529a`), `edge_inter_lap963_r1.npy`(`9d1c6f70…ed88`), crop `edge_crop_loaded_lap965.png`(`f067c3b3…24fe1`)·`edge_crop_production_lap965.png`(`44dbd8a2…b8b3`). 입력 lap963 mask `c70976a2…3eff`·trace `807cb0f1…6075`·pair `9e738803…e043`, lap961 mask `8db4a04b…d27`·trace `bf5f30df…6c4f`·pair `b5df22d4…dd9c`(기록 일치).
- 측정 / 판정:
  - 재계산: lap961·lap963 모두 교집합 9,880·y<480 6,243·x≥760·y<480 3,512, 두 교집합 픽셀 단위 동일. cache clipped 107·verify 실패 0·`[0,0,831,511]` trace 원문 일치 → **lap963 H-E 반증 수용(불일치 0)**.
  - `layer_move_calls`=0(scroll memmove 없음). present 60~150에 compose +620·covered 423,936→425,984(cache 전체 재그리기). 덤프별 가장자리 stale은 ord 6~34 808 → ord≥300 3,512로 일정.
  - 기하: 열별 stale이 x=760 8 → x=799 180으로 선형 증가. 행 288~480에 32행 주기 삼각형 6개 = origin_x=768·64×32 마름모 타일의 화면 안쪽 절반. 가장자리 3,512 중 2,869(81.7%)가 이 마름모 안. 나머지 643은 시계 글자(행 13~18)·로고(P6 명시 잔여).
  - **lap962 대안 H-E2(전송 offset) 기각:** `transfer_cache_to_screen`은 항등 매핑이고 stale은 타일 격자에 정확히 맞는다.
  - **원인 H-E3(FEASIBLE):** `g1_mirror2x.c` 비클립 바인드 분기(1563~1567행)가 cache 대상에도 `origin_x <= 800u - width`를 쓴다. cache frame은 832라 origin_x=768 타일이 miss일 때 바인드되지 않는다 → not ready → `compose_cache_layer` 미호출 → 이전 장면 layer 값이 남아 매 프레임 stale. 끝까지 바인드되지 않은 key 3개(keys 766−inserts 763)와 맞다.
  - `g1_mirror_replay_viewport`: **유지**(올바른 cache viewport, 안전 0·E-3 악화 없음, 계수 유지).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 문서만 변경. H-E3는 정적 경로 + raw 기하 + 계수로 세운 가설이며 아직 실행으로 확인되지 않았다(다음 work가 F-1~F-4로 판정). V2s pair HOLD·사용자 판단 큐는 그대로다. 사용자 마일스톤 승인 아님. G2/G5 수정·G3/G4 재개·커밋 0. 시작 시 디스크 여유 14GiB(<20GiB) — 다음 work가 실행 전에 PROMPT 규칙대로 정리해야 한다.
- 다음 한 가지: work(Sonnet) 1 lap — 카드 §4 그대로. 비클립 바인드 게이트를 `frame_width`로 바꾸고 계수 1개 추가, 정적/host 테스트 → fresh save006 scale2x pair 1회(lap963 r1 대비 F-1 ≤750·F-2 ≤7,150·F-3·F-4).
