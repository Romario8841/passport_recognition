import imutils
from imutils import contours
import cv2
import uuid
import numpy as np
from scipy import ndimage

import tesseract


class Passport:
    # Путь до оригинального изображения.
    filePath = False
    # Путь до файлов с именем, фамилией, отчеством.
    nameFilePath = False
    surnameFilePath = False
    patronymicFilePath = False

    # Минимальное соотношение ширины к высоте рамки для фото.
    PHOTO_MIN_RATIO = 0.7

    # Минимальное соотношение длины к высоте красной линии
    LINE_SEPARATOR_MIN_RATIO = 8

    # Отступ по краям для результирующего изображения.
    RESULT_IMAGE_NAME_MARGIN = 3

    # Параметры для уменьшенного изображения
    RESIZED_IMAGE_HEIGHT = 500
    RESIZED_IMAGE_PHOTO_MIN_HEIGHT = 50
    RESIZED_IMAGE_PHOTO_MIN_WIDTH = 50
    RESIZED_IMAGE_NAME_MIN_WIDTH = 6
    RESIZED_IMAGE_NAME_MIN_HEIGHT = 3
    RESIZED_IMAGE_NAME_MAX_HEIGHT = 16
    RESIZED_IMAGE_NAME_MIN_X = 10
    RESIZED_IMAGE_NAME_MIN_RIHGTH_INDENT = 45

    # Расширение для создаваемых файлов.
    RESULT_IMAGES_EXTENSION = 'jpg'
    # Папку для сохранения изображений.
    # RESULT_IMAGES_FOLDER = 'img'
    RESULT_IMAGES_FOLDER = 'passport_recognition\\img'

    def __init__(self, filePath):
        self.filePath = filePath

    # Нахождение ФИО на изображении.
    # true - если найдено, иначе false.
    def processFullName(self):
        image = cv2.imread(self.filePath)

        image = self.CorrectOrientation(image)
        if (image is None):
            return False

        return self.getSnub(image), self.processFullNameInternal(image)

    # Приводим изображение к правильной ориентации через последовательные повороты на 90 градусов.
    def CorrectOrientation(self, origImage):
        reducedImage = imutils.resize(origImage.copy(), height=self.RESIZED_IMAGE_HEIGHT)
        for degree in [0, 90, 180, 270]:
            rotatedImage = imutils.rotate_bound(reducedImage, degree)
            if (self.isCorrectOrientation(rotatedImage)):
                return imutils.rotate_bound(origImage, degree)

        return None

    # Правильная ли ориентация у изображения.
    # Основываемся на красной линии посередине паспорта и рамки для фото.
    def isCorrectOrientation(self, image):
        redLineInfo = self.getredLineInfo(image)
        if (redLineInfo is None):
            return False

        redLineRatio = redLineInfo['w'] / float(redLineInfo['h'])
        if (redLineRatio < self.LINE_SEPARATOR_MIN_RATIO):
            return False

        photoInfo = self.getPhotoInfo(image)
        if (photoInfo is None):
            return False

        # Рамка для фото должна быть ниже красной линии.
        return True if photoInfo['minY'] > redLineInfo['y'] else False

    # Нахождение красной линии посередине паспорта.
    # Если линия найдена, возвращается информация о ней в виде {x,y,w,h}, иначе None.
    def getredLineInfo(self, reducedImage):

        redImage = self.getRedOnImage(reducedImage)

        widthKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 2))
        redModifiedImage = cv2.dilate(redImage, widthKernel)

        heightKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 8))
        redModifiedImage = cv2.dilate(redModifiedImage, heightKernel)

        imageContours = cv2.findContours(redModifiedImage.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        imageContours = imutils.grab_contours(imageContours)

        lineContourInfo = None
        contourMaxWidth = 0
        lineContourInfoList =  []
        for c in imageContours:
            (x, y, w, h) = cv2.boundingRect(c)
            if (w > contourMaxWidth):
                contourMaxWidth = w
                lineContourInfo = {'x': x, 'y': y, 'w': w, 'h': h}
        return lineContourInfo

    # Нахождение рамки для фото.
    # Если фото найдено, возвращается информация о ней в виде {minX,maxX,minY,maxY}, иначе None
    def getPhotoInfo(self, reducedImage):
        redImage = self.getRedOnImage(reducedImage)

        squareKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        redModifiedImage = cv2.dilate(redImage, squareKernel)

        imageContours = cv2.findContours(redModifiedImage.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        imageContours = imutils.grab_contours(imageContours)

        photoInfo = None
        maxContourWidth = 0


        for c in imageContours:
            maxInColumns = np.amax(c, axis=0)
            minInColumns = np.amin(c, axis=0)

            # Пример формата: [[25 631]]
            height = maxInColumns[0][0] - minInColumns[0][0]
            width = maxInColumns[0][1] - minInColumns[0][1]
            ratio = width / height if width < height else height / width

            if height > self.RESIZED_IMAGE_PHOTO_MIN_HEIGHT and \
                width > self.RESIZED_IMAGE_PHOTO_MIN_WIDTH and \
                ratio > self.PHOTO_MIN_RATIO and \
                width > maxContourWidth:
                maxContourWidth = width

                photoInfo = {
                    'minX': minInColumns[0][0],
                    'maxX': maxInColumns[0][0],
                    'minY': minInColumns[0][1],
                    'maxY': maxInColumns[0][1]
                }

        return photoInfo

    # Получение только красной части на изображении
    def getRedOnImage(self, image):
#         hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

#         redRange1 = cv2.inRange(hsvImage, np.array([0, 70, 50]), np.array([10, 255, 255]))
#         redRange2 = cv2.inRange(hsvImage, np.array([170, 70, 50]), np.array([180, 255, 255]))
#         redRange3 = cv2.inRange(hsvImage, np.array([160, 100, 100]), np.array([179, 255, 255]))
#         redImage = cv2.bitwise_or(redRange1, redRange2)
#         redImage = cv2.bitwise_or(redImage, redRange3)

#         # Нужно поиграться с этими значениями
#         redRange1 = cv2.inRange(hsvImage, np.array([0, 70, 50]), np.array([10, 255, 255]))
#         redRange2 = cv2.inRange(hsvImage, np.array([170, 70, 50]), np.array([180, 255, 255]))
#         redRange3 = cv2.inRange(hsvImage, np.array([160, 100, 100]), np.array([179, 255, 255]))
#
#         redImage = cv2.bitwise_or(redRange1, redRange2)
#         redImage = cv2.bitwise_or(redImage,  redRange3)
#
#         cv2.namedWindow("Image")
#         cv2.imshow("Image", redImage)
#         cv2.waitKey(0)

        #-----Reading the image-----------------------------------------------------
        img = image

        #-----Converting image to LAB Color model-----------------------------------
        lab= cv2.cvtColor(img, cv2.COLOR_BGR2LAB)


        #-----Splitting the LAB image to different channels-------------------------
        l, a, b = cv2.split(lab)

        #-----Applying CLAHE to L-channel-------------------------------------------
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)

        #-----Merge the CLAHE enhanced L-channel with the a and b channel-----------
        limg = cv2.merge((cl,a,b))

        #-----Converting image from LAB Color model to RGB model--------------------
        final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        image = final
        hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
#         redRange1 = cv2.inRange(hsvImage, np.array([0, 70, 50]), np.array([10, 255, 255]))
#         redRange2 = cv2.inRange(hsvImage, np.array([170, 70, 50]), np.array([180, 255, 255]))
#         redRange3 = cv2.inRange(hsvImage, np.array([160, 100, 100]), np.array([179, 255, 255]))
        redRange1 = cv2.inRange(hsvImage, np.array([10, 70, 50]), np.array([10, 255, 255]))
        redRange2 = cv2.inRange(hsvImage, np.array([135, 70, 50]), np.array([180, 255, 255]))
        redRange3 = cv2.inRange(hsvImage, np.array([180, 100, 100]), np.array([179, 255, 255]))

        redImage = cv2.bitwise_or(redRange1, redRange2)
        redImage = cv2.bitwise_or(redImage,  redRange3)

#         cv2.namedWindow("Image")
#         cv2.imshow("Image", redImage)
#         cv2.waitKey(0)

        return redImage

    # Нахождение ФИО на изображении, которое уже находится в правильной ориентации,
    # имеет серединную красную линию и рамку для фото.

    def getSnub(self, origImage):

        reducedImage = imutils.resize(origImage.copy(), height=self.RESIZED_IMAGE_HEIGHT)

        photoInfo = self.getPhotoInfo(reducedImage)

        rotated_snub = ndimage.rotate(origImage, 90)
        rot_path = "passport_recognition\\images\\rotated_snub.jpg"
        # rot_path = "images\\rotated_snub.jpg"
#         rot_path = "images\\rotated_snub.jpg"
        status = cv2.imwrite(rot_path, rotated_snub)
        return rot_path


    def processFullNameInternal(self, origImage):

        reducedImage = imutils.resize(origImage.copy(), height=self.RESIZED_IMAGE_HEIGHT)

        redLineInfo = self.getredLineInfo(reducedImage)
        photoInfo = self.getPhotoInfo(reducedImage)

        fullNameMinX = photoInfo['maxX']

        fullNameMaxX = redLineInfo['x'] + redLineInfo['w']

        fullNameMinY = redLineInfo['y'] + redLineInfo['h']

        fullNameMaxY = photoInfo['maxY']

        # Вырезаем часть, где находится ФИО: ниже красной линии, и правее рамки для фото.
        fullNameImage = reducedImage[fullNameMinY:fullNameMaxY, fullNameMinX:fullNameMaxX]


        fullNameModifiedImage = cv2.cvtColor(fullNameImage, cv2.COLOR_BGR2GRAY)
        fullNameModifiedImage = cv2.threshold(fullNameModifiedImage, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 3))
        fullNameModifiedImage = cv2.morphologyEx(fullNameModifiedImage, cv2.MORPH_CLOSE, rectKernel)
