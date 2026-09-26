"""lap583 strategy: W49R 화면 판정식이 기존 PNG에서 참/거짓을 가르는지 오프라인 확인(읽기 전용).

N208 재발 방지: 카드 발행 전에 양성 대조(2026-09-20 같은 Xvfb/Wine 경로의 월드 렌더 캡처)와
음성 대조(lap581 W49 캡처)에 고정식을 적용해 PASS/FAIL이 갈리는지 본다. 게임 실행 0.
"""
import hashlib
import json
from pathlib import Path

from PIL import Image

CAPTURES = Path("/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/captures")
WORLD_BOX = (0, 30, 800, 470)       # 800x600 게임 창 안 HUD 상단줄·하단 패널 제외
MINIMAP_BOX = (60, 545, 120, 580)   # 미니맵 마름모 내부
LUMA_THRESHOLD = 24
V1_MIN_FRACTION = 0.30

CONTROLS = {
    "positive": [
        "20260920_024748_supply5000_shot-slot1200-scene.png",
        "20260920_024208_20260920_024130_3560257_0_3562559_scene_after_lobby_start_1789839728824961377.png",
        "20260920_024209_20260920_024130_3560257_0_3562559_minimap_before_1789839729916174613.png",
    ],
    "negative": [
        "20260925_052854_lap581_w49_preseed.png",
        "20260925_052856_lap581_w49_t0.png",
        "20260925_052955_lap581_w49_plus2000.png",
        "20260925_053354_lap581_w49_plus10000.png",
        "20260925_053354_lap581_w49_minimap.png",
    ],
}


def nonblack_fraction(image: Image.Image, box: tuple[int, int, int, int]) -> float:
    pixels = list(image.crop(box).getdata())
    return sum(1 for p in pixels if max(p[:3]) > LUMA_THRESHOLD) / len(pixels)


def main() -> None:
    rows = []
    for group, names in CONTROLS.items():
        for name in names:
            path = CAPTURES / name
            image = Image.open(path).convert("RGB")
            world = nonblack_fraction(image, WORLD_BOX)
            rows.append({
                "group": group,
                "file": name,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "size": list(image.size),
                "world_fraction": round(world, 4),
                "v1_pass": world >= V1_MIN_FRACTION,
                "minimap_interior_fraction": round(nonblack_fraction(image, MINIMAP_BOX), 4),
            })
    assertions = {
        "A1_positive_all_v1_pass": all(r["v1_pass"] for r in rows if r["group"] == "positive"),
        "A2_negative_all_v1_fail": not any(r["v1_pass"] for r in rows if r["group"] == "negative"),
        "A3_minimap_interior_blank_everywhere": all(r["minimap_interior_fraction"] == 0.0 for r in rows),
    }
    out = json.dumps({"rows": rows, "assertions": assertions}, ensure_ascii=False, sort_keys=True)
    print(out)
    print("canonical_sha256=" + hashlib.sha256(out.encode()).hexdigest())
    if not (assertions["A1_positive_all_v1_pass"] and assertions["A2_negative_all_v1_fail"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
