# -*- coding: utf-8 -*-
"""Number_plate_detection_CNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NXukSiiRhEh1lECShdc_VD4paBIDS0uF
"""

!sudo apt install tesseract-ocr
!pip install pytesseract

import math
import cv2


class ifChar:
    # this function contains some operations used by various function in the code
    def __init__(self, cntr):
        self.contour = cntr

        self.boundingRect = cv2.boundingRect(self.contour)

        [x, y, w, h] = self.boundingRect

        self.boundingRectX = x
        self.boundingRectY = y
        self.boundingRectWidth = w
        self.boundingRectHeight = h

        self.boundingRectArea = self.boundingRectWidth * self.boundingRectHeight

        self.centerX = (self.boundingRectX + self.boundingRectX + self.boundingRectWidth) / 2
        self.centerY = (self.boundingRectY + self.boundingRectY + self.boundingRectHeight) / 2

        self.diagonalSize = math.sqrt((self.boundingRectWidth ** 2) + (self.boundingRectHeight ** 2))

        self.aspectRatio = float(self.boundingRectWidth) / float(self.boundingRectHeight)


class PossiblePlate:

    def __init__(self):
        self.Plate = None
        self.Grayscale = None
        self.Thresh = None

        self.rrLocationOfPlateInScene = None

        self.strChars = ""


# this function is a 'first pass' that does a rough check on a contour to see if it could be a char
def checkIfChar(possibleChar):
    if (possibleChar.boundingRectArea > 80 and possibleChar.boundingRectWidth > 2
            and possibleChar.boundingRectHeight > 8 and 0.25 < possibleChar.aspectRatio < 1.0):

        return True
    else:
        return False


# check the center distance between characters
def distanceBetweenChars(firstChar, secondChar):
    x = abs(firstChar.centerX - secondChar.centerX)
    y = abs(firstChar.centerY - secondChar.centerY)

    return math.sqrt((x ** 2) + (y ** 2))


# use basic trigonometry (SOH CAH TOA) to calculate angle between chars
def angleBetweenChars(firstChar, secondChar):
    adjacent = float(abs(firstChar.centerX - secondChar.centerX))
    opposite = float(abs(firstChar.centerY - secondChar.centerY))

    # check to make sure we do not divide by zero if the center X positions are equal
    # float division by zero will cause a crash in Python
    if adjacent != 0.0:
        angleInRad = math.atan(opposite / adjacent)
    else:
        angleInRad = 1.5708

    # calculate angle in degrees
    angleInDeg = angleInRad * (180.0 / math.pi)

    return angleInDeg

import os
import zipfile

local_zip = '/content/folders.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('/content')
zip_ref.close()

from PIL import Image
import pytesseract
import argparse
import cv2
import os
import numpy as np
from google.colab.patches import cv2_imshow
import math

# this folder is used to save the image
temp_folder = '/content/plates'

# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", type=str, required=True, help="path to image")
# args = vars(ap.parse_args())

img = cv2.imread('/content/car2.png')
cv2_imshow(img)
# cv2.imwrite(temp_folder + '1 - original.png', img)

# hsv transform - value = gray image
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
hue, saturation, value = cv2.split(hsv)
print('hsv_value')
cv2_imshow(value)
# cv2.imwrite(temp_folder + '2 - gray.png', value)

# kernel to use for morphological operations
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

# applying topHat/blackHat operations
topHat = cv2.morphologyEx(value, cv2.MORPH_TOPHAT, kernel)
blackHat = cv2.morphologyEx(value, cv2.MORPH_BLACKHAT, kernel)
print('tophat')
cv2_imshow(topHat)
print('blackhat')
cv2_imshow(blackHat)
# cv2.imwrite(temp_folder + '3 - topHat.png', topHat)
# cv2.imwrite(temp_folder + '4 - blackHat.png', blackHat)

# add and subtract between morphological operations
add = cv2.add(value, topHat)
subtract = cv2.subtract(add, blackHat)
print('Substract')
cv2_imshow(subtract)
# cv2.imwrite(temp_folder + '5 - subtract.png', subtract)

