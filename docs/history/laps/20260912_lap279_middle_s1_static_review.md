# 2026-09-12 | lap 279 | lap278 S1 정적 조사 독립 검수 (middle)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, middle tier
  (진단·계획·컨펌). 외부 subagent/provider 호출 0. 게임 구현·hands-on 수정 0.
  lap 번호는 `loop/.lap_counter`=279를 그대로 사용했다(러너 전용 상태, 쓰지 않음).
- 가설 / 사용자 관찰: lap278이 여섯 행 중 다섯을 UNKNOWN으로 닫고 research blocker를
  선언한 것이 **조사 완결에 근거한 것인지**를 같은 읽기 전용 범위에서 독립 확인한다.
  사용자 신규 관찰 없음.
- 예상 PASS / FAIL 조건: lap278의 SHA 7종 재계산 일치 + entry/블록 주소 재현이 PASS 전제.
  §4 (i)/(ii)를 항목별로 재적용하고, lap278 판정과 다르면 근거를 제시해 교체한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md`에 §4.2 검수 절 추가,
  `docs/history/laps/probes/20260912_lap279_middle_s1_serializer_probe.py` 신규,
  `logs/lap279/s1_serializer_probe.json` 신규, `docs/STATUS.md` 갱신, 본 기록,
  `loop/ESCALATE_SOL` lap279 항목 추가. **게임 코드·comparator·producer·tests·원본
  EXE/DLL/assets·PASS 규칙·slot 강등 규칙 변경 0.** 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 인원 / 지도 / 군대 / fixture:
  원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (저장소 사본과 상위 사본 두 곳 모두 동일). 후보 없음.
  `../Syw2plus/save/save000.dat` `1c703551…629e719da` 3,093,902 B;
  `save006.dat` `616b7997…9289a0d064` 3,437,942 B — **읽지도 파싱하지도 않았다**
  (해시/크기만 재확인). `tools/runtime_env.py` `e4f6a834…22455837`,
  `tools/compare_g1_stage_b.py` `9b684cec…f32e426efdb`,
  `analysis/memory_maps/population_runtime_bridge_0910.md` `96eb29ab…fa1d1fb68` 전부 일치.
  환경 `.venv`/Linux 정적 도구(objdump/sha256sum). **게임 실행 0.** runtime fixture 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `objdump -D -Mintel -j .text` (범위 `0x440c20..0x440ff0`, `0x440ff0..0x442e00`,
  `0x42a920..0x42bc90`, `0x40f4b0..0x40f560`), `sha256sum`. PNG/capture 없음.
  probe: `docs/history/laps/probes/20260912_lap279_middle_s1_serializer_probe.py`
  → `logs/lap279/s1_serializer_probe.json`, **exit 0, failures=[]**.
  Fast: `make check` → **291 passed in 44.49s**, Ruff/compileall/mypy(10 files) 성공,
  `CONTEXT_PASS`; `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  save/load 두 entry에서 `fwrite`(`0x4DA39F`) 22회, `fread`(`0x4DA4A9`) 22회를 전부 열거해
  literal 블록 21개를 얻었고 **save 표와 load 표가 주소·크기·순서까지 동일**했다
  (`block_table_identical=true`). 승인 주소 대응(포함관계 산술):
  selection `0x899024`→bulk `0x892410` +0x6C14; `0x899028`→+0x6C18;
  logic tick `0x8924B8`→**+0xA8**; 존재배열 `0x8990C8`→+0x6CB8;
  player base `0x956770`→+0xC4360; map `0xB3DE34/36`→`0xB3DDA8` +0x8C/+0x8E;
  camera `0xB42D7C`(4B)+`0xB42D80`(4B) 인접 블록 = `_read_camera(0x00B42D7C, 8)`와 정확히 일치.
  유닛 로스터는 bulk 블록 밖이며 전용 경로 save `0x40F4B0`/load `0x40F4F0`이 처리한다:
  `edi=0x66B790`, 존재플래그 `esi=0x8990C8`, `WORD[esi]!=0`이면 `0x758` 레코드 1개를
  읽고/쓰고 `esi+=2, edi+=0x758`, `esi<0x899A28`. 슬롯 수 `(0x899A28-0x8990C8)/2=1200`이고
  `0x66B790 + 1200*0x758`이 **정확히 `0x892410`**(bulk 시작)에서 끝나 기하가 자기일관적이다.
  load는 bulk fread(`0x4412DC`) **이후** `0x441305`에서 로스터를 호출해 존재배열 의존 순서가 옳다.
  지도 레이어 serializer `0x42A920`은 `WORD[ecx+0x8C]`×`WORD[ecx+0x8E]`를 `imul`해 원소 수를
  만든다 — bounds는 저장 대상일 뿐 아니라 **역직렬화 크기 인자**다.
  → **여섯 행 전부 CONFIRMED**(§4 기준 (i)). lap278의 항목 1·2·3·5·6 UNKNOWN과
  research blocker 결론을 **반려**한다. 항목 4는 유지하되 근거를 강화했다.
  lap278의 "entry 명시 주소에 selection/camera/logic tick이 없다"와 "`0x892410` 참조는
  tick `0x8924B8`의 근거가 아니다"는 **사실과 다르다**(tick은 그 블록의 +0xA8).
  lap278 실패 원인은 증거 부족이 아니라 **조사 미완**(첫 블록에서 중단)이다.
  「좁은 static call-graph probe로 충분한가」에 대한 답: **충분하며 이번에 수행 완료.**
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  회귀 없음(코드·검사 규칙 무변경). 이것은 **S1 fixture의 정적 타당성**에 대한 1단 판정이며
  제품 G1 증거, 두 run의 실제 값 동일성 주장, Stage B 허가, runtime 쌍 예산, 마일스톤 승인이
  **아니다**. 자기 승인 금지에 따라 다음 새 세션이 이 검수를 다시 확인한다.
  **신규 G3 블로커:** bulk 블록은 `0x975D8C`에서 끝나 PlayerStruct 8개(`…0x973D50`)는
  들어가지만 16개(`…0x991330`)는 `0x1B5A4` 바이트 넘친다(`fits_16=false`).
  현재 저장 포맷에는 9~16번 플레이어를 직렬화할 공간이 **구조적으로 없다.** 기존 장면 서명
  owner8~15 사각과 별개의 더 깊은 문제다. G1 범위가 아니므로 수리하지 않고 기록만 한다.
  기존 위험 유지: WM_CLOSE teardown, 실제 후보 scene/input evidence, R17/R6-B-R2,
  offline 8건 주차, M-d/M-e 사각, G2~G4 미해결. 사용자 마일스톤 승인 없음.
- 다음 한 가지: work tier 인계 — 0x758 유닛 레코드의 x/y 필드 오프셋 고정과 PlayerStruct
  `active_units` 대응 필드 확인(둘 다 실행 예산 0의 정적 작업, §4.2.5). 그와 별개로
  runtime 쌍/Stage B 예산은 상위(Astra) 결정 대기이며 이 tier가 열지 않는다.
