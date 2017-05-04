from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from os.path import exists, join
from os import makedirs

def get_transcriptions_list(page):
    result = []
    url = "https://prabhupadavani.org/transcriptions/?page={}".format(page)
    request = Request(url, headers={'User-Agent' : "Magic Browser"})
    stream = urlopen(request)

    parser = BeautifulSoup(stream, "html5lib")
    nodes = parser.select(".transcription-title > a")
    for node in nodes:
        href = node.get("href")
        result.append(href)

    return result

def get_info(url):
    print("PAGE: ", url)
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

    return {
        "code": code,
        "title": title,
        "date": date,
        "location": location,
        "category": category,
        "content": content,
        "audio_url": audio_url }

def download_audio(info, path):
    if "audio_url" not in info:
        return
    if info["audio_url"] is None:
        return
    audio_url = info["audio_url"]
    audio_path = join(path, info["code"] + ".mp3")

    if exists(audio_path):
        print("AUDE: ", audio_path)
        return
    else:
        print("AUD : ", info["audio_url"])

    req = Request(audio_url, headers={'User-Agent' : "Magic Browser"})
    con = urlopen(req)
    with open(audio_path, "wb") as output:
        output.write(con.read())

def write_transcript(info, path):
    data = "<!DOCTYPE html><html><head><meta charset='utf-8'>"+\
        "<link rel='stylesheet' href='styles.css'>"+\
        "<script src='scripts.js'></script>"+\
        "</head><body><h1>{}</h1><div>{}</div><div>{}</div>{}</body></html>"\
        .format(info["title"], info["date"], info["location"], info["content"])

    filename = join(path, info["code"] + ".html")
    with open(filename, "w") as file:
        file.write(data)

def get_start_code(path, default=None):
    result = default or ""
    if exists(path):
        with open(path, "r") as file:
            result = file.read()
        print("Continuing from: {}".format(result))
    return result

def get_dir(info, create=False, root=None):
    code = info["code"]
    year = code[0:2]
    month = code[2:4]
    path = ""
    if root:
        path = root
    path = join(path, year, month)

    if not exists(path) and create:
        print("FLD : ", path)
        makedirs(path)

    return path

# Configuration
res_path = "resources"
dwn_path = "downloads"
last_path = join(dwn_path, "last.txt")
domain = "https://prabhupadavani.org"
#start_code = get_start_code(last_path, default="660304bgny")

# Main process
for page in range(1, 104):
    print("------- {} -------".format(page))
    links = get_transcriptions_list(page)

    for url in links:
        info = get_info(domain + url)
        path = get_dir(info, create=True, root=dwn_path)
        write_transcript(info, path)
        download_audio(info, path)
        #with open(last_path, "w") as file:
        #    file.write(info["code"].lower().replace(".", ""))
