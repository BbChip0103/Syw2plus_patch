# 2026-10-04 | lap914 | G1 W70 P5-H — 패널 원천 확정(`fnt/pannel*.spr` ← `0x4663E0`) / 패널 층 계약 / P5-H work 카드 (strategy)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5-1`, 러너 지정 strategy(큰 방향·상위 계획) 역할, 일반 작업자.
  자동 폴백 아님. 게임 코드·하네스·validator 수정0, 게임 실행0, build0, subagent0, 커밋0. `loop/.lap_counter` 914 읽기만
  (러너 주입 문구의 lap=913보다 파일이 최신이다).
- 가설 / 사용자 관찰: lap913 middle이 D-1R을 `PASS(partial)`로 받고, 패널 표면 800×203 중 161,878픽셀(99.68%)의 writer가 미분류라
  P5-H 구현 근거가 없다며 `HOLD_PANEL_ORIGIN_UNPROVEN`으로 승격했다. 이 세션의 질문은 (1) 패널 바닥을 무엇이 그리는가,
  (2) lap911의 층 미러 가설로 설명되는가, (3) work에 넘길 최소 계약(원천·색상키·표면·rect)은 무엇인가다.
  사용자 상시 지시(2026-10-03 14:37 G1 자율 지속, 구현 우선, 묻지 말고 결정)를 적용했다.
- 예상 PASS / FAIL 조건: 판정 회차다. 정적 추적으로 후보(`0x4663E0`이 `fnt\pannelj.spr`를 패널에 그린다)를 세운 뒤, 기존 raw로 깨뜨릴 수 있는
  예측 넷을 `recalculate.py` 머리에 적고 실행했다 — Q1 범주 10 픽셀이 pannelj 불투명 칸 위 ≥0.98(무관하면 0.823), Q2 PNG의 인덱스별 최빈 RGB
  일치율이 pannelj ≥0.70이고 다른 그림·어긋난 대조군보다 뚜렷이 높음, Q3 키 칸 위의 범주 10은 미니맵 구역 안, Q4 unknown은 y≥512.
  반증 기준은 Q1 <0.90 또는 Q2에서 pannelj가 최고가 아니거나 <0.5. 넷 다 성립했다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 `docs/work/active/G1_STRATEGY_W70_P5H_PANEL_LAYER_LAP914.md`,
  `analysis/memory_maps/g1_w70_p5h_panel_surface_writers_lap914.md`, 이 기록,
  `docs/history/20261004_lap914_prior_lap913_escalate_sol_archive.md`, `docs/history/20261004_inbox_lap914_precompaction.md`.
  갱신 `docs/STATUS.md`, `docs/feedback/INBOX.md`, `docs/feedback/APPROVALS.md`. `loop/ESCALATE_SOL` 제거(보존본과 `cmp` 일치 확인 뒤).
  제품/하네스/test/validator/golden/안전핀/원본/save/기존 raw·map·PNG 변경0. uncommitted. HEAD `5d128e2f79581050ae81b418116b3c5c9cd98355`는
  provenance일 뿐이다. 읽은 source SHA256: `g1_mirror2x.c` `e6f4d0ef10db2fda9a1dc7a837345af07c7b0ef9f2453ba254db8225ba1f8aab`,
  `g1_census.c` `940f48582a00a6a7cbd29919c33d47a4b87c017a7f7cd93b2c0991dd82e1d3d4`,
  `direct_draw_trace.c` `ea09ed6c836324decb31238a6d73539a6b24a68d92e3c8f200cf37841e7c7aef`(뒤 둘은 lap912 기록과 일치),
  `g1_hd_asset.c` `7833f32878c02944fbb02bc616192fe21d2860eb5f71781f16d74e69cd6feedf`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 새 실행 없음. 보호 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`를 읽기 전용으로 디스어셈블했다. 읽은 기존 증거는 lap912 census-only
  원본 lane(save006 `616b7997…d064`, 일본 패널) 한 장면이다. 8 player records는 활성 8인 부하 증명이 아니다.
  패널 그림 SHA256: `pannelk.spr` `941036da558f2c1fd96dc5eabd6d662ad1062be1f7f8ad282e531c3b98b4983e`,
  `pannelj.spr` `ca59e69786ca43561d20b296c04550cdab9ca6f736697344d0f8cf644fbd39e8`,
  `pannelc.spr` `4b7cf7f9ea8437f89670c45612374592ba4d1b938842c55e2b6cbe7995a8b5d9`.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap914_strategy_review/`.
  `i686-w64-mingw32-objdump -d -Mintel <원본 EXE> > exe_disasm.txt`, `.venv/bin/python recalculate.py`, `.venv/bin/python render_panel.py`.
  `recalculate.py` SHA256 `17c88e573368319b45b28425146ec980cffc8302b82e0d5ae1efccd57a91cc71`,
  `recalculation.json` SHA256 `f9d51b0857ba0e0d7b43095d1e61c17acaeb0147d8c142e8eb888d428ff458d7`,
  `render_panel.py` SHA256 `4bd00730b1e033df78212ce7aae9e55363f73cdfeabffeee4fed5c222b1a612a`,
  `pannelj_decoded_vs_selection_hud.png` SHA256 `5df1df081e5c3899c2b2626363395d7a8130ef4fa9bde17c846998794620e188`.
  입력 13개: `20261004_lap912_d1r_census_r2/artifacts/census/`의 map·raw·trace·probe-result·PNG 4장, `fnt/pannel{k,j,c}.spr`, 원본 EXE,
  lap counter(읽기만, 계산 전후 SHA 변화 0).

