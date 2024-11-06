total = 0

originals = []
probs = []
trues = []

while True:

    bet = str(input("Enter Odds i.e 12/5 or to stop type BREAK"))

    if bet == "BREAK":
        break

    bet = bet.split("/")

    bet = int(bet[0])/int(bet[1])

    odds = 1/bet

    total += odds

    probs.append(odds)
    originals.append(bet)


print(total)
print(total-1)

for i in probs:
    true = (i/total)
    #print("Was "+str(i)+" | Now "+str(true))
    trues.append(true)

n = 0
wager = 0.5
for i in trues:
    print((i*originals[n]), wager, (1-i))
    ev = (i*originals[n])-(wager*(1-i))
    print("EV"+str(n)+": "+str(ev))



