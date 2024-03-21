import requests


def moji(word):
    globalconfig = {'https': '127.0.0.1:7890', 'http': '127.0.0.1:7890'}
    
    try:
        response = requests.post(
            "https://api.mojidict.com/parse/functions/union-api",
            json={
                "functions": [
                    {
                        "name": "search-all",
                        "params": {
                            "text": word,
                            "types": [
                                102,
                                106,
                                103,
                            ],
                        },
                    },
                ],
                "_ApplicationId": "E62VyFVLMiW7kvbtVq3p",
            },
            headers={
                "content-type": "text/plain",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            },proxies={'https': '127.0.0.1:7890', 'http': '127.0.0.1:7890'}
        )

        result = ""

        for i in response.json()["result"]["results"]["search-all"]["result"][
            "word"
        ]["searchResult"]:
            result += '{}<br>{}<br><br>'.format(i["title"],i["excerpt"])

        return result

    except:
        return ""

if __name__=='__main__':
    m = moji('濡れ場')
    print(m)