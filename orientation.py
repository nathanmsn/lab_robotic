import RPi.GPIO as GPIO
import time
import datetime
import math
from HIMUServer import HIMUServer


#------------SETUP------------

#pins
servo0_pin = 12
servo1_pin = 35

#constants
pwm_period = 20 #ms

#GPiO setup
GPIO.setmode(GPIO.BOARD) #we use the board pin numbers (not BCM)
GPIO.setup(servo0_pin, GPIO.OUT)
GPIO.setup(servo1_pin, GPIO.OUT)

#Refresh rate setup
loop_time_curr = datetime.datetime.now()
loop_time_prev = loop_time_curr

#------------HIMU------------

#Listener class
class SensorListener:
    def __init__(self, serverInstance):
        self.__server = serverInstance
        self.s1_x_curr = 0 #current x sensor data
        self.s1_y_curr = 0
        self.s1_z_curr = 0
        
        self.s1_x_prev = 0 #previous x sensor data
        self.s1_y_prev = 0
        self.s1_z_prev = 0
        self.sensor_data_period = 0 #ms
        
    def notify (self, sensorData):
        loop_time_prev = loop_time_curr
        loop_time_curr = datetime.datetime.now()
        sensor_data_period = loop_time_curr - loop_time_prev
        
        sensor_1 = HIMUServer.strings2Floats(sensors[0]) #converts from Strings to floats
        s1_x_prev = s1_x_curr
        s1_y_prev = s1_y_curr
        s1_z_prev = s1_z_curr
        
        s1_x_curr = sensor_1[0]
        s1_y_curr = sensor_1[1]
        s1_z_curr = sensor_1[2]
        
        myGyro.gyro_x = getAngularPosition(s1_x_prev, s1_x_curr, myListener.sensor_data_period)
        myGyro.gyro_z = getAngularPosition(s1_z_prev, s1_z_curr, myListener.sensor_data_period)
        myGyro.pos_x = setDutyCycle(myGyro.gyro_x)
        myGyro.pos_z = setDutyCycle(myGyro.gyro_z)
        
        print("X position:" + str(myGyro.pos_x))
        print("Z position:" + str(myGyro.pos_z))
        print("Sensor period:" + str(myListener.sensor_data_period))
        
        #setPosition(1, myGyro.pos_x)
        #setPosition(0, myGyro.pos_z)
        

#------------STARTUP------------
myHIMUServer = HIMUServer()
myListener = SensorListener(myHIMUServer)
myHIMUServer.addListener(myListener)
myHIMUServer.start("UDP", 50000)

class GyroData:
    def __init__(self, gyro_x, gyro_z, pos_x, pos_z):
        self.gyro_x = gyro_x
        self.gyro_z = gyro_z
        self.pos_x = pos_x
        self.pos_z = pos_z

myGyro = GyroData(0, 0, 0, 0)

#------------PWM------------

#create PWM objects
p0 = GPIO.PWM(servo0_pin, 50) #PWM of 50Hz on servo pin 0
p1 = GPIO.PWM(servo1_pin, 50)
p0.start(2.5) #initialization of PWM object
p1.start(2.5)

#set 0 position


#------------FUNCTIONS------------

def getAngularPosition(angular_velocity1, angular_velocity2, sensor_data_period):
    #function that outputs a value in randians from radians/s
    angular_velocity_avg = 0.5*(angular_velocity2 - angular_velocity2)*sensor_data_period
    
    return angular_velocity_avg
    

def setDutyCycle (angular_position):
    #function that from angular value in radians gives back dutycycle of the PWM in ms
    if angular_position <= (-1/2)*math.pi:
        return 1
        
    elif angular_position >= (1/2)*math.pi:
        return 2
        
    else:
        return (math.pi)*angular_position + 1.5 # 0.5[ms]/90[degrees]


def setPosition (servoID, dutycycle):
    #function that sets the desired servo at a specified angle, given dutycycle
    pwm_percentage = (dutycycle/pwm_period)*100
    print(pwm_percentage)
    
    if servoID == 0:
        p0.ChangeDutyCycle(pwm_percentage) 
        
    if servoID == 1:
        p1.ChangeDutyCycle(pwm_percentage)
        
    time.sleep(0.5)

try:
    pass
           
except KeyboardInterrupt:
	p0.stop()
	p1.stop()
	GPIO.cleanup()
