import cv2 
from ultralytics import YOLO
import numpy as np
import pandas as pd 
import supervision as sv
import sys
sys.path.append("../")
from utils.stub_utils import read_stub, save_stub


class BallTracker:
    def __init__(self, model_path: str = None):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()
    
    def detect_frames(self, video_frames):
        """
        detect the objects in the frame and returns detection 
        args : 
             frames : Matlike 
        returns :
             detections : matlike 
        """
        batch_size = 20
        detections = []

        for i in range(0, len(video_frames), batch_size):
            batch_frame = video_frames[i:i+batch_size]
            batch_detection = self.model.predict(batch_frame)
            detections += batch_detection
        
        return detections

    def get_object_tracks(self, frames, read_from_stubs=False, stub_path=None):
        tracks = read_stub(read_from_stubs, stub_path)
        if tracks is not None:
            if len(tracks) == len(frames):
                return tracks 
        
        detections = self.detect_frames(frames)
        tracks = []

        for frame_num, detection in enumerate(detections):
            cls_names = detection.names
            cls_name_inv = {v: k for k, v in cls_names.items()}
            
            detection_supervision = sv.Detections.from_ultralytics(detection)
            detection_with_tracks = self.tracker.update_with_detections(detection_supervision)
        
            tracks.append({})
            choosen_bbox = None
            max_confidence = 0

            for frame_detection in detection_with_tracks:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                confidence = frame_detection[2]
                track_id = frame_detection[4]

                if cls_id == cls_name_inv["ball"]:
                    if confidence > max_confidence:
                        choosen_bbox = bbox
                        max_confidence = confidence
            
            # BUG FIX #1: Moved outside the loop
            if choosen_bbox is not None:
                tracks[frame_num][1] = {
                    "bbox": choosen_bbox
                }

        save_stub(stub_path, tracks)
        return tracks 

    def remove_wrong_detctions(self, ball_positions):
        maximum_allowed_distances = 150
        last_good_frame_index = -1

        for i in range(len(ball_positions)):
            current_bbox = ball_positions[i].get(1, {}).get("bbox", [])

            if len(current_bbox) == 0:
                continue

            if last_good_frame_index == -1:
                last_good_frame_index = i
                continue

            last_good_box = ball_positions[last_good_frame_index].get(1, {}).get("bbox", [])

            frame_gap = i - last_good_frame_index
            adjusted_max_distance = maximum_allowed_distances * frame_gap

            if np.linalg.norm(np.array(last_good_box[:2]) - np.array(current_bbox[:2])) > adjusted_max_distance:
                ball_positions[i] = {}
            else:
                last_good_frame_index = i
        
        return ball_positions

    def interpolate_ball_positions(self, ball_positions):
        
        ball_bboxes = []
        for x in ball_positions:
            bbox = x.get(1, {}).get("bbox", [])
            if bbox:
                ball_bboxes.append(bbox)
            else:
                ball_bboxes.append([None, None, None, None])
        
        # Check if we have any valid detections
        if not any(bbox[0] is not None for bbox in ball_bboxes):
            print("[WARN] No valid ball positions found for interpolation.")
            return ball_positions
        
        df_ball_positions = pd.DataFrame(ball_bboxes, columns=["x1", "y1", "x2", "y2"])
        
        # Interpolate and fill
        df_ball_positions = df_ball_positions.interpolate(method='linear').bfill().ffill()
        
        interpolated_positions = []
        for idx, row in df_ball_positions.iterrows():
            if pd.notna(row['x1']):
                interpolated_positions.append({
                    1: {"bbox": row.tolist()}
                })
            else:
                interpolated_positions.append({})
        
        return interpolated_positions