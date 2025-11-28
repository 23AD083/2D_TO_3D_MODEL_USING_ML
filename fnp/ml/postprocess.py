from typing import List, Dict, Any


def merge_ml_into_plan(plan: Dict[str, Any], ml_result: Dict[str, Any], pixels_per_meter: float, img_width: int, img_height: int) -> Dict[str, Any]:
    def px_to_m(point):
        x, y = point
        xm = (x - img_width / 2.0) / pixels_per_meter
        ym = (img_height / 2.0 - y) / pixels_per_meter
        return [xm, ym]

    rooms_m: List[List[List[float]]] = []
    for poly in ml_result.get("rooms", []):
        rooms_m.append([px_to_m(pt) for pt in poly])

    plan["rooms"] = rooms_m
    if "labels" in ml_result:
        plan["labels"] = ml_result["labels"]
    return plan


