import random
import csv

def read_stock_data(filename):
    f = open(filename)
    csv_reader = csv.reader(f)
    data = []
    for row in csv_reader:
        if row[0] != '600000':
            continue
        needed = row[1:5]
        needed += row[9:13]
        data.append(needed)
    f.close()
    return data

def evaluate(data, dna):
    fund = 100000.0
    total_interest = 0.0
    share = 0.0
    price = 0.0
    for day in range(len(dna)):
        op = dna[day]
        if op == 0:
            continue
        elif op == 1: # buy
            if fund > 0:
                price = float(data[day][4])
                share = fund / price
                fund = 0
        else: # sell
            if share > 0:
                close_price = float(data[day][7])
                fund = share *  close_price
                share = 0.0

    if share > 0:
        fund = share * float(data[len(data)-1][7])

    return fund - 100000.0


def generate_dna(length):
    operations = [1, 0, -1]
    return [operations[random.randint(0,2)] for i in range(length)]

def mate(dna1, dna2):
    length = len(dna1)
    point = random.randint(0, length-1)
    return [dna1[0:point] + dna2[point:],
            dna2[0:point] + dna1[point:]]

def mutate(dna):
    operations = [1, 0, -1]
    length = len(dna)
    point = random.randint(0, length-1)
    dna[point] = operations[random.randint(0, 2)]
    return dna

def simplify_dna(dna):
    current = dna[0]
    for index in range(1,len(dna)):
        if dna[index] == 0:
            continue
        elif dna[index] == current:
            dna[index] = 0
        else:
            current = dna[index]
    return dna

def train(steps = 1):
    selector = lambda individual: individual[0]
    data = read_stock_data('main_board/600000.csv')
    length = len(data)
    dnas = [simplify_dna(generate_dna(length)) for i in range(1000)]
    generation = [(evaluate(data, dna), dna) for dna in dnas]
    generation.sort(key = selector)
    next_generation = generation[-20:]
    for step in range(steps):
        next_generation.reverse()
        offsprings = []
        for i in range(len(next_generation) / 2):
            ind1 = next_generation[i*2]
            ind2 = next_generation[i*2 + 1]
            result = mate(ind1[1], ind2[1])
            mutate(result[0])
            mutate(result[1])
            dna1 = simplify_dna(result[0])
            dna2 = simplify_dna(result[1])
            offsprings.append((evaluate(data, dna1), dna1))
            offsprings.append((evaluate(data, dna2), dna2))
        offsprings.sort(key = selector)
        next_generation = offsprings

        interest = [ind[0] for ind in next_generation]
#        print 'Generation{}: {}'.format(step, interest)
    return next_generation[-1]


def macd(data):
    ema12 = []
    ema26 = []
    diff = []
    l12 = 2.0/(12+1)
    l26 = 2.0/(26+1)
    ema12.append(float(data[0][7]))
    ema26.append(float(data[0][7]))
    diff.append(0.0)
    for day in range(1, len(data)):
        close = float(data[day][7])
        ema12_yesterday = ema12[day-1]
        ema26_yesterday = ema26[day-1]
        e12 = close * l12 + ema12_yesterday * (1 - l12)
        e26 = close * l26 + ema26_yesterday * (1 - l26)
        ema12.append(e12)
        ema26.append(e26)
        diff.append(e12 - e26)

    dea = []
    dea.append(0.0)
    fp = 8.0/10.0
    ft = 2.0/10.0
    for day in range(1, len(data)):
        dea_yesterday = dea[day-1]
        diff_i = diff[day]
        dea_i = dea_yesterday * fp + diff_i * ft
        dea.append(dea_i)

    macd = []
    for day in range(len(data)):
        macd.append(dea[day] - diff[day])

    return (diff, dea, macd)
