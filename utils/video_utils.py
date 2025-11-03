import os
import sys
from logger import logger
import cv2
 

def read_video(video_path:str):
    """args : 
            path : str
    """

    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret ,frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    logger.info(f"Video has been read succesfully")
    return frames

def save_video(out_path: str, frames, fps=30):
    """ Save frames as a video """
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    if not frames:
        logger.info("no frames to save — video output aborted.")
        return

    valid_frames = [f for f in frames if f is not None]
    if not valid_frames:
        logger.info(" All frames are None — video output aborted.")
        return

    height, width = valid_frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

    for frame in valid_frames:
        out.write(frame)

    out.release()
    logger.info(f"video saved successfully: {out_path}")