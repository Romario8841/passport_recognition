# -*- coding: utf-8 -*-
import image_processing
import tesseract
import sys
from transliterate import translit
import json
import os.path




while True:

    with open('passport.jpg', "wb") as file:
            # Добавить аргумент при вызове файла, и его значение записать в переменную filepath
            filepath = sys.argv[1]

            passport = image_processing.Passport(filepath)
            isProcessSuccess = passport.processFullName()
            res = ""
            surnameFilePaths = passport.getProcessedSurnameFilePaths()
            nameFilePaths = passport.getProcessedNameFilePaths()
            patronymicFilePaths = passport.getProcessedPatronymicFilePaths()

            # get full name text


            # name = tesseract.ocr_core('img/name.jpg')
            if os.path.exists('passport_recognition/img/name.jpg'):
                name = tesseract.ocr_core('passport_recognition/img/name.jpg')
                name = ' '.join(name.split())
                # surname = tesseract.ocr_core('img/surname.jpg')
                surname = tesseract.ocr_core('passport_recognition/img/surname.jpg')
                surname = ' '.join(surname.split())
                # patronymic = tesseract.ocr_core('img/patronymic.jpg')
                patronymic = tesseract.ocr_core('passport_recognition/img/patronymic.jpg')
                patronymic = ' '.join(patronymic.split())

                # get birthdate text
                year = tesseract.dig_ocr_core('passport_recognition/img/year.jpg')
                # year = tesseract.dig_ocr_core('img/year.jpg')
                year = ' '.join(year.split())
                month = tesseract.dig_ocr_core('passport_recognition/img/month.jpg')
                # month = tesseract.dig_ocr_core('img/month.jpg')
                month = ' '.join(month.split())
                day = tesseract.dig_ocr_core('passport_recognition/img/day.jpg')
                # day = tesseract.dig_ocr_core('img/day.jpg')
                day = ' '.join(day.split())
                birth_date = f"{day}.{month}.{year}"

                # get snub text
                result = {
                    "name": name,
                    "surname": surname,
                    "patronymic": patronymic,
                    "birth_date": birth_date,
                }
                if type(isProcessSuccess) != bool:
                    snub = tesseract.ocr_core(isProcessSuccess[0])
                    snub = str(snub).split('\n')

                    result = {
                        "snub": snub[0],
                        "name": name,
                        "surname": surname,
                        "patronymic": patronymic,
                        "birth_date": birth_date,
                    }


                result = str(result).replace("\n", '')
                result = str(result).replace("'", '"')
                ru_result = str(result).replace("\r\n", '')

                en_result = translit(ru_result, language_code='ru', reversed=True)
                print(en_result)
                os.remove('passport_recognition/img/name.jpg')
                os.remove('passport_recognition/img/surname.jpg')
                os.remove('passport_recognition/img/day.jpg')
                os.remove('passport_recognition/img/month.jpg')
                os.remove('passport_recognition/img/year.jpg')
                os.remove('passport_recognition/img/patronymic.jpg')

            else:
                ru_result = tesseract.ocr_core(filepath)
                en_result = translit(ru_result, language_code='ru', reversed=True)
                print('Could not get structure data')
                print(en_result)

    break
