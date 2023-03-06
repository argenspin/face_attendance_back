import face_recognition
#import cv2
import numpy as np
import os
import pickle
from django.core.files.base import ContentFile
import base64
from concurrent.futures import ProcessPoolExecutor
from time import perf_counter
from sklearn import svm

temp_image__path_for_checking = 'temp_images/' + 'temp_face_img.jpg'
temp_face_img_dir = 'temp_face_images/'
face_dir = 'face_data_dir/'
model_dir = 'trained_models/'

def writeB64toImage(face_photo_b64):
    temp_img_location = temp_image__path_for_checking
    #Base64 string can be decoded from the 22nd character only. Thats why slicing is used
    face_photo_decoded = base64.b64decode((face_photo_b64[22:]))
    #open temp image and write decoded base64 image into it
    face_photo_image_file = open(temp_img_location,'wb')
    face_photo_image_file.write(face_photo_decoded)
    face_photo_image_file.close()

def writeB64toImagesAsStudentName(multple_face_photo_b64s,student_id):
    #Base64 string can be decoded from the 22nd character only. Thats why slicing is used
    i=1
    for face_photo_b64 in multple_face_photo_b64s:
        #78_face_1 
        filename = str(student_id) + '_face_' + str(i) + '.jpg'
        file_location = temp_face_img_dir + filename
        face_photo_decoded = base64.b64decode((face_photo_b64[22:]))
    #open temp image and write decoded base64 image into it
        face_photo_image_file = open(file_location,'wb')
        face_photo_image_file.write(face_photo_decoded)
        face_photo_image_file.close()
        i+=1

def writeFaceEncodingsAndStudentIdsToPickle(student_ids,known_face_encodings,file_location):
    known_face_encodings_and_ids = {}
    known_face_encodings_and_ids['student_ids'] = student_ids
    known_face_encodings_and_ids['known_face_encodings'] = known_face_encodings
    outfile = open(file_location,'wb')
    pickle.dump(known_face_encodings_and_ids,outfile)

def loadFaceData(filename):

    faceFile = open(filename,'rb')
    known_face_encodings_and_ids = pickle.load(faceFile)
    known_face_encodings = known_face_encodings_and_ids['known_face_encodings']
    student_ids = known_face_encodings_and_ids['student_ids']
    return known_face_encodings,student_ids


def loadModelAndTrainUsingStudentImages(face_data_file_location,model_file_location,student_id):
    
    #There should be more than one classname to train the model
    more_than_one_class = True
    try:
        known_face_encodings,student_ids = loadFaceData(face_data_file_location)
    except:
        known_face_encodings = []
        student_ids = []
    if(len(known_face_encodings) == 0 or len(student_ids) == 0):
        more_than_one_class = False
    print("error inside load modeltrain")
    for i in range(1,9):
        current_filename = str(student_id) + '_face_' + str(i) + '.jpg'
        current_file_location = temp_face_img_dir + current_filename
        print(current_file_location)
        img_file = open(current_file_location,'rb')
        try:
            face_photo = face_recognition.load_image_file(img_file)
            face_photo_encodings = face_recognition.face_encodings(face_photo)[0]
            student_ids.append(student_id)
            known_face_encodings.append(face_photo_encodings)
        except:
            print("error eccured")
    print("for loop completed")
    print(model_file_location)
    if more_than_one_class:
        try:        
            model_file = open(model_file_location,'rb')
            model = pickle.load(model_file)
        except:
            model_file = open(model_file_location,'wb')
            model = svm.SVC(probability=True)
        print(len(student_ids),len(known_face_encodings))
        print(student_ids)
        print("fitting started")
        model.fit(known_face_encodings,student_ids)
        model_file.close()
        print("model fitted completely")
        print("model classes:",model.classes_)
        model_file = open(model_file_location,'wb')
        pickle.dump(model,model_file)
    
    print(student_ids)
    writeFaceEncodingsAndStudentIdsToPickle(student_ids,known_face_encodings, face_data_file_location)
  


def addNewStudentFace(stud_class_name,student_id,multple_face_photo_b64s):

    writeB64toImagesAsStudentName(multple_face_photo_b64s,student_id)
    

    face_data_filename = stud_class_name + '_face_data.fac'
    face_data_file_location = face_dir + face_data_filename
    model_filename = stud_class_name + '_model.svm'
    model_file_location = model_dir + model_filename
    print(face_data_filename)
    print(model_filename)
    print(face_data_file_location)
    print(model_file_location)
    print(student_id)
    loadModelAndTrainUsingStudentImages(face_data_file_location,model_file_location,student_id)


def deleteAStudentsFaceEncodings(student_id,stud_class_name):
    student_id = int(student_id)
    print(student_id)
    face_data_filename = stud_class_name + '_face_data.fac'
    face_data_file_location = face_dir + face_data_filename
    known_face_encodings,student_ids = loadFaceData(face_data_file_location)
    indexes = []
    length = len(student_ids)
    print(student_ids)
    for i in range(0,len(student_ids)):
        if(student_ids[i] == student_id):
            indexes.append(i)
    print(indexes)
    i=0
    for index in indexes:
        popped = student_ids.pop(index-i)
        known_face_encodings.pop(index-i)
        i+=1
    print(student_ids)
#Check if the image contains any face
def checkIfFacePhotoIsValid(face_photo_b64):
    writeB64toImage(face_photo_b64)

    try:
        image = face_recognition.load_image_file(temp_image__path_for_checking)
        face_photo_encodings = face_recognition.face_encodings(image)[0]
        return True
    except:
        return False


def predictStudentIdFromFace(face_photo_b64,stud_class_name):
    model_filename = stud_class_name + '_model.svm'
    model_file_location = model_dir + model_filename
    writeB64toImage(face_photo_b64)
    model_file = open(model_file_location,'rb')
    model = pickle.load(model_file)
    image = face_recognition.load_image_file(temp_image__path_for_checking)
    face_encodings = face_recognition.face_encodings(image)[0]
    print(model.classes_)
    print(model.predict_proba([face_encodings]))
    return model.predict([face_encodings])

