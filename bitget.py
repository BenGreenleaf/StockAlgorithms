#bg_6d2823601bac54dbb01b06f279b0152f
#1c2e76b6d405bd0ec5846e496fbe7c76f39630da6c5c067785957df475b39015
#benandcharlie

from pybitget import Client
import datetime, time, random, statistics
import matplotlib.pyplot as plt

api_key = "bg_6d2823601bac54dbb01b06f279b0152f"
api_secret = "1c2e76b6d405bd0ec5846e496fbe7c76f39630da6c5c067785957df475b39015"
api_passphrase = "benandcharlie"

client = Client(api_key, api_secret, passphrase=api_passphrase)

data = []

leverage = 10

date = random.randint(1674075414, 1702933052)

print(date)

start = 1697334469000
end = 1703587669000
ns = ((end-start)//(1000*60*15*1000))+1

data = []
out = False

for j in range(0, ns):
    s = start + ((1000*60*15*1000)*(j))+(1000*60*15)
    e = s + ((1000*60*15*1000))
    
    if e > end:
        e = end
        out = True
        print("MET MET MET", s, e)

    if out == False:
        result = client.mix_get_candles(symbol="BTCUSDT_UMCBL", granularity="15m", startTime=s , endTime=e, limit=1000)
        #print(result)

        for r in reversed(range(len(result))):
            data.append(result[r])

    print(len(data), "\n")

result = data
print(datetime.datetime.fromtimestamp(float(result[0][0])/1000), len(result))
avg = 0

cache = []
lows = 0
highs = 0

for i in range(0,len(result)-5):
    max = 0
    min = 100000

    last = "neither"

    cache.append(float(result[i][4]))
    if len(cache) > 20:
        cache.pop(0)
        avgL = sum(cache)/len(cache)
        bbLower = avgL - (2*statistics.stdev(cache))

        if float(result[i][4]) < bbLower:

            for j in range(1,6):
                if float(result[i+j][4]) > max:
                    max = float(result[i+j][4])
                    last = "max"
                if float(result[i+j][4]) < min:
                    min = float(result[i+j][4])
                    last = "min"

            if last == "min":
                pDiff = (max-float(result[i][4]))/float(result[i][4])
                avg += pDiff
                highs += 1

            else:
                pDiff = (float(result[i][4])-min)/float(result[i][4])
                avg += pDiff
                lows += 1


avg = avg/(len(result)-5)

print(avg*100)
print(highs/(highs+lows))

sl = avg*0.7
tp = avg*0.8

ws = 0
ls = 0

p = 0



def sim(a, b):

    openTradesMax = 0
    tps = []
    sls = []
    cache = []
    xs = []
    ys = []
    p = 0
    ws = 0
    ls = 0
    n = 0

    for i in result:
        cache.append(float(i[4]))
        bbLower = 0
        if len(cache) > 20:
            cache.pop(0)
            avgL = sum(cache)/len(cache)
            bbLower = avgL - (2*statistics.stdev(cache))

        if float(i[4]) < bbLower:
            tp = float(i[4])*(1+(a/100))
            sl = float(i[4])*(1-(b/100))

            tps.append(tp)
            sls.append(sl)

        removedtp = []
        removedsl = []
        for j in range(0,len(sls)):
            if float(i[3]) <= sls[j]:
                removedtp.append(tps[j])
                removedsl.append(sls[j])
                p -= b/100
                ls += 1

        for j in removedtp:
            tps.remove(j)
        for j in removedsl:
            sls.remove(j)
        
        removedtp = []
        removedsl = []
        for j in range(0,len(tps)):
            if float(i[2]) >= tps[j]:
                removedtp.append(tps[j])
                removedsl.append(sls[j])
                p += a/100
                ws += 1

        for j in removedtp:
            tps.remove(j)
        for j in removedsl:
            sls.remove(j)


        if len(tps) > openTradesMax:
            openTradesMax = len(tps)

        xs.append(n)
        ys.append(p)
        n += 1

    if ws > 0:
        wRate = (ws/(ws+ls))
    else:
        wRate = 0

    p -= (len(sls)*(a+(b*-1)))/100

    if openTradesMax == 0:
        openTradesMax = 1

    p = p/openTradesMax

    for j in range(0,len(ys)):
        ys[j] = ys[j]/openTradesMax

    return(p, openTradesMax, wRate, len(sls), xs, ys)

data = sim(1.1, 5.0)
print(data)
plt.plot(data[4], data[5])
plt.show()
#1.1, 9.9
#
max = 0
best = []

for k in range(0, 100):
    k = k/10

    for m in range(0,100):
        m = m/10

        res, tradeNum, wRate, lenSls, x, y = sim(k,m)
        if res > max:
            max = res
            best = [k,m, tradeNum, wRate, lenSls, x, y]

    print(max*100, best)
    

print(best, max*100)

time.sleep(100000)

def simulaton(a, b):
    sl = avg*a
    tp = avg*b

    ws = 0
    ls = 0

    p = 0

    for i in range(0,len(result)-15):
        fee = float(result[i][1])*(0.08/100)
        upperStop = float(result[i][1])+((float(result[i][1]))*sl)
        upperTake = float(result[i][1])+((float(result[i][1]))*tp)+fee

        lowerStop = float(result[i][1])-((float(result[i][1]))*sl)
        lowerTake = float(result[i][1])-((float(result[i][1]))*tp)-fee

        uslBreak = False
        utpBreak = False
        lslBreak = False
        ltpBreak = False

        for j in range(1,len(result)-i):
                if float(result[i+j][2]) > upperStop:
                    uslBreak = True
                if float(result[i+j][2]) > upperTake:
                    utpBreak = True

                if float(result[i+j][3]) < lowerStop:
                    lslBreak = True
                if float(result[i+j][3]) < lowerTake:
                    ltpBreak = True


                if uslBreak == True and lslBreak == True and utpBreak == False and ltpBreak == False:
                    ls += 1
                    p -= ((upperStop-lowerStop)/float(result[i+j][2]))+(0.08/100)
                    break

                elif uslBreak == True and utpBreak == True and lslBreak == False:
                    ws += 1
                    p += ((upperTake-upperStop)/float(result[i+j][2]))-(0.08/100)
                    break

                elif lslBreak == True and ltpBreak == True and uslBreak == False:
                    ws += 1
                    p += ((lowerStop-lowerTake)/float(result[i+j][2]))-(0.08/100)
                    break

                if j == (len(result)-i):
                    ls += 1
                    p -= (0.08/100)
                    break

    return((ws/(ws+ls)), p, ws, ls)

min = -1
best = []
for t in range(40, 81):
    t = t/10
    for f in range(0, 150):
        f = f/10
        res = simulaton(t,f)
        if res[1] > min:
            best = res, t, f
            min = res[1]
        print(res, t, f)

print(best)

        
#4.7, 11.3     


    