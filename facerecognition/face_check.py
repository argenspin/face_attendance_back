import face_recognition
#import cv2
import os
import pickle
import base64
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor
from time import perf_counter
from sklearn import svm
from skimage.io import imread, imsave
from skimage.transform import rotate
from skimage.util import random_noise
from numpy import fliplr
from collections import Counter


temp_img_path_for_identifying = 'temp_images/'
temp_image__path_for_checking = 'temp_images/'
temp_face_img_dir = 'temp_face_images/'
face_dir = 'face_data_dir/'
model_dir = 'trained_models/'

def getModelFileLocation(stud_class_name):
    model_filename = stud_class_name + '_model.svm'
    model_file_location = model_dir + model_filename
    return model_file_location
def getFaceDataFileLocation(stud_class_name):
    face_data_filename = stud_class_name + '_face_data.fac'
    face_data_file_location = face_dir + face_data_filename
    return face_data_file_location

def createAugmentedImages(file_location):
    image = imread(file_location) /255
    flipped = fliplr(image)
    rotated = rotate(image,angle=30)
    noised = random_noise(image,var=0.1**2)
    file_location = file_location.replace('.jpg','')
    rotated_path = file_location+'rotated'+'.jpg'
    flipped_path = file_location+'flipped'+'.jpg'
    noised_path = file_location+'noised'+'.jpg'
    imsave(flipped_path,flipped)
    imsave(noised_path,noised)
    imsave(rotated_path,rotated)

def writeCurrentB64ImageAsStudentID(face_photo_b64,student_id,i):
    filename = str(student_id) + '_face_' + str(i) + '.jpg'
    file_location = temp_face_img_dir + str(student_id) + '/' + filename
    face_photo_decoded = base64.b64decode((face_photo_b64[22:]))
#open temp image and write decoded base64 image into it
    face_photo_image_file = open(file_location,'wb')
    face_photo_image_file.write(face_photo_decoded)
    createAugmentedImages(file_location)
    face_photo_image_file.close()
    print("current image write completed!")


def writeB64toImagesAsStudentID(multiple_face_photo_b64s,student_id):
    try:
        os.mkdir(temp_face_img_dir+str(student_id))
    except:
        print("directory already exists")
        pass
    #Base64 string can be decoded from the 22nd character only. Thats why slicing is used
    i=0
    results = []
    with ProcessPoolExecutor(max_workers=8) as executor:
        for face_photo_b64 in multiple_face_photo_b64s:
            results.append(executor.submit(writeCurrentB64ImageAsStudentID,face_photo_b64,student_id,i))
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


def getCurrentEncodingsAndIds(student_id,student_image,student_images_location):
    try:
        img_location = student_images_location + student_image
        #img_file = open(student_image,'rb')
        face_photo = face_recognition.load_image_file(img_location)
        face_photo_encodings = face_recognition.face_encodings(face_photo)[0]
        return [face_photo_encodings,student_id]
    except:
        return []
def loadModelAndTrainUsingStudentImages(face_data_file_location,model_file_location,student_id, operation='create',no_of_images=0):
    
    #There should be more than one classname to train the model
    more_than_one_class = True
    try:
        known_face_encodings,student_ids = loadFaceData(face_data_file_location)
    except:
        known_face_encodings = []
        student_ids = []
    print("lengths before training:",len(known_face_encodings),len(student_ids))
    student_images_location = temp_face_img_dir + str(student_id) + '/'
    student_images = os.listdir(student_images_location)
    results = []
    if no_of_images>0:
        with ProcessPoolExecutor(max_workers=8) as executor:
            for student_image in student_images:
                results.append(executor.submit(getCurrentEncodingsAndIds,student_id,student_image,student_images_location))
        results = [r.result() for r in results]
        print(results)
        # current_student_ids = [result[1] for result in results]
        # current_face_encodings = [result[0] for result in results]
        current_student_ids = []
        current_face_encodings = []
        for result in results:
            if len(result)>0:
                current_face_encodings.append(result[0])
                current_student_ids.append(result[1])

        for i in range(len(current_student_ids)):
            known_face_encodings.append(current_face_encodings[i])
            student_ids.append(current_student_ids[i])
        print(len(student_ids))
        print(len(known_face_encodings))
    print("for loop completed")
    print(model_file_location)
    if(len(known_face_encodings) <= 32  or len(student_ids) <=32 ):
        more_than_one_class = False

    if more_than_one_class:
        model_file = open(model_file_location,'wb')
        model = svm.SVC(probability=True)
        print(student_ids)
        print("fitting started")
        model.fit(known_face_encodings,student_ids)
        model_file.close()
        print("model fitted completely")
        print("model classes:",model.classes_)
        model_file = open(model_file_location,'wb')
        pickle.dump(model,model_file)
    else:
        try:
            os.remove(model_file_location)
        except:
            print("couldnt delete model")
    
    print(student_ids)
    writeFaceEncodingsAndStudentIdsToPickle(student_ids,known_face_encodings, face_data_file_location)


