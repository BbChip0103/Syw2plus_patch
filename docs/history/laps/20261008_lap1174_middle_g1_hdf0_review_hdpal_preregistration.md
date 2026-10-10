# 2026-10-08 | lap1174 | G1 middle — H-HDF0 독립 검수 · H-HDPAL(화면 팔레트별 HD 팩) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / middle(중간 계획·컨펌). 게임 실행 0, 게임 DLL·EXE·하네스·C·도구·테스트 source 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1173 work → middle). 원문 byte 일치 보존 `docs/history/laps/20261008_lap1174_preserved_lap1173_escalate_sol.txt`(SHA256 `3dbd75c6f7c795ee…`), 보존 뒤 삭제. `loop/STOP` 없음, INBOX·APPROVALS 새 지시·반려·사용자 G1 시험 결과 없음.
- **디스크: 여유 3.1 GB**(lap1173 종료 4.2 GB → 이 회차 시작 3.1 GB; 이 회차는 게임 실행 0, 공유 temp에 스크립트·JSON 수 KB만 씀. 줄어든 1.1 GB의 출처는 이 회차가 확인하지 않았다 — 같은 디스크를 쓰는 다른 프로세스/루프 가능성). run 1회분(≈5 GB) 미만 → §6 디스크 조건·root 보고(ESCALATE_SOL).
- 목표: G1 — INBOX 2026-10-07 19:3x HD 그림 경로 ⑤ 검수. H-HDPAL은 ⑤ 안의 결함 수리이며 DESIGN 마일스톤 경계가 아니다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH. 원본 그림은 읽기만.
- 후보 source(uncommitted) SHA256 앞 16자 8개 = work 기록과 일치(`g1_hd_asset.c` `fdeb20ff9fa19756`·`.h` `9695ff2289d19f03`·`g1_hd_pack.h` `f30559b696bbae1d`·`g1_mirror2x.c` `d9b67b5fb495c66a`·`direct_draw_trace.c` `6c68b3054e624146`·`g1_hd_convert.py` `d84706e1a8143a53`·`test_g1_hd_pack.py` `2aaf0bd83167024b`·`test_g1_hd_convert.py` `185bb07097fc2cf3`). lap1173 full check 로그(exit 0, 1931 passed·5 skipped, CONTEXT_PASS) 뒤 바뀐 tools·tests·patches·checks·Makefile 0(`find -newer`).

## 1. 독립 재계산 (work `scripts/`·`metrics_*.json` 미사용)

공유 temp `20261008_lap1174_middle_review/`: `recalc_hdf0.py`(`a866ebe8bc40fad2…`)→`recalc_hdf0.json`(`3ad949f70c93b593…`). 원본 raw `.spr` 직접 읽기, 팩 파일 직접 해석, `trace_raw.jsonl` 상태별 집계, 캡처 직접 비교, 키 로그 digest를 원본 `TitelMainButton_plus.Spr` 전 오프셋 FNV-1a(128 B) 스캔 + 저장소 추출기 RLE 행 디코더로 1x 유도.

