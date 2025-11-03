class PassAndInterceptionDetector:
    def __init__(self):
        pass

    def detect_passes(self,ball_aquisition,player_assignment):

        passes = [-1] * len(ball_aquisition)
        prev_holder = -1 
        prev_frame_num = -1 

        for frame_num in range(1,len(ball_aquisition)):
            if ball_aquisition[frame_num -1] != -1 :
                prev_holder = ball_aquisition[frame_num-1]
                prev_frame_num = frame_num -1

            current_holder = ball_aquisition[frame_num]

            if prev_holder != -1 and current_holder != -1 and prev_holder != current_holder:
                prev_team = player_assignment[prev_frame_num].get(prev_holder,-1)
                current_team = player_assignment[frame_num].get(current_holder,-1)

                if prev_team == current_team and prev_team != -1:
                    passes[frame_num] = prev_team
                    
        return passes


    def detect_interceptions(self,ball_aquisition,player_assignment):

        interceptions = [-1] * len(ball_aquisition)
        prev_holder = -1 
        prev_frame_num = -1 

        for frame_num in range(1,len(ball_aquisition)):
            if ball_aquisition[frame_num -1] != -1 :
                prev_holder = ball_aquisition[frame_num-1]
                prev_frame_num = frame_num -1

            current_holder = ball_aquisition[frame_num]

            if prev_holder != -1 and current_holder != -1 and prev_holder != current_holder:
                prev_team = player_assignment[prev_frame_num].get(prev_holder,-1)
                current_team = player_assignment[frame_num].get(current_holder,-1)

                if prev_team != current_team and prev_team != -1 and current_team != -1:
                    interceptions[frame_num] = current_team
                        
        return interceptions