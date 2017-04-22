from bs4 import BeautifulSoup
from urllib.request import urlopen, Request

def get_info(url):
    r = Request(url, headers={'User-Agent' : "Magic Browser"})
    f = urlopen(r)
    s = BeautifulSoup(f, "html5lib")

    # Metadata
    date = s.select(".meta-data > span")[0].contents[1][8:]
    location = s.select(".meta-data > span")[1].contents[2].string
    category = s.select(".meta-data > span")[2].contents[2].string
    code = s.select(".meta-data > span")[3].contents[1][7:]

    # Content
    title = s.select("h2.title")[0].string
    content = str(s.select("article.post-content")[0])

    # Audio
    audio_url = None
    audio_token = s.select("ul.sm2-playlist-bd > li > a")
    if audio_token:
        audio_url = audio_token[0].get("href")
        if audio_url.startswith("//"):
            audio_url = "https:" + audio_url

    # Next page
    next_url = s.select("div.next-prev-navigation > a.float-right")[0].get("href")

    return ({
        "code": code,
        "date": date,
        "location": location,
        "category": category,
        "content": content,
        "audio_url": audio_url
    }, next_url)

def download_audio(audio_url, code):
    print(audio_url)
    # Download audio file
    req = Request(audio_url, headers={'User-Agent' : "Magic Browser"})
    con = urlopen(req)
    with open(code + ".mp3","wb") as output:
        output.write(con.read())

def write_transcript(name, data):
    data = "<html><body>{}</body></html>".format(data)

    with open(name, "w") as file:
        file.write(data)

domain = "https://prabhupadavani.org"
url = "/transcriptions/660304bgny/"

while url is not None:
    info, url = get_info(domain + url)
    write_transcript(info["code"]+".html", info["content"])
    if info["audio_url"]:
        download_audio(info["audio_url"], info["code"])
    print(info["code"])
