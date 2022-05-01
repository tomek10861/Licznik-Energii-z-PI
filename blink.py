from gpiozero import Button
from time import sleep
from datetime import datetime
import requests
import subprocess


domoticzIP="192.168.55.24:8080"
DomoticzIDXGetNet="81"
DomoticzIDXSendToNet="82"
DomoticzIDXGetSolar="83"
#Pobieranie aktulanej produkcji z falownika (w moim przypadku skrypt bashowy)
inverterCurrentProduction="./currentSolarPower.sh actual"
#Wartość krtytczyna szacunkowa przy której energia naliczona to energia oddana
SolarBorderValue=450
timeCount = 413

#Dioda informująca o nabitych kilowatach (pin GPIO)
pulsesDiode = Button(3, pull_up=True)
#Dioda informująca o prądzie wstecznym (pin GPIO)
reverseCurrentDiode = Button(17, pull_up=True)

print(pulsesDiode)
print(reverseCurrentDiode)

count = 0
start_time = datetime.now()
oldSolarPower=0
todaySolarPower=0


while True:
#Zliczanie mignięć
    if pulsesDiode.is_pressed:
        sleep(0.02)
        count += 1
        while pulsesDiode.is_pressed:
            sleep(0.02)
    time_delta = datetime.now() - start_time
    sleep(0.001)

#Jeśli przekroczony zdefiniowaną jednostkę czasu
    if time_delta.total_seconds() >= timeCount:
        actualPower=int(round(count/(timeCount/3600)))
        domoticzGetFromNet = "http://"+domoticzIP+"/json.htm?type=command&param=udevice&idx="+DomoticzIDXGetNet+"&nvalue=0&svalue=0;"
        domoticzSendToNet = "http://"+domoticzIP+"/json.htm?type=command&param=udevice&idx="+DomoticzIDXSendToNet+"&nvalue=0&svalue=0;"
        domoticzGetSolar = "http://"+domoticzIP+"/json.htm?type=command&param=udevice&idx="+DomoticzIDXGetSolar+"&nvalue=0&svalue=0;"



        #Jeśli nie wykryto prądu wstecznego
        y=0
        if not reverseCurrentDiode.is_pressed:
            for x in range(10):
                if not reverseCurrentDiode.is_pressed:
                    sleep(0.02)
                    y+=1
            if y>4:
                oldSolarPower=0
                todaySolarPower=0
                domoticzGetFromNet = "http://"+domoticzIP+"/json.htm?type=command&param=udevice&idx="+DomoticzIDXGetNet+"&nvalue=0&svalue="+str(actualPower)+";"+str(count)
                print('Not deteced reverseCurrent '+domoticzGetFromNet)

        #Jeśli wykryto prąd wsteczny
        if reverseCurrentDiode.is_pressed:
            inverterOutPut = subprocess.check_output(inverterCurrentProduction, shell=True)
            actualSolarPower=int(inverterOutPut.decode("utf-8"))
# #Obliczanie średniej produkcji

#zabezpieczenie przez odczytami zerowymi z falownika
            if not actualSolarPower > 2:
                inverterOutPut = subprocess.check_output(inverterCurrentProduction, shell=True)
                actualSolarPower=int(inverterOutPut.decode("utf-8"))
            oldSolarPower=actualSolarPower

            PowerDiff=actualPower-actualSolarPower
            #jeśli produkcja większa od SolarBorderValue to rachujemy
            print(PowerDiff)
            if PowerDiff > 0:
                domoticzGetFromNet = "http://"+domoticzIP+"/json.htm?type=command&param=udevice&idx="+DomoticzIDXGetNet+"&nvalue=0&svalue="+str(actualPower)+";"
                print('Power Diff > 0'+domoticzGetFromNet)
            if PowerDiff <= 0:
            #wysłanie energi wygenerowanej
                domoticzSendToNet = "http://"+domoticzIP+"/json.htm?type=command&param=udevice&idx="+DomoticzIDXSendToNet+"&nvalue=0&svalue="+str(actualPower)+";"
                print('Power Diff <= 0'+domoticzSendToNet)
            #Wysłanie energi pobranej z foto
                domoticzGetSolar = "http://"+domoticzIP+"/json.htm?type=command&param=udevice&idx="+DomoticzIDXGetSolar+"&nvalue=0&svalue="+str(abs(PowerDiff))+";"



        #Wyślij dane do domoticza
        f = requests.get(domoticzGetFromNet)
        if(f.status_code!=200):
            logFile = open("power.log", "a")
            result=str(start_time.strftime("%Y-%m-%d, %H:%M:%S"))+';HTTP Error Request;'+DomoticzIDXGetNet+';'+str(f.status_code);
            logFile.write(result)
            logFile.close()
        f = requests.get(domoticzSendToNet)
        if(f.status_code!=200):
            logFile = open("power.log", "a")
            result=str(start_time.strftime("%Y-%m-%d, %H:%M:%S"))+';HTTP Error Request;'+DomoticzIDXSendToNet+';'+str(f.status_code);
            logFile.write(result)
            logFile.close()
        f = requests.get(domoticzGetSolar)
        if(f.status_code!=200):
            logFile = open("power.log", "a")
            result=str(start_time.strftime("%Y-%m-%d, %H:%M:%S"))+';HTTP Error Request;'+DomoticzIDXGetSolar+';'+str(f.status_code);
            logFile.write(result)
            logFile.close()

        start_time = datetime.now()
        count = 0
