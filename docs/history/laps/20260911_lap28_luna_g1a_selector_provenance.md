# 2026-09-11 | lap 28 | G1-A selector 정적 provenance work

- 목표 / 가설: lap26 FAIL은 원본 selector 결함보다 `0x004ED848`을 PS7 버튼의 즉시 상태로
  간주한 계약 문제일 수 있다. 두 PS7 control의 생성·hit-test·callback부터 실제 write/branch까지
  추적해 이 가설의 정적 경계를 고정한다.
- 역할: Codex 새 세션, 사용자 지정 hands-on Luna/high work. 자기 결과를 최종 승인하지 않는다.
  게임/하네스/EXE/DLL/asset 변경과 새 실행은 하지 않았다.
- 원본 / 환경 / fixture: SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`인 격리 PE32 원본,
  기존 lap26 artifact만 참고. 새 fixture·Wine·display를 만들지 않았다.
- 명령: `sha256sum`으로 원본을 재확인하고 `objdump -h`, `objdump -s`,
  `objdump -d -Mintel`로 `0x00424A9F`, `0x004B8A10`, `0x004B91E0`, `0x00404C20`,
  `0x00405540`, `0x00405550`, `0x004B9341`, `0x004B9390`을 읽기 전용 대조했다.
- 결과: PS dispatcher가 `0x004B8A10`에서 두 object `0x0106A600`/`0x0106A7C8`을 만들고,
  `0x004B91E0` poll이 `0x00405560`→`0x00404C20`→vtable `+0x54`로 hit-test/input
  callback을 전달한다. callback state는 `[object+0xA4]`에 쓰고 읽는다. 이후 branch가
  `0x004ED848`에 WORD 0 또는 1을 기록한다. 정확한 old bytes와 chain은
  `analysis/memory_maps/player_offsets.md` lap28에 기록했다.
- 판정: **STATIC PROVENANCE PASS / UI LABEL SEMANTICS UNKNOWN**. chain은 확인됐지만 object
  순서와 한국어 `여럿이하기`/`혼자하기` 대응은 바이너리 정적 자료만으로 확정되지 않는다.
  따라서 `혼자=1/여럿=0`, lap26 click gate, 입력 전달 및 실제 selector run은 PASS로 쓰지 않는다.
- 검증: 원본 SHA PASS. make/check·runtime 테스트는 구현 변경이 없어 새로 요구되는 변경 검증이
  아니며, 이 lap에서 게임 실행·g1-baseline·patch old/new/restore는 SKIP(N/A)다. 문서 장부만
  갱신했고 commit/push는 하지 않았다.
- 다음: 새 Sol/high가 원본 SHA·주소·old bytes·vtable edge·label 의미 경계를 독립 확인한다.
  확인 전에는 하네스/게임 변경과 새 run을 시작하지 않는다.
