import re
from urllib import request
from bs4.element import PageElement
import lib
from urllib.request import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import webbrowser
##########################################################################

webbrowser.register('chrome',None,webbrowser.BackgroundBrowser("C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
domain = "https://gogoanime.vc"
url ="https://gogoanime.vc/anime-list.html?page="
headers = {'User-Agent': 'Chrome/39.0.2171.95'}
brouser = webdriver.Chrome(executable_path="C:/Users/user/Documents/Weeb Room Anim/Crawler/chromedriver.exe")

def get_anim_all(anims):
    db_item = []
    for i in anims:
        brouser.get(i)
        page = brouser.page_source
        
        #page = requests.get(i,headers=headers).content
        soup = BeautifulSoup(page, "html.parser")
        ########################### Name
        title = soup.find("h1")
        title = BeautifulSoup(str(title), "html.parser").getText()
        #print(title)
        ########################### Info
        info = soup.find("div",class_="anime_info_body_bg")
        info = BeautifulSoup(str(info), "html.parser")
        image = info.find("img")["src"]
        info = info.find_all("p",class_="type")
        info = BeautifulSoup(str(info), "html.parser").getText()
        info = info[1:len(info)-2]
        info = info.replace('\n', ' ')
        #print(info)
        ############################ tags
        othernames = info[info.find(" Other name:"):].replace("Other name:","")
        #print("other names>>",othernames)
        ##############################year#######################
        year = info[info.find(" Released: "):].replace(" Released: ","")
        year = year[:year.find(",")]
        ############################ status
        status = info[info.find(" Status:"):].replace(" Status:","")
        status = status[:status.find(",")]
        #print("Status>>",status)
        #############episodes
        episodes=[]
        episodes_temp = []
        episode = soup.find(id="load_ep")
        episode = BeautifulSoup(str(episode), "html.parser")
        episode = episode.findAll("a")
        for i in episode:
            episodes_temp.append(domain+str(i["href"]).replace(" ",""))
        for i in episodes_temp:
            episodes.append(get_epsode_DL(i))
        brouser.close
        #################compileing####################
        item = {"title":title,"discription":info,"status": status,"tags":othernames,"episodes": episodes, "year": year, "img":image}
        db_item.append(item)
        print(item)
        quries = anime_to_query(item)
        for sql in quries:
            run_query(sql)
            print("inserted......")
        print("*******************************************************************************************")
    
    return(db_item)

def get_epsode_DL(url):
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    starturl = url

    download = soup.find("li",class_="dowloads")
    download = download.find("a")
    episode = -1
    url = download["href"]

    page = requests.get(url).content
    download = BeautifulSoup(page, "html.parser")
    download = download.findAll("div",class_="dowload")
    for i in download:
        content =  BeautifulSoup(str(i), "html.parser").text
        if content.find("360P - mp4") >-0:
            #proceed vid link 
            i = BeautifulSoup(str(i), "html.parser")
            i = i.find("a")
            x = str(content).replace("\n"," ").replace(" ",""),i["href"]
            print(x)
            webbrowser.get('chrome').open(url)


anims = ["https://gogoanime.vc/category/kono-subarashii-sekai-ni-shukufuku-wo-","https://gogoanime.vc/category/kono-subarashii-sekai-ni-shukufuku-wo-2"]
get_anim_all(anims)