def bak_loadModelAndTrainUsingStudentImages(face_data_file_location,model_file_location,student_id, operation='create',no_of_images=0):
    
    #There should be more than one classname to train the model
    more_than_one_class = True
    try:
        known_face_encodings,student_ids = loadFaceData(face_data_file_location)
    except:
        known_face_encodings = []
        student_ids = []
    print("lengths before training:",len(known_face_encodings),len(student_ids))
    student_images_location = temp_face_img_dir + str(student_id) + '/'
    student_images = os.listdir(student_images_location)
    if no_of_images>0:
        for student_image in student_images:
            #current_filename = str(student_id) + '_face_' + str(i) + '.jpg'
            #current_file_location = temp_face_img_dir + current_filename
            print(student_image)
            try:
                img_location = student_images_location + student_image
                #img_file = open(student_image,'rb')
                face_photo = face_recognition.load_image_file(img_location)
                face_photo_encodings = face_recognition.face_encodings(face_photo)[0]
                student_ids.append(student_id)
                known_face_encodings.append(face_photo_encodings)
            except:
                print("error eccured")
            try:
                pass
                #os.remove(current_file_location)
            except:
                print("couldnt delete")
                pass
    print("for loop completed")
    print(model_file_location)
    if(len(known_face_encodings) <= 32  or len(student_ids) <=32 ):
        more_than_one_class = False

    if more_than_one_class:
        model_file = open(model_file_location,'wb')
        model = svm.SVC(probability=True)
        print(student_ids)
        print("fitting started")
        model.fit(known_face_encodings,student_ids)
        model_file.close()
        print("model fitted completely")
        print("model classes:",model.classes_)
        model_file = open(model_file_location,'wb')
        pickle.dump(model,model_file)
    else:
        try:
            os.remove(model_file_location)
        except:
            print("couldnt delete model")
    
    print(student_ids)
    writeFaceEncodingsAndStudentIdsToPickle(student_ids,known_face_encodings, face_data_file_location)
  


def addNewStudentFace(stud_class_name,student_id,multiple_face_photo_b64s):
    print(len(multiple_face_photo_b64s))
    writeB64toImagesAsStudentID(multiple_face_photo_b64s,student_id)
    face_data_file_location = getFaceDataFileLocation(stud_class_name)
    model_file_location = getModelFileLocation(stud_class_name)
    no_of_images = len(multiple_face_photo_b64s)
    loadModelAndTrainUsingStudentImages(face_data_file_location,model_file_location,student_id, no_of_images=no_of_images)


def deleteAStudentsFaceEncodings(student_id,stud_class_name):
    #student_id = student_id
    print(student_id)
    face_data_file_location = getFaceDataFileLocation(stud_class_name)
    known_face_encodings,student_ids = loadFaceData(face_data_file_location)
    indexes = []
    print("lengths before deleting:",len(known_face_encodings),len(student_ids))
    print(student_ids)
    for i in range(0,len(student_ids)):
        if(student_ids[i] == student_id):
            indexes.append(i)
    print(indexes)
    i=0
    for index in indexes:
        student_ids.pop(index-i)
        known_face_encodings.pop(index-i)
        i+=1
    print("lengths after deleting:",len(known_face_encodings),len(student_ids))

    writeFaceEncodingsAndStudentIdsToPickle(student_ids,known_face_encodings,face_data_file_location)
    print(student_ids)

