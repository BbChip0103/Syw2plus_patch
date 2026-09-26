# 2026-09-21 | lap 429 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high / **work(실무)**.
  세션 지정 역할과 `docs/MODEL_ROUTING.md`/`docs/STATUS.md` 「다음 한 가지」(work Sonnet5/high)가 일치.

- 가설 / 사용자 관찰: W16 카드
  (`docs/work/active/G2_UNIT_700_CORRUPTION_EXTENT_LAP428.md`) P-K —
  lap427 `movement_state_probe_pj.py`의 읽기 창만 `+0x6e0`~`+0x71c` 16 DWORD로 넓혀
  `unit3565+0x700` 오염이 표적 쌍 write(K1)인지 블록 복사(K2)인지 산발(K3)인지 비재현(K4)인지
  가른다. fixture/DENSE/STOP_TICK/K-guard는 lap421~427과 동일.

- 예상 PASS / FAIL 조건: 전이 sample에서 바뀐 창 내 DWORD 개수 `n`으로 K1~K4 중 하나로 확정.
  **이번 lap은 이 측정에 도달하지 못했다** — 아래 인프라 blocker로 게임 실행 자체를
  시작하지 않았다.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - 제품 코드/바이너리 변경 **0**. 게임 소스(`Syw2plus_re/Syw2plus`) 변경 **0**.
  - 새 파일(uncommitted, git 미추적 temp): `temp/Syw2plus_patch/g2_capacity/
    20260921_lap429_unit_700_corruption_extent_prep/movement_state_probe_pk.py`.
  - 문서 변경(이 세션): `docs/STATUS.md`(129줄, 「다음 한 가지」/「검증 상태」/「바퀴 기록」
    각 1개 항목 갱신), `loop/ESCALATE_SOL`(§16 신규), 이 파일.
  - `LOOP_ALLOW_COMMITS`가 설정되지 않았으므로 커밋 **0**(uncommitted로 보존).

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 SHA(직접 재해시): `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
    (`Syw2plus_re/Syw2plus/syw2plus_original.exe`) — 불변, `docs/MODEL_ROUTING.md`/과거 lap
    핀과 일치.
  - 후보 SHA(예정, 미빌드 실행): `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`
    (N=4001 marked compat, lap413/414/419/420/421/423/425/427과 동일).
  - fixture(예정, 미실행): op7 resource-only, 8 owner, N=4001, seed42, display `:3847`
    (새 번호, `:3846`은 lap427이 사용).
  - 실제 실행 환경: 이번 lap은 **게임을 실행하지 않았다.** 대신 리포지토리 환경만 확인 —
    공유 루트 파일시스템 `df -h /`: `1.7T 크기, 1.6T 사용, 3.9G 여유, 100% 사용`.
    `df -i /`: inode 12% 사용(공간이 문제이지 inode는 아니다).
    `who`: `bbchip13`(seat0/tty2), `lww`(pts/23, pts/34), `dev_00`(현재 세션) 동시 활성.
    `local/runtime/`: 141개 회차 디렉터리, 합계 341G(예: `20260920_024257_3565924_0` 단독 2.7G).
    `temp/Syw2plus_patch/g2_capacity/`: 2.2G(작음, 문제 아님).

- 실행 명령 / 로그 / 캡처 경로 및 해시:
  1. `python3 -m pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
     patches/population/test_runtime_bridge_contract.py -q` → `6 passed in 90.79s`.
  2. `bash checks/safety.sh check` → `SAFETY_PASS`.
  3. `sha256sum syw2plus_original.exe`(원본 위치) →
     `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(불변 확인).
  4. `df -h /`, `df -i /`, `who`, `ps -u 900/910`, `du -sh local/runtime`,
     `du -sh local/runtime/20260920_024257_3565924_0`, `ls local/runtime | wc -l` — 위 수치의
     직접 근거(명령 스스로가 증거이며 파일로 별도 저장하지 않음, 세션 로그에 원문 보존).
  5. `python3 -m py_compile .../movement_state_probe_pk.py` → 예외 없음.
     `python3 -c "import ast; ast.parse(open(p).read())"` → `AST_OK`.
  6. `diff` lap427 `movement_state_probe_pj.py` vs 신규 `movement_state_probe_pk.py` →
     델타가 정확히 (a) docstring, (b) `win`/`WIN_LO_OFFSET`/`WIN_COUNT` 필드 1개,
     (c) `request_id` 접두사, (d) `display`(`:3846`→`:3847`), (e) `schema` 태그, (f) 로그
     문자열의 lap 번호 나열, **6곳**뿐임을 확인 — 새 가설/새 주소 추가 없음.
  - `runtime_env.prepare()` 호출/Xvfb/wine 기동은 **시도하지 않았다**(아래 판정 근거).

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - targeted 6 passed / `SAFETY_PASS` / 원본 불변 — **PASS**(Fast 게이트).
  - probe delta 검증(컴파일+diff 최소성) — **PASS**.
  - W16 P-K 본 측정(게임 실행, K1~K4 판정) — **BLOCKED**(디스크, 카드 §3의 실패 예산이
    아니라 인프라 전제조건 미충족). "실패 가설 2회"에 해당하지 않는다 — 가설을 시도조차
    하지 않았다.
  - `make check`(전체 784) — **SKIP**, 이번 회차 source 미변경(N22 규칙 적용, INBOX
    2026-09-20 21:58/N22 그대로).

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 회귀 없음(제품 코드 변경 0).
  - **신규 위험 1건(제품과 무관, 인프라):** 공유 루트 디스크 3.9G/100% 여유. 다음 게임 실행
    카드(W16 포함, 그리고 향후 모든 G2 P-계열 실행 회차)가 이 상태로는 **전부 막힌다.**
    강행 시 이 세션이 아닌 다른 사용자 세션에 영향을 줄 수 있어 이번 lap은 강행하지 않았다.
  - 독립 검수: 아직 없음(이번 lap 자체가 work 1회차). middle이 `loop/ESCALATE_SOL` §16을
    다음에 처리해야 한다.
  - 사용자 승인: `local/runtime/` 대량 정리는 destructive라 사용자/middle 승인 없이는
    시도하지 않았다.

- 다음 한 가지: middle(또는 필요 시 사용자)이 `loop/ESCALATE_SOL` §16의 판정 3건
  (local/runtime 정리 여부·방식, 정책 전까지 G2 실행 전면 정지 인지, DEFAULT_RUNTIME_ROOT를
  `/data`로 옮기는 안의 채택 여부)을 처리한 뒤, 다음 work가 `movement_state_probe_pk.py`를
  그대로(셸 background 금지, 동기 실행) 돌려 W16 P-K를 완료한다.
