import cv2
import numpy as np
import sys 
sys.path.append("../")
from utils.bbox_utils import get_center_of_bbox,bbox_height,bbox_width


def draw_triangle(frame, bbox, color, track_id=None):
    x1, y1, x2, y2 = map(float, bbox)
    cx, cy = get_center_of_bbox(bbox)

    tip_y = int(y1 - 15)
    base_y = int(y1 + 5)
    triangle_coordinates = np.array([
        [cx, tip_y],         
        [cx - 10, base_y],   
        [cx + 10, base_y]     
    ], np.int32)

    cv2.drawContours(frame, [triangle_coordinates], 0, color, cv2.FILLED)
    cv2.drawContours(frame, [triangle_coordinates], 0, (0, 0, 0), 1)  
    return frame

def draw_ellipse(frame, bbox, color, track_id=None):

    x1, y1, x2, y2 = map(float, bbox)
    min_h_bbox = int(y2)  

    cx = int((x1 + x2) / 2)
    width = int(x2 - x1)

    cv2.ellipse(
        frame,
        center=(cx, min_h_bbox),               
        axes=(int(width / 2), int(0.35 * width)),  
        angle=0,
        startAngle=-45,
        endAngle=235,
        color=color,
        thickness=2,
        lineType=cv2.LINE_4
    )

    # Draw ID rectangle
    rectangle_width = 40
    rectangle_height = 20
    x1_rect = cx - (rectangle_width // 2)
    x2_rect = cx + (rectangle_width // 2)
    y1_rect = min_h_bbox - (rectangle_height // 2) + 15
    y2_rect = min_h_bbox + (rectangle_height // 2) + 15

    if track_id is not None:
        cv2.rectangle(
            frame,
            (int(x1_rect), int(y1_rect)),
            (int(x2_rect), int(y2_rect)),
            color,
            cv2.FILLED
        )
        x1_text = x1_rect + 12
        if track_id > 99:
            x1_text -= 10
        cv2.putText(
            frame,
            str(int(track_id)),
            (int(x1_text), int(y1_rect + 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 0),
            2
        )

    return frame
