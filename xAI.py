# -*- coding: utf-8 -*-
"""u-jhellison.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oBeO1mQIjlTVoGjhoe__ddriGDtdQji8
"""

from google.colab import drive
drive.mount('/content/gdrive')

import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import cv2
import imutils
from google.colab.patches import cv2_imshow
import imutils
import pandas as pd

TRAINING_DATA_PATH = "/content/gdrive/MyDrive/Images/train"
TESTING_DATA_PATH = "/content/gdrive/MyDrive/Images/test"

TRAINING_DATA_CSV = "/content/gdrive/MyDrive/Images/assignment5_training_data_metadata.csv"

CATEGORIES = ["normal", "virus", "bacteria"]

content = pd.read_csv(TRAINING_DATA_CSV, usecols = ['image_name', 'type'], low_memory = True)
training_list = {}

#Looping through every row, defining category for each image, skipping 'stress smoking' - not enough samples
for index, row in content.iterrows():
    if pd.isna(row['type']):
        training_list.update({row['image_name'].lower(): 0})
    else:
      if row['type'].lower() != "stress-smoking":
        training_list.update({row['image_name'].lower(): CATEGORIES.index(row['type'].lower())})

#Setting image size for training data
IMG_SIZE = 250

training_data = []
newIndex = 0

normalNumber, normalIndex = 0, []
virusNumber, virusIndex = 0, []
bacteriaNumber, bacteriaIndex = 0, []
smokeNumber, smokeIndex = 0, []

#Looping through every image from TRAINING_DATA_PATH, reading it, resizing it and adding to the training data.
for img in os.listdir(TRAINING_DATA_PATH):
  index = training_list.get(img.lower())
  if index != None:
    newIndex += 1
    if CATEGORIES[index] == "virus":
      virusNumber += 1
      virusIndex.append(img)
    elif CATEGORIES[index] == "bacteria":
      bacteriaNumber += 1
      bacteriaIndex.append(img)
    else:
      normalNumber += 1
      normalIndex.append(img)
    
    img_array = cv2.imread(os.path.join(TRAINING_DATA_PATH, img), cv2.IMREAD_GRAYSCALE)   #reading the image - then resizing it
    img_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
    training_data.append([img_array, index])
  #print(newIndex)    #used for debugging - just so you know if the program is running correctly

import random
from random import randint
 
def generateImage(_img):  #Rotating an image for +- maxRotateAngle.
  maxRotateAngle = 1.5
  rotated = imutils.rotate(_img, (random.random() * (2*maxRotateAngle)) - maxRotateAngle)
  return rotated
 
def dataAug():  #Generating new images as a part of data augmentation --> equalizing a number of images.
  most = max(normalNumber, virusNumber, bacteriaNumber)
  for norm in range(most-normalNumber):
    index = randint(0, len(normalIndex))
    img_array = cv2.imread(os.path.join(TRAINING_DATA_PATH, virusIndex[index]), cv2.IMREAD_GRAYSCALE)
    try:
      img_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
      training_data.append([generateImage(img_array), 0])
    except Exception as e:
      pass

  for vir in range(most-virusNumber):
    index = randint(0, len(virusIndex)-1)
    img_array = cv2.imread(os.path.join(TRAINING_DATA_PATH, virusIndex[index]), cv2.IMREAD_GRAYSCALE)
    try:
      img_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
      training_data.append([generateImage(img_array), 1])
    except Exception as e:
      pass

  for bac in range(most-bacteriaNumber):
    index = randint(0, len(bacteriaIndex)-1)
    img_array = cv2.imread(os.path.join(TRAINING_DATA_PATH, virusIndex[index]), cv2.IMREAD_GRAYSCALE)
    try:
      img_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
      training_data.append([generateImage(img_array), 2])
    except Exception as e:
      pass

dataAug()

import random
random.shuffle(training_data) #Shuffling the data.

X, y = [], []

for features, label in training_data: #Dividing labels and features.
  X.append(features)
  y.append(label)

import pickle

#Saving the training data.
#Using pickle to save the arrays, so there is no need of running the code above multiple times
pickle_out = open("/content/gdrive/MyDrive/x.pickle", "wb")
pickle.dump(X, pickle_out)
pickle_out.close()

pickle_out = open("/content/gdrive/MyDrive/y.pickle", "wb")
pickle.dump(y, pickle_out)
pickle_out.close()

import tensorflow as tf

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten, Conv2D, MaxPooling2D

import pickle

#Loading previously stored training data.
X = pickle.load(open("/content/gdrive/MyDrive/x.pickle", "rb"))
y = pickle.load(open("/content/gdrive/MyDrive/y.pickle", "rb"))

X = np.array(X).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
y = np.array(y)
X = X/255 #normalization - the image values are always between 0-255, so by dividing them by 255 we get a 0-1 range
#######
# got the best results with normalization, widely used for image ML
#######

#Creating a CNN model.
model = Sequential()

model.add(Conv2D(64, (6,6), input_shape = X.shape[1:]))
model.add(Activation("relu"))
model.add(MaxPooling2D(pool_size=(4,4)))

model.add(Conv2D(64, (6,6)))
model.add(Activation("relu"))
model.add(MaxPooling2D(pool_size=(4,4)))

model.add(Flatten())  #Flattening 2D layers to 1D(Dense layers).

model.add(Dense(128, activation=tf.nn.relu))
model.add(Dense(64, activation=tf.nn.relu))
model.add(Dense(3, activation=tf.nn.softmax))

model.compile(loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

model.fit(X, y, batch_size=16, validation_split=0.05, epochs=4)   #training the model

model.save("/content/gdrive/MyDrive/4epochs.model")

import pandas as pd
import numpy as np

DATA_CSV = '/content/gdrive/MyDrive/Images/assignment5_test_data_metadata.csv' 

content = pd.read_csv(DATA_CSV, usecols = ['image_name', 'id'], low_memory = True)

def predict(imageName): #Loading images from TESTING_DATA_PATH and predicting their value.
  img_array = cv2.imread(os.path.join(TESTING_DATA_PATH, imageName), cv2.IMREAD_GRAYSCALE)
  img_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
  img_array = np.array(img_array).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
  img_array = img_array/255
  prediction = model.predict([img_array])
  return np.argmax(prediction)+1

new_content = []
for index, row in content.iterrows(): #Creating DataFrame for output.csv file.
  new_content.append([row['id'], predict(row['image_name'])])

new_content = pd.DataFrame(new_content, columns=['id', 'type'])
new_content.to_csv('/content/gdrive/MyDrive/output8epochs.csv', index =False)