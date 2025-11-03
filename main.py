from logger import logger 
from utils.video_utils import read_video, save_video
from trackers import PlayerTracker, BallTracker
from drawers import (
    PlayerTrackDrawer,
    BallTrackDrawer,
    TeamBallControlDrawer,
    PassInterceptionDrawer,
    CourtKeypointDrawer
)
from team_asssigner import TeamAssigner
from ball_aquisition import BallAquisitionDetector
from pass_and_interception_detector import PassAndInterceptionDetector
from court_keypoint_detector import CourtKeyPointDetector


def main():
    
    logger.info("=" * 80)
    logger.info("STARTING BASKETBALL VIDEO ANALYSIS PIPELINE")
    logger.info("=" * 80)
    
    # ============================================================================
    # VIDEO INPUT
    # ============================================================================
    logger.info("Reading input video...")
    video_frames = read_video("input_video/video_3.mp4")
    logger.info(f"Successfully loaded {len(video_frames)} video frames")
    
    
    # ============================================================================
    # PLAYER TRACKING
    # ============================================================================
    logger.info("-" * 80)
    logger.info("PLAYER TRACKING MODULE")
    logger.info("-" * 80)
    
    logger.info("Initializing player tracker...")
    player_tracker = PlayerTracker("models/playerandballditection.pt")
    logger.info("Player tracker initialized successfully")
    
    logger.info("Processing player tracking (loading from stub)...")
    player_tracks = player_tracker.get_object_tracks(
        video_frames,
        read_from_stubs=True, 
        stub_path="stubs/player_tracks.pkl"
    )
    
    frames_with_players = sum([1 for frame_tracks in player_tracks if frame_tracks])
    logger.info(f"Player tracking complete - {frames_with_players} frames contain player data")
    
    
    # ============================================================================
    # BALL TRACKING
    # ============================================================================
    logger.info("-" * 80)
    logger.info("BALL TRACKING MODULE")
    logger.info("-" * 80)
    
    logger.info("Initializing ball tracker...")
    ball_tracker = BallTracker("models/playerandballditection.pt")
    logger.info("Ball tracker initialized successfully")
    
    logger.info("Processing ball tracking (loading from stub)...")
    ball_tracks = ball_tracker.get_object_tracks(
        video_frames,
        read_from_stubs=True, 
        stub_path="stubs/ball_tracks.pkl"
    )
    
    frames_with_balls = sum([1 for frame_tracks in ball_tracks if frame_tracks])
    logger.info(f"Initial ball tracking complete - {frames_with_balls} frames contain ball data")
    
    logger.info("Removing incorrect ball detections...")
    ball_tracks = ball_tracker.remove_wrong_detctions(ball_tracks)
    logger.info("Wrong ball detections removed successfully")
    
    logger.info("Interpolating missing ball positions...")
    ball_tracks = ball_tracker.interpolate_ball_positions(ball_tracks)
    logger.info("Ball position interpolation complete")
    
    frames_with_balls_after = sum([1 for frame_tracks in ball_tracks if frame_tracks])
    logger.info(f"Ball tracking finalized - {frames_with_balls_after} frames contain ball data after processing")
    
    
    # ============================================================================
    # TEAM ASSIGNMENT
    # ============================================================================
    logger.info("-" * 80)
    logger.info("TEAM ASSIGNMENT MODULE")
    logger.info("-" * 80)
    
    logger.info("Initializing team assigner...")
    team_asssigner = TeamAssigner()
    logger.info("Team assigner initialized successfully")
    
    logger.info("Assigning players to teams (loading from stub)...")
    player_assignment = team_asssigner.get_player_teams_across_frames(
        video_frames,
        player_tracks,
        read_from_stub=True,
        stub_path="stubs/player_assignment_stubs.pkl"
    )
    logger.info("Team assignment complete")
    
    
    # ============================================================================
    # BALL POSSESSION DETECTION
    # ============================================================================
    logger.info("-" * 80)
    logger.info("BALL POSSESSION DETECTION MODULE")
    logger.info("-" * 80)
    
    logger.info("Initializing ball acquisition detector...")
    ball_aquisition_detector = BallAquisitionDetector()
    logger.info("Ball acquisition detector initialized successfully")
    
    logger.info("Detecting ball possession across frames...")
    ball_aquisition = ball_aquisition_detector.detect_ball_possession(player_tracks, ball_tracks)
    logger.info("Ball possession detection complete")
    
    
    # ============================================================================
    # PASS AND INTERCEPTION DETECTION
    # ============================================================================
    logger.info("-" * 80)
    logger.info("PASS AND INTERCEPTION DETECTION MODULE")
    logger.info("-" * 80)
    
    logger.info("Initializing pass and interception detector...")
    pass_and_interception_detector = PassAndInterceptionDetector()
    logger.info("Pass and interception detector initialized successfully")
    
    logger.info("Detecting passes...")
    passes = pass_and_interception_detector.detect_passes(ball_aquisition, player_assignment)
    logger.info(f"Pass detection complete - {len(passes)} passes detected")
    
    logger.info("Detecting interceptions...")
    interceptions = pass_and_interception_detector.detect_interceptions(ball_aquisition, player_assignment)
    logger.info(f"Interception detection complete - {len(interceptions)} interceptions detected")
    
    
    # ============================================================================
    # COURT KEYPOINT DETECTION
    # ============================================================================
    logger.info("-" * 80)
    logger.info("COURT KEYPOINT DETECTION MODULE")
    logger.info("-" * 80)
    
    logger.info("Initializing court keypoint detector...")
    court_keypoint_detector = CourtKeyPointDetector("models/keypoint_cout.pt")
    logger.info("Court keypoint detector initialized successfully")
    
    logger.info("Detecting court keypoints (loading from stub)...")
    court_keypoints = court_keypoint_detector.get_court_keypoints(
        video_frames,
        read_from_stub=True,
        stub_path="stubs/court_keypoint_detector_stubs.pkl"
    )
    logger.info("Court keypoint detection complete")
    
    
    # ============================================================================
    # VIDEO RENDERING
    # ============================================================================
    logger.info("-" * 80)
    logger.info("VIDEO RENDERING MODULE")
    logger.info("-" * 80)
    
    logger.info("Initializing player track drawer...")
    player_tracks_drawer = PlayerTrackDrawer()
    logger.info("Drawing player tracks and assignments on video frames...")
    player_video_frames = player_tracks_drawer.draw(
        video_frames,
        player_tracks,
        player_assignment,
        ball_aquisition
    )
    logger.info("Player tracks rendered successfully")
    
    logger.info("Initializing ball track drawer...")
    ball_track_drawer = BallTrackDrawer()
    logger.info("Drawing ball tracks on video frames...")
    ball_video_frames = ball_track_drawer.draw(player_video_frames, ball_tracks)
    logger.info("Ball tracks rendered successfully")
    
    logger.info("Initializing team ball control drawer...")
    team_ball_control_drawer = TeamBallControlDrawer()
    logger.info("Drawing team ball control statistics...")
    output_video_frames = team_ball_control_drawer.draw(
        ball_video_frames,
        player_assignment,
        ball_aquisition
    )
    logger.info("Team ball control statistics rendered successfully")
    
    logger.info("Initializing pass and interception drawer...")
    pass_and_interception_drawer = PassInterceptionDrawer()
    logger.info("Drawing passes and interceptions...")
    output_video_frames = pass_and_interception_drawer.draw(
        output_video_frames,
        passes,
        interceptions
    )
    logger.info("Passes and interceptions rendered successfully")
    
    logger.info("Initializing court keypoint drawer...")
    court_keypoint_drawer = CourtKeypointDrawer()
    logger.info("Drawing court keypoints...")
    output_video_frames = court_keypoint_drawer.draw(output_video_frames, court_keypoints)
    logger.info("Court keypoints rendered successfully")
    
    
    # ============================================================================
    # VIDEO OUTPUT
    # ============================================================================
    logger.info("-" * 80)
    logger.info("SAVING OUTPUT VIDEO")
    logger.info("-" * 80)
    
    logger.info("Saving processed video to output_video/video_2.avi...")
    save_video("output_video/video_2.avi", output_video_frames, 30)
    logger.info("Output video saved successfully")
    
    logger.info("=" * 80)
    logger.info("BASKETBALL VIDEO ANALYSIS PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()