import re
from urllib import request
from bs4.element import PageElement
import lib
from urllib.request import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

##########################################################################


domain = "https://gogoanime.vc"
url ="https://gogoanime.vc/anime-list.html?page="
headers = {'User-Agent': 'Chrome/39.0.2171.95'}
#Change To Driver Path
brouser = webdriver.Chrome(executable_path="C:/Users/user/Documents/Weeb Room Anim/Crawler/chromedriver.exe")

def scrapeL(url):
    page = requests.get(url).content
    links = []
    try:
        soup = BeautifulSoup(page, "html.parser")
        soup = soup.findAll("ul",class_="listing")
        soup = BeautifulSoup(str(soup), "html.parser")
        soup = soup.findAll("a")

        for i in soup:
            links.append(domain+i["href"])
        print("Loading....")
        return(links)
    except:
        return(links)

def Get_allanim(): 
    anims = []
    for i in range(int(input("start>>>>>>>>>>")),int(input("end?>>>>>>>>>>>>>>>"))):
        list = scrapeL(url+str(i))
        

        if len(list)<1:
            print("End _________________________")
            m = input()
            break
        else:
            print ("page",">>",i)
            for i in list:
                anims.append(i)
    return(anims)

def get_anim_all():
    db_item = []
    for i in Get_allanim():
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
    vidlinks = ""
    for i in download:
        content =  BeautifulSoup(str(i), "html.parser").text
        if content.find("- mp4") >-0:
            #proceed vid link 
            i = BeautifulSoup(str(i), "html.parser")
            i = i.find("a")
            x = (str(content).replace("\n"," ").replace(" ",""),i["href"])
            if i["href"].find(".mp4")!= -1:
                vidlinks = x
                break
    if len(vidlinks) == 0 :
        vidlinks=("fallback",url)
    ################################################episode
    episode = int(starturl[starturl.find("episode-"):].replace("episode-",""))
    

    print("Episode : ",episode)
    print("Url : ",starturl)
    print("Videos : ",vidlinks)
    return(episode,url,vidlinks)

def anime_to_query(i={}):
    series_query = "INSERT IGNORE INTO `series`(`title`, `imagelink`, `year`, `discription`, `status`, `tags`) VALUES "
    episode_query = "INSERT IGNORE INTO `episodes`(`series`, `episode`, `episode_video_url`, `episode_direct_download`) VALUES "
    series_items = []
    episode_items= []
    x = "('[value-2]','[value-3]','[value-4]','[value-5]','[value-6]','[value-7]')".replace("[value-2]",re.escape(i["title"])).replace("[value-3]",i["img"]).replace("[value-4]",i["year"]).replace("[value-5]",re.escape(i["discription"])).replace("[value-6]",i["status"]).replace("[value-7]",re.escape(i["tags"]))

    series_items.append(x)

    for episode,downloadlink,video in i["episodes"]:
        ##(`series`, `episode`, `episode_video_url`, `episode_direct_download`)
        ##([value-1],[value-2],[value-3],[value-4])
        v = "('[value-1]','[value-2]','[value-3]','[value-4]')".replace("[value-1]",re.escape(i["title"])).replace("[value-2]",str(episode)).replace("[value-4]",downloadlink)
        if video[0] =="fallback":
            v = v.replace("[value-3]","none")
        else:
            v = v.replace("[value-3]",video[1])
        episode_items.append(v)

    series_items=list(enumerate(series_items))
    for index,item in series_items:
        if index == 0:
            series_query = series_query+item
        else:
            series_query = series_query+","+item

    episode_items=list(enumerate(episode_items))
    for index,item in episode_items:
        if index == 0:
            episode_query = episode_query+item
        else:
            episode_query = episode_query+","+item
    return(series_query,episode_query)

def run_query(sql):
    ## Edit if You Want To Add To your DB
    url = "http://localhost/WeebsRoomUpgrade/uploader/EXQ.php"
    obj = { 'Q' : '%%','QQ' : sql }
    page = requests.post(url, data = obj)
    print(page.content)

get_anim_all()
