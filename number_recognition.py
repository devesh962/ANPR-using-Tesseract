# -*- coding: utf-8 -*-
"""number_recognition.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ybt8gmOoNS70cIkKoENRjLc0WiRlr5Y3
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPool2D
from keras import optimizers
from keras.datasets import mnist
from keras.utils import to_categorical
import keras


# ### loading mist hand written dataset

(X_train, y_train), (X_test, y_test) = mnist.load_data()
print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)




# ## Applying threshold for removing noise 

_,X_train_th = cv2.threshold(X_train,127,255,cv2.THRESH_BINARY)
_,X_test_th = cv2.threshold(X_test,127,255,cv2.THRESH_BINARY)




# ### Reshaping 

X_train = X_train_th.reshape(-1,28,28,1)
X_test = X_test_th.reshape(-1,28,28,1)




# ### Creating categorical output from 0 to 9

y_train = to_categorical(y_train, num_classes = 10)
y_test = to_categorical(y_test, num_classes = 10)


# ## cross checking shape of input and output

print(X_train.shape, y_train.shape)
print(X_test.shape, y_test.shape)


# # Creating CNN model

input_shape = (28,28,1)
number_of_classes = 10

model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3),activation='relu',input_shape=input_shape))

model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPool2D(pool_size=(2, 2)))

model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(128, activation='relu'))

model.add(Dropout(0.5))
model.add(Dense(number_of_classes, activation='softmax'))

model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=keras.optimizers.Adadelta(),metrics=['accuracy'])

model.summary()

history = model.fit(X_train, y_train,epochs=100, shuffle=True,
                    batch_size = 200,validation_data= (X_test, y_test))


#model.save('digit_classifier2.h5')

import cv2
import numpy as np        
import matplotlib.pyplot as plt
from scipy import ndimage
import math
from keras.models import load_model
from google.colab.patches import cv2_imshow


# loading pre trained model

def predict_digit(img):
    test_image = img.reshape(-1,28,28,1)
   
    return np.argmax(model.predict(test_image))


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
    #cv2.drawContours(img, contours, -1, (0,255,0), 3)


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
            #cv2_imshow(roi)
            th,fnl = cv2.threshold(roi,127,255,cv2.THRESH_BINARY)

            # getting prediction of cropped image
            pred = predict_digit(roi)
            print(pred)
            
            # placing label on each digit
            (x,y),radius = cv2.minEnclosingCircle(cnt)
            
            img_org = put_label(img_org,pred,x,y)

    return img_org
  
  
x=get_output_image(morphed)
y=cv2.imread(morphed)
cv2_imshow(y)
cv2_imshow(x)

from IPython.display import display, Javascript
from google.colab.output import eval_js
from base64 import b64decode

def take_photo(filename='photo.jpg', quality=0.8):
  js = Javascript('''
    async function takePhoto(quality) {
      const div = document.createElement('div');
      const capture = document.createElement('button');
      capture.textContent = 'Capture';
      div.appendChild(capture);

      const video = document.createElement('video');
      video.style.display = 'block';
      const stream = await navigator.mediaDevices.getUserMedia({video: true});

      document.body.appendChild(div);
      div.appendChild(video);
      video.srcObject = stream;
      await video.play();

      // Resize the output to fit the video element.
      google.colab.output.setIframeHeight(document.documentElement.scrollHeight, true);

      // Wait for Capture to be clicked.
      await new Promise((resolve) => capture.onclick = resolve);

      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d').drawImage(video, 0, 0);
      stream.getVideoTracks()[0].stop();
      div.remove();
      return canvas.toDataURL('image/jpeg', quality);
    }
    ''')
  display(js)
  data = eval_js('takePhoto({})'.format(quality))
  binary = b64decode(data.split(',')[1])
  with open(filename, 'wb') as f:
    f.write(binary)
  return filename

from IPython.display import Image
try:
  filename = take_photo()
  print('Saved to {}'.format(filename))
  
  # Show the image which was just taken.
  display(Image(filename))
except Exception as err:
  # Errors will be thrown if the user does not have a webcam or if they do not
  # grant the page permission to access it.
  print(str(err))