# -*- coding: utf-8 -*-
"""Number_Plate_4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19ej1GXv7TWFKUOCnGlODUKLwzUPpHYmc
"""

!pip install -U -q kaggle
!mkdir -p ~/.kaggle

from google.colab import files
files.upload()

!cp kaggle.json ~/.kaggle/

!chmod 600 /root/.kaggle/kaggle.json

!kaggle datasets download -d crawford/emnist

import os
import zipfile

local_zip = '/content/emnist.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('/content')
zip_ref.close()

import numpy as np 
import pandas as pd

from tensorflow import keras


import matplotlib.pyplot as plt

train_data_path = '/content/emnist-balanced-train.csv'
test_data_path = '/content/emnist-balanced-test.csv'

train_data = pd.read_csv(train_data_path, header=None)

train_data.head(10)

# The classes of this balanced dataset are as follows. Index into it based on class label
class_mapping = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabdefghnqrt'
# source data: https://arxiv.org/pdf/1702.05373.pdf

class_mapping[34]

train_data.shape

num_classes = len(train_data[0].unique())
row_num = 8

plt.imshow(train_data.values[row_num, 1:].reshape([28, 28]), cmap='Greys_r')
plt.show()

img_flip = np.transpose(train_data.values[row_num,1:].reshape(28, 28), axes=[1,0]) # img_size * img_size arrays
plt.imshow(img_flip, cmap='Greys_r')

plt.show()

def show_img(data, row_num):
    img_flip = np.transpose(data.values[row_num,1:].reshape(28, 28), axes=[1,0]) # img_size * img_size arrays
    plt.title('Class: ' + str(data.values[row_num,0]) + ', Label: ' + str(class_mapping[data.values[row_num,0]]))
    plt.imshow(img_flip, cmap='Greys_r')

show_img(train_data, 90)

# 10 digits, 26 letters, and 11 capital letters that are different looking from their lowercase counterparts

num_classes = 47 
img_size = 28

def img_label_load(data_path, num_classes=None):
    data = pd.read_csv(data_path, header=None)
    data_rows = len(data)
    if not num_classes:
        num_classes = len(data[0].unique())
    
    # this assumes square imgs. Should be 28x28
    img_size = int(np.sqrt(len(data.iloc[0][1:])))
    
    # Images need to be transposed. This line also does the reshaping needed.
    imgs = np.transpose(data.values[:,1:].reshape(data_rows, img_size, img_size, 1), axes=[0,2,1,3]) # img_size * img_size arrays
    print(imgs.shape)
    labels = keras.utils.to_categorical(data.values[:,0], num_classes) # one-hot encoding vectors
    
    return imgs/255., labels

