# 2026-09-12 | lap 304 | G1/S1 lap303 U1~U5 독립 검수 + 모드 인자 출처 확정

- lap 번호 근거: `loop/.lap_counter` = **304**(에이전트는 읽기만 함). 이번 호출의 runtime 배너는
  `lap=303`을 표시했으나 `loop/PROMPT.md`가 "현재 파일 값이 이번 runtime lap 번호"라고 못박아
  파일 값 304를 사용했다. 배너/카운터 불일치는 기록만 하고 카운터를 수정하지 않았다.
- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / middle tier
  (진단·계획·확인). 게임 코드 hands-on 수정 없음, 실행 없음.
- 가설 / 사용자 관찰: lap303의 writer 20개·해상도 5종·중심식은 손으로 적은 표에서 나왔다.
  같은 사실을 **명령 스트림과 파일 이미지에서 다시 유도**하면 독립 검수가 되고, 그 과정에서
  "구성 시점 해상도 미확정" 블로커가 정적으로 좁혀질 수 있다.
- 예상 PASS / FAIL 조건: 재유도 결과가 lap303과 수치까지 일치하면 ACCEPT, 어긋나면 FAIL.
  lap303 산출물 SHA가 바뀌었거나 두 fresh run이 다르면 FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `docs/history/laps/probes/20260912_lap304_middle_lap303_mode_source_review_probe.py`
    SHA `2047f839a0a5bdb3b6b359c70b6355f4e1247a5b226e27602a8e717c218b1db2`.
  - `logs/lap304/middle_lap303_mode_source_review.json`
    SHA `d0ed2696ec2b84b5c7ab03343cd13eda22fb8a17a1628f1242d5832ae1d70b93`.
  - `docs/history/laps/20260912_status_lap304_compaction.md`
    SHA `7fb6925970acb6a118fed88d91e4b7745e7793e64175d7e69e3bf8fd3ad51274` (STATUS 원문 130줄 보존).
  - `docs/STATUS.md`와 본 history 추가. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(읽기 전용), 후보 없음.
  - 원본 sprite `../Syw2plus/yfnt/saveloadtitle.spr`
    `7d154cdbf37dbea78c162ada870e656a039a224c5aa63ee52d86d8123c08a5c5`, header `[9,320,310,1]`.
  - offline Linux `.venv` + `/usr/bin/objdump`; 활성 플레이어/지도/군대 없음.
  - 게임/Wine/Xvfb/Stage B/runtime 예산/PNG/클릭 실행 **0**.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `.venv/bin/python docs/history/laps/probes/20260912_lap304_middle_lap303_mode_source_review_probe.py`
    두 회 exit0, 출력 바이트 동일(`d0ed2696…ae1d70b93`).
  - 그 안에서 lap303 probe를 두 번 재실행 → 둘 다 exit0, `5079de5a…b869d540`으로 저장본과 일치.
  - `make check` → **292 passed**, Ruff/compileall/mypy/CONTEXT_PASS (`logs/lap304/make-check.log`).
  - `bash checks/safety.sh check` → **SAFETY_PASS** (`logs/lap304/safety.log`).
  - probe 자체 `ruff check` 통과. 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **R1 U4/U5 재현 ACCEPT**: lap303 source `257c0563…`·report `5079de5a…` 불변, 두 fresh run
    바이트 동일, `failures=[]`, report가 `lap=303`과 자기 파일명을 정확히 기록.
  - **R2 U1/U2 ACCEPT(독립 유도)**: `cmp eax,0x7`(0x4644B8)에서 분기 수 8을 얻고 점프테이블
    `0x464B68`의 8개 DWORD를 **이미지 바이트로** 읽어 분기 주소를 복원 → 각 분기의
    `[esi+0x4]/[esi+0x8]` imm32 쌍 16개, 서로 다른 해상도 **5종**
    (320×200/640×480/800×600/1024×768/1280×1024). lap303 표와 주소·수치까지 일치.
  - **R3 direct writer ACCEPT-WITH-NOTE**: `0xE5BF1C`/`0xE5BF20`의 4바이트 참조를 파일 이미지에서
    전수 스캔해 **111개**, 디스어셈블 참조도 111개로 정확히 대응. 그중 쓰기는
    `0x431B79/0x431B7F/0x4324B8/0x4324C2` **4개**뿐이고 나머지 107개는 읽기.
    주의: lap303 정규식은 `mov <SIZE> PTR ds:…,`만 보므로 `a3` moffs 인코딩
    (`mov ds:0xe5bf1c,eax`)이 있었다면 놓쳤다. 이 이미지에는 그 형태가 없어 결과는 유효하다.
  - **R4 U3 ACCEPT-WITH-CORRECTION**: 실제 명령열은 `sar/sar/sub`가 아니라
    `cdq; sub eax,edx; sar reg,1`(0 방향 반올림 부호 나눗셈)을 **화면·다이얼로그 양쪽**에 적용한다
    (`0x4D6271/0x4D6272`, `0x4D6317/0x4D6318`, `0x4D6321/0x4D6328`, `0x4D6339/0x4D633A`).
    lap303 Python `halve_toward_zero`는 이 의미를 이미 맞게 구현했으므로 **수치 영향 0**이지만,
    lap303 앵커 집합은 그 4쌍을 빼고 있어 해당 바이트 드리프트를 못 잡는다(가드 사각).
    5개 해상도 origin/슬롯 rect를 독립 재계산해 lap303 값과 전부 일치
    (800×600 → origin `(240,145)`, slot0 `[260,119,540,143]`; 320×200만 화면 밖).
  - **R5 writer 범위 ACCEPT(하한 확정)**: `mov ecx,0xE5BF18` **773개** 호출지점에서 시작해
    ecx 별칭이 보존된 직접 호출만 depth≤3으로 닫으면 **90개 메서드**가 나오고, 그중
    `[this+0x4]/[this+0x8]`를 쓰는 함수는 `FUN_004644A0` **하나뿐**(16개 쓰기).
    → 직접 4 + 간접 16 = **20**이 이 닫힘 안에서는 전수, 전체로는 여전히 하한.
    남은 fail-open: `push 0xE5BF18` **291개**(객체를 스택 인자로 넘기는 경로), 가상/간접 호출,
    depth 3 제한.
  - **R6 신규 발견 — 모드 인자 출처 확정(CONFIRMED-STATIC)**: `ds:0x4ED810` 참조는 이미지 전체에서
    **6개뿐이며 전부 읽기**(쓰기 0). 값은 `.data` 초기화 이미지에서 **3**.
    `FUN_004644A0`은 `dec eax`→`cmp eax,0x7` 후 `table[2] = 0x464502` → **800×600**을 쓴다.
    `0x4644A0`의 호출자는 둘뿐이고 **둘 다 이 전역에서 모드를 받는다**:
    `0x4643C0`(←`FUN_00464360` 인자2, `0x423D50`에서 push) / `0x464C64`(←`FUN_00464BF0` 단일 인자,
    `0x42484E`·`0x424E85`·`0x4D0FCB`에서 공급). → lap301 후보 **A `(240,145)`가 정적 우세**,
    후보 B `(160,85)`는 모드 테이블 경로에서는 선택되지 않는다.
    caveat: `0x4ED810`은 쓰기 가능한 `.data`라 계산 포인터/파일 로드에 의한 런타임 변경은
    실행 없이 배제할 수 없고, `0x4324B8`(640×480 고정)·`0x431B79`(런타임 값) 두 직접 writer는
    모드 테이블 이후에도 전역을 덮을 수 있다. 따라서 **G1 제품 승격은 아니다.**
  - **R7 provenance ACCEPT**: `logs/lap299`(`8e735a9a…`), `logs/lap301`(`c312b42e…`),
    `logs/lap302`(`5190920f…`) 불변. lap303 소스가 pin하는 SHA는 원본 EXE·sprite 2개뿐이라
    W3식 미래 산출물 pin 함정 없음. lap301 report가 여전히 `"lap": 299`로 자기 lap을 오기하는
    기존 회귀는 **그대로 보존**했다(과거 기록을 고쳐 쓰지 않는다).
  - 제품 판정: G1~G4 **전부 미완료 유지**. PASS 완화·승격 없음.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 이번 바퀴는 middle tier 검수·진단이며 게임 코드/패치를 만들지 않았다. 사용자 승인 없음.
  - R6는 **정적 근거**다. 다이얼로그 구성 시점의 실제 전역값은 여전히 미관측이고,
    버튼 hitbox·슬롯 선택·로드 전이는 UNKNOWN이다.
  - work tier handoff(아래 V1~V3)는 전부 정적 범위이며 실행 허가를 요청하지 않는다.
- 다음 한 가지: 다음 새 work(Luna/Sonnet5/high)가 아래 V1~V3를 새 파일에서 수행한다.
  - **V1**: `push 0xE5BF18` 291개 인자 경로에서 피호출 함수가 `[arg+0x4]/[arg+0x8]`를 쓰는지
    조사해 writer 하한 20을 갱신하거나 20이 전수임을 밝힌다(정적, 실행 없음).
  - **V2**: `0x4324B8`(무조건 640×480 리셋)과 `0x431B79`(런타임 ebp/edi)를 포함하는
    `FUN_00431AB0`의 실행 조건과, 저장/불러오기 다이얼로그 구성(`0x4D6312` 읽기) 대비 **순서**를
    정적으로 유도한다. 이것이 R6의 800×600을 뒤집을 수 있는 유일한 정적 경로다.
  - **V3**: 중심식 가드에 `cdq`/`sub eax,edx` 4쌍(R4)과 `a3` moffs 쓰기 형태(R3)를 포함하도록
    앵커/정규식을 넓힌 회귀 probe를 새 파일로 만든다. 기존 lap303 산출물은 수정하지 않는다.
