# 2026-10-04 | lap 952 | G1 W70 lap951 미후킹 잔여 독립 검수 · 기준2 명시 잔여 판정 · 반투명 overlay writer 인계

- 실제 provider/model/effort / 지정 역할: middle(Claude Code `claude-opus-5-5`, high, Fast OFF), 진단·계획·확인. 게임·하네스·source·test·DLL·validator 변경0, 새 게임 실행0, commit0. `loop/.lap_counter` 952 읽기만.
- 가설 / 사용자 관찰: lap951 residual 마스크·수치는 raw로 재현되고, PS3 정상 상태 비GDI 잔여(lap951 표기 "미니맵 상자")의 정체를 raw+PNG로 좁힐 수 있다.
- 예상 PASS / FAIL 조건: PASS = 제품 helper 없는 재계산이 두 run 64 present 모두 `unhooked_pixels`·bbox와 일치, source/raw SHA = 기록, 기본 모드 raw가 lap949와 동일. FAIL = 불일치·SHA 불일치·근거 충돌.
- 변경 파일 / source fingerprint / 커밋: 새 카드 `docs/work/active/G1_MIDDLE_W70_RESIDUAL_ACCEPTANCE_OVERLAY_WRITER_HANDOFF_LAP952.md`, 이 기록, STATUS. uncommitted. source 7파일 SHA = lap951 기록(카드 §1).
- 원본 SHA / 후보 SHA / 환경 / fixture: 보호 원본 EXE `b56986e0…a8ac` 재해시 MATCH(read-only). 두 residual run probe-result `status PASS`·`source_unchanged`·`game_removed` true. census-only 800×600, save006·PS9 메뉴. 8 player records는 활성8인 부하증명 아님.
- 실행 명령 / 로그 / 캡처: `.venv/bin/python temp/Syw2plus_patch/20261004_lap952_middle_review/recalc_lap952.py`(스크립트 SHA `b47fe43142380427a8fd78fdff956485df2e427ec28c8f12c116fc82024f622a`) → `recalc_lap952.json` SHA `1fd5935bdb197360d9b7f354843ebb951bc2ffa57a8aa4d0189b4af5f38df121`. 대조 PNG(같은 폴더): `ps3_core40_overlay_minimap.png` `42960945…cc59`, `ps3_box_crop.png` `fa3b54c1…184a`, `ps3_present3_extra_overlay.png` `8a815648…3d75`, `ps9_last_overlay.png` `adf489fd…d578`, `ps3_logo_4captures.png` `f3fd505a…1e7d`, `ps3_sel_vs_prod_half.png` `5a94e2a6…c55c`.
- 측정값 / 판정:
  - 재계산 불일치 0(128/128 record, header·순번·{0,1} 마스크). PS3 r6 last 2,625(0.547%)·p50 2,635·min 2,284·max 21,423(4.463%, present 3)·core 2,529·합집합 2,782; PS9 2,622(0.546%) 상수, 텍스트 사각형 99.54%. 기본 PS3 raw 이벤트×키·건수가 lap949와 동일, Blt 64/64. PS3 r6 Blt 86/86, 제외 non-screen 22 = 101×40 표본 22.
  - **정정:** PS3 "미니맵 상자" 2,102px는 미니맵이 아니라 우하단 **화면 고정 반투명 로고 워터마크 "임진록2+ 조선의 반격"**(64 present 지속 2,076px, x702~792·y380~438, 카메라 이동 뒤에도 같은 위치). 실제 미니맵(좌하단)은 잔여 없음.
  - PS3 present 1~7 과도 17~19k px는 같은 run `selection.png`의 반투명 회오리 효과 위치와 일치, 8번째부터 ≤45px.
  - lap951 residual 장치·TextOutA 귀속 **PASS(partial)** 수용(Lock 실패 주입·HDC→surface 미구현).
  - 기준1 분류: GDI 글자 = 명시 잔여 P7; 로고·회오리 = 미후킹 반투명 overlay, 명시 잔여(P6 후보), writer 미확인.
  - **기준2 명시 잔여 ≤5% 조항: 측정 창 안 충족(부분)** — PS3 최악 4.463%(여유 0.54%p, 장면 의존), PS9 0.546%. hook된 writer의 미러 미커버분 합산과 HD coverage ≥90%는 미측정 → 기준2 전체·G1 HOLD.
  - 기본 모드 non-screen Blt 분리: 적용하지 않음(기본 64/64 PASS, 실패 없이 gate 의미 변경 불필요).
  - 전사 정정 2건(raw 재해시로 확인): lap951 기록 PS9 raw `8dfa0618…e4b` → 실제 `…e5b4`, 기본 PS3 raw `07a0bf44…df25` → 실제 `…25df`. 파일 자체는 불변.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: hook bbox 과소 가설은 표본 기반으로 가능성 낮음(완전 배제 아님). 반투명 효과가 많은 장면의 5% 초과 위험. G1 사용자 승인·D-2·P5 메뉴 미러·P-6·HD coverage HOLD. ESCALATE 조건 없음.
- 다음 한 가지: work(Sonnet) 1 lap — opt-in 하드웨어 watchpoint(PS3 present source 픽셀 (782,380))로 반투명 overlay writer EIP를 잡고(불가 시 원본 EXE 정적 대안), measurement-only census target으로 넣어 PS3 로고 상자 미후킹 2,102 → ≤100px를 실측한다(카드 §5).
