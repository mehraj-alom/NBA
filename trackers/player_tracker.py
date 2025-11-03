from ultralytics import YOLO
import supervision as sv 
import sys
sys.path.append("../")
from utils.stub_utils import read_stub,save_stub

class PlayerTracker:
    def __init__(self,model_path : str = None):
        """requres Model path 
        args : model : str (Path)
        """
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()



    def detect_frames(self , frames):
        """
        detect the objects in the frame and returs detection 
        args : 
             frames : Matlike 
        returns :
             detections : matlike 
        """
        batch_size = 20
        detections = []

        for i in range(0,len(frames),batch_size):
            batch_frame = frames[i:i+batch_size]
            batch_detection = self.model.predict(batch_frame)
            detections += batch_detection

        return detections

    
    def get_object_tracks(self,frames,read_from_stubs=False,stub_path=None):

        tracks = read_stub(read_from_stubs,stub_path)
        if tracks is not None:
            if len(tracks) == len(frames):
                return tracks 

        detections = self.detect_frames(frames)
        tracks = []
        
        
        for frame_num , detection in enumerate(detections):
            cls_names = detection.names 
            cls_names_inv = {v:k for k , v in cls_names.items()}
            
            detection_supervision = sv.Detections.from_ultralytics(detection) # change to supervision_style 

            detection_with_tracks = self.tracker.update_with_detections(detection_supervision)
            
            tracks.append({})

            for frame_detection in detection_with_tracks:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                track_id = frame_detection[4]

                if cls_id == cls_names_inv["player"]:
                    tracks[frame_num][track_id] = {
                        "box" : bbox
                    }
                    
        save_stub(stub_path,tracks)
        return tracks 
