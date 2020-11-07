import numpy as np
import simpy
import random
import matplotlib.pyplot as plot

num_airstrips = 2 #Antall flystriper
delay_probability = 0.8

landingTime = 60 #Hvor lang tid flyet bruker på å lande
takeOffTime = 60 #Hvor lang tid flyet bruker på å ta av

MU_DELAY = 200
MU_TURNAROUND = 2700

ArrivalTime = []
interArr = [0]
landingQueue = 0
takeOffQueue = 0
landingQueueTime = []
takeOffQueueTime = []

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
    global landingQueue
    global takeOffQueue
    yield env.timeout(delay)
    arrivalTime = env.now
    print('Plane arrived at %d' % env.now)

    with runway.request(priority=1) as landReq:
        landingQueue += 1
        yield landReq
        landingQueue -= 1
        print(arrivalTime)
        print(env.now)
        endTime = env.now
        landingQueueTime.append(endTime - arrivalTime)
        yield env.process(land())

    yield env.process(turn_around())
    takeOffWait = env.now
    takeOffQueue += 1

#    with airport.strip.request(priority=2) as takeOffReq:
    with runway.request(priority=2) as takeOffReq:
        yield takeOffReq
        takeOffQueue -= 1
        takeOffQueueTime.append(env.now - takeOffWait)
        yield env.process(takeOff())

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
        arrTime = int(t + delay)
        ArrivalTime.append(arrTime)


        interArrTime = arrTime - interArr[-1]
        interArr.append(interArrTime)

        # Holder før nytt fly genereres.
        t_hold = 60
        time = scheduled(t)

        yield env.timeout(np.maximum(t_hold, time))

def land():
    yield env.timeout(landingTime)
    print('The plane has landed at %d' % env.now)

def turn_around():
    turn_aroundTime = np.random.gamma(7, MU_TURNAROUND/3)  # hvor lang tid flyet bruker fra det har landet til det skal ta av igjen
    yield env.timeout(turn_aroundTime)
    print('The plane is ready to take off %d' % env.now)

def takeOff():
    yield env.timeout(takeOffTime)
    print('The plane left at %d' % env.now)

def getAverageLandingQueueTime():
    sum = 0
    for element in landingQueueTime:
        sum += element
    average = sum / len(landingQueueTime)
    return average

def getAverageTakeOffQueueTime():
    sum = 0
    for element in takeOffQueueTime:
        sum += element
    average = sum / len(takeOffQueueTime)
    return average

env = simpy.Environment()
runway = simpy.PriorityResource(env, capacity=2)
env.process(generatePlane(env))
env.run(until=68400)

plot.legend(['Landing', 'Take-off'])
plot.xlabel('Number of planes')
plot.ylabel('Queue time (seconds)')
plot.title('Time spent in anding and take-off times for every plane.', fontsize=16)
plot.plot(landingQueueTime, "b")
plot.plot(takeOffQueueTime, "g--")
plot.show()

print(getAverageLandingQueueTime())
print(getAverageTakeOffQueueTime())