| 항목 | work 값 | 재계산 | 판정 |
|---|---|---|---|
| `yfnt/title.spr` 전 바이트 FNV-1a | 1777000796, 헤더 0xBF4, 0xFE 0 | 헤더 = 파일 크기 − 480,000 = 3,060(0xBF4), FNV **1777000796**, 0xFE 0 | 일치 |
| PS5·PS7 hash | 269350933 = `titlelobby.spr`·3908910012 = `titleprotocol.spr` | 같은 값, trace PS5 733/733·PS7 159/159 present의 `menu_copy_hash_last`와 일치 | 일치 |
| 팩 이름·크기·키 | `f69eae15c_800x600.idx8`, 1,920,000 B, sha `3da00c8c…` | hex(1777000796) = `69eae15c`, 1,920,000 B, sha 같음, 0xFE 0, `pack_cf` 사본 byte 동일 | 일치 |
| 팩 충실도(새) | — | 2×2 평균 vs 1x: `title_plus.PAL` 기준 **1.91**, `imjin2.pal` 기준 15.76 → 팩은 타이틀 팔레트로 올바르게 양자화 | 새 확인 |
| `title.spr` = baseline PS9 화면 | 90.08% | 90.08% | 일치 |
| F1 PS9 | 72 present, fs 72/1/0/0, menu 72·변화 0, HD 100, p95 14 | 같은 값 | 일치 |
| OFF1 PS9 | 68, 0/0/0/0, HD 100, p95 13 | 같은 값(p95 13.65 → 13은 반올림 차) | 일치 |
| G1 PS9·PS3 | 70, 70/1/0/0, HD 100, p95 14; PS3 1,536 HD min 99.948·p95 7 | 같은 값, 안전 7종 0·fallback 0·dropped 0 | 일치 |
| G1 miss 892 | PS7 159 + PS5 733 | PS7 끝 159·PS5 끝 892(누적), reject 0, PS5·PS7 hash 각각 1개(변화 없음) | 일치 |
| F1 PS3 | 881, HD min 99.261, p95 7 | 같은 값 | 일치 |
| 캡처 2×2 평균 차 | 위쪽 F1 2.51·OFF1 0.78, 버튼 F1 0.38, G1 버튼 11.05(>16 25.4%), 비균일 0.424/0.224 | 2.513·0.783·0.380·11.053(0.2541)·0.4241/0.224 | 일치 |
| 버튼 팔레트 귀속 | `TitelMainButton_plus` 3프레임, imjin2 4.76/5.08/5.89 vs title_plus 19.46/21.39/15.13 | digest `a83c4e8f`·`1f48ec5a`·`dc851d30` 모두 원본 파일 안 오프셋 발견, 독립 디코드 1x 대비 imjin2 **4.76/5.08/5.89** vs title_plus **19.46/21.39/15.13** | 일치 |

## 2. 코드 검토 (`g1_hd_asset_fullscreen_frame`·`transfer_block_copy_to_screen` 800×600 분기·`g1_hd_pack_format_name`)

1. **덮어쓰기 위치:** 팩 덮어쓰기는 기존 Scale2x `g1_frame_copy_apply`(coverage·expected 갱신) 뒤 `g_mirror`만 바꾼다. `g1_frame_copy_accepts`가 800×600을 (0,0)에서만 받으므로 행 0부터 1600×1200 전체를 쓰는 것이 맞다. 같은 present 안 뒤 writer(버튼·로고)는 그 위에 그린다(G1 버튼이 팩 위에 보이는 것으로 실측). 결함 없음.
2. **부분 복사 혼재 위험 확인:** 같은 원본에서 일부 사각형만 다시 복사하면(Scale2x 조각) HD 그림 안에 이음매가 생길 수 있다 → F1·G1 PS9·PS7·PS5 `partial_copy_calls` 0(매 present 전체 복사). 이번 장면 위험 없음.
3. **로더:** 크기 정확 일치·키 색 0xFE 한 바이트라도 있으면 reject·마지막 hit 1장 캐시·miss/reject 이름 8개 기억. PS5·PS7은 hash가 각각 1개로 고정이라 8슬롯 한계에 닿지 않는다(G1 실측). 공개(경미): 서로 다른 전체 화면 hash가 8개를 넘으면 9번째부터는 present마다 `CreateFileA` 재시도(성능), HeapAlloc 실패도 영구 reject로 기억, 두 팩 그림을 번갈아 보이면 전환마다 1.92 MB 재적재. 이번 범위 영향 0, 기록만.
4. **이름:** `g1_hd_pack_format_name`은 prefix만 다르고 `h` 경로 동작 불변(테스트 102 passed, 이 회차 실행).

## 3. 크롭 직접 열람

`F1_face`: 얼굴·투구 윤곽·밝기 동일, 질감만 부드러움. `G1_buttons`: 아래(후보) 버튼 8개 테두리·바탕에 빨강·노랑 잡음 — 글자는 읽히나 명백한 가시 결함, work 서술과 같다.

## 4. 판정