#         print('-')
#         cv2.namedWindow("Image")
#         cv2.imshow("Image", fullNameModifiedImage)
#         cv2.waitKey(0)
#         print('-')
        imageContours = cv2.findContours(fullNameModifiedImage.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        imageContours = imutils.grab_contours(imageContours)

        (sortedContours, boundingBoxes) = contours.sort_contours(imageContours, method="top-to-bottom")
        countNameContours = 0



        origImageRatio = origImage.shape[0] / float(self.RESIZED_IMAGE_HEIGHT)

        for с in sortedContours:

            (x, y, w, h) = cv2.boundingRect(с)

            if w > self.RESIZED_IMAGE_NAME_MIN_WIDTH and \
                self.RESIZED_IMAGE_NAME_MIN_HEIGHT < h < self.RESIZED_IMAGE_NAME_MAX_HEIGHT and \
                x > self.RESIZED_IMAGE_NAME_MIN_X and \
                fullNameImage.shape[1] - x > self.RESIZED_IMAGE_NAME_MIN_RIHGTH_INDENT:
                countNameContours = countNameContours + 1

                origImageCut = origImage[
                               int(((y + fullNameMinY - self.RESULT_IMAGE_NAME_MARGIN) * origImageRatio)):int(
                                   ((y + h + fullNameMinY + self.RESULT_IMAGE_NAME_MARGIN) * origImageRatio)),
                               int(((x + fullNameMinX - self.RESULT_IMAGE_NAME_MARGIN) * origImageRatio)):int(
                                   ((x + w + fullNameMinX + self.RESULT_IMAGE_NAME_MARGIN) * origImageRatio))
                               ]
                filePath = self.getUniqueFilePath(countNameContours)
                cv2.imwrite(filePath, origImageCut)

                if (countNameContours == 1):
                    self.surnameFilePath = filePath
                elif (countNameContours == 2):
                    self.nameFilePath = filePath
                elif (countNameContours == 3):
                    self.patronymicFilePath = filePath
                elif (countNameContours == 4):
                    self.birthDateFilePath = filePath
                elif (countNameContours == 5):
                    self.birthDateFilePath = filePath
                elif (countNameContours == 6):
                    self.birthDateFilePath = filePath
                elif (countNameContours == 7):
                    self.testDateFilePath = filePath
                if (countNameContours == 7):
                    break

        return True if countNameContours == 3 else False




    def getProcessedNameFilePaths(self):
        return self.getProcessedImagesVariants(self.nameFilePath, 1)

    def getProcessedSurnameFilePaths(self):
        return self.getProcessedImagesVariants(self.surnameFilePath, 2)

    def getProcessedPatronymicFilePaths(self):
        return self.getProcessedImagesVariants(self.patronymicFilePath, 3)

    # Обработка изображения для улучшенного распознавания
    # Возвращается массив путей для преобразованных файлов
    def getProcessedImagesVariants(self, filePath, ind):
        return

    def getUniqueFilePath(self, ind):
        if ind == 1:
            return self.RESULT_IMAGES_FOLDER + '\\' + 'surname' + '.' + self.RESULT_IMAGES_EXTENSION
            # customThresholdFilePath = self.RESULT_IMAGES_FOLDER + '/' + 'name' + '.' + self.RESULT_IMAGES_EXTENSION
        elif ind == 2:
            return self.RESULT_IMAGES_FOLDER + '\\' + 'name' + '.' + self.RESULT_IMAGES_EXTENSION
        elif ind == 3:
            return self.RESULT_IMAGES_FOLDER + '\\' + 'patronymic' + '.' + self.RESULT_IMAGES_EXTENSION
        elif ind == 4:
            return self.RESULT_IMAGES_FOLDER + '\\' + 'year' + '.' + self.RESULT_IMAGES_EXTENSION
        elif ind == 5:
            return self.RESULT_IMAGES_FOLDER + '\\' + 'month' + '.' + self.RESULT_IMAGES_EXTENSION
        elif ind == 6:
            return self.RESULT_IMAGES_FOLDER + '\\' + 'day' + '.' + self.RESULT_IMAGES_EXTENSION
        elif ind == 7:
            return self.RESULT_IMAGES_FOLDER + '\\' + 'test' + '.' + self.RESULT_IMAGES_EXTENSION
        # return self.RESULT_IMAGES_FOLDER + '/' + str(uuid.uuid4()) + '.' + self.RESULT_IMAGES_EXTENSION