## 측정값 / 판정

**lap913 HOLD 해소 — 패널 바닥은 `fnt\pannel{k,j,c}.spr` 한 프레임을 렌더러 프리미티브 `0x4663E0`이 그린 것 / P5-H `FEASIBLE` /
패널 층 계약 H1~H5 / 다음 work = P5-H 구현 / G1 HOLD.**

1. 정적: 패널 표면 `[0x104F814]`(생성 `0x4922D0`, 800×203, 색상키 `0xFE`)를 잠그는 곳은 6곳, 쓰는 것은 5곳이다 — `0x4663E0` 호출 4곳
   (`0x41B787`·`0x41C5A0`·`0x424965`·`0x441533`)과 미니맵 한 곳(`0x41C524` 지형 직접 쓰기, `0x41C52E` 점 set_pixel).
   `0x4663E0(x,y,w,h,src)`는 rect 전체를 쓰며 src의 `0xFE n`을 목적지에 `0xFE` n개로 쓴다. census 9 pin에 없었다.
2. 그림: `0x419B50(nation)`이 `fnt\pannelk.spr`·`pannelj.spr`·`pannelc.spr` 중 하나를 `0xB92CE0`에 읽는다. header는 `(9, 831, h, 1)`,
   h = 163·143·160. `0x4663E0` 알고리즘으로 831×h를 풀면 세 파일 모두 파일 끝과 정확히 맞는다(데이터 offset 3060).
3. Q1: census map 64장의 범주 10 픽셀 4,449,556개가 **전부** pannelj 불투명 칸 위(1.000, 맵별 최솟값 1.000), y<457에는 0.
   무관한 그림이면 기대값 0.823이다.
4. Q2: pannelj 일치율 `selection` 0.735 · `drag` 0.796 · `minimap` 0.784 · `production` 0.793. pannelk 0.256~0.267, pannelc 0.266~0.281,
   어긋난 pannelj(dx3 dy2 / dx−5) 0.307~0.353.
5. Q3: 키 칸 위의 범주 10은 0픽셀(미니맵 자리는 그림에서 불투명 검정이다). Q4: 마지막 맵 unknown 7,251은 전부 y 512..599이고 전부 pannelj
   불투명 칸이다 — 지형 전사가 다시 덮지 않는 행에서 안 바뀐 패널 픽셀이며, census가 바뀐 픽셀만 적어서 남은 것이다.
6. 전사: 표본 19개 전부 `BltFast((0,457) ← [0,0,800,143], flags 17)`, 반환 `0x41C60C`. 143 = pannelj 높이. y 457..479의 pannelj 불투명 칸은
   2,157, 같은 행의 범주 10은 맵 1·32·64에서 1,582·2,101·2,101.
7. 그림 직접 확인: 풀어 그린 pannelj(앞 800열)와 `selection.png` y457..599를 위아래로 붙여 봤다. 미니맵 마름모·초상화 원·F1~F11 칸·명령 4×3 칸이
   같은 자리다. 캡처 쪽에는 깃발·초상화·버튼·글자가 얹혀 있다.
8. 폭 831 > pitch 800: 행이 800에서 접힌다. 오프라인으로 접어 보면 버퍼의 행 0..142는 그림의 앞 800열과 143/143행 같다.
   frame 800×143의 SHA256 `f649fe68a8f9a71b9e451c01cb5b0a1d79fbb06607cc8d566d3d30d108b66000`을 work의 실행 대조값(PH-b)으로 줬다.
