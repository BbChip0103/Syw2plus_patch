# 2026-10-11 | lap1270 | H-TRVAR2613 staging handoff

- 역할/모델: hands-on work; Codex App에서 resolved ID/effort 미노출, 추측하지 않음.
- 가설/조건: lap1264의 default-on display DLL + `.hd` 입력과 실제 8-lane Wine 결과가 INBOX 승인 스테이징 계약에 부합하면 같은 실행은 재사용하고, 새 조립물만 검증한다. 전달 파일에는 공식/변형 EXE와 안내문을 넣지 않으며 bat에서 `SYW2_G1_HD_PACK`을 설정하지 않는다.
- 이전 결과 독립 대조: lap1264 구현/테스트 SHA 및 raw SHA는 lap1265 기록과 동일. 두 변형 모두 newgame off/on·save006 off/on PASS. 공식2613 baseline pair/save006 및 변형 EXE들은 display-only Wine startup/newgame/load만 증명한다. `tree_plus` runtime-mask reject1 UNKNOWN은 공개 유지. Windows·G2 pool/8인 부하·G9 자리순서·G1 마일스톤은 미검증.
- 스테이징: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261011_lap1270_htrvar/user_test_staging/`. `_inmm.dll` SHA256 `205b89b2c6ff3ae530ed3cbb705b644ea454404a0efee37de3980a85da36c28c`; sidecar `sibling_tree_v3` 39,937 파일/1,063,405,486 B를 같은 상대경로로 복사; 782 `.hd` dirs. 3 direct bat은 각각 official2613, G2_G6_G8, G2_G6_G8_G9 이름을 실행하고 `g1_via_dxwnd.bat`은 기존 계약대로 `dxwnd\dxwnd.exe`를 연다. EXE 0, TXT 0, pack env 0.
- SHA 목록: `FILES.sha256` 39,942 entry, 파일 SHA256 `151148f2b5ffd6e4ad12013ce32de53c94e78d894a52d83f7271a19283656707`; staged 모든 entry와 sidecar 원본 경로/바이트를 재계산 비교해 MATCH. DLL/bat 포함 총 39,943 files, 1,067,854,351 B(목록 포함).
- 실제 실행/회귀: 새 게임 실행 없음. 동일 DLL/sidecar에서 lap1264 8-lane raw와 lap1265 fresh middle 결과 재사용; 실행 재반복은 검증 과잉 방지 규칙에 따라 SKIP. 전체 Fast 재실행 불필요(제품 코드 변경 없음).
- 변경: `docs/STATUS.md`, 이 lap 기록; 스테이징은 공유 temp만. 기존 uncommitted 제품 변경·raw·원본·pins 보존. `260921_temp` 배치/이전판 archive/커밋 없음.
- 다음 한 가지: fresh middle이 새 스테이징 manifest·bat·sidecar 구조와 기존 raw 범위를 독립 확인. PASS 후 root가 INBOX 사전승인에 따라 전달/기존판 archive; Windows/G2/G9/G1 acceptance는 미검증으로 공개.
