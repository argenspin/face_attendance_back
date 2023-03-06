import pickle
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
import face_recognition
file = open('S4CS_face_data.fac','rb')
datas = pickle.load(file)
known_face_encodings = datas['known_face_encodings']
student_ids = datas['student_ids']
print(student_ids)

image = open('test_img.jpg','rb')
image = face_recognition.load_image_file(image)
encodings = face_recognition.face_encodings(image)[0]

param_grid = {
         'C': [1e3, 5e3, 1e4, 5e4, 1e5],
          'gamma': [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.1],
          }
clf = GridSearchCV(SVC(kernel='rbf', class_weight='balanced',probability=True), param_grid)
clf = clf.fit(known_face_encodings, student_ids)

file = open('S4CS_model.svm','rb')
model = pickle.load(file)

print(model.predict_proba([encodings])[0])
print(clf.predict_proba([encodings])[0])
