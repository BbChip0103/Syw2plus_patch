# 2026-10-07 | lap1163 | G1 work — H-HDP1 ③ HUD 패널 1장 시범 (기존 `SYW2_G1_HD_PACK` 경로)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / work(실무). C·하네스 변경 0. 도구 1개(`tools/g1_hd_convert.py`)와 그 테스트 1개를 수리(아래 §1). 커밋 0.
- 입력: lap1162 middle 사전등록 §4(`20261007_lap1162_middle_g1_hdef1_review_hdp1_preregistration.md`). `loop/STOP`·새 반려·사용자 G1 시험 결과 없음.
- 가설: 기존 엔진 패널 경로는 `SYW2_G1_HD_PACK` 디렉터리의 키 파일을 읽어 Scale2x 대신 쓴다. lap1159 team-safe `.idx8`(A)와 바이큐빅 2배→`convert`→`panel-idx8`(B)를 관측 키로 두면 적재되고 화면에 전달된다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 실행 전후 MATCH. 환경: 격리 Wine·Xvfb 1600×1200, `tools/g1_saved_scene_probe.py --new-game-path --new-game-start --new-game-act --hd-source scale2x`(lap1161 D-4 NG5와 같은 장면·플래그 없는 저장소 빌드), env `SYW2_G1_HD_PACK=Z:\…\pack*`만 바깥에서 추가. 활성 8 player records(부하 증명 아님), 새 임의 게임.
- 산출물(공유 temp `20261007_lap1163_work_hdp1/`): `fix/pannel{k,c,j}_{A,B}.idx8`, `metrics.json`, `p2_*.json`, `crops/`, `scripts/`(`run.sh`·`p0.py`·`p2.py`·`p2b.py`), `run_<라벨>/`(10개). 런타임 `local/runtime/lap1163_hdp1_*`는 game 사본만 삭제, manifest·output·prefix·로그 보존.

## 1. 결함 발견·수리 (사전등록에 없던 것)

사전등록은 팩을 `831×h×4` B로 명시했고 lap1159 `panel-idx8`도 그렇게 만들었다. 첫 실행 3회(A·B·D)는 관측 키와 정확히 일치(run A)해도 `panel_hd_pack_loaded=0`이었다. 추적:

1. env는 wine 프로세스까지 도달(`/proc/<wineserver>/environ`에서 `SYW2_G1_HD_PACK=Z:\…\packD` 확인, run E).
2. `strace -f -e trace=openat`(run G)에서 적중 키 파일 openat **성공(fd 90)**, 그런데 loaded 0 → 파일은 열렸고 크기/검증에서 거절. (`strace -P`는 Wine이 dirfd 상대로 열어 못 잡는다 — 첫 시도 F는 무효.)
3. 엔진 소비자 `panel_load_hd_pack`은 `expected_bytes = G1_PANEL_WIDTH(800) × h × 4`이고 검증 소스 `g_panel_expected`는 원본 writer 때문에 831열 중 **앞 800열**이다(`g1_panel_fold_frame`). 실제로 트레이스 `panel_frame_sha256`(c `0137064a…`·k `c7aaf198…`)가 `.src`의 앞 800열 SHA와 **정확히 일치**(c·k 모두 True; 순차 겹쳐쓰기 가설은 False). 즉 팩은 `1600×2h`(= 800×h×4 B)여야 하고 lap1159의 831폭 `.idx8`은 크기 불일치로 항상 거절됐다. lap1159 Y-2 `engine_pack_valid`는 폭 831 모델로 계산돼 이 불일치를 못 잡았다.
4. 수리: `tools/g1_hd_convert.py` `PANEL_ENGINE_WIDTH=800` — `panel-idx8`은 HD 프레임의 앞 1600열만 쓰고 보고에 `source_width`를 둔다. RED→GREEN `tests/test_g1_hd_convert.py::test_panel_idx8_keeps_only_the_engine_panel_width`(17 passed). 새 팩은 엔진 검사기(`y5_valid`)를 폭 800으로 돌려 c·k·j × A·B 6개 전부 유효 1.

## 2. 측정 (사전등록 §4)

