import requests
from urllib.parse import quote
import re

# language_list_translator_inner = ["zh", "ja", "en","ru","es","ko","fr","cht","vi","tr","pl","uk","it","ar"]

def youdao(word):
    globalconfig = {'https': '127.0.0.1:7890', 'http': '127.0.0.1:7890'}
    
    try:
        # text=requests.get('https://dict.youdao.com/result?word={}&lang={}'.format(quote(word), "ja"), proxies=globalconfig).text
        text=requests.get('https://dict.youdao.com/result?word={}&lang={}'.format(quote(word), "ja")).text

        fnd=re.findall('<div class="head-content"(.*?)>([\\s\\S]*?)</span>(.*?)</div>',text)
        save=[] 

        asave=[]
        for ares  in fnd[0]:
            res=re.findall('>(.*?)<',ares+'<')
            for _ in res: 
                for __ in _:
                    if __ !='':

                        asave.append(__)
        save.append(''.join(asave))
            
        fnd=re.findall('<div class="each-sense"(.*?)>([\\s\\S]*?)</div></div></div>',text)
        for _,ares in fnd:
            asave=[]
            res=re.findall('>(.*?)<',ares+'<')
            for __ in res:
                
                if __ !='':

                    asave.append(__)
            save.append('<br>'.join(asave))

        fnd=re.findall('<li class="word-exp"(.*?)>([\\s\\S]*?)</span></li>',text)
        for _,ares in fnd:
            asave=[]
            res=re.findall('>(.*?)<',ares+'<')
            for __ in res:
                
                if __ !='':

                    asave.append(__)
                
            save.append('<br>'.join(asave))
    except:
        return ""

    return '<br><br>'.join(save)
    

if __name__=='__main__':
    y = youdao('武田')
    print(y)

