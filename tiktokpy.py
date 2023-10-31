import asyncio
import io
import glob
import os
import urllib.request
from os import path
import aiohttp
from bs4 import BeautifulSoup
from tiktokapipy.async_api import AsyncTikTokAPI
from TikTokApi import TikTokApi
from tiktokapipy.models.video import Video

import time
import requests
from urllib.request import urlopen
import re

link = 'https://www.tiktok.com/@anime.gifx/video/7240134116832857370?is_from_webapp=1&sender_device=pc&web_id=7258161386462561794'
directory = 'downloads'
file_path_link = 'link_profile.txt'

def txt_to_lst(link):
    try:
        stopword=open(link,"r")
        lines = stopword.read().split('\n')
        return lines
    except Exception as e:
          print('ERROR FILE')

from pathlib import Path
#create download folder for store file
# Path(directory).mkdir(exist_ok=True)

async def save_slideshow(video: Video):
    # this filter makes sure the images are padded to all the same size
    vf = "\"scale=iw*min(1080/iw\,1920/ih):ih*min(1080/iw\,1920/ih)," \
         "pad=1080:1920:(1080-iw)/2:(1920-ih)/2," \
         "format=yuv420p\""

    for i, image_data in enumerate(video.image_post.images):
        url = image_data.image_url.url_list[-1]
        # this step could probably be done with asyncio, but I didn't want to figure out how
        urllib.request.urlretrieve(url, path.join(directory, f"temp_{video.id}_{i:02}.jpg"))

    urllib.request.urlretrieve(video.music.play_url, path.join(directory, f"temp_{video.id}.mp3"))

    # use ffmpeg to join the images and audio
    command = [
        "ffmpeg",
        "-r 2/5",
        f"-i {directory}/temp_{video.id}_%02d.jpg",
        f"-i {directory}/temp_{video.id}.mp3",
        "-r 30",
        f"-vf {vf}",
        "-acodec copy",
        f"-t {len(video.image_post.images) * 2.5}",
        f"{directory}/temp_{video.id}.mp4",
        "-y"
    ]
    ffmpeg_proc = await asyncio.create_subprocess_shell(
        " ".join(command),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await ffmpeg_proc.communicate()
    generated_files = glob.glob(path.join(directory, f"temp_{video.id}*"))

    if not path.exists(path.join(directory, f"temp_{video.id}.mp4")):
        # optional ffmpeg logging step
        # logging.error(stderr.decode("utf-8"))
        for file in generated_files:
            os.remove(file)
        raise Exception("Something went wrong with piecing the slideshow together")

    with open(path.join(directory, f"temp_{video.id}.mp4"), "rb") as f:
        ret = io.BytesIO(f.read())

    for file in generated_files:
        os.remove(file)

    return ret

async def save_video(video: Video, api: AsyncTikTokAPI):
    # Carrying over this cookie tricks TikTok into thinking this ClientSession was the Playwright instance
    # used by the AsyncTikTokAPI instance
    async with aiohttp.ClientSession(cookies={cookie["name"]: cookie["value"] for cookie in await api.context.cookies() if cookie["name"] == "tt_chain_token"}) as session:
        # Creating this header tricks TikTok into thinking it made the request itself
        async with session.get(video.video.download_addr, headers={"referer": "https://www.tiktok.com/"}) as resp:
            return await resp.read()
        

#Download Video Without watermark in Website 
def downloadVideo(folder,link, id):
    print(f"Downloading video {id} from: {link}")
    cookies = {
        '_ga': 'GA1.1.1165586716.1691898609',
        '_ga_ZSF3D6YSLC': 'GS1.1.1691923353.4.0.1691923353.0.0.0',
        '__gads': 'ID=a3e72ca9d4fca627-22ba3f3fd1e20036:T=1691898608:RT=1692149087:S=ALNI_Mb_fiTzFdueBt3FaZm9zOTMpY1VpA',
        '__gpi': 'UID=00000c2befeaa984:T=1691898608:RT=1692149087:S=ALNI_MZw4JmIHGBokqkgWT6W_YbPvlOkAQ',
        'FCNEC': '%5B%5B%22AKsRol8j2QeMgzzWk5FIVHPHDjP1PAkQb9bsbRECA265rhU2uhBZZLogEbMuGxDYEmMiSierLXSG0WULW3JrlA6tzWdHydebrk7Wy56RgE4YtU0cX4qFczuXkRAxoKzDnRMkh8P6sQhCw4AqPpruZfK2lYsW530bhg%3D%3D%22%5D%2Cnull%2C%5B%5D%5D',
    }

    headers = {
        'authority': 'ssstik.io',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'cookie': '_ga=GA1.1.1165586716.1691898609; _ga_ZSF3D6YSLC=GS1.1.1691923353.4.0.1691923353.0.0.0; __gads=ID=a3e72ca9d4fca627-22ba3f3fd1e20036:T=1691898608:RT=1692149087:S=ALNI_Mb_fiTzFdueBt3FaZm9zOTMpY1VpA; __gpi=UID=00000c2befeaa984:T=1691898608:RT=1692149087:S=ALNI_MZw4JmIHGBokqkgWT6W_YbPvlOkAQ; FCNEC=%5B%5B%22AKsRol8j2QeMgzzWk5FIVHPHDjP1PAkQb9bsbRECA265rhU2uhBZZLogEbMuGxDYEmMiSierLXSG0WULW3JrlA6tzWdHydebrk7Wy56RgE4YtU0cX4qFczuXkRAxoKzDnRMkh8P6sQhCw4AqPpruZfK2lYsW530bhg%3D%3D%22%5D%2Cnull%2C%5B%5D%5D',
        'hx-current-url': 'https://ssstik.io/en',
        'hx-request': 'true',
        'hx-target': 'target',
        'hx-trigger': '_gcaptcha_pt',
        'origin': 'https://ssstik.io',
        'referer': 'https://ssstik.io/en',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    }

    params = {
        'url': 'dl',
    }

    data = {
        'id': link,
        'locale': 'en',
        'tt': 'S2dzNnc5',
    }
    
    response = requests.post('https://ssstik.io/abc', params=params, cookies=cookies, headers=headers, data=data)
    downloadSoup = BeautifulSoup(response.text, "html.parser")
    # print(downloadSoup)
    # return
    downloadLink = downloadSoup.a["href"]
    videoTitle = downloadSoup.p.getText().strip()

    print("Saving the video :>")
    mp4File = urlopen(downloadLink)
    # Feel free to change the download directory
    with open(f"{folder}/{id}-{videoTitle}_devop.mp4", "wb") as output:
        while True:
            data = mp4File.read(4096)
            if data:
                output.write(data)
            else:
                return

ms_token = os.environ.get(
    "ms_token", None
)  # set your own ms_token, think it might need to have visited a profile


async def user_video(user_name):
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        user = api.user(user_name)
        # user_data = await user.info()
        # print(user.videos(count=10))
        folderDL =  f"download_{user_name}"
        #create download folder for store file
        Path(folderDL).mkdir(exist_ok=True)
        i = 1
        async for video in user.videos(count=5):
            vid = video.as_dict["video"]["id"]
            url= f"https://www.tiktok.com/@{user_name}/video/{vid}"
            downloadVideo(folderDL,url,i)
            downloadVideo( link_url,1)
            time.sleep(10)
            i+=1

async def TiktokAPIMain():
    profile = txt_to_lst(file_path_link)
    print( f"How Many Profile: {len(profile)}")
    async with AsyncTikTokAPI() as api:
        profile = txt_to_lst(file_path_link)
        print(len(profile))
        for pro_href in profile:
            # print(pro_href)
            username = re.findall(r"@(\w+)", pro_href)
            # User: User = await api.user()
            # print(User)
            video: Video = await api.user(username[0])
            print(video)
            
            return

            #get all video by user name
            await user_video(username[0])
            # time.sleep(5)

        
    #     return
        # if video.image_post:
        #     # downloaded = await save_slideshow(video,api)
        #     print('Downloading video [slide]...')
        # else:
        #     print('Downloading video ...')
        #     # print(video.author_name)
        #     link_url = "https://www.tiktok.com/@askmebuy/video/7239557341903899905?is_from_webapp=1&sender_device=pc"
            
        #     return
        #     downloaded = await save_video(video,api)
        #     #Path to dir folder video
        #     # path_video = path.join(directory, f"video_{video.id}.mp4")
        #     # with open(path_video, "wb") as f:
        #     #     f.write(downloaded)
        #     #Remove watermark from video
        #     print('Video downloaded. Removing watermark from the video...')
        #     # video_no_water = await remove_watermark(path_video)
        #     # print('Watermark removed. File path:', video_no_water)


    # do something with the downloaded video (save it, send it, whatever you want).
if __name__ == "__main__":
    asyncio.run(TiktokAPIMain())