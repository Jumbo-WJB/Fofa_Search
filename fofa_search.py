import aiohttp
import asyncio
import base64
import json
import argparse
import csv
import os

async def Search_Keywords(url,output):
    outputs = []
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            jsonhtml = json.loads(html)
            # print(jsonhtml)
            htmlsize = jsonhtml['size']
            htmlresults = jsonhtml['results']
            for i in range(0,htmlsize):
                host,ip,domain,port,title = htmlresults[i]
                print(host,ip,domain,port,title)
                outputs.append([host,ip,domain,port,title])

    if output:
        if os.path.exists(output):
            with open(f"{output}","r") as csvfile:
                reader = csv.reader(csvfile)
                for i,rows in enumerate(reader):
                    if i == 0:
                        row = rows
                        if 'host' and 'ip' and  'domain' and 'port' and 'title' in row:
                            with open(f"{output}","a+") as csvfile:
                                writer = csv.writer(csvfile)
                                # writer.writerow(["host","ip","domain","port","title"])
                                for o in outputs:
                                    writer.writerow([o[0],o[1],o[2],o[3],o[4]])

                        else:
                            with open(f"{output}","a+") as csvfile:
                                writer = csv.writer(csvfile)
                                writer.writerow(["host","ip","domain","port","title"])
                                for o in outputs:
                                    writer.writerow([o[0],o[1],o[2],o[3],o[4]])
                                    
        else:
            with open(f"{output}","a+") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["host","ip","domain","port","title"])
                for o in outputs:
                    writer.writerow([o[0],o[1],o[2],o[3],o[4]])

        print(f"结果已保存到{output}")

                

async def CheckKey(email,key):
    print("check fofa key.....")
    url = f"https://fofa.so/api/v1/info/my?email={email}&key={key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            if "fofa_server" not in html:
                print("fofa key error,please check your key")
                return False
            else:
                print("fofa key is true")
                return True



def main():
    parser = argparse.ArgumentParser(description="FOFA Search.")
    parser.add_argument("--email",help="fofa email",required=True)
    parser.add_argument("--key",help="fofa key",required=True)
    parser.add_argument("--keyword",help="fofa search keyword",required=True)
    parser.add_argument("--file",help="local file for search")
    parser.add_argument("--output",nargs="?",help="csv for output",required=False,default=False)
    args = parser.parse_args()
    if args.email and args.key and args.keyword:
        FOFA_EMAIL = args.email
        FOFA_KEY = args.key
        loop = asyncio.get_event_loop()
        task = loop.create_task(CheckKey(FOFA_EMAIL,FOFA_KEY))
        loop.run_until_complete(task)
        # print(task.result())
        if task.result() and args.file:
            with open(args.file) as f:
                for i in f.readlines():
                    i = i.strip()
                    search_keywords = args.keyword.replace("$FOFAKEYWORD$",i)
                    print(f"搜索的关键词为: {search_keywords}")
                    search_keyword = base64.b64encode(search_keywords.encode()).decode()
                    # print(search_keyword)
                    url = f"https://fofa.so/api/v1/search/all?email={FOFA_EMAIL}&key={FOFA_KEY}&qbase64={search_keyword}&size=10000&fields=host,ip,domain,port,title"
                    # print(url)
                    loop = asyncio.get_event_loop()
                    task = loop.create_task(Search_Keywords(url,args.output))
                    loop.run_until_complete(task)
                    # print(task.result())


        elif task.result():
            search_keywords = args.keyword
            print(f"搜索的关键词为: {search_keywords}")
            # search_keywords = b'domain="htisec.com"'
            search_keyword = base64.b64encode(search_keywords.encode()).decode()
            # print(search_keyword)
            url = f"https://fofa.so/api/v1/search/all?email={FOFA_EMAIL}&key={FOFA_KEY}&qbase64={search_keyword}&size=10000&fields=host,ip,domain,port,title"
            # print(url)
            loop = asyncio.get_event_loop()
            task = loop.create_task(Search_Keywords(url,args.output))
            loop.run_until_complete(task)
            # print(task.result())


            

main()