9. 계약(카드 §2): H1 반환 주소 4곳으로 패널 버퍼 결합 + 전사 때 잠근 포인터·pitch 일치, H2 `0x4663E0` hook과 800×h frame·자산 키,
   H3 층 평면과 키 규칙(키가 아닌 칸은 키 subpixel을 내지 않는다), H4 색상키 전사와 내용 대조(다르면 nearest), H5 패널 대상의 다른 writer는
   screen 합성 안 함. 미니맵은 hook하지 않는다(원천 그림 없음, 내용 대조가 nearest로 보낸다).
10. lap913 handoff와 다른 점: 3번의 두 선택지(패널 한정 관측 probe / P5-T 우선)를 고르지 않고 P5-H를 바로 구현한다. census 결함 두 건은
    다음 census 회차의 첫 작업으로 보류했다. "완성 800 화면 확대를 HD asset이라 부르지 않는다"는 유지 — 단위는 자산 프레임이다(카드 §3).
11. 사전 등록 PH-c: 유효 coverage p50 0.692 → 0.82~0.86(범주 10 p50 70,637.5 + unknown 7,251). 90%에는 P5-T가 더 필요하다
    (범주 6·7 p50 합 54,588.5 = 11.4%).

- PASS/FAIL/SKIP: 판정 완료(재계산 재현 가능). hook·층 구현·실행은 work 몫이며 이 회차에서 실행되지 않았다.
  `make lint`·`make typecheck`·문서 연동 테스트·`checks/safety.sh check`·`checks/context_limits.py` 결과는 STATUS에 적는다.
  전체 `make check`와 새 runtime은 **SKIP** — 이 회차는 문서만 바꿨고, 다음 work가 source를 바꾼 뒤 전체 Fast를 돌린다.
  과거 full-test exit0(lap912 포함)은 현재 검증으로 쓰지 않는다.
- 승격 marker 처리: lap913 `loop/ESCALATE_SOL`(SHA256 `c32b285ddddefc0d84adcc0458ea6a01623283800c8ce420f8740d99a2720472`)을
  `docs/history/20261004_lap914_prior_lap913_escalate_sol_archive.md`에 byte-exact 보존하고 `cmp` 일치 확인 뒤 제거했다. 판정으로 해소했으며
  다음 회차를 work로 보낸다. 이 세션에는 승격 조건(미설명 필수 검사 실패·근거 충돌·마일스톤 경계)이 없다 — 재계산은 lap913 수치와 일치했고
  (패널 set_pixel 522, 전사 표본 19, unknown 7,251), P단계 전환은 마일스톤 경계가 아니다(lap858 판정).
- 문서 한도: INBOX 342줄 전문(SHA256 `c8202281b74db18593ed189eb96d48faec7c0fa7904391c77b9f1e8067995546`)을
  `docs/history/20261004_inbox_lap914_precompaction.md`에 byte-exact 보존한 뒤, 체크 완료 6항목(lap786 전사 오류 처리, lap802·803·804 G2 Phase C/D,
  17:0x G1 production cell 힌트, lap908 middle 색인)만 포인터로 바꿨다. 상시 지시·미결·반려 삭제0.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `0x4663E0`이 패널에 쓰는 순간을 hook으로 본 적은 없다(결과 픽셀 대조다, PH-b가 실행에서 확인).
  조선·명 패널(높이 163·160)과 gate가 닫힌 장면은 미실행이다. 전사에 더하는 읽기 전용 Lock과 114,400칸 대조의 비용은 재지 않았다
  (현재 p95 여유 +8~9ms/한도 +16ms). 패널 가장자리 한 픽셀은 키 규칙 때문에 nearest와 같다. `ds:0xE5D42C`를 직접 읽는 다른 네 곳
  (`0x406077`·`0x493374`·`0x49339A`·`0x4B5485`)의 대상은 보지 않았다. P5-H·P5-T·D-2 스크롤 성능·최종 입력·전체 HD coverage ≥ 90%·
  두 번째 장면·G1 사용자 승인은 미검증이다. 계획 승인·G1 마일스톤 아님. 제품 코드·실행 증거가 늘지 않은 회차가 lap913·914 연속 2회이므로
  다음은 반드시 work 실행이다.
- 다음 한 가지: work가 `G1_STRATEGY_W70_P5H_PANEL_LAYER_LAP914.md` §4.1을 수행한다 — 단위 RED(접힘 frame·키 규칙·전사·결합) → H1~H5 구현 →
  fresh pair GREEN(PH-a·PH-b 포함) → B′ 2 pair → C 3 pair, HUD 1600 캡처 직접 확인.
