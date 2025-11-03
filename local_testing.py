from ultralytics import YOLO

model = YOLO("models/playerandballditection.pt")

result = model.predict('input_video/video_1.mp4', save = True)
print(reult[0])
for box in result[0].boxes:
    print(box) 