def editStudentFace(current_stud_class_name,updated_stud_class_name,student_id,multiple_face_photo_b64s=[]):
    no_of_images = len(multiple_face_photo_b64s)
    if(current_stud_class_name == updated_stud_class_name):
        if(no_of_images>0):
            deleteAStudentsFaceEncodings(student_id,current_stud_class_name)
            writeB64toImagesAsStudentID(multiple_face_photo_b64s,student_id)
            face_data_file_location = getFaceDataFileLocation(current_stud_class_name)
            model_file_location = getModelFileLocation(current_stud_class_name)
            no_of_images = len(multiple_face_photo_b64s)
            loadModelAndTrainUsingStudentImages(face_data_file_location,model_file_location,student_id,operation='edit',no_of_images=no_of_images)
        else:
            print("Nothing to do here")
    else:
        if(no_of_images==0):
            #Tran
            transferStudentFaceEncodingsToAnotherClass(current_stud_class_name,updated_stud_class_name,student_id)

        else:
            #Delete face_encodings from current class and retrain the model
            deleteAStudentsFaceEncodings(student_id,current_stud_class_name)
            face_data_file_location = getFaceDataFileLocation(current_stud_class_name)
            model_file_location = getModelFileLocation(current_stud_class_name)
            loadModelAndTrainUsingStudentImages(face_data_file_location,model_file_location,student_id,operation='edit')
            #Add the new face encodings to new class and train it           
            face_data_file_location = getFaceDataFileLocation(updated_stud_class_name)
            model_file_location = getModelFileLocation(updated_stud_class_name)
            writeB64toImagesAsStudentID(multiple_face_photo_b64s,student_id)
            loadModelAndTrainUsingStudentImages(face_data_file_location,model_file_location,student_id,operation='edit',no_of_images=no_of_images)

def transferStudentFaceEncodingsToAnotherClass(current_stud_class_name,updated_stud_class_name,student_id):
    #Delete face encodings from current class and retrain it
    current_face_data_file_location = getFaceDataFileLocation(current_stud_class_name)
    try:
        known_face_encodings,student_ids = loadFaceData(current_face_data_file_location)
    except:
        known_face_encodings = []
        student_ids = []
    students_face_encodings_to_transfer = []
    students_ids_to_transfer =[]
    indexes = []
    print("lengths before deleting:",len(known_face_encodings),len(student_ids))
    print(student_ids)
    for i in range(0,len(student_ids)):
        if(student_ids[i] == student_id):
            indexes.append(i)
    print(indexes)
    i=0
    for index in indexes:
        students_ids_to_transfer.append(student_ids.pop(index-i))
        students_face_encodings_to_transfer.append(known_face_encodings.pop(index-i))
        i+=1
    #print("lengths after deleting:",len(known_face_encodings),len(student_ids))
    writeFaceEncodingsAndStudentIdsToPickle(student_ids,known_face_encodings,current_face_data_file_location)
    current_model_file_location = getModelFileLocation(current_stud_class_name)
    known_face_encodings,student_ids = loadFaceData(current_face_data_file_location)
    loadModelAndTrainUsingStudentImages(current_face_data_file_location,current_model_file_location,student_id,operation='edit')
    
    #Add face encodings to updated class and retrain it
    updated_face_data_file_location = getFaceDataFileLocation(updated_stud_class_name)
    try:
        known_face_encodings,student_ids = loadFaceData(updated_face_data_file_location)
    except:
        known_face_encodings = []
        student_ids = []
    print("student_ids in updated file before writing:",student_ids)
    for i in range(len(students_ids_to_transfer)):
        student_ids.append(students_ids_to_transfer[i])
        known_face_encodings.append(students_face_encodings_to_transfer[i])
    print("student_ids in updated file after writing:",student_ids)
    writeFaceEncodingsAndStudentIdsToPickle(student_ids,known_face_encodings,updated_face_data_file_location)
    updated_model_file_location = getModelFileLocation(updated_stud_class_name)
    known_face_encodings,student_ids = loadFaceData(updated_face_data_file_location)
    loadModelAndTrainUsingStudentImages(updated_face_data_file_location,updated_model_file_location,student_id,operation='edit')


def deleteStudentFace(stud_class_name,student_id):
    deleteAStudentsFaceEncodings(student_id,stud_class_name)
    face_data_file_location = getFaceDataFileLocation(stud_class_name)
    model_file_location = getModelFileLocation(stud_class_name)
    loadModelAndTrainUsingStudentImages(face_data_file_location,model_file_location,student_id,operation='edit')


