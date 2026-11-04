from marksweep.scoring import roll_up, band_for
from marksweep.pipeline import merge_boxes


def test_roll_up_redistributes_na():
    bd = [{"key": "visual", "weight": 0.3, "score": 80, "na": False},
          {"key": "aural", "weight": 0.1, "score": 0, "na": True},
          {"key": "conceptual", "weight": 0.15, "score": 60, "na": False},
          {"key": "goods_services", "weight": 0.15, "score": 60, "na": False},
          {"key": "distinctiveness", "weight": 0.15, "score": 90, "na": False},
          {"key": "bad_faith", "weight": 0.15, "score": 30, "na": False}]
    s = roll_up(bd)
    assert 60 < s < 70 and band_for(s) == "red"


def test_merge_boxes_dedups_and_drops_specks():
    res = [{"concept": "brand logo", "boxes": [{"left": 0, "top": 0, "right": 100, "bottom": 100, "object_id": "1"},
                                                {"left": 2, "top": 2, "right": 98, "bottom": 98, "object_id": "2"},
                                                {"left": 500, "top": 500, "right": 510, "bottom": 510, "object_id": "3"}]},
           {"concept": "printed brand name", "boxes": [{"left": 300, "top": 0, "right": 400, "bottom": 50, "object_id": "1"}]}]
    out = merge_boxes(res, 1000, 1000)
    assert len(out) == 2 and {b["concept"] for b in out} == {"brand logo", "printed brand name"}
