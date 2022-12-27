import face_recognition
#import cv2
import numpy as np
import os
import pickle
from django.core.files.base import ContentFile
import base64

temp_image_path = 'temp_images/face_photo.jpg'


def base64_file(data, name=None):
    _format, _img_str = data.split(';base64,') #Split the base64 string and its format(jpg,png etc)
    _name, ext = _format.split('/') 
    if not name:
        name = _name.split(":")[-1]
    #Return filename and file
    return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext))

def writeB64toImage(face_photo_b64):
    #Base64 string can be decoded from the 22nd character only. Thats why slicing is used
    face_photo_decoded = base64.b64decode((face_photo_b64[22:]))
    #open temp image and write decoded base64 image into it
    face_photo_image_file = open(temp_image_path,'wb')
    face_photo_image_file.write(face_photo_decoded)
    face_photo_image_file.close()

def writeFaceEncodingsAndStudentIdsToPickle(student_ids,known_face_encodings,filename):
    known_face_encodings_and_ids = {}
    known_face_encodings_and_ids['student_ids'] = student_ids
    known_face_encodings_and_ids['known_face_encodings'] = known_face_encodings
    outfile = open(filename,'wb')
    pickle.dump(known_face_encodings_and_ids,outfile)

    try:
        os.remove(temp_image_path)
    except:
        pass

def loadFaceData(filename):
    faceFile = open(filename,'rb')
    known_face_encodings_and_ids = pickle.load(faceFile)
    known_face_encodings = known_face_encodings_and_ids['known_face_encodings']
    student_ids = known_face_encodings_and_ids['student_ids']
    return known_face_encodings,student_ids

def addNewStudentFace(filename,student_id,face_photo_b64):

    writeB64toImage(face_photo_b64)
    try:
        known_face_encodings,student_ids = loadFaceData(filename)
    except:
        known_face_encodings = []
        student_ids = []

    print(student_ids)
    face_photo = face_recognition.load_image_file(temp_image_path)
    face_photo_encodings = face_recognition.face_encodings(face_photo)[0]
    known_face_encodings.append(face_photo_encodings)
    student_ids.append(student_id)
    print(student_ids)
    writeFaceEncodingsAndStudentIdsToPickle(student_ids,known_face_encodings,filename)

def editStudentFace(current_filename,updated_filename,student_id,face_photo_b64):

    writeB64toImage(face_photo_b64)
    face_photo = face_recognition.load_image_file(temp_image_path)
    face_photo_encodings = face_recognition.face_encodings(face_photo)[0]

    print(current_filename)
    print(updated_filename)
    if(current_filename==updated_filename):
        print("If part worked")
        known_face_encodings,student_ids = loadFaceData(current_filename)
        face_data_index = student_ids.index(student_id)
        print(face_data_index)
        known_face_encodings[face_data_index] = face_photo_encodings
        writeFaceEncodingsAndStudentIdsToPickle(student_ids,known_face_encodings,current_filename)
    else:
        deleteStudentFace(current_filename,student_id)
        addNewStudentFace(updated_filename,student_id,face_photo_b64)
        return

    #Find the index of student_id in student_ids to update face encodings for student with that student_id

def deleteStudentFace(filename,student_id):
    known_face_encodings,student_ids = loadFaceData(filename)
    student_id = int(student_id)
    face_data_index = student_ids.index(student_id)
    known_face_encodings.pop(face_data_index)
    student_ids.pop(face_data_index)
    writeFaceEncodingsAndStudentIdsToPickle(student_ids,known_face_encodings,filename)








    