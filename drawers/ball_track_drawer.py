import cv2
from .utils import draw_triangle

class BallTrackDrawer:
    def __init__(self):
        self.ball_pointer_color = (0,255,0)
    
    def draw(self, video_frames, tracks):
        output_video_frames = []

        for frame_num, frame in enumerate(video_frames):
            frame = frame.copy()

            # Safety: make sure there is a corresponding track dict for this frame
            if frame_num < len(tracks):
                ball_dict = tracks[frame_num]
            else:
                ball_dict = {}  # no ball in this frame

            for track_id, ball in ball_dict.items():
                frame = draw_triangle(frame, ball["bbox"], self.ball_pointer_color)

            output_video_frames.append(frame)

        return output_video_frames


    # def draw_frame(self, frame, ball_track):
    #     """
    #     Draws ball pointer on a single frame (compatible with memory-safe main()).
    #     """
    #     # Reuse the existing draw() logic on just one frame
    #     output_frame = self.draw([frame], [ball_track])[0]
    #     return output_frame
