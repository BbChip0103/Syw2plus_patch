# 2026-10-08 | lap1172 | G1 middle — H-HDS1 독립 검수 · H-HDF0(⑤ 전체 화면 그림 HD 자리) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / middle(중간 계획·컨펌). 게임 실행 0, 게임 DLL·EXE·하네스·C·도구·테스트 source 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1171 work → middle). 원문 byte 일치 보존 `docs/history/laps/20261008_lap1172_preserved_lap1171_escalate_sol.txt`(SHA256 `bedc6a8e8a70a468…`), 보존 뒤 삭제. `loop/STOP` 없음, INBOX·APPROVALS 새 지시·반려·사용자 G1 시험 결과 없음.
- 디스크: 여유 **5.8 GB**(lap1171 종료 7.1 GB → 이 회차 시작 5.8 GB, 이 회차는 게임 실행 0·공유 temp 스크립트/JSON 수 KB만 씀). 20 GB 규칙 미달이며 run 1회(게임 사본 약 2.7 GB + prefix 약 1.2 GB)도 빠듯하다 → §7 디스크 조건.
- 목표: G1 — INBOX 2026-10-07 19:3x HD 그림 경로 ④-4 검수, ⑤ 사전등록. ESCALATE_SOL의 "다음 ⑤/⑥ 사전등록"은 HD 그림 경로 하위 단계 전환이고 DESIGN 마일스톤 경계가 아니다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH. 원본 그림은 읽기만.
- 후보 source(uncommitted): `tools/inmm_stub/g1_hd_asset.c` `83a340e5aef6bc30`·`g1_hd_asset.h` `1934612c33e3148a`·`direct_draw_trace.c` `12a9ad7894091bd3`·`tests/test_g1_hd_pack.py` `e0c2d4734f384fc0` = work 기록과 일치. lap1171 full check 로그(`6d72ffa1e33e…`, exit 0, 1920 passed·5 skipped) 뒤 바뀐 tools·tests·patches·checks·Makefile 0(`find -newer`).

## 1. 독립 재계산 (work `scripts/`·`metrics_*.json` 미사용)

공유 temp `20261008_lap1172_middle_review/`: `recalc_hds1.py`(`356b8d7b54ab9c45…`)→`recalc_hds1.json`(`01919248dc5d3473…`). 키 로그·`trace_raw.jsonl` 직접 집계, 원본 `.ytl`을 파일 전 오프셋 FNV-1a(128 B) 스캔 + 새 행 디코더(`<skip, count, count 화소>`)로 1x 불투명 유도 → `pack_c` 2×2 블록·키 로그 `selfcheck`와 비교, S2·OFF1·S1 캡처로 같은 장면 밝기 대조.

| 항목 | work 값 | 재계산 | 판정 |
|---|---|---|---|
| 키 결과 S1/S2/OFF1 | hits 501/529/348·miss 38/57/31·reject 2/0/2·skip 0/0/159 | 키 로그 결과 줄 = trace 카운터 같은 값(S1 hit 156+lut 195+shade 150=501) | 일치 |
| shade hits·rejects(사유 5종) | 150/191/0, 0 | 같은 값, 사유별 0 | 일치 |
| selfcheck 화소·multi 키·LUT bytes | 153,600/193,536·149/190·1,209,600/1,559,296 | 같은 값(키 로그 합 = trace) | 일치 |
| writer별 matched hit | 음영 84/84·66/66, 90/90·101/101, OFF1 0/82·0/63 | 같은 값. tinted S1 `0x466540` 136/136·`0x466EA0` 59/61(=0.990 합산), A/B·지형 100% | 일치 |
| PS3 HD min·안전 7종·fallback·dropped·`identity_invalid_sources` | 99.947/100/99.946, 0 | 전체 PS3 present 1,535/1,535/1,534: 같은 값, 0 | 일치 |
| PS3 p95 | 8/7/8(창별 최대) | 전체 PS3 기준 7/7/7 | 정의 차(lap1166·1170과 같음), 모두 ≤9 |
| 음영 키 실루엣 | (work: 팩 대응 수치) | 켬 run 고유 shade_hit 키 **108개 전부** 독립 디코드 1x 불투명 = 팩 2×2 블록 | 새 확인 |
| 자기 검사 범위 | 키당 `selfcheck`(예 1,024) | 108/108 키에서 키 로그 `selfcheck` = 독립 디코드 1x 불투명 화소 수(`0x468CC0` 46·`0x4690A0` 62) → 자기 검사가 모든 불투명 화소를 실제로 비교했다 | 새 확인 |
| slots | 예 30~31 | 범위 1~46(64 상한 미만) | 공개 |
| identity refresh | (미기록) | 3 run 모두 `identity_cache_refreshes` 0 | 새 확인(§2-③) |

