import json
import re
import urllib
import requests
import threading


class monitorCrypto:

    currPrice = {}
    cryptoPair_coinb = ['BTC-INR;buy', 'BTC-INR;sell', 'LTC-INR;buy', 'LTC-INR;sell', 'ETH-INR;buy', 'ETH-INR;sell',
              'BCH-INR;buy', 'BCH-INR;sell']
    crypto_zeb = ['BTC-INR','LTC-INR','ETH-INR','XRP-INR','BCH-INR']
    PriceDiff={}
    telegramapikey= "1654450890:AAGIcNXyJE6zJUqi6bm1dX5fh6Ng2-0GYRw"
    chatid='557428602'
    msg=''

    def getCoinbaseRates(self):
        for i in self.cryptoPair_coinb:
            crypto = i.split(";")[0]
            transtype = i.split(";")[1]
            threading.Thread(target=self.callcoinbapi,args=(crypto,transtype,)).start()
        print(self.currPrice)
    def callcoinbapi(self,crypto,transtype):
            #print("https://api.coinbase.com/v2/prices/" + crypto + "/" + transtype)
            r = requests.get("https://api.coinbase.com/v2/prices/" + crypto + "/" + transtype).content
            coinbResponse = json.loads(r)
            #print(coinbResponse['data']['amount'])
            self.currPrice[crypto[0:4:1] + transtype + "-coinbase"] = coinbResponse['data']['amount']


    def getZebpayRates(self):
        for i in self.crypto_zeb:
            crypto= i[0:4]
            r = requests.get("https://www.zebapi.com/pro/v1/market/"+i+"/ticker").content
            zeb_resp= json.loads(r)
            self.currPrice[crypto+"buy-zebpay"]= zeb_resp['buy']
            self.currPrice[crypto+"sell-zebpay"]= zeb_resp['sell']

    def getUnocoinRates(self):
        r= requests.get("https://api.unocoin.com/api/trades/in/all/all").content
        unoresp=json.loads(r)
        unorespk= json.loads(r).keys()
        #print(r)
        for i in unorespk:
            if not re.match(r"BTC|ETH|XRP|LTC|BCH",i):
                continue
            #print(i+" "+unoresp[i]['buying_price'])
            self.currPrice[i+"-buy-unocoin"] = unoresp[i]['buying_price']
            self.currPrice[i+"-sell-unocoin"] = unoresp[i]['selling_price']
        #print(self.currPrice)

    def getCoindcxRates(self):
        r= requests.get("https://api.coindcx.com/exchange/ticker").content
        resp= json.loads(r)
        #print(resp)
        for i in range(len(resp)):
            if not re.match("BTCINR|LTCINR|ETHINR|XRPINR|BCHINR",resp[i]['market']):
                continue
        #print(resp[i]['market'][0:3]+"-buy-"+f"coindcx:{resp[i]['bid']}")
        self.currPrice[resp[i]['market'][0:3]+"-sell-"+"coindcx"] = resp[i]['bid']
        self.currPrice[resp[i]['market'][0:3]+"-buy-"+"coindcx"] = resp[i]['ask']

    def createPriceDiff(self):

        for i,vi in self.currPrice.items():
            if i.split("-")[1] == "sell":
                continue
            for j,vj in self.currPrice.items():

                if j.split("-")[1] == "buy":
                    continue
                if i.split("-")[0] != j.split("-")[0] or i.split("-")[2] == j.split("-")[2] or float(vi)-float(vj)>0:
                    continue
                #print(f'The price of {i.split("-")[0]} in {i.split("-")[2]} is {vi} and in {j.split("-")[2]} is {vj}.\nProfit prospect: {(float(vj)-float(vi))*100/float(vi)}%')
                self.PriceDiff[i.split("-")[0] +'-'+ i.split("-")[2]+'-'+j.split("-")[2]] = (float(vj)-float(vi))*100/float(vi)
        sortedPrDif= sorted(self.PriceDiff.items(), key=lambda kv: kv[1], reverse=True)
        #print(self.PriceDiff)
        print(sortedPrDif)
        self.PriceDiff = sortedPrDif

    def createmessage(self):
        i=1
        for k,pp in self.PriceDiff:
            if i==6:
                break
            crypto=k.split("-")[0]
            buyplat= k.split("-")[1]
            sellplat= k.split("-")[2]
            if(pp>7):
                self.msg=self.msg+'\n'+f'{i}. The price of {crypto} in {buyplat} is {round(float(self.currPrice[crypto+"-buy-"+buyplat]),2)} and in {sellplat} is {round(float(self.currPrice[crypto+"-sell-"+sellplat]),2)}.\nProfit prospect: {round(float(pp),2)} percent.'
            i=i+1
        print(f'https://api.telegram.org/bot{self.telegramapikey}/sendmessage?chat_id=-{self.chatid}&text={urllib.parse.quote_plus(self.msg)}')

    def sendNotification(self):
        r=requests.get(f'https://api.telegram.org/bot{self.telegramapikey}/sendmessage?chat_id=-{self.chatid}&text={ urllib.parse.quote_plus(self.msg)}')
        print(r)


#def callmonitor():
obj = monitorCrypto()
obj.getCoindcxRates()
obj.getCoinbaseRates()
obj.getZebpayRates()
obj.getUnocoinRates()
obj.createPriceDiff()
obj.createmessage()
obj.sendNotification()
