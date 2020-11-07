import numpy as np
import simpy
import random
import matplotlib.pyplot as plot

delay_probability = 0.5
MU_DELAY = 200
landingTime = 60 #Hvor lang tid flyet bruker på å lande
takeOffTime = 60 #Hvor lang tid flyet bruker på å ta av
ArrivalTime = [0]
interArr = []

def scheduled(t):
    if t >= 0 and env.now < 10800:
        return(np.random.exponential(120))

    elif t >= 10800 and env.now < 21600:
        return(np.random.exponential(30))

    elif t >= 21600 and env.now < 36000:
        return(np.random.exponential(150))

    elif t >= 36000 and env.now < 54000:
        return(np.random.exponential(30))
    else:
        return(np.random.exponential(120))

def plane(env, delay):
    yield env.timeout(delay)
    print('Plane arrived at %d' % env.now)

def generatePlane(env):
    while True:
        delay = 0
        t = env.now

        # Avgjør om flyet er forsinket eller ikke
        rand = np.random.choice([True, False], p=[delay_probability, 1 - delay_probability])
        if rand:
            delay = int(np.random.gamma(3, MU_DELAY/3))

        print('Generate plane at %d' % t)
        env.process(plane(env, delay))
        arrTime = int(t)
        interArrTime = abs(arrTime - ArrivalTime[-1])
        ArrivalTime.append(arrTime)
        interArr.append(interArrTime)
        t_hold = 60
        time = scheduled(t)
        yield env.timeout(np.maximum(t_hold, time))

def averageInterArrivalTime():
    sum = 0
    for element in interArr:
        sum += element
    average = sum / len(interArr)
    return average


env = simpy.Environment()
env.process(generatePlane(env))
env.run(until=68400)

plot.plot(interArr)
plot.xlabel('Plane number')
plot.ylabel('Inter-arrival time')
plot.title('Inter-arrival time with mu delay: ' + str(MU_DELAY), fontsize=16)
plot.show()
print(averageInterArrivalTime())
