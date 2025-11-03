
from .utils import draw_ellipse,draw_triangle

class PlayerTrackDrawer:
    def __init__(self,team_1_color=[255,245,230],team_2_color=[128,23,0]):
        self.default_player_team_id = 1
        self.team_1_color = team_1_color
        self.team_2_color = team_2_color

    def draw(self, video_frames, tracks, player_assignment,ball_aquisition):
        output_video_frames = []
 
        for frame_num, frame in enumerate(video_frames):
            frame = frame.copy()

            # Safety: make sure there is a corresponding track dict for this frame
            if frame_num < len(tracks):
                player_dict = tracks[frame_num]
            else:
                player_dict = {}  #no players in this frame

            player_assignment_for_frame = player_assignment[frame_num]

            player_id_has_ball = ball_aquisition[frame_num]
             
            for track_id, player in player_dict.items():
                team_id = player_assignment_for_frame.get(track_id,self.default_player_team_id)

                if team_id == 1:
                    color = self.team_1_color
                else:
                    color = self.team_2_color
                
                if track_id == player_id_has_ball:
                    frame = draw_triangle(frame , player["box"],(0,0,255))


                frame = draw_ellipse(frame, player["box"],color, track_id)# --> refer here : this is player_track  #(np.int64(13): {'box': [739.2302856445312, 287.12835693359375, 815.6257934570312, 478.91632080078125]}, 
                                                                    #np.int64(4): {'box': [641.2548217773438, 239.69195556640625, 705.9413452148438, 401.013427734375]}, 
                                                                    # np.int64(11): {'box': [804.435302734375, 436.29425048828125, 909.1319580078125, 677.1433715820312]}, 
                                                                    # np.int64(126): {'box': [613.2178955078125, 317.50421142578125, 682.761962890625, 494.25921630859375]}}])


            # Append the frame after all players are drawn
            output_video_frames.append(frame)

        return output_video_frames
