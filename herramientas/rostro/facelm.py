import sys,cv2,numpy as np,mediapipe as mp
from mediapipe.tasks.python import vision,BaseOptions
import os; M=os.path.join(os.path.dirname(os.path.abspath(__file__)),'face_landmarker.task')
def landmarks(path):
    det=vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=M),num_faces=3,min_face_detection_confidence=0.2,min_face_presence_confidence=0.2))
    im=cv2.imread(path); H,W=im.shape[:2]
    r=det.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=cv2.cvtColor(im,cv2.COLOR_BGR2RGB)))
    return [np.array([[p.x*W,p.y*H] for p in f],np.float32) for f in r.face_landmarks]
if __name__=='__main__':
    F=landmarks(sys.argv[1]); print(len(F))
    im=cv2.imread(sys.argv[1])
    for f in F:
        for x,y in f: cv2.circle(im,(int(x),int(y)),1,(0,0,255),-1)
    cv2.imwrite(sys.argv[2],im)