# applying gaussian blur on subtract image
blur = cv2.GaussianBlur(subtract, (5, 5), 0)
print('Blur')
cv2_imshow(blur)
# cv2.imwrite(temp_folder + '6 - blur.png', blur)

# thresholding
thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 19, 9)
print('Thresh')
cv2_imshow(thresh)
# cv2.imwrite(temp_folder + '7 - thresh.png', thresh)

# check for contours on thresh
# if using OpenCV 3.4
imageContours, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

# else, if OpenCV >= 4, try
#contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

# get height and width
height, width = thresh.shape

# create a numpy array with shape given by threshed image value dimensions
imageContours = np.zeros((height, width, 3), dtype=np.uint8)

# list and counter of possible chars
possibleChars = []
countOfPossibleChars = 0

# loop to check if any (possible) char is found
for i in range(0, len(contours)):

    # draw contours based on actual found contours of thresh image
    cv2.drawContours(imageContours, contours, i, (255, 255, 255))

    # retrieve a possible char by the result ifChar class give us
    possibleChar = ifChar(contours[i])

    # by computing some values (area, width, height, aspect ratio) possibleChars list is being populated
    if checkIfChar(possibleChar) is True:
        countOfPossibleChars = countOfPossibleChars + 1
        possibleChars.append(possibleChar)
        
print('imagecontours')

cv2_imshow(imageContours)
# cv2.imwrite(temp_folder + '8 - imageContours.png', imageContours)

imageContours = np.zeros((height, width, 3), np.uint8)

ctrs = []

# populating ctrs list with each char of possibleChars
for char in possibleChars:
    ctrs.append(char.contour)

# using values from ctrs to draw new contours
cv2.drawContours(imageContours, ctrs, -1, (255, 255, 255))
print('imagecontours')
cv2_imshow(imageContours)
# cv2.imwrite(temp_folder + '9 - contoursPossibleChars.png', imageContours)

plates_list = []
listOfListsOfMatchingChars = []

for possibleC in possibleChars:

    # the purpose of this function is, given a possible char and a big list of possible chars,
    # find all chars in the big list that are a match for the single possible char, and return those matching chars as a list
    def matchingChars(possibleC, possibleChars):
        listOfMatchingChars = []

        # if the char we attempting to find matches for is the exact same char as the char in the big list we are currently checking
        # then we should not include it in the list of matches b/c that would end up double including the current char
        # so do not add to list of matches and jump back to top of for loop
        for possibleMatchingChar in possibleChars:
            if possibleMatchingChar == possibleC:
                continue

            # compute stuff to see if chars are a match
            db = distanceBetweenChars(possibleC, possibleMatchingChar)

            ab = angleBetweenChars(possibleC, possibleMatchingChar)

            changeInArea = float(abs(possibleMatchingChar.boundingRectArea - possibleC.boundingRectArea)) / float(
                possibleC.boundingRectArea)

            changeInWidth = float(abs(possibleMatchingChar.boundingRectWidth - possibleC.boundingRectWidth)) / float(
                possibleC.boundingRectWidth)

            changeInHeight = float(abs(possibleMatchingChar.boundingRectHeight - possibleC.boundingRectHeight)) / float(
                possibleC.boundingRectHeight)

            # check if chars match
            if db < (possibleC.diagonalSize * 5) and ab < 12.0 and changeInArea < 0.5 and changeInWidth < 0.8 and changeInHeight < 0.2:
                listOfMatchingChars.append(possibleMatchingChar)

        return listOfMatchingChars


    # here we are re-arranging the one big list of chars into a list of lists of matching chars
    # the chars that are not found to be in a group of matches do not need to be considered further
    listOfMatchingChars = matchingChars(possibleC, possibleChars)

    listOfMatchingChars.append(possibleC)

    # if current possible list of matching chars is not long enough to constitute a possible plate
    # jump back to the top of the for loop and try again with next char
    if len(listOfMatchingChars) < 3:
        continue

    # here the current list passed test as a "group" or "cluster" of matching chars
    listOfListsOfMatchingChars.append(listOfMatchingChars)

    # remove the current list of matching chars from the big list so we don't use those same chars twice,
    # make sure to make a new big list for this since we don't want to change the original big list
    listOfPossibleCharsWithCurrentMatchesRemoved = list(set(possibleChars) - set(listOfMatchingChars))

    recursiveListOfListsOfMatchingChars = []

    for recursiveListOfMatchingChars in recursiveListOfListsOfMatchingChars:
        listOfListsOfMatchingChars.append(recursiveListOfMatchingChars)

    break

