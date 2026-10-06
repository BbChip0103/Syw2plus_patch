# 2026-10-01 | lap 829 | G1 W70 P1 asset-key feasibility review

- 실제 provider/model/effort / 지정 역할: current native Codex session; middle tier 지정. 런타임의 정확한 model ID/effort는 이 surface에 노출되지 않아 주장하지 않음.
- 목표 / 가설: lap828 fixed-terrain writer raw를 독립 재계산하고, `0x468C30` source가 안정적인 `(tile file, frame)` key로 한 bounded work lap 안에 귀속 가능한지 판정한다.
- 예상 PASS / FAIL 조건: raw SHA·3 watch hit·PS3 writer 귀속이 재현되고 원본 정적 계산식이 file/frame→source를 직접 고정하면 `FEASIBLE`; 저수준 cache copy 외 key 경계가 없으면 `BLOCKED`; raw와 disassembly가 충돌하면 즉시 재승격한다.
- 변경 파일 / source fingerprint / 커밋: 문서 압축 archive, `docs/STATUS.md`, `docs/feedback/APPROVALS.md`, 이 lap 기록. 게임/하네스/EXE 변경 없음, 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / fixture: protected original `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`; lap828 private Wine32/Xvfb run만 read-only 재검수했다.
- 실행 명령 / 근거: `sha256sum`으로 writer/census/present raw를 재계산하고 `jq`로 event를 재집계; protected original을 `objdump -d -M intel --start-address=0x435400 --stop-address=0x435680` 및 `0x468c20..0x468cc0`로 확인; 기존 YTL 계약 `../Syw2plus_re/analysis/memory_maps/ytl_scanline_rle_00468c30_0811.md`를 대조했다.
- raw 재계산: writer-events `b7e9fc9c5d1e5c71ac64ac1e5747bef631c1f6536fc962d2e65287a88aa45178`, census `53c2d3bf5fff852ec549746e1fa92e9f92509038a15555c18a062ae88541d957`, present `b32f7bc5e33a680dde370bf090e69163d46641af54a419230aa9bf0f5ac5e0cc`로 lap828 기록과 일치. 이벤트는 entry 181, watch-arm 1, write 3이다.
- runtime 확인: 세 write 모두 PS3/tick `2188291105`, origin `0x4324E0`, fixed points `(64,64)/(416,256)/(768,448)`이며 writer는 `0x468C93/0x468C9C`. 이는 fixed buffer와 YTL row copy 연결을 지지하지만 자체로 asset key를 담지는 않는다.
- 정적 확인: `FUN_00435400` entry `0x435400`의 arg1은 tile-file id, arg2는 frame id다. `0x43540F..0x43541D`가 `file*0xBF8`을 만들고, `0x435568..0x435593`은 `index=file*0x2FE+frame`, `source=[0xB65E8C+file*0xBF8]+[0xB65758+4*index]`로 `0x468C30`에 넘긴다. clipped/fog branches도 같은 base/offset table을 쓴다.
- 기존 독립 근거: YTL 433개/15,820 frame 전수에서 file-local offset table과 `[skip,count,pixels]` 행 계약이 고정돼 있고, runtime table의 앞 44 offset이 `hill0.ytl` 44 frame과 순서대로 대응한다. 따라서 `(file,frame,source digest)`는 검증 가능한 stable key 후보이며 광범위 resource ownership 추적은 불필요하다.
- 판정: **`FEASIBLE` (high confidence), G1 HOLD.** lap828의 `BLOCKED/strategy`는 저수준 watchpoint가 key를 직접 노출하지 않았다는 정확한 경계였고, 현재 정적 근거와 충돌하지 않는다. `loop/ESCALATE_SOL`은 archive 후 해소한다.
- work-tier handoff: 제품 코드 없이 trace/test만 수정해 `0x435400`의 6개 인자와 renderer buffer를 기록하고, `0x435593/0x4355D7/0x43561E/0x435662` 및 `0x435910/0x435959` 중 실제 branch에서 pushed source를 기록한다. 같은 event에서 위 table 식을 독립 계산해 equality를 raw에 남긴다.
- work PASS: same save006+RIGHT fresh run에서 PS3·renderer buffer `0xBA3D30`, nonzero file/frame event, computed source==pushed source, 동일 key의 source-byte digest 반복 일치, camera 변화, source unchanged, cleanup PASS. 이 조건이면 P1 asset-key mapping PASS(partial)로 넘긴다.
- work FAIL/중단: fixed-buffer write가 있는데 `0x435400`이 0회이거나 table equality가 깨지면 raw/static 충돌로 즉시 `ESCALATE_SOL`; key는 잡히나 동일 key digest가 변하면 mutation 원인을 한 회차 안에서 가르고 설명 불가 시 `BLOCKED/strategy`. W70/Scale2x/GDI 구현은 이 probe 전 금지한다.
- 다음 한 가지: Luna/work가 위 exact runtime key trace를 fresh 1회차로 구현·실행하고 raw+targeted tests+Fast를 남긴다.
