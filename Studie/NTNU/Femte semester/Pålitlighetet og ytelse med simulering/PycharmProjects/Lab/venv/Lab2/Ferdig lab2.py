import numpy as np
import simpy
import random
import matplotlib.pyplot as plot

num_runways = 8 #Antall flystriper
num_deiceTrucks = 5 #Antall deicebiler
num_plowTrucks = 1 #Antall brøytebiler

landingTime = 60 #Hvor lang tid flyet bruker på å lande
takeOffTime = 60 #Hvor lang tid flyet bruker på å ta av
deice_time = 600
plow_time = 600
fill_runway_time = 2700

delay_probability = 0.5

MU_DELAY = 0
MU_TURNAROUND = 2700

planeNR = 1

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

    with deiceTruck.request(priority=1) as deiceReq:
        yield deiceReq
        yield env.process(deice())

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


def deice():
    "Plane is deiced before takeoff."
    print('Plane is deiced at %d ' % env.now)
    yield env.timeout(deice_time)

def plow():
    with runway.request(priority=0) as plowReq:
        yield plowReq
        with plowTruck.request() as plowed:
            yield plowed
            yield env.timeout(plow_time)

def fillRunway():
    while true:
        try:
            yield env.timeout(fill_runway_time)
            plow()
        except simpy.Interrupt:
            pass

def snow(env):
    fullRunway = np.random.exponential(scale=fill_runway_time)
    while True:
        snow_time = np.random.exponential(scale=3600)
        no_snow_time = np.random.exponential(scale=7200)
        yield env.timeout(no_snow_time)
        times = int(snow_time // fullRunway)
        extra = snow_time % fullRunway

        if times == 0:
            yield env.timeout(snow_time)
        else:
            for n in range(times):
                yield env.timeout(fullRunway)
                for n in range(num_runways):
                    print("Runway", n + 1, "needs plowing")
                    env.process(plow())
            yield env.timeout(extra)

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
plowTruck = simpy.PriorityResource(env, capacity=num_plowTrucks)
deiceTruck = simpy.PriorityResource(env, capacity=1)

env.process(generatePlane(env))
env.process(snow(env))

env.run(until=68400)

plot.xlabel('Number of planes')
plot.ylabel('Queue time (seconds)')
plot.title('Time spent in landing and take-off times for every plane.', fontsize=16)
plot.plot(landingQueueTime, "b")
plot.plot(takeOffQueueTime, "g--")
plot.ylim(0, 2000)
plot.show()

print(landingQueueTime)
print(takeOffQueueTime)
print("average landing queue time:", getAverageLandingQueueTime())
print("average take-off queue time:", getAverageTakeOffQueueTime())