imageContours = np.zeros((height, width, 3), np.uint8)

for listOfMatchingChars in listOfListsOfMatchingChars:
    contoursColor = (255, 0, 255)

    contours = []

    for matchingChar in listOfMatchingChars:
        contours.append(matchingChar.contour)

    cv2.drawContours(imageContours, contours, -1, contoursColor)

print("finalContours")
cv2_imshow( imageContours)
# cv2.imwrite(temp_folder + '10 - finalContours.png', imageContours)

for listOfMatchingChars in listOfListsOfMatchingChars:
    possiblePlate = PossiblePlate()

    # sort chars from left to right based on x position
    listOfMatchingChars.sort(key=lambda matchingChar: matchingChar.centerX)

    # calculate the center point of the plate
    plateCenterX = (listOfMatchingChars[0].centerX + listOfMatchingChars[len(listOfMatchingChars) - 1].centerX) / 2.0
    plateCenterY = (listOfMatchingChars[0].centerY + listOfMatchingChars[len(listOfMatchingChars) - 1].centerY) / 2.0

    plateCenter = plateCenterX, plateCenterY

    # calculate plate width and height
    plateWidth = int((listOfMatchingChars[len(listOfMatchingChars) - 1].boundingRectX + listOfMatchingChars[
        len(listOfMatchingChars) - 1].boundingRectWidth - listOfMatchingChars[0].boundingRectX) * 1.3)

    totalOfCharHeights = 0

    for matchingChar in listOfMatchingChars:
        totalOfCharHeights = totalOfCharHeights + matchingChar.boundingRectHeight

    averageCharHeight = totalOfCharHeights / len(listOfMatchingChars)

    plateHeight = int(averageCharHeight * 1.5)

    # calculate correction angle of plate region
    opposite = listOfMatchingChars[len(listOfMatchingChars) - 1].centerY - listOfMatchingChars[0].centerY

    hypotenuse = distanceBetweenChars(listOfMatchingChars[0],
                                                listOfMatchingChars[len(listOfMatchingChars) - 1])
    correctionAngleInRad = math.asin(opposite / hypotenuse)
    correctionAngleInDeg = correctionAngleInRad * (180.0 / math.pi)

    # pack plate region center point, width and height, and correction angle into rotated rect member variable of plate
    possiblePlate.rrLocationOfPlateInScene = (tuple(plateCenter), (plateWidth, plateHeight), correctionAngleInDeg)

    # get the rotation matrix for our calculated correction angle
    rotationMatrix = cv2.getRotationMatrix2D(tuple(plateCenter), correctionAngleInDeg, 1.0)

    height, width, numChannels = img.shape

    # rotate the entire image
    imgRotated = cv2.warpAffine(img, rotationMatrix, (width, height))

    # crop the image/plate detected
    imgCropped = cv2.getRectSubPix(imgRotated, (plateWidth, plateHeight), tuple(plateCenter))

    # copy the cropped plate image into the applicable member variable of the possible plate
    possiblePlate.Plate = imgCropped

    # populate plates_list with the detected plate
    if possiblePlate.Plate is not None:
        plates_list.append(possiblePlate)

    # draw a ROI on the original image
    for i in range(0, len(plates_list)):
        # finds the four vertices of a rotated rect - it is useful to draw the rectangle.
        p2fRectPoints = cv2.boxPoints(plates_list[i].rrLocationOfPlateInScene)

        # roi rectangle colour
        rectColour = (0, 255, 0)

        cv2.line(imageContours, tuple(p2fRectPoints[0]), tuple(p2fRectPoints[1]), rectColour, 2)
        cv2.line(imageContours, tuple(p2fRectPoints[1]), tuple(p2fRectPoints[2]), rectColour, 2)
        cv2.line(imageContours, tuple(p2fRectPoints[2]), tuple(p2fRectPoints[3]), rectColour, 2)
        cv2.line(imageContours, tuple(p2fRectPoints[3]), tuple(p2fRectPoints[0]), rectColour, 2)

        cv2.line(img, tuple(p2fRectPoints[0]), tuple(p2fRectPoints[1]), rectColour, 2)
        cv2.line(img, tuple(p2fRectPoints[1]), tuple(p2fRectPoints[2]), rectColour, 2)
        cv2.line(img, tuple(p2fRectPoints[2]), tuple(p2fRectPoints[3]), rectColour, 2)
        cv2.line(img, tuple(p2fRectPoints[3]), tuple(p2fRectPoints[0]), rectColour, 2)
        print("detected")
        cv2_imshow(imageContours)
        # cv2.imwrite(temp_folder + '11 - detected.png', imageContours)
        print("detectedOriginal")
        cv2_imshow(img)
        # cv2.imwrite(temp_folder + '12 - detectedOriginal.png', img)
        print('plates')
        cv2_imshow(plates_list[i].Plate)
        print(i)
        cv2.imwrite(temp_folder+'/plates.png' , plates_list[i].Plate)

