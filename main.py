from tinkoff_voicekit_client import ClientSTT
import datetime
import wave
import contextlib
from sys import argv
import psycopg2
import os

API_KEY = ""
SECRET_KEY = ""

client = ClientSTT(API_KEY, SECRET_KEY)

def recognizeAudio(path):
    audio_config = {
        "encoding": "LINEAR16",
        "sample_rate_hertz": 8000,
        "num_channels": 1
    }
    # recognise method call
    response = str(client.recognize(path, audio_config))
    startStr = response.index("'transcript': '") + 15
    endStr = response.index("', 'confidence'")
    return response[startStr:endStr]

def timeAudio(path):
    audiofile = path
    with contextlib.closing(wave.open(audiofile, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        length = frames / float(rate)
        return (length)


def saveLog(step, answer, tel, path, text, bd):
    idFile = open("id.txt", "r", encoding="utf8")
    id = idFile.readline(1)
    idFile.close()
    idFil = open("id.txt", "w", encoding="utf8")
    idFil.write(str(int(id) + 1))
    idFil.close()
    file = open("log.txt", "a", encoding="utf8")
    data = datetime.datetime.now().strftime("%d.%m.%Y")
    time = datetime.datetime.now().strftime("%H:%M:%S")
    result = ""
    if(step == 1):
        if(answer == 0):
            result = "АО"
        else:
            result = "человек"
    elif(step == 2):
        if (answer == 0):
            result = "отрицательно"
        else:
            result = "положительно"
    else:
       print("")
    timeA = timeAudio(path)
    line = "Date: " + str(data) +" Time: "+ str(time) +" ID: "+ str(id) +" Result: "+ str(result) +" Tel: "+ str(tel) +" Lenght audio: "+ str(timeA) +" Text: "+ str(text) + "\n"
    file.write(line)
    file.close()
    if(bd == True):
        dbConnect(data, time, id, result, tel, timeA, text)



def analysAudio(audioPath, tel, BDFlag, step):
    textInAudio = recognizeAudio(audioPath)
    answer = 2
    if(step == 1):
        if("автоответчик" in textInAudio):
            answer = 0
        else:
            answer = 1
    elif(step == 2):
        if ("да" or "говорите" or "конечно" in textInAudio):
            answer = 0
        elif("нет" or "неудобно" or "не" in textInAudio):
            answer = 1
    else:
        print("Неверно введён этап распознования")
    saveLog(step, answer, tel, audioPath, textInAudio, BDFlag)

    return answer

def dbConnect(data, time, id, res, tel, t, recog):
    conn = psycopg2.connect(dbname='xlab', user='postgres',
                            password='123456Ll', host='localhost')
    cursor = conn.cursor()
    ins = "INSERT INTO xlab VALUES ('" + str(data) + "', '" + str(time) + "', '" + str(id) + "', '" + str(res) + "', '" + str(tel) + "', '" + str(t) + "', '" + str(recog) +"')"
    insert = (ins)
    cursor.execute(insert)
    conn.commit()
    cursor.close()
    conn.close()

def main():
    print("Путь к файлу: ")
    pathToFile = input()
    print("Номер телефона: ")
    telephoneNumber = input()
    print("Флаг БД: ")
    bdFlag = input()
    print("Этап распознавания: ")
    TR = input()
    analysAudio(pathToFile, telephoneNumber, bool(bdFlag), int(TR))
    os.remove(pathToFile)
try:
    script, pathToFile, telephoneNumber, bdFlag, TR = argv
except ValueError:
    main()