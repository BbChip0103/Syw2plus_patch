# 2026-10-09 | lap 1203 | G1 middle — H-HDA0 검수 · HD 그림 경로 마일스톤 경계(root 전달) · 디스크

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / 중간 계획·컨펌(middle). 게임 run 0·C/tools/tests 변경 0·커밋 0.
- 입력: lap1202 work `loop/ESCALATE_SOL`(원문 byte 일치 보존 `docs/history/laps/20261009_lap1203_preserved_lap1202_escalate_sol.txt` `87fa28a041b8a787`, 보존 뒤 삭제). `loop/STOP` 없음. INBOX·APPROVALS에 새 지시·반려·사용자 G1 시험 결과 없음. `loop/.lap_counter` = 1203.
- 가설: lap1202 `pack_all`은 현재 도구 규약(확장 이름)을 지키고, 효과·로고 덮어쓰기가 충돌 이름 조회를 깨지 않으며, A1·PA 수치는 raw에서 그대로 재현된다.
- 측정식(사전 기록): manifest 전 파일 재계산 불일치 0, `.amb` 657개 = 범위 129..65536·기본 이름 0·확장 이름 L 일치, 덮어쓰기 뒤 확장 마커 L 불변, 키 로그 재분류(마커 stem 기본 이름 hit 0), trace 재계산 = work 수치, pair 상태 leaf 차이 = work 보고, 실행 DLL = 현재 소스 재빌드(타임스탬프류 외 동일).
- 새 스크립트·결과: 공유 temp `20261009_lap1203_middle_review/` — `recalc_pack.py`(`db74356d34ccd160`)·`recalc_keys.py`(`c45056512c728bfb`)·`recalc_pair.py`(`f70c5a498eb50bbf`)·`recalc_trace.py`(`cde3eec86b86c5eb`), 결과 json 4개(`recalc_pack.json` `82d4f76dcc539266`·`recalc_keys.json` `cb6ef77db8ac5f1b`·`recalc_pair.json` `b03b1e353f8958a9`·`recalc_trace.json` `36238fb12ee6ddef`). 모두 work 스크립트를 쓰지 않고 raw만 읽었다.

## 1. 팩 구성(ESCALATE 1)

- **manifest:** `pack_all` 29,957파일 전수 SHA256 재계산 → 항목 불일치 **0**, 정렬 텍스트 SHA256 = 파일 SHA256 = `2440260fa3c05757…` 일치. 디렉터리별 `cecc4681` 29,954·타이틀 계열 3개 각 1.
- **마커:** `.amb` **657**개, 전부 4 B·L 160..12173(범위 129..65536 안)·**기본 이름 `.idx8` 0**·확장 이름 파일 존재·확장 이름 L = 마커 L(불일치 0). 확장 이름 파일 3,661개, 마커 없는 확장 이름 stem 0. idx8 합 29,296.
- **덮어쓰기 규칙(효과 팩 우선) 타당성:** `pack_hdb4` 413파일 중 idx8·`.amb` 412개가 `pack_all`과 byte 동일, 기본 팩 대비 다른 바이트 403·같은 9(work 보고와 같다). 나머지 1개는 `digest_index.json`(덮어쓰지 않음, work 공개 3과 같다). 효과 팩의 마커 2개(`h1c5411c5_104x80` L=160·`he88d0c4c_160x120` L=12173)는 기본 팩 마커와 **같은 L**이고 확장 이름 파일 집합도 같다(덮어쓴 확장 이름 3개는 그림 바이트만 다름). 그래서 덮어쓰기가 충돌 조회 규약을 바꾸지 않는다. 기본 이름 덮어쓰기는 같은 picture(digest·w·h 같음, 비충돌)의 stand-in 교체일 뿐이다. 효과 팩에만 있는 새 이름 0이라 "효과 팩이 비충돌로 본 이름이 전역에서는 충돌"인 경우도 없다. 효과 팩이 lap1194·1198에서 키 경로 selfcheck를 통과한 초안이고 selfcheck는 1x 원본 재생이라 stand-in 내용과 무관하다 → **규칙 수용**.
- 기본 팩의 비덮어쓰기 29,540파일은 `pack_all`과 동일, 기본·효과·로고 어디에도 없는 파일 0, 타이틀 계열 3파일은 `pack_hdf1`과 동일.

## 2. 키 로그 재분류(ESCALATE 2)

| run | 결과 줄 | 마커 stem | 마커 stem 기본 이름 hit | miss |
|---|---|---|---|---|
| A1 | hit 367·shade_hit 560·lut_hit 338·miss 38 = 1,303 | 137(hit 43·lut 5·shade 89) 전부 hit | **0**(파일 자체 0) | 38, 전부 키의 팔레트 디렉터리에 기본 이름 파일 없음 |
| PA | hit 266·lut_hit 532·shade_hit 97·miss 15 = 910 | 67(hit 29·lut 38) 전부 hit | **0** | 15, 같음 |