**같은 장면 밝기(새 지표, 게임 화면 y<480):** 후보 2×2 평균 휘도 − baseline 1x 휘도를 baseline 밝기 구간별로 보면, 음영·안개가 있는 어두운 구간(휘도 1~40)에서 S2 +1.92/+1.73(ps3_start/act), 음영 끔 대조 OFF1(음영 키 = 원본 Scale2x) +2.26/+2.67로 같은 수준이다. 팩을 음영 없이 붙였다면 이 구간이 크게 밝아져야 한다 → 음영 유지의 정량 근거. 8 px 블록 평균 차는 S2 0.78/2.81·OFF1 2.45/2.16(work 0.86/3.11·2.66/2.38과 정의 차 — 휘도 vs RGB, 순서 같음). S1은 22.0/23.7로 lane 맵 불일치(work 제외 판단 확인).

## 2. 코드 검토 (`capture_shade`·`shade_prepare`·`shade_apply`·`build_hd_frame`)

1. **표 읽기 범위·경계:** 음영표 검사 64×64×2 = 8,192 B, 최대 인덱스 `((63<<6)+63)·2+1` = 8,191; 역표 262,144 B, 최대 `(63<<12)+(63<<6)+63` = 262,143; 팔레트 768 B. 성분 ≥64·T 값 ≥64·`s` ≥64는 range reject → 범위 밖 읽기 없음. 결함 없음.
2. **크기 일치:** `capture_shade`는 `key->width/height`로 RLE를 검사하고 `shade_prepare`는 `identity_width/height`로 다시 걷는다. `g1_mirror2x.c` 두 bind 호출(3217·3250줄)이 begin과 같은 `width, height`를 넘기므로 같다(108/108 selfcheck = 1x 불투명이 실측 확인). 결함 없음.
3. **클립판 identity 가정(`0x4690A0`):** identity는 전체 viewport 재호출(3217줄 경로)이고, `identity_written`이 0인 화소는 검사에서 빠진다. 62개 클립판 키 전부 selfcheck = 전체 1x 불투명 → 클립 없이 비교됨. `s` 인덱싱이 원본과 달랐다면 다단계(`slots`>1) 키에서 불일치가 났어야 하는데 0 → 인덱싱 실측 확인.
4. **[공개·잠재 결함] 표 변경 뒤 낡은 LUT 재적용:** 키 동일성에 source digest·aux(음영 지도) digest는 들어가지만 renderer 표는 안 들어간다. 표가 바뀌면 같은 키의 1x 출력이 달라져 `g1_hd_asset_compare_visible_frame_in_viewport`가 identity를 비우고(refresh) 새 identity로 `build_hd_frame`을 다시 부르는데, 이때 `pack_state == HIT`라 `shade_prepare`(자기 검사)는 다시 돌지 않고(`shade_src`도 이미 해제) **옛 LUT를 새 프레임에 적용**한다. 즉 "감지 UNKNOWN"(work 공개 (d))은 정정: 감지 신호는 이미 있다 — 음영 HIT 키의 refresh = 표 변경(이 writer는 목적지를 읽지 않으므로 다른 원인 없음). 이번 3 run은 refresh 0이라 실제 영향 0. 수리(최소): refresh된 음영 HIT 키는 `PACK_SHADE_REJECT`(Scale2x)로 내리거나, `shade_src`를 유지해 `PACK_UNTRIED`로 되돌려 새 표로 재준비·재검사. **팩 음영을 기본 켬·사용자 전달하기 전 필수 backlog**(H-HDS1r).
5. **경미:** 팩 miss·실루엣 reject 키는 `shade_src`(키당 수 KB)를 키 퇴출 때까지 들고 있다(해제는 HIT 경로에서만). 메모리 영향 작음(miss 음영 키 ≤11개), 기록만.
6. 끔 env·checker `0x468E10` → `skip_aux`, 팩 env 없으면 무변화(기본 켬 사용자 판 동작 불변) 확인. 테스트 46 passed(이 회차 실행).

## 3. 크롭 직접 열람

`S2_fog_R`: 밭 작물과 오른쪽 어두운 안개 그라디언트 경계 위치·밝기 단계 동일, 평탄하게 밝아진 곳 없음. `S2_edge_TL`: 지도 가장자리 검은 영역과 회색 돌 지형 경계·나무 위치 동일. `S2_mid`: 건물·돌 지형·밭 경계 동일, 돌 지형 밝기 유지. 질감만 부드러움(바이큐빅 stand-in), 1x 칸 격자 계단 미관측. work 서술과 같다.

