# 2026-09-12 | lap 320 | 목표 G1 (M1, lap319 F1 독립 검수)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle(진단·계획·확인)**.
  게임 코드·EXE·DLL·assets·pin·`tools/`·`patches/` 변경 **0**. 다른 모델을 실행하거나 대행 승인하지 않았다.
- 가설 / 사용자 관찰: lap319 work의 F1 수리(값=원본 PE, 경계=주소 델타, 정상 접힘 성공·손상 수집 FAIL)가
  lap318 §4 수용표대로 성립하는지. lap315/lap316/lap319 probe를 **import하지 않고** 원본 PE와 fresh objdump에서
  바이트·경계·불변식을 재유도하고, lap319가 덮지 않은 부정 입력에서 실제로 fail-closed인지 확인한다.
- 예상 PASS / FAIL 조건: PASS = 753/753/7/724·unresolved 0·writer 4/0·gate·실패 arm·접힘 27·두 reset 10B가
  독립 방법으로 일치하고, lap319 보고서가 재현되며, 미검증 부정 입력이 전부 FAIL로 닫힌다.
  FAIL = 수치 불일치, 보고서 비재현, 부정 입력의 무징후 성공, 필수 게이트 예상 밖 실패.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): **전부 uncommitted**(`LOOP_ALLOW_COMMITS` 기본 0).
  - `docs/history/laps/probes/20260912_lap320_middle_lap319_f1_review_probe.py`
    `68cbfb4b30fc20b21cb6a4e539a9d044aa29530810b941cdea59daf5a85226c7`
  - `tests/test_lap320_middle_review_probe.py`
    `e1d420d26800a5075d8f1de2ebdbdd4a45c535f1b0d9469fa7a4692d9d42d7f8`
  - `logs/lap320/lap320_lap319_f1_review.json`
    `3d0022b88d694fd1a17c76073d47622c796bab2be188a90d83d325f0a24f60da` (stdout SHA와 동일, 2회 byte-identical)
  - `docs/history/laps/20260912_status_lap319_compaction.md`
    `87288a9ed72e5c995325275550c4394b966a20ba3cb1bd2e838d6c13739ff873` (원문 SHA `2b697659…f388d3e3`, 127줄)
  - `docs/STATUS.md`(갱신), 이 기록. lap313~319 산출물·pin·원본은 **무변경**(입력 SHA 3종 재확인).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 세션 전후 불변(`make doctor` 확인).
  후보 EXE/DLL/assets **없음**. 환경 = 정적 분석만(objdump 2.42 + 직접 PE 헤더 파싱). 게임/Wine/Xvfb/Stage B/
  PNG/클릭 **0**. 활성 플레이어·지도·군대·생성 fixture **해당 없음**(실행 증거가 아니다).
  합성 fixture 4종(열이 다음 명령 침범 / 짧은 연속줄 / 파일 바이트 불일치 / 명령 행 부재) + 실제 두 reset.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `python3 docs/history/laps/probes/20260912_lap320_middle_lap319_f1_review_probe.py` → exit 0,
  stdout SHA `3d0022b8…a24f60da`(연속 2회 동일) = 저장 report SHA.
  `.venv/bin/python -m pytest tests/test_lap320_middle_review_probe.py -q` → **11 passed**.
  `make check` → **361 passed** + Ruff/compileall/mypy/CONTEXT_PASS (`logs/lap320/make-check.log`, rc=0).
  `bash checks/safety.sh check` → **SAFETY_PASS** (`logs/lap320/safety.log`, rc=0). 캡처 없음.
  갱신 후 `docs/STATUS.md` = **130줄**, SHA `7cf3aa94b29c78c1fb3c5227d017d4adc1e9c5649b99b599a43c36d30f3105a2`.
  `loop/.lap_counter`(=320)는 읽기만 했다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **독립 재유도(§A, import 없음, 방법을 의도적으로 교체).** 창 `0x431AB0..0x4324D6` 명령 **753**,
    entry 도달 **753**, 실패 arm **7**, 성공 arm **724**, unresolved **0** — lap319 주장과 **일치 PASS**.
  - 화면 전역 writer를 **텍스트가 아니라 디코드된 바이트**로 인식(`c7 05 <abs32> <imm32>` 10B와
    `89 /r mod=00 rm=101 <abs32>` 6B 두 인코딩) → `{0x431B79, 0x431B7F, 0x4324B8, 0x4324C2}` **4개**,
    실패 arm writer **0**, 성공 arm writer **4**, 성공 ret `0x4324D5`는 실패 arm 밖 — **일치 PASS**.
  - gate `0x431AF2` 파일 바이트 `750a` → taken `0x431AFE`; 실패 arm `0x431AF4` 파일 10B
    `5f5e5d33c05b83c434c3` — **일치 PASS**.
  - 접힘은 "열 폭 > 7"이 아니라 **열 폭 ≠ 주소 델타**로 검출: 창 안 **27개**, 전부 **절단**이고 초과 0건.
    **신규 사실(lap318이 적지 않은 분해):** 27개 모두 주 행이 정확히 **7B**이고 실제 길이는
    **8B×17, 9B×4, 10B×6**이다. 두 reset은 10B 여섯 중 둘이다. objdump는 한 행에 7B를 넘겨 찍지 않으므로
    lap318의 "7B 초과 명령 27개"는 **길이 기준**으로 읽어야 하고 열 기준으로 읽으면 0이 된다(표기 정정, 수치 영향 0).
  - 두 reset 재유도: `0x4324B8` 파일 10B `c7051cbfe50080020000`(대상 `0xE5BF1C`, imm **640**),
    `0x4324C2` 파일 10B `c70520bfe500e0010000`(대상 `0xE5BF20`, imm **480**). 주 행 7B + 연속줄 3B 재조립 =
    파일 10B = 주소 델타 10 — 세 출처 **전부 일치 PASS**.
  - 창 전체 재조립 무결성: 연속줄 누락·gap·초과 **0건**, 재조립 열이 파일 바이트와 불일치한 명령 **0건**,
    명령 행 주소와 겹치는 연속줄(phantom) **0건**(전체 listing 명령 행 306,218 / 연속줄 5,338) — **PASS**.
  - **재현성(§C):** lap319 probe를 subprocess로 2회 재실행 → exit 0/0, stdout byte-identical,
    stdout SHA = 저장 report SHA `09e012dc…f4161def` — 손 전사 아님 **PASS**. lap319 입력 3종 SHA는 기록과 일치.
  - **적대적 입력(§B, lap319 테스트가 덮지 않은 4종):** 열이 다음 명령을 침범 →
    `column_overlaps_next_instruction`, 연속줄이 짧음 → `column_shorter_than_address_delta`,
    파일 바이트 불일치(변조 이미지) → `column_not_pe_prefix`, 명령 행 부재 → `missing_instruction_row`.
    **4종 전부 fail-closed PASS**. lap318 §4 (d) "다음 주소 < 시작+길이"에 해당하는 경로는 lap319 테스트가
    연속줄-커서 overlap만 덮어 **미행사 상태였고, 이번에 실제로 닫혀 있음을 확인**했다.
  - **판정: lap319 F1 work = ACCEPT (middle 기술 컨펌).** 값·경계·연속성·부정 fixture가 독립 재유도와
    일치하고 보고서가 재현된다. 제품 증거 **0**, runtime/Stage B **0**, S1 종결 **REJECT** 유지,
    G1~G4 **미완료** 유지. 이것은 **사용자 마일스톤 승인이 아니다**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - **N4(신규, 수치 영향 0, work 후속 후보):** lap319 `main()`은 `checks` 리스트를 **선평가**하므로 reset 행이
    `missing_instruction_row`/`missing_next_address_boundary`로 실패하면 `boundary_length` 키가 없어
    **KeyError 트레이스백**으로 죽는다. 값이 새지 않으니 fail-open은 아니지만 **FAIL 판정 JSON이 남지 않는다**.
    이번 §B가 해당 dict에 `boundary_length`가 실제로 없음을 확인했다.
  - **N5(신규, 수치 영향 0):** lap319에 남은 직접 행 조회(gate 행, `collect_contiguous_rows`)는 새 길이
    불변식을 쓰지 않는다. 다만 (i) gate는 파일 2B와 교차 검증되고 (ii) `collect_contiguous_rows`는 접힌 명령을
    만나면 커서 불일치로 `is_contiguous=False`를 돌려준다(이번에 직접 실행해 확인). 두 대상 모두 현재 접히지
    않아 수치 영향이 없다. 규칙 완화가 아니라 **잔여 사각의 명시**다.
  - **UNKNOWN 유지:** N1(실제 간접분기 0 → lap315 E1 수리 inert), N2(창 안 call 31개 미추적, callee 쓰기·
    cross-function 순서), N3(`0x432497`/`0x4324A6`의 `ds:0xB3AC88`=`0x33F`, `ds:0xB3AC8C`=`0x1FF` 의미),
    W3 stale pin(재pin은 Astra/사용자 결정), map↔dialog 실제 event/thread 순서, 실제 좌표·클릭 결과.
  - `loop/ESCALATE_SOL` 없음(이번 바퀴 필수 게이트 전부 예상대로 통과, 마일스톤 경계 아님).
- 다음 한 가지: **F1은 이번 ACCEPT로 종결**이다. 다음은 상위(Astra) 결정 대상이다 — F1 종료 후 lap317 결정4가
  예고한 "runtime 계약 미제출 봉투의 문서 검토 복귀"로 갈지, N4 정리를 work에 한 번 더 줄지, 아니면 W3 재pin을
  올릴지. middle/work 단독으로 runtime/Stage B/Wine/Xvfb/제품 EXE를 시작하지 않는다.