cv2.waitKey(0)

import cv2
import numpy as np
import glob
import pytesseract

plates = glob.glob("/content/plates/*.png")
processed = glob.glob("/content/processed/*.png")
resized = glob.glob("/content/resized/*.png")
bordered = glob.glob("/content/bordered/*.png")


def Threshold(plates):
    for i, plate in enumerate(plates):
        img = cv2.imread(plate)

        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        cv2_imshow(gray)

        ret, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
        print('Threshold')
        cv2_imshow(thresh)

        threshMean = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 10)
        print('Adaptive_Threshold')
        cv2_imshow(threshMean)

        threshGauss = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 51, 27)
        print('Thresh_Gauss')
        cv2_imshow(threshGauss)
        cv2.imwrite("/content/processed/plate{}.png".format(i), threshGauss)

        cv2.waitKey(0)


def res(processed):
    for i, image in enumerate(processed):
        image = cv2.imread(image)

        ratio = 200.0 / image.shape[1]
        dim = (200, int(image.shape[0] * ratio))

        resizedCubic = cv2.resize(image, dim, interpolation=cv2.INTER_CUBIC)

        cv2.imwrite("/content/resized/plate{}.png".format(i), resizedCubic)


def addB(resized):
    for i, image in enumerate(resized):
        image = cv2.imread(image)

        bordersize = 10
        border = cv2.copyMakeBorder(image, top=bordersize, bottom=bordersize, left=bordersize, right=bordersize,
                                    borderType=cv2.BORDER_CONSTANT, value=[255, 255, 255])

        cv2.imwrite("/content/bordered/plate{}.png".format(i), border)

        
def cle(borders):
    detectedOCR = []

    for i, image in enumerate(borders):
        image = cv2.imread(image)
        img=image.copy()

        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(image=edges, rho=1, theta=np.pi / 180, threshold=100, lines=np.array([]),
                                minLineLength=100, maxLineGap=80)
        #print(lines.shape)
#         for x in range(0, len(lines)):
#           for x1,y1,x2,y2 in lines[x]:
#             cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
#         print('hough')
#         cv2_imshow(img)
         

        try:
          a, b, c = lines.shape
          for i in range(a):
              x = lines[i][0][0] - lines[i][0][2]
              y = lines[i][0][1] - lines[i][0][3]
              if x != 0:
                  if abs(y / x) < 1:
                      cv2.line(image, (lines[i][0][0], lines[i][0][1]), (lines[i][0][2], lines[i][0][3]), (255, 255, 255),
                              1, cv2.LINE_AA)
        except AttributeError:
          print('shape not found')

        se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        gray = cv2.morphologyEx(image, cv2.MORPH_CLOSE, se)
        print('morph')
        cv2_imshow(gray)
        cv2.imwrite("/content/morphed/plate{}.png".format(i), morphed)
        
        
Threshold(plates)
res(processed)
addB(resized)
cle(bordered)