## 4. 판정

**H-HDS1 `PASS(partial, 기술·격리)` 수용.** 판정 영향 불일치 0. 정정 1·공개 4:
1. (정정) 표 변경 "감지 UNKNOWN" → 감지 신호(음영 HIT 키 identity refresh)는 있으나 코드가 쓰지 않아 낡은 LUT를 재적용한다(§2-4). 이번 run refresh 0 → 판정 영향 없음, 수리 backlog H-HDS1r(기본 켬·전달 전 필수).
2. (공개) p95 8/7/8은 창별 최대, 전체 PS3 기준 7/7/7.
3. (공개) 켬/끔 같은 맵 직접 쌍 없음 — 대신 같은 장면 밝기 구간 비교(§1)로 음영 유지를 정량 확인.
4. (공개) miss 음영 키 `shade_src` 보유(§2-5).
5. (공개) 화질 평가 아님(바이큐빅 stand-in), 기본 켬·전달 아님, checker `0x468E10`·tinted 클립 판정(lap1170 §3)은 backlog 그대로.

## 5. ⑤ 선택 근거 (이번 회차, 정적·오프라인)

- INBOX 19:3x 순서상 ④ 다음은 ⑤ 전체 화면(800×600) HD 자리, 그다음 ⑥ 유닛 경로.
- lap1157 추출 manifest: 800×600 전체 화면 그림은 **raw(비압축) `.spr`**다 — `fnt/launchscreen_plus.spr`(타이틀), `ybriefingfnt/C01/c01*.Spr` 등(브리핑), `BattleSpr/Back.Spr`, `Online/GameSpr/SelectChar.Spr` 등. 큰 RLE는 `Online/VillageBack/*_back.spr` 일부뿐(Online은 이 판 경로 아님).
- 현재 팩 `pack_c`(digest 이름 92,842)에는 RLE 프레임만 있고 raw 800×600 프레임은 없다(400×300 이상 이름 73개 중 800×600은 `Online/VillageBack/Market_Back.Spr` 하나). lap1171 NG5 키 로그에도 400×300 이상 키는 타이틀 로고 `fnt/launchscreen.spr` 546×178 하나뿐 → **raw 전체 화면 그림은 현재 키 경로(A/B·지형·tinted·음영 writer) 밖**이다. 화면 도달 경로(소프트웨어 복사 vs DirectDraw 서피스 BltFast)는 미확인(lap1148 정적: PS20 브리핑 프레임은 `0x4B23B5`→`0x4D4620`이 뒤 버퍼에 BltFast/Blt).
- 따라서 ⑤의 첫 work는 **경로 귀속 + 가능성 판정**이고, `FEASIBLE`이면 같은 회차에 그림 1장(타이틀) 최소 적용까지 간다.

## 6. 다음 work 사전등록(Sonnet) — H-HDF0: ⑤ 전체 화면 raw 그림 경로 귀속 → 조건부 1장 적용

**가설.** raw 800×600 `.spr` 전체 화면 그림(타이틀 `fnt/launchscreen_plus.spr`, 브리핑 `ybriefingfnt/…`)은 원본에서 한 지점(소프트웨어 복사 writer 또는 오프스크린 서피스 → 뒤 버퍼 BltFast)으로 화면에 오르고, 그 지점에서 1x 픽셀이 읽히며 원본 파일 프레임과 digest로 대응된다. 그러면 기존 팩 이름 규칙 `h<digest>_<w>x<h>.idx8`로 HD 프레임을 찾아 그 영역의 미러(현재 Scale2x)를 대체할 수 있다.

