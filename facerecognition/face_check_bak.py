import face_recognition
#import cv2
import numpy as np
import os
import pickle
from django.core.files.base import ContentFile
import base64
from concurrent.futures import ProcessPoolExecutor
from time import perf_counter

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

def detectFaceFromPickle(filename,images_to_detect):
    frequently_matched_id = -1
    known_face_encodings,student_ids = loadFaceData(filename)
    matched_ids_and_counts = {}
    start = perf_counter()
    for image in images_to_detect:
        try:
            writeB64toImage(image)
            face_photo = face_recognition.load_image_file(temp_image_path)
            image_encodings = face_recognition.face_encodings(face_photo)[0]
            compared_list = face_recognition.compare_faces(known_face_encodings, image_encodings)
            current_matched_id = student_ids[compared_list.index(True)]
            if current_matched_id in matched_ids_and_counts.keys():
                matched_ids_and_counts[current_matched_id] += 1
            else:
                matched_ids_and_counts[current_matched_id] = 0           
        except:
            pass
    print(matched_ids_and_counts)
    try:
        if len(matched_ids_and_counts) > 0:
            dict_values = list(matched_ids_and_counts.values())
            frequently_matched_index = dict_values.index(max(dict_values))
            print(frequently_matched_index)
            dict_keys = list(matched_ids_and_counts.keys())
            frequently_matched_id = dict_keys[frequently_matched_index]
    except:
        print("exception occured")
        pass
    print(perf_counter()-start)
    print(frequently_matched_id)
    return frequently_matched_id

def detectFaceFromPickleMultiProcess(filename,images_to_detect):
    frequently_matched_id = -1
    known_face_encodings,student_ids = loadFaceData(filename)
    matched_ids_and_counts = {}
    n=0
    results = []
    start = perf_counter()
    #use multiprocessing to find matching ids of images_to_detect
    with ProcessPoolExecutor(max_workers=4) as executor:
        for image in images_to_detect:
            future_obj = executor.submit(findCurrentMatchedId,n,image,known_face_encodings,student_ids)
            results.append(future_obj)
            n+=1
    all_matched_ids = [r.result() for r in results ]

    print(all_matched_ids)
    frequently_matched_id = max(all_matched_ids, default=-1)
    print(frequently_matched_id)
    print(perf_counter()-start)
    return frequently_matched_id
    #print(time.perf_counter()-start)       


def findCurrentMatchedId(n,image,known_face_encodings,student_ids):
    current_matched_id = -1
    try:
        temp_image_path = writeB64toImageUsingN(image,n)

        face_photo = face_recognition.load_image_file(temp_image_path)
        image_encodings = face_recognition.face_encodings(face_photo)[0]
        compared_list = face_recognition.compare_faces(known_face_encodings, image_encodings)
        current_matched_id = student_ids[compared_list.index(True)]
    except:
        return -1
    return current_matched_id

def writeB64toImageUsingN(face_photo_b64,n):
    #Base64 string can be decoded from the 22nd character only. Thats why slicing is used
    face_photo_decoded = base64.b64decode((face_photo_b64[22:]))
    #open temp image and write decoded base64 image into it
    temp_image_path  = 'temp_images/'+'temp_image_'+str(n)+'.jpg'
    face_photo_image_file = open(temp_image_path,'wb')
    face_photo_image_file.write(face_photo_decoded)
    face_photo_image_file.close()
    return temp_image_path








    