**H-HDF0 `PASS(partial, 기술·격리)` 수용.** 판정 영향 불일치 0. 정정 0·공개 4:
1. (공개·결함) **HD 팩 프레임은 그림이 실제로 표시되는 화면 팔레트로 양자화돼야 한다.** `pack_c`(lap1169)는 전부 `imjin2.pal`로 만들어져 타이틀(`title_plus.PAL`) 버튼이 변색한다. PS5 배경 = `titlelobby.spr`가 `titlelobby_plus.PAL`로 baseline과 88.25% 일치(새 확인)이므로 PS5도 다른 팔레트, PS7 = `titleprotocol.spr`는 `title_plus`·`titlelobby_plus` 모두 불일치(0.3%·7.4%) → PS7 팔레트 미확인. G1 PS7·PS5 캡처 평균 차 0.81·0.67(끔 대조 없음 → 변색 여부 UNKNOWN). 로고 키 `6ab9f5ec`(546×178)도 G1에서 hit했지만 PS9 로고 영역 차는 F1과 같음(2.947) → 표시 화면 미확인. **팩을 기본 켬·사용자 전달하기 전 필수 수리 → work H-HDPAL(§6).** PS3 imjin2 화면의 lap1167~1171 합격은 유효.
2. (공개) PS9 p95 ≤9 사전등록 기준은 이 하네스 PS9에서 팩 없이도 13~14라 판별력 없음 → 켬/끔 대조(14 vs 13.65)로 대체 수용.
3. (공개) 로더 경미 사항(§2-3).
4. (공개) 화질 평가 아님(바이큐빅 stand-in), 1장만, 기본 켬·전달 아님.

## 5. 다음 선택 근거

- ⑤ 확장(PS5 `titlelobby`·PS7 `titleprotocol`·브리핑)은 모두 타이틀 외 팔레트 화면이고, 이미 있는 `pack_c`도 그 화면들에서 hit한다. 팔레트 정체 없이 팩을 늘리면 변색이 퍼진다 → **H-HDPAL을 ⑤ 확장·⑥보다 먼저.**
- 엔진에서 팔레트를 읽을 곳: stub은 `IDirectDrawPalette::SetEntries`를 후킹하지 않고, 렌더러 `+0x419A0`(768 B, H-HDS1이 음영 계산에 사용, PS3 자기 검사 불일치 0) 하나뿐이다. 이 값이 타이틀 화면에서도 화면 팔레트를 따라가는지는 미확인 → HP-0에서 먼저 확인.
- 게임 안 팔레트 교체(`night1~4.pal`) 가능성: 같은 색인 의미의 어두운 판이면 imjin2 팩이 그대로 맞으므로, 엄격한 팔레트 일치만 쓰면 HD가 꺼질 수 있다 → 디렉터리 하드링크로 명시 허용(디스크 0).

## 6. 다음 work 사전등록(Sonnet) — H-HDPAL: HD 팩을 화면 팔레트별로 분리

**가설.** 그림이 표시되는 순간의 화면 팔레트(768 B)를 엔진이 읽어 digest `pal8`로 만들 수 있고, 팩을 `<pack>\<pal8>\<이름>`으로 나누면 다른 팔레트 화면에서는 팩이 miss → Scale2x로 떨어져 변색이 사라지고, 같은 팔레트 화면의 HD 적용(PS3 지형·tinted·음영, PS9 타이틀)은 그대로 유지된다.

**단계.**
- HP-S(정적, 디스크 무관): 원본 EXE에서 렌더러 `+0x419A0` 팔레트를 쓰는 곳과 `IDirectDrawPalette::SetEntries`/`CreatePalette` 호출 지점을 objdump로 찾아, 타이틀(`title_plus`)·대기실(`titlelobby_plus`)·인게임(`imjin2`) 팔레트 적재가 `+0x419A0`에 반영되는지 판정. 반영되면 소스 = `+0x419A0`, 아니면 소스 = SetEntries 후킹(마지막으로 primary 팔레트에 넣은 256 항목).
- HP-0(옵트인 진단, run 필요): 키 로그와 fullscreen 조회에 `pal` = 선택한 소스 768 B의 FNV-1a 8자리를 추가(기본 끔 env 또는 기존 키 로그 env에만). NG5 1 run(PS9→PS7→PS5→PS3)으로 상태별 `pal` 고유값과 present 수를 세고, 오프라인으로 `pal/*.pal`(×4 정규화, 엔진 형식 확인)과 대조해 PS9=`title_plus`·PS5=`titlelobby_plus`·PS3=`imjin2` 확인, PS7·로고 표시 화면 팔레트 식별. PS3 안에서 `pal`이 바뀌면 그 값들 기록.
- HP-1(수리): ① 엔진: A/B·지형·tinted·음영 키의 팩 조회와 `fullscreen` 조회 경로를 `<pack>\<pal8>\<이름>`으로 바꾼다(`pal8`은 키 생성/조회 시점 값, 키 동일성에 포함 → 팔레트가 바뀌면 다른 키). 루트 직속 이름은 더 이상 읽지 않는다(조용한 변색 경로 제거). 끔 env 없음(안전 쪽 기본). trace `hd_pack_pal_misses`(팔레트 디렉터리 없음 수)·키 로그 `pal`. ② 도구: `pack`·`fullscreen`에 `--pal <파일>` 필수화, 출력 `<out>/<pal8>/`(pal8은 HP-0에서 확인한 엔진 형식으로 계산). ③ 기존 팩 이전: `pack_c`를 새로 만들지 말고 `<pack>/<imjin2 pal8>/`로 **하드링크**(디스크 0), 타이틀 f 파일은 `<title_plus pal8>/`. 버튼 등 타이틀 화면용 프레임은 이번에 다시 만들지 않는다(miss → Scale2x가 정답).
- 테스트: 호스트 테스트로 pal 디렉터리 조회·다른 pal miss·루트 직속 이름 무시·도구 `--pal` 필수/pal8 계산(RED→GREEN, 변이 확인 1개 이상).

