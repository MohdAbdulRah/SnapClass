import dlib
import numpy as np 
import face_recognition_models
from sklearn.svm import SVC

import streamlit as st 

from src.database.db import get_all_students

#Load heavy models only once (very important for performance)
@st.cache_resource
def load_dlib_models():
     detector =  dlib.get_frontal_face_detector() #Detects faces in an image

     sp = dlib.shape_predictor(
          face_recognition_models.pose_predictor_model_location()
     ) # Finds facial landmarks: eyes,nose,mouth -- Used to align face properly.

     facerec = dlib.face_recognition_model_v1(
          face_recognition_models.face_recognition_model_location()
     ) #This is the main model. It converts face → embedding vector (128D). [0.80,-0.03,...]

     return detector,sp,facerec

#Convert image → face embeddings
def get_face_embeddings(image_np):
     detector,sp,facerec = load_dlib_models() #Load Models
     faces = detector(image_np,1) #finds all faces in image,1 = upsample once (better detection)
     #output = [face1,face2,face3]

     encodings = [] #for storing embeddings

     for face in faces:
          shape = sp(image_np,face) #Finds facial landmarks
          face_descriptor = facerec.compute_face_descriptor(image_np,shape,1) #It converts face → embedding vector (128D)
          encodings.append(np.array(face_descriptor)) #convert to numpy and added it to encodings 
     return encodings
# Return all Faces
# [
#  [0.1, 0.2, ...],
#  [0.8, 0.3, ...]
# ]
# Each face = one student candidate

@st.cache_resource
def get_trained_model():
     X = []
     y = []

     student_db = get_all_students() #Get all Students
     if not student_db:
          return None
     for student in student_db: #Travel through Each Student
          embedding = student.get('face_embeddings') #for each student get the face_mebeddings column
          if embedding:
               X.append(np.array(embedding)) #Convert the embedding to numpy and add it to X
               y.append(student.get('student_id')) #store coreesponding student Id in y
     if len(X) == 0:
          return 0
     #Here Loading the => SVC linear decision boundary,probability enabled,handles imbalance
     clf = SVC(kernel='linear',probability=True,class_weight='balanced')
     #Remind SVC and check in notes i.e dividing into planes
     try:
          clf.fit(X,y)
     except ValueError:
          pass
     return {'clf' : clf,'X' : X,'y':y}  #Return the train model + training data 


def train_classifier():
     st.cache_resource.clear() #Removes the Cached Model
     model_data = get_trained_model() #Returns model,X,y
     return bool(model_data) #True if training succeeded


def predict_attendance(class_image_np): #Input classroom Image
     encodings = get_face_embeddings(class_image_np) #Get the Face Emebddings of all the students in the picture [[0.90,-0.76...],[9.09,0.34,..]]

     detected_student = {}
# Stores the detected student
#      {
#   5: True,
#   8: True
#    }
     model_data = get_trained_model()# get the model,X,y

     if not model_data: #Model not found
          return detected_student,[],len(encodings)
     #Extract Model Parts
     clf = model_data['clf']
     X_train = model_data['X']
     y_train = model_data['y']

     all_students = sorted(list(set(y_train)))#All student Ids and used set to store unique values

     for encoding in encodings: #Each face in classroom image
          if len(all_students) >= 2: #If more than one students exists in Unique
               predicted_id = int(clf.predict([encoding])[0]) #Then SVC Predicts
          else:#If one student only 
               predicted_id = int(all_students[0])  #by default the one and only one student  
          student_embedding = X_train[y_train.index(predicted_id)] #Getting the face embedding of predicted Id 
          best_match_score = np.linalg.norm(student_embedding-encoding)
# This is Euclidean distance.
# smaller = better match
# larger = bad match
          resembelence_threshold = 0.6 #distance <= 0.6 → valid match
          if best_match_score <= resembelence_threshold: #Mark present
               detected_student[predicted_id] = True
     return detected_student,all_students,len(encodings)
# Outputs:

# detected_student
# Who is present
# {5: True, 8: True}

# all_students
# All enrolled IDs

# len(encodings)
# Number of faces detected




# Classroom Image
#       ↓
# Detect faces (dlib)
#       ↓
# Convert faces → 128D embeddings
#       ↓
# Load trained SVM model
#       ↓
# Predict student ID for each face
#       ↓
# Validate using Euclidean distance
#       ↓
# Return attendance list
     
