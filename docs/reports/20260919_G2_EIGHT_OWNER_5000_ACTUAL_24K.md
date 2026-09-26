# G2 8인 각 전비5000 실제24k 실행 결과

실행: 2026-09-19T21:28:57.037994+09:00. 결과: **엄격 안정성 FAIL**.

## 실제 관측
- 새격리32bit Wine prefix, 핀된 원본/후보/bridge/save 사용. 8명 모두 첫 sample `used=cap=5000`, 총1160 occupied로 시작. fixture는 원본1200-slot 안의 assisted high-cost 구성이다.
- 원본 tick10020→34185, Δ24165 / 725.015초 / 146 samples. 관측read error0, tick rollback0, 프로세스 crash0, cleanup잔류0. G2 observer 자체는 `PASS_DURATION_MILESTONE`; G1 aggregate FAIL은 이 카드와 무관한 입력tag 미실행 때문이다.
- 독립 분석: mismatch sample0, peak occupied1176(1199동시점유 미도달), 1343 unique IDs, hp<=0→gap→newID24 chains, owner4 new TYPE7 IDs11. 정적cost와 occupied ledger는 146×8=1168 comparisons 전부일치.

## 실패 판정
- sample140 tick33185부터 마지막146까지 owner1 `used=5003 > cap=5000` 7회 연속.
- 직전구간 동일 fullID394322/slot1106/TYPE23이 owner3→owner1로 바뀌고 owner1 used4993→5003. 소유권이전과 +10cost 동반은 관측했으나 정확call 인과는 instrumentation 없으므로 미확정.
- 따라서 crash 없이24k가 흘렀다는 사실만으로 '8인 각5000 안정' PASS할 수 없다. cap 불변식이 깨졌고 arbitrary low-cost/globalpool/expanded save/LAN/144k도 미검증이다. 이전9/17과 동일현상이 재현됐다.

## 증거
- 외부: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260919_eight_owner_5000_stability_actual_v1`
- observer: `official_run1/g2_stock_24k_observation/summary.json`, trace `samples.jsonl`
- 독립: `independent_analysis_v1/analysis.json`; terminal `root_terminal_receipt_v1.json`
- 보호8pins 재해시 기록, 원본/reference/shared source 변경없음.