**측정식(합격).**
- HP-S/HP-0: 팔레트 소스 1개 확정, PS9·PS5·PS3 `pal` = 각각 `title_plus`·`titlelobby_plus`·`imjin2`(불일치면 그 사실과 실제 값 기록 → 판정 `BLOCKED` 또는 소스 교체 1회).
- HP-1 run(합본 팩 = `<imjin2>/pack_c` 하드링크 + `<title_plus>/f69eae15c…`): NG5 1 run + save006 pair 1 run. PS9 버튼 영역 2×2 평균 차 ≤ 1.0(F1 0.38 수준, 지금 G1 11.05), PS9 fullscreen hits = menu 호출 수·rejects 0, PS3 HD min ≥ 99.9·tinted/음영/지형 matched hit 비율 lap1171 S2 수준(±2%p)·안전 7종·fallback·dropped 0, 팔레트 소스 진단 크래시 0.
- 원본 보호: 원본 EXE·그림 SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존.
- **디스크(필수):** 시작 전 `df`. **여유 5 GB 미만이면 run(HP-0·HP-1 run)을 시작하지 말고** HP-S와 HP-1 ①②의 코드·호스트 테스트까지만 하고(엔진 경로는 팔레트 소스를 HP-S로 확정한 경우에만, 미확정이면 도구·테스트만) `BLOCKED(디스크)`로 기록·ESCALATE_SOL(root). 다른 회차 산출물·원본·공유 raw 삭제 금지, 자기 회차 game 사본만 정리.
- **비목표:** 새 HD 그림 제작(PS5/PS7 전면·버튼 title 팔레트판), ⑥ 유닛, H-HDS1r, tinted 클립 판정, 기본 켬·사용자 전달, 화질 평가.
- **중단:** 실패 가설 2회 또는 60분(가능성). 커밋·원본/참고 쓰기 금지. 산출물 공유 temp `<날짜>_lap<N>_work_hdpal/`. 끝나면 lap 기록 → `make lint`·`typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).
- **그다음:** H-HDPAL 수용 뒤 ⑤ 확장(PS5 `titlelobby`·PS7 `titleprotocol` 전면 그림을 각 화면 팔레트로), 그 뒤 ⑥ 유닛 경로. backlog: H-HDS1r(필수), 로더 miss 슬롯 8 한계·reject 영구 기억(§2-3), tinted 클립 판정, lap1172 backlog 유지.

## 7. 검사

- focused `tests/test_g1_hd_pack.py`·`test_g1_hd_convert.py`·`test_g1_mirror2x.py` **102 passed/4.23s**(로그 `logs/gates/lap1174-middle-focused.log` `0f3fa03b86e6d91c…`). `checks/safety.sh check`·CONTEXT 결과는 STATUS 검증 줄에 보강한다.
- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. tools·tests·C source는 lap1173 full PASS(1931 passed) 그대로다.

## 다음 행동

root: 디스크 여유 3.1 GB(<5 GB) 확보(ESCALATE_SOL). work(Sonnet) H-HDPAL(§6) — 디스크 미확보면 HP-S·코드·호스트 테스트까지만. 사용자 G1 시험 결과가 오면 최우선.
