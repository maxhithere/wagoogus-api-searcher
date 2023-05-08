import time
import json
import requests
from rich import print
from discord_webhook import DiscordWebhook, DiscordEmbed
import subprocess
import aiohttp
import asyncio
import json
import traceback
import logging


openjson = open('config.json') # from jeldo
conf = json.load(openjson)# from jeldo
cookie = "cookiesearcher.txt" # file to ur cookie
webhook_url = "put webhook url here"

snipedIds = []

cookies = [[i, ""] for i in conf["cookie"]]
if type(conf["cookie"]) == str:
    with open(conf["cookie"], "r") as f:
        cookies = [[i, ""] for i in f.read().replace(";", "").splitlines()]



def betterPrint(text):
    now = time.strftime('%r')
    print(f"[bold grey53][{now}] [/] {text}")

def get_x_token(cookie):
    return requests.post('https://auth.roblox.com/v2/logout', headers={'cookie': '.ROBLOSECURITY='+ cookie}).headers['x-csrf-token']


async def get_item_info(items):
    print(f"Getting item info for {items}")
    details = await request_details(items)
    print(f"Received item details for {items}")
    return await extract_data(details)

async def request_details(items):
    xt = get_x_token(cookies[0][0])
    headers = {
        'cookie': f'.ROBLOSECURITY={cookies[0][0]};',
        'x-csrf-token': xt
    }
    payload = {"items": [{"itemType": "Asset", "id": int(items)}]}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post('https://catalog.roblox.com/v1/catalog/items/details',
                                    json=payload,
                                    headers=headers) as response:
                response_data = await response.text()
        
                return json.loads(response_data)
    except Exception as e:
        print(e)
        return

async def extract_data(details):
    return details['data']


async def sendWebhook(val):
    print('posting webhook')

    embed = DiscordEmbed(
        title=val['name'],
        url=f"https://www.roblox.com/catalog/{val['id']}",
        color="03b2f8"
    )
    embed.add_embed_field(name='Price', value=val.get('price', 'Offsale'))
    embed.add_embed_field(name='Creator', value=val['creatorName'])
    embed.add_embed_field(name='Stock', value=f"{val['unitsAvailableForConsumption']}")

    msg = DiscordWebhook(url=webhook_url)
    msg.add_embed(embed)
    msg.execute()
    


async def main():
    print('starting')
    while 1:
        try:
            ids = await latest()
            for id in ids:
                if id not in snipedIds:
                    snipedIds.append(id)
                    val = await get_item_info(id) 
                    betterPrint(f"[aquamarine1]Sniped {id}")
                    await sendWebhook(val[0])
        except Exception as e:
            traceback.print_exc()
            print(f"Exception occurred: {str(e)}")
            pass
        await asyncio.sleep(1.1)


async def fetch_json(session, url, headersss):
    async with session.get(url, headers=headersss) as response:
        data = await response.json()
        return data
    


headerss = {
    "key": "api key here",
    "wagoo-verify": "let-me-in"
}


async def latest():
  async with aiohttp.ClientSession() as session:
      awaited = await fetch_json(session, 'https://wagoogus.com/wagoo-api', headerss)
      betterPrint(f"[aquamarine1]Received latest item - {awaited['assetid']}")
      r = awaited
      rData = r['assetid']
      ids = []
      ids.append(rData)
      return ids

asyncio.run(main())