def writeB64toImage(face_photo_b64):
    temp_img_location = temp_image__path_for_checking + 'temp_' + '.jpg'
#Base64 string can be decoded from the 22nd character only. Thats why slicing is used
    face_photo_decoded = base64.b64decode((face_photo_b64[22:]))
#open temp image and write decoded base64 image into it
    face_photo_image_file = open(temp_img_location,'wb')
    face_photo_image_file.write(face_photo_decoded)
    face_photo_image_file.close()
    return temp_img_location

#Check if the image contains any face
def checkIfFacePhotoIsValid(face_photo_b64):

    temp_img_location = writeB64toImage(face_photo_b64)
    try:
        image = face_recognition.load_image_file(temp_img_location)
        face_photo_encodings = face_recognition.face_encodings(image)[0]
        return True
    except:
        return False



#Used for writing images send from frontend for verification into indexed jpg files
def writeB64ToImageForIdentifying(imageB64,index):
    temp_img_location = temp_img_path_for_identifying + 'temp_image_' + str(index) + '.jpg'
    #Base64 string can be decoded from the 22nd character only. Thats why slicing is used
    face_photo_decoded = base64.b64decode((imageB64[22:]))
    #open temp image and write decoded base64 image into it
    face_photo_image_file = open(temp_img_location,'wb')
    face_photo_image_file.write(face_photo_decoded)
    face_photo_image_file.close()  
    return temp_img_location  

def findCurrentMatchedId(index,imageB64,model):
    temp_img_location = writeB64ToImageForIdentifying(imageB64,index)
    try:
        image = face_recognition.load_image_file(temp_img_location)
        face_encodings = face_recognition.face_encodings(image)[0]
        try:
            os.remove(temp_img_location)
        except:
            print("couldnt delete dtect image")
        probabilities = list(model.predict_proba([face_encodings]))
        probabilities = list(probabilities[0])
        probs_copy = probabilities.copy()
        most_probable = max(probabilities)
        predicted_id = model.predict([face_encodings])[0]
        probs_copy.pop(probs_copy.index(max(probs_copy)))
        second_most_probable = probs_copy[probs_copy.index(max(probs_copy))]
        probs_copy.pop(probs_copy.index(max(probs_copy))) 
        #There should be atleast three classes in the model. This try block is if in case there is less than three classes
        try:      
            third_most_probable =  probs_copy[probs_copy.index(max(probs_copy))]
        except:
            third_most_probable = second_most_probable
        print(probabilities)
        print("Most probable percentage: ",most_probable*100,"%")
        if(most_probable>0.85):
            return predicted_id
        elif most_probable>0.5 and (second_most_probable+third_most_probable)<=(most_probable/2):
            return predicted_id
        elif most_probable<0.5:
            if (second_most_probable+third_most_probable)<=(most_probable/2):
                return predicted_id
            # if most_probable>0.45 and second_most_probable<(most_probable/2):
            #     return predicted_id
            # elif (second_most_probable+third_most_probable) <= (most_probable/2):
            #     return predicted_id
            else:
                return -1
        else:
            return -1
    except: 
        return -1


def predictStudentIdFromFace(images_to_detect,stud_class_name):
    model_file_location = getModelFileLocation(stud_class_name)
    try:
        model_file = open(model_file_location,'rb')
    except:
        print("Model file for the specified stud_class_name not found")
        return -1
    model = pickle.load(model_file)
    detected_ids = []
    print(model.classes_)
    index=1
    results = []
    start = perf_counter()
    with ProcessPoolExecutor(max_workers=8) as executor:
        for imageB64 in images_to_detect:
            future_obj = executor.submit(findCurrentMatchedId,index,imageB64,model)
            results.append(future_obj)
            index+=1
    all_matched_ids = [r.result() for r in results ]
    print(all_matched_ids)
    print(findMostRepeatedValueFromList(all_matched_ids))
    print("time: ",perf_counter()-start)
    return findMostRepeatedValueFromList(all_matched_ids)

def findMostRepeatedValueFromList(values):
    values = Counter(values)
    return values.most_common(1)[0][0]