- **정정 1(PA 분해):** work 기록의 PA "hit 237"은 비마커 hit만 센 값이다. hit 전체는 266 = 237 + 마커 hit 29. 마커 67·miss 15·reject 0은 맞다. 판정 영향 없음.
- **정정 2(`0x466D50` 32×32 miss 6의 원인):** work는 "기본 이름 파일은 있으나 miss, 원인 미조사"라고 적었다. 재분류하면 이 6키(digest `2627fe1c`·`d83ee9e6`·`f53ae0f3` 등)는 팔레트가 타이틀 계열(`296963d9`·`84428eed`·`e24d0e6d`)이다. 그 디렉터리에는 전체 화면 파일 1개만 있다. `cecc4681`(imjin2)에는 같은 이름이 있지만, 엔진은 H-HDPAL(lap1176·1177 수용) 설계대로 **키의 화면 팔레트 디렉터리만** 본다. 그래서 miss가 나고 Scale2x로 폴백한다. 즉 결함·회귀가 아니라 설계된 폴백이다. 같은 digest가 lap1176 F1·F2·G1·H1·P0b 키 로그에도 같은 팔레트로 miss다(직접 grep). 남은 일은 "타이틀 계열 스프라이트(버튼 등) 팔레트별 팩"이고, 업스케일러 단계에서 같이 만들면 된다(backlog).
- 나머지 miss(A1 `0x468C30` 63×48 4·`0x4664D0` 68×22 1 등)는 팩 범위 밖 이름이다(기본 이름·마커 모두 없음).

## 3. trace·pair 재계산(ESCALATE 3)

- **A1 trace(8,116줄, 파싱 실패 0):** present PS9 70·PS7 161·PS5 724·PS3 6,031, PS3 301.8 s·p95 **6**(p99 7·최대 28 단발·중앙값 5), stale present 1개(225.5 s 79 px), 안전 7종 0, `mismatch` 필드 비0 없음, `fallback` 필드 비0 없음, `hd_pack_ext_hits` 137·misses 0·rejects 0, `hd_pack_fullscreen_hits` **955 = 70+161+724**·misses·rejects 0·loads 3, `hd_pack_pal_misses` 0, dropped 0, cache 최대 33,117,672 B·축출 0, 음영 selfcheck 570,448 px. keyed: `0x4672E0` 6,031/6,031·`0x467580` 216/216·`0x467B00` 310(fallback 0, mirrored 317 = 빈 창 7)·`0x4685C0` 685(fallback 0)·`0x467FD0` 1,592/1,592·`0x466B50` 1,241·`0x466BE0` 12. 비0 `reject_*` 필드는 전부 기존 mirror 경로 계수(bounds/target, 팩 reject 아님)다. **work 수치와 전부 일치.**
- **PA vs lap1196 PD:** 상태 leaf(PASS/FAIL/HOLD/BLOCKED/UNKNOWN/SKIP·bool) 225개 중 차이 **1개** = `capture_visual_comparisons.production.v2s_raw_status` FAIL→PASS. work 보고(200 leaf 기준, 차이 1)와 같은 결론이다.
- **보강(v2s_raw 차이 원인 귀속):** PD는 효과 팩(`pack_hdb2b`)만 켠 run이다. PA는 imjin2 유닛·지형 전체 stand-in 팩을 켠 run이다. 과거 pair 25개를 직접 대조했다. 전체 imjin2 팩을 켠 run(lap1176 F1·F2, lap1182 P0·P1, lap1184 P1·P2, lap1186 PU)은 모두 raw 1,690~1,800 PASS·unexplained 551~570이다. 팩 없음·효과만 켠 run(lap1173·1176 F0·1188~1196)은 raw 2,805~2,932 FAIL·unexplained 51~198이다. PA는 raw 1,542·unexplained **634**로 앞의 계열이다. 즉 "좋은 방향"이 아니라 **팩 켬 서명**이다. 바이큐빅 stand-in이 Scale2x 기준과 다르므로 흑색 블록이 줄어드는 대신 Scale2x로 설명 안 되는 블록이 는다. W-1 gate(unexplained ≤2,000)는 PASS다.
- **새 위험(공개, 마일스톤 판단 입력):** W-1 gate는 "Scale2x로 설명되지 않는 흑색"을 센다. 실제 업스케일러 팩은 Scale2x와 더 다르므로 unexplained가 634보다 커질 수 있다. 2,000을 넘으면 gate가 FAIL한다. 그러면 화질이 좋아져도 기술 gate가 막는 구조다. gate·validator 완화는 사용자 승인 사안이라 지금은 바꾸지 않는다. 업스케일러 팩 첫 run 때 측정하고 판단한다.

## 4. DLL·source·원본

- 실행 DLL `7b1c2203ca285473…`(`dll_sha_run.txt`)을 현재 `tools/inmm_stub` 사본에서 다시 빌드했다(공유 temp `…/rebuild/`, 저장소 무변경). 결과 `c0e7f3234e731ba1`, 크기 같음, 차이 6 B = PE 타임스탬프 0x88·체크섬 0xD8·디버그 디렉터리 타임스탬프 0x5AC04(각 2 B) → 동일 판정.
- lap1201 기록 뒤로 새 파일은 `tools/inmm_stub/_inmm.dll`·`lib_inmm.a`(빌드 산출물)뿐이다. source 변경 0.
- 원본 EXE SHA256 `b56986e0…08a8ac` MATCH.