**단계.**
- F-0(오프라인): manifest의 raw 프레임 중 fw×fh ≥ 640×480 목록, 각 프레임 픽셀 시작 128 B FNV-1a digest와 충돌 여부 기록(공유 temp JSON). 같은 digest가 둘 이상이면 해당 그림은 대상에서 빼고 기록.
- F-1(런타임 귀속, 옵트인 진단만): 기존 하네스로 PS9 타이틀(`--title-button` 없이 정착) + PS20 브리핑(`--scenario-start --scenario-play --scenario-briefing-dwell`)을 격리 실행하고, 기존 screen watch/census/ddraw 호출 표(`--screen-watch-state 9|20`, `--census-state`, lap1119 ddraw 표)로 **전체 화면의 50% 이상을 덮는 쓰기**의 EIP/ddraw 호출·원본 서피스·크기를 귀속한다. 그 지점의 1x 원본 픽셀(서피스 Lock 또는 writer 인자) 시작 128 B digest가 F-0과 일치하는지 확인(필요한 최소 진단 C 추가 허용, 기본 끔 env).
- 판정: 타이틀 또는 브리핑 중 1장 이상이 "귀속 지점 확정 + digest 일치 + 후보 미러가 그 영역을 어디서 만드는지(어느 hook 경로) 확인"이면 **`FEASIBLE`**, 지점이 wined3d 내부 등 읽을 수 없는 곳뿐이면 `BLOCKED`(근거·대안 기록), digest 불일치(가공된 그림)면 `NOT_FEASIBLE`(가공 내용 기록).
- F-2(`FEASIBLE`이고 60분 안일 때만, 그림 1장 = 타이틀 우선): `g1_hd_convert.py pack`이 raw 프레임에도 같은 이름 규칙으로 HD 파일(바이큐빅 stand-in, 가장자리 복제 규칙)을 쓰게 하고, 귀속 지점의 미러에서 팩 HIT면 Scale2x 대신 팩 프레임을 쓰는 최소 C(끔 env `SYW2_G1_HD_PACK_FULLSCREEN=0`, 팩 env 없으면 무변화). 자기 검사: 팩 프레임 2×2 블록 대표값이 아니라 **1x 원본 digest 일치 + 크기 2w×2h 정확**만 요구(불투명 전면이라 실루엣 없음). trace `hd_pack_fullscreen_hits/misses`.
- 테스트(F-2 시): 호스트 테스트로 raw 이름 규칙·끔 env·miss 폴백·trace 필드(RED→GREEN, 변이 확인 1개 이상).

**측정식.**
- F-0: 대상 raw 프레임 수·digest 고유율 기록.
- F-1: PS9·PS20 각각 귀속 결과(EIP/ddraw 호출·서피스·크기·digest 일치 여부)와 판정 1개.
- F-2 합격(실행 시): 켬 2 run 크래시·안전 7종·fallback·dropped 0, 해당 PS HD min ≥ 같은 하네스 끔 대조 run 값(참고: lap1149 PS20 켬 100)·p95 ≤ 9, `fullscreen_hits` ≥ 1(대상 그림), 끔 대조 1 run에서 hits 0·이전 화면과 같음, 크롭(공유 temp) 한 장에서 그림 위치·구도 baseline과 같음(질감만 다름). NG5 PS3 비회귀(HD min ≥ 99.9·안전 0) 1 run.
- **디스크:** 시작 여유 5.8 GB(<20 GB). 실행 전 여유를 재고, **run 1회분(게임 사본 약 2.7 GB + prefix 약 1.2 GB + 여유 1 GB ≈ 5 GB) 미만이면 시작하지 말고 `BLOCKED(디스크)`로 기록·ESCALATE_SOL로 root 보고**(다른 회차 산출물·원본·공유 raw 삭제 금지, 자기 회차 game 사본만 정리). run은 순차 1개씩, 각 run 직후 game 사본 삭제 확인.
- 원본 보호: 원본 EXE·그림 SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존.
- **비목표:** ⑥ 유닛 경로, 다른 raw 그림 전부, Online 경로, H-HDS1r(§2-4)·tinted 클립 판정 수리, 기본 켬·사용자 전달, 화질 평가, 팩 저장소 반입.
- **중단:** 실패 가설 2회 또는 60분(가능성 조사 기준). 커밋·원본/참고 쓰기 금지. 산출물 공유 temp `<날짜>_lap<N>_work_hdf0/`. 끝나면 lap 기록 → (C·테스트 변경 시) `make lint`·`typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).
- **그다음:** F 결과에 따라 ⑤ 확장(브리핑·기타 raw) 또는 ⑥ 유닛 경로(`0x466B50`/`0x466BE0` 키 경로화 + 메모리 대책). backlog: **H-HDS1r(음영 키 refresh 시 재검사, 기본 켬·전달 전 필수)**, tinted 클립 판정(lap1170 §3), 상수 이름 정정, miss 음영 키 `shade_src` 해제, normal 테마 장면, `ytl_narrow` 828, 충돌 이름 처리, writer 허용 목록 일반화, lap1166 backlog 유지.

## 7. 검사

- `checks/safety.sh check`·CONTEXT·focused 결과는 STATUS 검증 줄에 보강한다. focused `tests/test_g1_hd_pack.py`·`tests/test_g1_hd_convert.py` 46 passed(로그 `logs/gates/lap1172-middle-focused.log`).
- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. tools·tests·C source는 lap1171 full PASS(1920 passed) 그대로다.

## 다음 행동

work(Sonnet) H-HDF0(§6). 디스크 여유가 run 1회분 미만이면 시작하지 말고 root 보고. 사용자 G1 시험 결과가 오면 최우선이다.
