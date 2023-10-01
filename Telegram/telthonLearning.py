from telethon import TelegramClient, events, sync
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
import openai
import pytz
import json
import re
import keys
from geopy.geocoders import Nominatim

api_id = keys.telegramID
api_hash = keys.telegramHash
openai.api_key = keys.openaiKey

"""
Get: the Telegram client and group
Do: Reads the channel latests messages and save them in a json file
"""
def get_TelegramReports(group, cl):
    
   # Reads the reports that already saves in the database 
    with open('Telegram/AllNews.json') as f: 
        reportDict = json.load(f)
    
    # Gets the new messages from the group
    new_posts = cl.iter_messages( 
        entity=group,
        limit = 10,
        min_id = reportDict["Reports"][0]["Id"], #change the min_id to the last id that saved in the json file
        reverse=True
    )
    
    gpt_Instructions = [
    {"role": "system", "content":"You are an israeli news worker, you get a war report and you need to return this info (if mention):A translation of the Hebrew report exactly as given,  Where the event took place, what country or organization  did the action and how many injuries or kills there was "},
    {"role": "system", "content":"Pls responde only with the info you understood from the report there no need to be nice or write other things"},
    {"role": "system", "content":'Pls return the info in a JSON format. Here is the expected JSON format: {"Title": A short title for the report, "Text": The translation of the report from Hebrew to English, "Place": the most specific place of the report in one word maximum 2,"Attacker": the army or terror organization that pulled the action,"Casualties": how many kills/injured people in number from the report for example 2 killed 0 Injured}'},
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

        clean_message_text = re.sub("[^א-ת ]", "", text)
    
        gpt_Instructions.append({"role": "user", "content": clean_message_text})

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
    
    # Overide the json file with the new reports
    with open('Telegram/AllNews.json', 'w') as f:
        json.dump(reportDict, f,indent=2) 
    
    
# Creates a Telegram client that can read messages from groups
with TelegramClient('session_name', api_id, api_hash) as client:
    title = 'חדשות הביטחון'         # The title of the channel we want to read from
    channel = client(GetFullChannelRequest(title))

    get_TelegramReports(channel.full_chat, client)




print('Done')