import tensorflow as tf
    from tensorflow import keras
    import numpy as np # linear algebra
    import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

    import keras
    from keras.models import Sequential
    from keras.layers import Dense, Dropout, Flatten
    from keras.layers import Conv2D, MaxPooling2D,BatchNormalization
    from keras import backend as K

    model = keras.models.Sequential()

    output_size=num_classes
    model.add(Conv2D(32, kernel_size = 3, activation='relu', input_shape = (28, 28, 1)))
    model.add(BatchNormalization())
    model.add(Conv2D(32, kernel_size = 3, activation='relu'))
    model.add(BatchNormalization())
    model.add(Conv2D(32, kernel_size = 5, strides=2, padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(0.4))

    model.add(Conv2D(64, kernel_size = 3, activation='relu'))
    model.add(BatchNormalization())
    model.add(Conv2D(64, kernel_size = 3, activation='relu'))
    model.add(BatchNormalization())
    model.add(Conv2D(64, kernel_size = 5, strides=2, padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(0.4))

    model.add(Conv2D(128, kernel_size = 4, activation='relu'))
    model.add(BatchNormalization())
    model.add(Flatten())
    model.add(Dropout(0.4))
    model.add(Dense(output_size, activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='Adam', metrics=['accuracy'])
model.summary()

for layer in model.layers:
    print(layer.get_output_at(0).get_shape().as_list())

X, y = img_label_load(train_data_path)
print(X.shape)
print(y.shape)

class myCallback(keras.callbacks.Callback):
  def on_epoch_end(self,epoch,logs={}):
    if(logs.get('acc')>95.0):
      print("\n reached 99.9% accuracy so cancelling training!")
      self.model.stop_training = True

callbacks = myCallback()

data_generator = keras.preprocessing.image.ImageDataGenerator(validation_split=.2)

data_generator_with_aug = keras.preprocessing.image.ImageDataGenerator(validation_split=.2,
                                            width_shift_range=.2, height_shift_range=.2,
                                            zoom_range=.2, shear_range=.3)



training_data_generator = data_generator.flow(X, y, subset='training')
validation_data_generator = data_generator.flow(X, y, subset='validation')
history = model.fit_generator(training_data_generator, 
                              steps_per_epoch=500, epochs=500, # can change epochs to 10
                              validation_data=validation_data_generator,validation_steps=100,callbacks=[callbacks])

import cv2
import numpy as np        
import matplotlib.pyplot as plt
from scipy import ndimage
import math
from keras.models import load_model
from google.colab.patches import cv2_imshow


# loading pre trained model

def predict_digit(img):
    plt.imshow(img)
    test_image = img.reshape(-1,28,28,1)

    predicted_indices=np.argmax(model.predict(test_image))
    print(predicted_indices)
    #labels = (training_data_generator.class_indices)
    #labels = dict((v,k) for k,v in labels.items())
    #print(labels)
    #predictions = [labels[k] for k in predicted_indices]
    return class_mapping[predicted_indices]


#putting label
def put_label(t_img,label,x,y):
    font = cv2.FONT_HERSHEY_SIMPLEX
    l_x = int(x) - 10
    l_y = int(y) + 10
    cv2.rectangle(t_img,(l_x,l_y+5),(l_x+35,l_y-35),(0,255,0),-1) 
    cv2.putText(t_img,str(label),(l_x,l_y), font,1.5,(255,0,0),1,cv2.LINE_AA)
    
    return t_img

# refining each digit
def image_refiner(gray):
    org_size = 22
    img_size = 28
    rows,cols = gray.shape
    
    if rows > cols:
        factor = org_size/rows
        rows = org_size
        cols = int(round(cols*factor))        
    else:
        factor = org_size/cols
        cols = org_size
        rows = int(round(rows*factor))
    gray = cv2.resize(gray, (cols, rows))
    cv2_imshow(gray)
    
    #get padding 
    colsPadding = (int(math.ceil((img_size-cols)/2.0)),int(math.floor((img_size-cols)/2.0)))
    rowsPadding = (int(math.ceil((img_size-rows)/2.0)),int(math.floor((img_size-rows)/2.0)))
    
    #apply apdding 
    gray = np.lib.pad(gray,(rowsPadding,colsPadding),'constant')
    cv2_imshow(gray)
    return gray




def get_output_image(path):
  
    img = cv2.imread(path,2)
    img_org =  cv2.imread(path)

    ret,thresh = cv2.threshold(img,127,255,0)
    im2,contours,hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img, contours, -1, (0,255,0), 3)


    for j,cnt in enumerate(contours):
        epsilon = 0.01*cv2.arcLength(cnt,True)
        approx = cv2.approxPolyDP(cnt,epsilon,True)
        
        hull = cv2.convexHull(cnt)
        k = cv2.isContourConvex(cnt)
        x,y,w,h = cv2.boundingRect(cnt)
        
        
        if(hierarchy[0][j][3]!=-1 and w>10 and h>10):
            #putting boundary on each digit
            contours=cv2.rectangle(img_org,(x,y),(x+w,y+h),(0,255,0),2)
            #cv2.drawContours(img,contours , -1, (0,255,0), 3)
            
            #cropping each image and process
            roi = img[y:y+h, x:x+w]
            roi = cv2.bitwise_not(roi)
            roi = image_refiner(roi)
            th,fnl = cv2.threshold(roi,127,255,cv2.THRESH_BINARY)

            # getting prediction of cropped image
            pred = predict_digit(roi)
            print(pred)
            
            # placing label on each digit
            (x,y),radius = cv2.minEnclosingCircle(cnt)
            img_org = put_label(img_org,pred,x,y)

    return img_org
  
  
x=get_output_image('indiaAP.jpg')
cv2_imshow(x)
