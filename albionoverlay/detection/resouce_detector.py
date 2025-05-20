import onnxruntime as ort
import numpy as np
import yaml
import cv2

class Detector:
    def __init__(
            self,
            onnx_path: str,
            data_yaml: str,
            input_size: int = 640,
            iou_thres: float  = 0.45
        ):
        # load class names
        with open(data_yaml) as f:
            data = yaml.safe_load(f)
        self.class_names: list[str] = list(data['names'].values())
        self.nc = len(self.class_names)

        # ONNX session
        available_providers = ort.get_available_providers()
        if "CUDAExecutionProvider" in available_providers:
            self.session = ort.InferenceSession(onnx_path, providers=["CUDAExecutionProvider"])
            print("[INFO] Using GPU for inference.")
        else:
            self.session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
            print("[INFO] CUDA not available. Falling back to CPU.")
        self.input_name = self.session.get_inputs()[0].name
        self.input_size = input_size

        self.iou_thres  = iou_thres

    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        img = cv2.resize(frame, (self.input_size, self.input_size))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)/255.0
        img = np.transpose(img, (2,0,1))[None,:,:,:]
        return img

    def postprocess(
            self,
            pred: np.ndarray,
            orig_shape: tuple[int,int],
            selected_classes: list[str]=None,
            conf_threshold: float = None
        ) -> list[tuple[int,int,int,int,float,str]]:
        """
        pred: (1, N, 4+nc) → [xc,yc,w,h,, class_conf1..class_conf_nc]
        Returns list of (x1,y1,x2,y2,conf,cls_name)
        """
        H, W = orig_shape
        dets = pred[0].T  # shape (N,5+nc)
        boxes, scores, class_ids = [], [], []
        for det in dets.tolist():
            # first 4 elements are box 
            x_center, y_center, width, height = det[:4]
            # the rest are class confidences
            class_confs = det[4:]
            # pick best class
            cls_id = int(np.argmax(class_confs))
            cls_conf = class_confs[cls_id]
            cls_name = self.class_names[cls_id]

            if cls_conf < conf_threshold:
                continue
            if selected_classes and cls_name not in selected_classes:
                continue

            # scale coords back to original frame size
            x1 = int((x_center - width/2) * W / self.input_size)
            y1 = int((y_center - height/2) * H / self.input_size)
            x2 = int((x_center + width/2) * W / self.input_size)
            y2 = int((y_center + height/2) * H / self.input_size)

            boxes.append([x1, y1, x2-x1, y2-y1])
            scores.append(cls_conf)
            class_ids.append(cls_id)


        # NMS
        idxs = cv2.dnn.NMSBoxes(boxes, scores, conf_threshold, self.iou_thres)
        results = []
        if len(idxs):
            for i in idxs.flatten():
                x,y,w,h = boxes[i]
                cid = class_ids[i]
                results.append((x, y, x+w, y+h, scores[i], self.class_names[cid]))
        return results

    def detect(
            self,
            frame: np.ndarray,
            selected_classes: list[str]=None,
            conf_thres: float = None,
        ) -> list[tuple[int,int,int,int,float,str]]:

        inp = self.preprocess(frame)
        out = self.session.run(None, {self.input_name: inp})[0]
        return self.postprocess(out, frame.shape[:2], selected_classes, conf_thres)
