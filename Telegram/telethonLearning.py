from telethon import TelegramClient, events, sync
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
import openai
import pytz
import json
import re
import keys
from geopy.geocoders import Nominatim
from datetime import datetime

api_id = keys.telegramID
api_hash = keys.telegramHash
openai.api_key = keys.openaiKey

"""
Get: the Telegram client and group
Do: Reads the channel latests reports and save them in a json file
"""
def get_TelegramReports(group, cl):
    
   # Reads the reports that already saves in the database 
    with open('Telegram/AllNews.json') as f: 
        reportDict = json.load(f)
    
    # Gets the new messages from the group
    new_posts = cl.iter_messages( 
        entity=group,
        limit = 30,
        min_id = reportDict["Reports"][0]["Id"], #change the min_id to the last id that saved in the json file
        reverse=True
    )
    
    gpt_Instructions = [
    {"role": "system", "content":"You are an israeli news worker, you get a war report and you need to return this info (if mention):A translation of the Hebrew report exactly as given,  Where the event took place, what country or organization  did the action and how many injuries or kills there was "},
    {"role": "system", "content":"Pls responde only with the info you understood from the report there no need to be nice or write other things"},
    {"role": "system", "content":'Pls return the info in a JSON format. Here is the expected JSON format: {"Title": A short title for the report, "Text": The translation of the report from Hebrew to English, "Place": the most specific place of the report in one word maximum 2 and the name of the country,"Attacker": the army or terror organization that pulled the action,"Casualties": how many kills/injured people in number from the report for example 2 killed 0 Injured}'},
    {"role": "system", "content":"DO NOT RETURN ANY INFORMATION IN A DIFFERENT LANGUAGE THAN ENGLISH"},
    {"role": "system", "content":"If some of the data don't mention just write Not entioned"},
    ]


    # set the time zone of the messeges to israel's time zone
    tz = pytz.timezone('Asia/Riyadh') 
    
    
    # Creating a dict for each message we want to insert to the json file 
    # Giving the chat gpt the report in Hebrew and he translate it to English and getting useful information from the report
    
    for message in new_posts: 
        # Hendeling the time str
        reportTime = message.date.astimezone(tz)
        reportTime = reportTime.strftime("%H:%M:%S, %Y-%m-%d")
        
        text = str(message.text).replace('חדשות הביטחון****', '')
        text = text.replace('דובר צה"ל:', '')

        #clean_message_text = re.sub("[^א-ת ]", "", text)
    
        gpt_Instructions.append({"role": "user", "content": text})

        # Initialize Nominatim API
        geolocator = Nominatim(user_agent="MyApp")


        complation = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages = gpt_Instructions,
                temperature = 0
            )   
        info = complation.choices[0].message.content
        infoToJson = json.loads(info)
        
        try:
            location = geolocator.geocode(infoToJson['Place'])
            lat = location.latitude
            lon = location.longitude
            coordinates = {'LAT': lat, 'LON':lon}
        except:
            coordinates = {}
            print('no place')
        temp = {
                "Id": message.id,
                "Title": infoToJson['Title'],
                "Text": infoToJson['Text'],
                "Place": infoToJson['Place'],
                "Coordinates": coordinates,
                "Attacker": infoToJson['Attacker'],
                "Casualties": infoToJson['Casualties'],
                "PubilshTime": reportTime,
                "Child_Reports" : []
                }
        reportDict['Reports'].insert(0,temp)
        print('Added Report')
    
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    print("Update Time:", current_time)  
    reportDict['LastUpdate'] = current_time
    # Overide the json file with the new reports
    with open('Telegram/AllNews.json', 'w') as f:
        json.dump(reportDict, f,indent=2) 
    


"""
Get: the Telegram client and group
Do: Reads the channel latests alerts and save them in a json file
"""
def get_RedAlerts(group, cl):
    
    # Reads the reports that already saves in the database 
    with open('Telegram/AllNews.json') as f: 
        reportDict = json.load(f)
    
    # Set Israel's time zone
    tz = pytz.timezone('Asia/Riyadh') 

    # Gets the new alert from the channel
    new_alerts = cl.iter_messages( 
            entity=group,
            limit = 20,
            min_id = reportDict["Alerts"][0]["Id"], #change the min_id to the last id that saved in the json file
            #min_id = 9350,
            reverse=True
        )
    
    # Initialize Nominatim API
    geolocator = Nominatim(user_agent="MyApp")
    
    
    for alert in new_alerts:
        # take only the first sentence of the alert
        title = alert.text.split('[')[0]
        reportTime = alert.date.astimezone(tz)
        reportTime = reportTime.strftime("%H:%M:%S, %Y-%m-%d")
        alertPlacesDict = []
        if title != "":
            # split the Title of the event from the list of places
            alertPlaces = title.split(' at ')[1]    
            
            # split each place from the list of places and get their coordantes
            for place in alertPlaces.split(', '):
                try:
                    # Get the place coordinates
                    location = geolocator.geocode(place+ ' Israel')
                    lat = location.latitude
                    lon = location.longitude
                    coordinates = {'Name': place ,'LAT': lat, 'LON':lon}
                    alertPlacesDict.append(coordinates)
                except:
                    continue
            # creates new alert object
            temp = {
                        "Id": alert.id,
                        "Type": title.split(' at ')[0],
                        "Title": title,
                        "Places": alertPlacesDict,
                        "Time": reportTime
                    } 
            # add the new alert to the dict
            reportDict['Alerts'].insert(0,temp)
            print('Added Alert')
        
        
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        reportDict['LastUpdate'] = current_time
        # Overide the json file with the new reports
        with open('Telegram/AllNews.json', 'w') as f:  
            json.dump(reportDict, f,indent=2) 
        



# Creates a Telegram client that can read messages from groups
with TelegramClient('session_name', api_id, api_hash) as client:
    
    # News
    news = 'חדשות הביטחון'         # The title of the channel we want to read from
    newschannel = client(GetFullChannelRequest(news))

    get_TelegramReports(newschannel.full_chat, client)

    # Red Alerts
    redAlerts = 'CumtaAlertsEnglishChannel'
    redAlertChannel = client(GetFullChannelRequest(redAlerts))
    get_RedAlerts(redAlertChannel.full_chat, client)


print('Done')