## 5. 판정

**H-HDA0 `PASS(partial, 기술·격리)` 수용.** 집계: 판정 영향 불일치 0 · 정정 2(PA hit 분해, `0x466D50` miss 원인 = H-HDPAL 설계 폴백) · 보강 1(v2s_raw = 전체 팩 켬 서명) · 새 위험 공개 1(W-1 unexplained와 실제 업스케일 팩). 제품 결함 0. 기본 켬·사용자 전달 아님.

이로써 INBOX 19:3x 지시 ①~⑥과 효과 갈래의 **엔진·도구 준비가 끝났다.** 즉 원본 추출 → 외부 업스케일러 RGB → `convert`(팔레트·실루엣 강제) → `pack`(확장 이름) → 한 팩 디렉터리 → 엔진 키 경로를 stand-in으로 끝까지 검증했다. 남은 G1 HD 화질 이득은 **사용자 업스케일러 결과**가 있어야 생긴다. stand-in 팩은 사용자에게 보이는 화질 이득이 없다.

## 6. 마일스톤 경계 판단(ESCALATE 4) → root 전달

- **시험판 재스테이징: 지금은 하지 않는다.** stand-in 팩을 넣은 판은 화질 이득이 없고, 1.6 GB 팩 배포 부담만 생긴다. 기본 켬 DLL 묶음(lap1151판 `8a3837fb…`) 뒤 가시 수리도 없다(lap1153~1202는 가시 효과 ≈0인 계측 수리(H-OS1)·작은 GDI 글자 수리(H-OS2, 측정식 FAIL)와, 팩이 없으면 동작하지 않는 팩·키 경로뿐이다). 사용자 lap1151판 결과가 오면 그것이 최우선이다.
- **사용자 판단 요청(APPROVALS lap1203, 비차단):** 업스케일러 단계로 넘어갈지 묻는다. 선택지:
  1. **업스케일러 입력 묶음을 받는다.** 루프가 1배 인덱스 PNG(char·tile·fnt 43,622프레임, 약 0.6 GB)와 사양·명령을 공유 temp에 만든다. 사용자가 업스케일러를 돌려 RGB 결과를 주면 루프가 `convert`·`pack`·격리 실게임 확인 → 시험판으로 잇는다. **디스크 확보가 먼저 필요하다**(추출 0.6 GB + 결과 RGB 약 0.7 GB + 팩 1.6 GB + run).
  2. 사용자가 이미 업스케일 결과를 가지고 있으면 위치만 알려 준다(사양 문서 경로 규칙 `hd/<원본 상대경로>/<프레임4자리>.png`).
  3. 업스케일러 단계는 나중에 한다. 루프는 G1 잔여 backlog(아래 §7)를 계속한다.
- **디스크(root 대상):** 여유 **6.8 GB**로 사전등록 기준 7 GB 미만이다. 새 게임 run을 시작할 수 없다. 대량 삭제는 사용자 승인 사안이라 middle은 하지 않는다. root가 사용자 승인을 받아 확보한다. 후보: lap1175 전례처럼 오래된 `local/runtime/` private run을 정리하고(2026-10-08 이전, 원본/참고/공유 raw·기록 제외), 쓸모가 끝난 개별 갈래 팩(`pack_hdf1` 909 MB 등)은 `pack_all` 수용 뒤 archive를 판단한다.

## 7. root 처리 뒤 다음 한 가지(조건부)

- 사용자 선택 1·2 → middle이 work H-HDU2(업스케일러 입력 묶음 생성 또는 사용자 결과 `convert`·`pack`·NG5+pair 실게임 1회, W-1 unexplained 측정 포함)를 사전등록한다.
- 사용자 답 전 또는 선택 3이면 다음 work는 **게임 run 0 backlog**다(디스크 무관). 먼저 lap1201 i15 테스트 공백(summary 이벤트가 `MAX−2`에서 직렬화 실패할 때 overflow 이름 `serialize` 고정)을 테스트 1개와 필요 시 C 한 줄로 닫는다. 디스크가 확보되면 그다음은 타이틀 계열 스프라이트 팔레트별 팩(§2 정정 2, PS9·PS7·PS5 버튼 HD) 사전등록이다.

## 8. 검사

검사 결과는 STATUS에 보강한다(PROMPT ⑥: 기록을 먼저 쓰고 검사 뒤에는 고치지 않는다). 계획: `checks/safety.sh check`, focused 6파일(lap1201과 같음). 전체 `make check`는 SKIP(source 변경 0, lap1200 full PASS 2042 유지).

## 다음 행동

root가 `loop/ESCALATE_SOL`(마일스톤 경계 + 디스크)을 처리한다. 사용자 G1 시험 결과가 오면 그것이 최우선이다.