- **P-0:** A·B 모두 도구 `check` 통과(B 변환 `pass`, 위반 0, 동률 8,800 px 중 4,064 draft 해소)·엔진 검사기 유효 1. 사전등록의 "`.src` 앞 128 B 디지털 = `a3216fad`?"는 **불일치**(`4ab644cf`)지만 원인은 입력 오지정: 엔진은 **RLE 데이터**(`.spr` 오프셋 3060 = 0xBF4)의 앞 128 B FNV-1a를 쓴다. 3패널 모두 이 오프셋에서 런타임 digest 일치(k `a3216fad`·c `2aa149c7`·j `5939fabc`) → `h`는 파일에서 오프라인으로 계산 가능·안정.
- **P-1 적재 PASS(partial):** run H(패널 k, B 팩 `…s07b65628_ha3216fad_831x163`) `panel_hd_pack_loaded=1`·`panel_key_subpixels_emitted` 0·lock/pointer/pitch/foreign 0·안전 7종 0·fallback 0·dropped 0·크래시 0·`scale2x_validator` PASS(`hd_mask_outside_diff` 0 = 실루엣 밖 변화 0)·PS3 HD min **99.936**(≥99.9)·p95 7 ms(lap1161 D-4 6 ms 대비 +1 ≤ +3). run J(패널 j, A 팩) 적재 1·같은 안전 0·HD min 100·p95 7. 팩 없음·불량 크기 run(none·A·B·D·E·G·I)은 전부 loaded 0·같은 안전 0(G는 strace 하에서 p95 8, 비교 제외). 결정 전 실패 run 7개(키 불일치 아님, 크기 불일치)는 §1에 설명.
- **P-2 화면 전달(B, 패널 k, 기준 = 같은 패널 팩 없는 run D) PASS:** 화면 패널 영역 = y 874..1200 × x 0..1600(1200−2h), 보고 대응 y0 탐색 874 확정. 색 대응은 `imjin2.pal×4`가 99%에 못 미쳐(관측 픽셀이 더 어두움: 예 idx 3 `(44,68,60)` vs `(56,80,68)`, 팩 없는 캡처 일치 0.20) **팩 없는 캡처에서 유도한 표**(160 색 인덱스, 불투명 화소 일치 0.82~0.91; 나머지는 미니맵·자원 숫자 등 동적 표시)를 쓴다. B≠A 불투명 화소 111,302 중 팩 없는 캡처가 A 기대색과 일치하는(다른 writer가 안 덮은) 91,636~94,656 px에서 B 캡처가 B 팩 색과 같은 비율 **ps3_start 0.9816·ps3_act 0.9793·ps3_produce 0.9776**(≥0.95). (b가 사전등록 판별 기준.) **공개:** (a) "패널 영역 변경 ≥10,000" 수치는 98,238~102,019 px로 충족하지만 **판별력 없음** — 같은 패널 두 팩 없는 run(A·D)끼리도 99,785~116,857 px 달라진다(임의 지도·미니맵·자원). 표는 B에서만 쓰이는 인덱스 6,861 px를 알 수 없어 제외. 팩 영역 캡처 크롭: `crops/`.
- **P-3(A):** j(A는 Scale2x와 동일, 차 0 px)·run I(팩 없음) vs J(A 팩) 영역 변경 54,257~68,175 px는 장면 잡음 수준이라 효과로 읽지 않는다. k의 A는 엔진 Scale2x와 27 px만 다름(lap1159)이라 별도 확인하지 않았다(기준 아님).
- **P-4 포인터(run별 패널·`s` 포인터, `h` digest는 패널당 고정):** lap1161 k `07bdc5f8` · none c `07baf3f8` · B c `07bdd8e8` · A k `07bdc5f8` · D k `07b65628` · E c `07baf3f8` · G c `07bdd8e8` · H k `07b65628` · I j `07bdc5f8` · J j `07bdc5f8`. 같은 패널도 run마다 포인터가 2종 이상(c: `baf3f8`·`bdd8e8`, k: `bdc5f8`·`b65628`)이고 어느 패널이 뜨는지(c/k/j)도 run마다 달라 **런타임 포인터는 키로 쓸 수 없다**. 키는 `h`(RLE 데이터 digest, 오프라인 계산 가능)+크기로 충분히 고유해 보인다 → ④ 일반 로더 첫 항목: `s` 필드 제거(또는 (파일, 프레임) 안정 식별자).

## 3. 판정

**H-HDP1 `PASS(partial, 기술·격리)`**: ③ 시범으로 기존 경로가 B 팩(업스케일러형)을 실제 화면까지 전달함을 입증(P-1·P-2·P-4). 단서: 포인터 키는 run마다 달라 현 형태로는 사용자 제품에 쓸 수 없고(④), 사전등록의 831폭·`.src` digest 가정 두 개를 정정(§1·P-0), 전달 판 `.idx8`는 이번에 만든 800열 규격만 유효. 업스케일 화질 평가·G1 사용자 합격 아님. 비교 대상은 같은 패널의 서로 다른 임의 지도 run이다(장면 비동일, 판별은 패널 영역 색 대응으로만).

## 4. 검사·한계

- 이번 변경: `tools/g1_hd_convert.py`(상수·crop·보고 필드)·`tests/test_g1_hd_convert.py`(테스트 1개). `make lint`·`make typecheck` PASS. 전체 `make check`는 STATUS 검증 줄에 보강한다.
- 한계: 같은 패널 쌍(k)에서만 P-2 측정, c는 팩 있는 run이 없어 적재 미확인(c 팩 적재는 key `…2aa149c7…160`로 만들어 두었으나 c가 뜬 run은 모두 크기 불일치 팩이었다). `.idx8` 규격(800열) 문서화는 도구 docstring에만 있다.
- 디스크: 런타임 prefix 10개 각 1.2 GB 보존, 여유 35 GB.

## 다음 행동

middle(Opus) 독립 검수: 새 스크립트로 H 캡처 패널 색 대응 재계산(특히 §2 P-2 유도표 방식·판별력)·`panel_frame_sha256`=앞 800열 SHA 재계산·`strace`로 적중 키 파일 적재 확인·`tools/g1_hd_convert.py` crop 수리 검토 → 수용 시 ④(일반 HD 그림 로더: 키에서 `s` 제거·`(file,frame)` 식별) 사전등록. 사용자 G1 시험 결과가 오면 최우선.
