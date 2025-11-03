import sys 
sys.path.append("../")
from utils import measure_distance , get_center_of_bbox
class BallAquisitionDetector:

    def __init__(self):
        self.distance_threshold = 40
        self.min_frames = 7
        self.containment_threshold = 0.8
    
    def get_key_basketball_player_assignment_points(self,player_bbox,ball_center):

        ball_center_x = ball_center[0]
        ball_center_y = ball_center[1]
        
        x1,y1,x2,y2 = player_bbox
        width = x2 - x1 
        height = y2 - y1
    
        output_points = []
        
        if ball_center_y > y1 and ball_center_y < y2:
            output_points.append((x1,ball_center_y))
            output_points.append((x2,ball_center_y))
    
    
        if ball_center_x>x1  and ball_center_x < x2:
            output_points.append((ball_center_x, y1))
            output_points.append((ball_center_x, y2))

        

        output_points += [
            (x1,y1), # top left pint 
            (x2,y2),# buttom right point
            (x1,y2), # buttom left corner
            (x2,y2), # buttom right corner
            (x1+width//2,y1), # top center
            (x1+width//2,y2), # buttom center
            (x1,y1+height//2), # left corner
            (x2,y1+height//2) # right center
        ]

        return output_points
    

    def find_min_distance_to_ball(self,ball_center,player_bbox):
        key_points = self.get_key_basketball_player_assignment_points(player_bbox, ball_center)
 
        return min(measure_distance(ball_center, key_point) for key_point in key_points)

    
        ###                        OR 

        # min = 90090
        # for key_point in key_points:
        #     distance = measure_distance(ball_center,key_point)
        #     if min > distance :
        #         min = distance

        # return min       

    def calculate_ball_containment_ratio(self,player_bbox,ball_bbox):
        px1 , py1, px2 , py2 = player_bbox
        bx1 , by1 , bx2 , by2 = ball_bbox

        ball_area = (bx2 - bx1 ) * (by2 - by1)

        intersection_x1 = max(px1,bx1)
        intersection_y1 = max(py1,by1)
        intersection_x2 = min(px2,bx2)
        intersection_y2 = min(py2,by2)

        if intersection_x2 < intersection_x1 or intersection_y2 < intersection_y1:

            return 0 

        intersection_area = (intersection_x2 - intersection_x1) * (intersection_y2 - intersection_y1)

        containment_ratio = intersection_area / ball_area

        return containment_ratio 
    

    def find_best_candidate_for_possession(self,ball_center,player_tracks_frame,ball_bbox):

        high_containment_players = [] # 1st priority 
        reguler_distance_players = []

        for player_id , player_info in player_tracks_frame.items():
            player_bbox = player_info.get("box", [])
            # #--- DEBUGGING ---
            # print(f"--- FRAME ---") 
            # #--- END DEBUGGING ---
            if not player_bbox:
                continue
            
            containment = self.calculate_ball_containment_ratio(player_bbox,ball_bbox)
            min_distance = self.find_min_distance_to_ball(ball_center,player_bbox)

            # # --- DEBUGGING ---
            # if containment > 0.01:
            #     print(f"  Player {player_id}: containment={containment:.2f}")
            # if min_distance < 500: # Print any player within 500px
            #     print(f"  Player {player_id}: min_distance={min_distance:.2f}")
            
            
            if containment > self.containment_threshold:
                high_containment_players.append((int(player_id),containment)) # Cast to int
            else:
                    reguler_distance_players.append((int(player_id),min_distance)) # Cast to int
        if high_containment_players:
            best_candidate =  max(high_containment_players,key=lambda x : x[1])    # key=lambda x: x[1] means: When comparing each item, 
                                                                                    #use its second element (x[1]) for comparison.
            return best_candidate[0]
        
        # if second priority 
        if reguler_distance_players:
            best_candidate = min(reguler_distance_players,key= lambda x : x[1])
            if best_candidate[1] < self.distance_threshold:
                return best_candidate[0]
        
        return -1 
   
    def detect_ball_possession(self, player_tracks, ball_tracks):
        num_frames = len(ball_tracks)
        possession_list = [-1] * num_frames
        consicutive_possision_count = {}
        prev_possessor = None  # keeps track of last known ball holder

        for frame_num in range(num_frames):
            # get ball info for this frame
            ball_info = list(ball_tracks[frame_num].values())[0] if ball_tracks[frame_num] else {}
            if not ball_info:
                continue

            ball_bbox = ball_info.get("bbox", [])
            if not ball_bbox:
                continue

            # get ball center
            ball_center = get_center_of_bbox(ball_bbox)

            # find best player candidate in this frame
            best_player_id = self.find_best_candidate_for_possession(
                ball_center, player_tracks[frame_num], ball_bbox
            )

            if best_player_id != -1:
                # if a new player seems to have the ball, reset others
                if best_player_id != prev_possessor:
                    consicutive_possision_count = {best_player_id: 1}
                else:
                    # continue counting consecutive frames
                    consicutive_possision_count[best_player_id] = (
                        consicutive_possision_count.get(best_player_id, 0) + 1
                    )

                # update last possessor
                prev_possessor = best_player_id

                # only mark possession if the player has held the ball for enough frames
                if consicutive_possision_count[best_player_id] >= self.min_frames:
                    possession_list[frame_num] = best_player_id

            else:
                # no player near the ball in this frame
                prev_possessor = None
                consicutive_possision_count = {}

        return possession_list
