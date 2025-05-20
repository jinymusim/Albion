from albionoverlay.utils.utils import iou

class SimpleTracker:
    def __init__(self, iou_thresh=0.5, max_lost=10):
        self.next_id = 1
        self.tracks = {}  # id -> [box, class_name, conf, age]
        self.iou_thresh = iou_thresh
        self.max_lost = max_lost

    def update(self, detections):
        updated = {}
        unmatched_dets = detections.copy()
        used_ids = set()

        # First pass: match with IOU
        for tid, (prev_box, name, _, age) in list(self.tracks.items()):
            best_match = None
            best_iou = self.iou_thresh
            for i, det in enumerate(unmatched_dets):
                x1, y1, x2, y2, conf, cls = det
                if cls != name:
                    continue
                iou_score = iou((x1, y1, x2, y2), prev_box)
                if iou_score > best_iou:
                    best_iou = iou_score
                    best_match = (i, det)

            if best_match:
                i, det = best_match
                del unmatched_dets[i]
                updated[tid] = [det[:4], name, det[4], 0]
                used_ids.add(tid)
            else:
                # Increase age if not matched
                if age < self.max_lost:
                    updated[tid] = [prev_box, name, 0.0, age + 1]

        # Second pass: new detections
        for det in unmatched_dets:
            x1, y1, x2, y2, conf, cls = det
            updated[self.next_id] = [(x1, y1, x2, y2), cls, conf, 0]
            self.next_id += 1

        self.tracks = updated

        # Return active tracks
        results = []
        for tid, (box, cls, conf, age) in updated.items():
            if age == 0:  # only return freshly matched
                x1, y1, x2, y2 = box
                results.append((x1, y1, x2, y2, conf, cls, tid))
        return results
