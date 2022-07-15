import mysql.connector

import image_processing
import tesseract
import sys
import json

#


while True:

    with open('passport.jpg', "wb") as file:
            # Добавить аргумент при вызове файла, и его значение записать в переменную filepath
            filepath = sys.argv[1]
            passport = image_processing.Passport(filepath)
            isProcessSuccess = passport.processFullName()

            # if (isProcessSuccess == False):
            #     print('error')
            #

            res = ""
            surnameFilePaths = passport.getProcessedSurnameFilePaths()
            nameFilePaths = passport.getProcessedNameFilePaths()
            patronymicFilePaths = passport.getProcessedPatronymicFilePaths()
            surname = tesseract.ocr_core('passport_recognition/img/surname.jpg')
            snub = tesseract.ocr_core(isProcessSuccess[0])
            snub = str(snub).split('\n')

            result = {
                'snub': snub[0]
            }

            surname = surname.split('\n')

            # удаление ненужных элементов
            for i in surname:
                if i.lower().startswith('и'):
                    result.update({"name": i})
                if i.lower().startswith('пик'):
                    result.update({"surname": i})
                if i.lower().startswith('о'):
                    result.update({"patronymic": i})
                if i.lower().startswith('м'):
                    result.update({"birth_date": i})
            result = str(result).replace("'", '"')
            result = str(result).replace("\r\n", '')
            print(result)


    break
