from django.shortcuts import render
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import date
import datetime
# Create your views here.
def index(request):

    if request.method=='POST':
        #Processing the web page using json object
        #import statements
        airport=request.POST.get('airport',None)


        Hour = ['0', '6', '12', '18']
        a='__NEXT_DATA__ = '
        b='module'
        fly='flights'
        today=date.today()
        todayTime=datetime.datetime.utcnow()+datetime.timedelta(hours=5,minutes=28)

        flight_number=[]
        arrival_time=[]
        origin_time=[]
        origin=[]
        airlines=[]
        Flight_Data=[]
        Tail_number=[]
        Flight_status=[]

        for h in Hour:



            response = requests.get('https://www.flightstats.com/v2/flight-tracker/arrivals/'+airport+'/?year='+str(today.year)+'&month='+str(today.month)+'&date='+str(today.day)+'&hour='+h)
            #getting the input from the web page


            #creating an instance of soup from the input data
            soup=BeautifulSoup(response.text,'html.parser')

            #seperating the json object out of the complete html
            scripts=soup.find_all('script')
            text=scripts[2].get_text()

            jason=(text.split(a))[1].split(b)[0]
            jason=(jason.split(fly))[2].split(',"showCodeshares')[0]
            jason='{"flights'+jason+'}'

            #working out with jason and extracting the data
            wjson=json.loads(jason)





            for i in range(len(wjson['flights'])):

                date_string = wjson['flights'][i]['arrivalTime']['time24']
                date_object = datetime.datetime.strptime(date_string, '%H:%M')

                if todayTime.time()<=date_object.time():

                    origin_time.append(wjson['flights'][i]['departureTime']['time24'])
                    arrival_time.append(wjson['flights'][i]['arrivalTime']['time24'])
                    airlines.append(wjson['flights'][i]['carrier']['name'])
                    flight_number.append(wjson['flights'][i]['carrier']['fs'] +' - '+wjson['flights'][i]['carrier']['flightNumber'])
                    origin.append(wjson['flights'][i]['airport']['city'])
    
                    if ((date_object.hour+(date_object.minute)/60) - (todayTime.hour+(todayTime.minute)/60)) <1:
                        tempLink=wjson['flights'][i]['url']
                        tempResp=requests.get('https://www.flightstats.com/v2'+tempLink)
                        tempSoup=BeautifulSoup(tempResp.text,'html.parser')
                        scripts2=tempSoup.find_all('script')
                        text2=scripts2[2].get_text()
                        jason2=text2.split('"status":{"')[1].split(',"delay":{"d')[0]
                        jason2=('{"'+jason2 +'}')
                        wjson2=json.loads(jason2)
                        Flight_status.append(wjson2['status'] + '  '+wjson2['statusDescription'])


                    else:

                        Flight_status.append('-')





        Flight_Data=[[flight_number[i],origin[i],origin_time[i],arrival_time[i],airlines[i],Flight_status[i]] for i in range(0,len(flight_number))]

        my_data={'flight_data':Flight_Data}

        return render(request,'infoDisplay/index.html',context=my_data)
    else:
        return render(request,'infoDisplay/index.html')
