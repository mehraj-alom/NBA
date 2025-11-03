
import numpy as np
import cv2

class TeamBallControlDrawer:
    def __init__(self):
        pass

    def get_team_ball_control(self, player_assignment, ball_aquisition):
        team_ball_control = []
        for player_assignment_frame, ball_aquisition_frame in zip(player_assignment, ball_aquisition):

            if ball_aquisition_frame == -1:
                team_ball_control.append(-1)
                continue
            if ball_aquisition_frame not in player_assignment_frame:
                team_ball_control.append(-1)
                continue
       
            if player_assignment_frame[ball_aquisition_frame] == 1:
                team_ball_control.append(1)  # team 1 has ball
            else:
                team_ball_control.append(2)  # team 2 has ball

        return np.array(team_ball_control)

    def draw(self, video_frames, player_assignment, ball_aquisition):
        team_ball_control = self.get_team_ball_control(player_assignment, ball_aquisition)
        output_video_frames = []

        for frame_num, frame in enumerate(video_frames):
            if frame_num == 0:
                continue

            frame_drawn = self.draw_frame(frame, frame_num, team_ball_control)
            output_video_frames.append(frame_drawn)
        
        return output_video_frames

    def draw_frame(self, frame, frame_num, team_ball_control):
        overlay = frame.copy()
        font_scale = 0.7
        font_thickness = 2

        # overlay position
        frame_height, frame_width = overlay.shape[:2]
        rect_x1 = int(frame_width * 0.6)
        rect_y1 = int(frame_height * 0.75)
        rect_x2 = int(frame_width * 0.9)
        rect_y2 = int(frame_height * 0.9)
        
        # text positions
        text_x = int(frame_width * 0.63)
        text_y1 = int(frame_height * 0.80)
        text_y2 = int(frame_height * 0.88)

        # draw overlay box
        cv2.rectangle(overlay, (rect_x1, rect_y1), (rect_x2, rect_y2), (255, 255, 255), -1)
        alpha = 0.8
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        
        team_ball_control_till_frame = team_ball_control[:frame_num + 1]
        team_1_num_frames = np.sum(team_ball_control_till_frame == 1)
        team_2_num_frames = np.sum(team_ball_control_till_frame == 2)

        total_frames = len(team_ball_control_till_frame)
        if total_frames > 0:
            team_1 = team_1_num_frames / total_frames
            team_2 = team_2_num_frames / total_frames
        else:
            team_1 = team_2 = 0

        cv2.putText(frame, f"Team 1 Ball Control: {team_1 * 100:.2f}%", (text_x, text_y1),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), font_thickness)
        cv2.putText(frame, f"Team 2 Ball Control: {team_2 * 100:.2f}%", (text_x, text_y2),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), font_thickness)
        
        return frame 
