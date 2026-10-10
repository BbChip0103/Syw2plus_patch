# 2026-10-07 | lap1104 | G1 middle — H-UA2 독립 검수 → 수용, G1 사용자 시험 요청

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, source 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1103 work), lap1103 기록, lap1102 §4 사전등록. INBOX 새 지시 없음(구현 우선·묻지 말고 결정·G1 최우선 유지), APPROVALS 새 반려 없음, `loop/STOP` 없음.
- ESCALATE_SOL 처리: 원문을 byte 그대로 `docs/history/laps/20261007_lap1104_preserved_lap1103_escalate_sol.txt`(SHA256 `85310534f41e26fe…7f74`, cmp 일치)에 보존한 뒤 삭제했다. 이번 회차는 마일스톤 사용자 확인 경계라서 root 전달용 새 ESCALATE_SOL을 만든다(§4).
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…a8ac`, stock `_inmm.dll` `03192987…f160` 모두 read-only MATCH.
- fixture: lap1103 UA2-3 비합성 save006(`616b7997…`, index 7) full pair 1회. 활성 8인 증명이 아니다.

## 1. 독립 재계산 (새 스크립트, work 스크립트 재사용·import 없음)

공유 temp `20261007_lap1104_middle_review/`에 두었다.
- `recalc_lap1104.py`(`c24fd4c1…c010`) → `recalc_lap1104.json`(`458970d8…5c16`): 검사 63개.
- `rebuild_lap1104.py`(`ec7dac55…351e`) → `rebuild_lap1104.json`(`b1a73072…3d60`): 검사 5개 + make.

판정 불일치는 **0**이다. 기록 불일치는 2건 나왔는데, 둘 다 판정에 영향이 없다.

| 항목 | 결과 |
|---|---|
| SHA 주장(스테이징 4파일·bridge DLL·source 3파일·로그 2개·원본 EXE) | 일치. 스테이징 디렉터리는 정확히 4파일. run exit 0 |
| **기록 정정 1(전사 오류)** | lap1103 기록 §2·§3에서 스크립트 SHA 두 개가 서로 뒤바뀌어 있었다. 실제 값은 `run_ua2_3.sh` = `9f8602c2…775a7e`, `make_staging.py` = `3ed3ef3a…51154d`이다. 파일 내용(run 명령·staging 생성)은 기록 설명과 맞는다 |
| pair-result(`a92111dd…a714`) | `status` PASS·`scene_state_equal`·input_effect 7/7 true·minimap parity PASS·V2/V2s/V2q/Scale2x 전 tag PASS·loaded PASS. execution_source unchanged이고, 하네스 SHA는 현재 트리 `0f5ab722…`와 같다. 양 lane EXE SHA 4/4·source_unchanged·cleanup ok·game 디렉터리 없음·prefix 프로세스 0. 캡처 12개 SHA 일치. 후보 창 1600×1200 scale 2·hd_source scale2x |
| 후보 `trace_close` FAIL(run_id 불일치)·`mirror_validator` BLOCKED(nearest oracle 0.776) | lap1101 UA1-3과 문자 그대로 같다. `--candidate-no-present-trace`(run_id 없음) 모드에서 예상되는 진단이고 pair gate 밖이다. lap1102가 수용한 상태와 같다 |
| (a) 후보 `drive_c` | `inmm_unit_ticks.jsonl` **없음**. 남은 inmm 파일 9개(present trace 4.38MB·sfx 0.49MB·watch 0.36MB·input 0.12MB·나머지 <50KB). `inmm_stub.log`에 unit_tick 언급 0 |
| (b) baseline `drive_c` | `inmm_unit_ticks.jsonl` 52,784,966 B(≥1MB). env를 넣지 않은 기본 동작이 유지된다 |
| DLL 문자열 | 새 DLL에서 `INMM_STUB_NO_UNIT_TICKS` 1회, lap1101 DLL에서 0회. bridge DLL = 스테이징 DLL |
| `.bat` 2개 vs lap1101 | 각각 `set INMM_STUB_NO_UNIT_TICKS=1` 한 줄만 추가됐고 삭제는 0, CRLF 유지 |
| **기록 정정 2(표현)** | bridge 소스는 트리와 **byte 동일이 아니다**. 차이는 하네스 supply-bridge 변환뿐이다: `inmm_stub.c`에 `supply_probe` 2줄, Makefile SRCS에 `runtime_bridge.c`(`patches/population/`, `923fd1e1…`). bridge 매니페스트의 원본 입력 57개 SHA는 모두 현재 트리와 같다. lap1102 기록과 같은 구조다 |
| **독립 재조립**(트리 복사 → 위 변환을 하나씩 검증한 뒤 적용 → mingw `make`) | 436,267 B. 다른 바이트 6개(136·137·216·217·331780·331781)가 모두 PE의 COFF TimeDateStamp·CheckSum·export/debug TimeDateStamp 안에 있다. 즉 **타임스탬프를 마스크하면 스테이징 DLL과 동일**하다(재빌드 SHA `44799ef0…5f29`) |
| 소스 계약(직접 읽음) | `dump_units_at_tick`에서 env를 `GetEnvironmentVariableA`로 1회 읽어 static 캐시에 둔다. 값이 있으면 `CreateFileA` **전에** return한다. env가 없으면 기존 경로 그대로다. `git diff` 기준 `inmm_stub.c` 변경은 이 8줄뿐이다. 빈 문자열 env는 0을 반환해 꺼진 상태로 취급되고, `.bat` 값 `1`은 켜진다 |

## 2. 공개 UNKNOWN (d) 결정 — 닫음: 애니메이션 위상 차이, opt-out 귀속 근거 없음. 추가 pair 없음

같은 계산으로 lap1099 u0까지 넓혀 보았다.

| 비교 | baseline lane | candidate lane |
|---|---|---|
| menu 1103↔1101↔1099u0 | 0·0 | 0·0 |
| loaded 1103↔1101 / 1101↔1099u0 | **16,633** / 0 | **99,878** / 0 |
| selection 1103↔1101 / 1101↔1099u0 | 0 / **14,966** | **110,882** / 0 |
| production 1103↔1101 / 1101↔1099u0 | 0 / 0 | 42,816 / **36,284** |

- opt-out이 들어가지 않은 run 사이(1099u0↔1101)에서도 baseline selection 14,966 px, 후보 production 36,284 px 차이가 이미 있었다. 그러므로 "lap1099~1101 loaded가 0 px로 일치했다"는 사실은 결정론을 증명하지 않는다. 캡처 tag마다 run 간 변동이 원래 있다.
- 후보 loaded 차이를 시각화했다(`d_loaded_candidate_1103_1101_diff.png` `1b1a5e14…`). 차이는 맵 중앙의 회오리 이펙트 프레임, 좌하단 깃발 애니메이션, 작은 불꽃, 상단 유닛 1곳에 몰려 있다. 32×32 타일 1,850개 중 207개다. 한쪽에만 있는 흑색 픽셀은 268/300으로 대칭에 가깝다. stale 덩어리·흑색 블록·UI 위치 이동은 없다. 같은 pair 안의 loaded gate는 PASS이고, nearest_equal 0.9107로 1101의 0.8941보다 높다. V2s unexplained 60(1101은 31)도 ≤2,000이다.
- 로드 tick은 baseline/후보 기준 1103 24571/24569, 1101 24570/24568, 1099u0 24570/24567이다. 1~3 tick 위상 차가 run마다 있다.
- 결론: (d)는 동적 프레임(이펙트 애니메이션 위상) 차이다. opt-out은 파일 I/O를 없앨 뿐이고, 그 결과 생길 수 있는 타이밍 변화도 run 간 자연 변동과 같은 종류다. 결정론이 없는 상태에서 flag 있음/없음 pair를 1회씩 더 돌려도 원인을 가를 수 없으므로 추가 실행은 하지 않는다. 사용자 시험을 막는 사유가 아니다.

## 3. 판정

- **H-UA2 `PASS(partial, 기술·격리)` 수용.** 기록 정정 2건(스크립트 SHA 뒤바뀜, bridge = 트리 + supply 변환). 제품 마감이나 사용자 합격이 아니다.
- 안내문의 사소한 표현(비차단, 공개만): ① 파일 목록 2번이 아직 "환경변수 3개를 켜고"라고 적혀 있다. 실제 `.bat`은 4개를 설정한다(같은 문서 10행은 4개로 맞게 적혀 있음). ② "이번 개정본(lap1101)" 문구는 C:\ 수리가 들어간 판을 가리키는 과거 표기다. 기능 사실은 틀리지 않으므로 스테이징 SHA를 바꾸지 않고 root 전달문에 적는다.
- 열린 위험(유지·공개): 실제 Windows ACL·`.bat`/DxWnd env 전달 미실행, C:\·`%TEMP%` 동시 실패는 정적 근거만 있음, 실제 Windows 1600×1200 모드·1080p 표시, 사용자 `ddraw.dll`, BGM, G2/G5/G6G7 EXE 조합 미측정. 명시 잔여(P6 로고·GDI 글자·반투명 일부)와 HUD/전체 HD coverage·두 번째 장면은 남는다.

## 4. 사용자 시험 요청·root 전달

- APPROVALS에 **G1 사용자 시험 요청(lap1104)**을 올린다. 마일스톤 사용자 확인이다. 모델 기술 수용은 사용자 합격이 아니다.
- 스테이징은 공유 temp `20261007_lap1103_work_hua2/user_test_staging/`의 4파일이다(DLL `94213374…`, direct `.bat` `2da323e8…`, dxwnd `.bat` `29a35d2e…`, 안내문 `97f4bd75…`). `260921_temp` 배치는 사용자 폴더라서 root가 한다.
- `loop/ESCALATE_SOL`(root 전달)을 만든다. 사용자 판단은 비차단이고, 루프는 G1 독립 작업을 계속한다.

## 5. 검사

- 기록을 freeze한 뒤 `checks/safety.sh check`·`checks/context_limits.py`·focused G1 테스트(`tests/test_g1_mirror2x.py` 등)를 돌린다. 결과는 STATUS에만 쓴다.
- 전체 `make check`는 SKIP한다. 이번 변경은 문서뿐이고, source·하네스·테스트 SHA는 lap1103 full PASS(1698) 때와 같다(§1 SHA 일치).

## 다음 한 가지

사용자 시험은 대기하지만 루프를 막지 않는다. 다음 루프 회차는 middle(Opus)이다.
- 할 일: G1 남은 항목 중 다음 work 가설 하나를 사전등록한다.
- 우선순위: HUD/GDI·전체 HD coverage ≥90% 측정 또는 두 번째 장면 중 하나를 STATUS backlog에서 고른다.
- 기준: 측정식을 먼저 정한다.
- 사용자 시험 결과가 들어오면 그것을 최우선으로 처리한다.
