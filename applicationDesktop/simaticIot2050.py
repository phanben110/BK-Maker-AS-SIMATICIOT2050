#Import library custom for Tuining Machine Learning
# from linearRegession.BEN_TuningPID import TuningPID as TuningPIDML 
#Import libray custom for send and receive data with AWS 
from aws.BEN_DynamoDB import DynamoDB as cloudAWS 

#------------set up for PID ML---------------
#set up tuning PID ussing Machine learning 
# PID = TuningPIDML(pathKp="linearRegession/models/kp.pt",pathKi="linearRegession/models/ki.pt",pathKd="linearRegession/models/kd.pt",debug=True) 
#load model 
# PID.loadPIDmodel()

#------------set up for cloudAWS ---------------------
cloud = cloudAWS()


#---------Begin tuining--------------------
# kp,ki,kd = PID.beginTuning(kp=12,ki=12.6,kd=7.6,k1=8.6505,k2=22.4136,k3=0.0439,q1=True)
# print ( kp,ki,kd )

#----------Begin interact with cloudAWS--------------
# receive data from cloud aws
dataDevice =  cloud.receiveData(table="Device",id=1)
print (dataDevice)

# get the final ID in the cloud 
finalID = cloud.getFinalID(table="Device") 
print (finalID)

#send data to table Machine Learning 
#cloud.sendData(table="MachineLearning",id=26,name="Ben Dep Trai",online=True, kp=3.333,ki=4,kd=5, setPoint=34, controlBit=2)

#send data to table Device 
#cloud.sendData(table="Device",id=26,name="Ben Dep Trai",online=True, kp=3.333,ki=4,kd=5, k1=3.2, k2=3.3, k3=4.3, q1=True)

# print ( cloud.sendData(table="ML",
#                        id=6,name="Ben Dep Trai",
#                        online=True, 
#                        kp=3.333,ki=4,kd=5,
#                        movePara=False,moveToPos=False,stop=False, autoTune=False,
#                        setpoint=3.2))
# print ( cloud.sendData(table="Device",
#                        id=6,name="Ben Dep Trai",
#                        online=True,
#                        busy=False,
#                        kp=3.333,ki=4,kd=5,
#                        k1=3, k2=3, k3=4,
#                        sp=2, pv=4.3, cv=3
#                        ))
# print ( cloud.sendData(table="App",
#                        id=6,name="Ben Dep Trai",
#                        online=True, 
#                        kp=3.333,ki=4,kd=5,
#                        ZN=False,ML=False,status="stop",
#                        cvMax = 3, cvMin=3, sp1 = 3, sp2 =3,
#                        q1= False, q2= False, q3= False
#                        ))

