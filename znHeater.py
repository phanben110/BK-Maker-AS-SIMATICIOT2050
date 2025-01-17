#Import library custom for Tuining Machine Learning
from linearRegession.BEN_TuningPID import TuningPID as TuningPIDML 
from linearRegession.BEN_clutering import PIDDataset 
#Import libray custom for send and receive data with AWS 
from aws.BEN_DynamoDB import DynamoDB as cloudAWS 
print ("***BK-MAKER AS Team")

import time  
from numpy import random 
import numpy as np
from random import randint
#------------set up for PID ML---------------
#set up tuning PID ussing Machine learning 

PID = TuningPIDML(pathKp="linearRegession/models/kp.pt",pathKi="linearRegession/models/ki.pt",pathKd="linearRegession/models/kd.pt",debug=True) 
#load model 

print ("***Load model AI...")
PID.loadPIDmodel()
cluPID = PIDDataset() 
cluPID.loadDataset()

timeOut = 3

#------------set up for cloudAWS ---------------------
cloud = cloudAWS()

def setpointCalc():
#    dataML =  cloud.receiveData(table="ML",id=1)
#    setpointV = int(dataML["control"]["setpoint"])
#    if setpointV == 150: 
#        setpointV = 200
#    else : 
#        setpointV = 150
#    return setpointV
    return 70

def sendDataAutotune(idDevice,status,kp,ki,kd,pid=False):
    if pid == False:
        setpoint = setpointCalc()
        cloud.sendData(table="ML",
                       id=1, currentID=int(idDevice)+1  , name="Motor_1",
                       online=True, 
                       kp=kp,ki=ki,kd=kd,
                       movePara=False,moveToPos=False,stop=False,autoTune=True,
                       setpoint=setpoint)
        time.sleep(2)

        cloud.sendData(table="ML",
                       id=1, currentID=int(idDevice) +1  , name="Motor_1",
                       online=True, 
                       kp=kp,ki=ki,kd=kd,
                       movePara=True,moveToPos=False,stop=False,autoTune=True,
                       setpoint=setpoint)
        time.sleep(2)

        cloud.sendData(table="ML",
                       id=1, currentID=int(idDevice) +1  , name="Motor_1",
                       online=True, 
                       kp=kp,ki=ki,kd=kd,
                       movePara=False,moveToPos=False,stop=False,autoTune=False,
                       setpoint=setpoint)
        time.sleep(1)
    else:
        setpoint = setpointCalc()

        cloud.sendData(table="ML",
                       id=1, currentID=int(idDevice)+1  , name="Motor_1",
                       online=True, 
                       kp=kp,ki=ki,kd=kd,
                       movePara=True,moveToPos=False,stop=False,autoTune=False,
                       setpoint=setpoint)
        time.sleep(2)

        cloud.sendData(table="ML",
                       id=1, currentID=int(idDevice) +1  , name="Motor_1",
                       online=True, 
                       kp=kp,ki=ki,kd=kd,
                       movePara=False,moveToPos=False,stop=False,autoTune=False,
                       setpoint=setpoint)
        time.sleep(2)

def checkCondML(k1,k2,k3,preK1,preK2,preK3,q1,q2,q3): 
    if q1 and preK1 < k1:
            return True 
    elif q2 and preK2 < k2: 
            return True 
    elif q3 and preK3 < k3: 
            return True 
    else:
        return False 

def bestPID(storePID,q1,q2,q3): 
    if q1 : 
        listQ1=list()
        for i in range(len(storePID)): 
            listQ1.append(storePID[i][3])
        n = np.argmin(listQ1)
        return storePID[n]
    if q2 : 
        listQ2=list()
        for i in range(len(storePID)): 
            listQ2.append(storePID[i][4])
        n = np.argmin(listQ2)
        return storePID[n]

    if q3 : 
        listQ3=list()
        for i in range(len(storePID)): 
            listQ3.append(storePID[i][5])
        n = np.argmin(listQ3)
        return storePID[n]








#finalID = cloud.getFinalID(table="App") 
#----------Begin interact with cloudAWS--------------
# receive data from cloud aws
check = True
statusZN0=True
statusZN1=True 
statusZN2=True
statusZN3=True
statusZN4=True
while True :
    if check:
        print ("***Step 1: Get data from DynamoDB AWS")
        print ("***Step 2: Waiting signal from app...")
    else: 
        print (".", end="", flush=True)
        time.sleep(0.1)

    dataApp =  cloud.receiveData(table="App",id=1)
    dataML =  cloud.receiveData(table="ML",id=1)
    dataDevice =  cloud.receiveData(table="Device",id=1)

    cuKp = float( dataDevice["PID"]["kp"])
    cuKi = float( dataDevice["PID"]["ki"])
    cuKd = float( dataDevice["PID"]["kd"])

    idDevice = int(dataDevice["currentID"]) 

    runML = bool(dataApp["control"]["ML"])
    runZN = bool(dataApp["control"]["ZN"])
    if runML:
        print ("-----------This method no support, please chose another method!---------")
        continue
    storePID = list()

    if runML == True and runZN == False: 
        check = False
        Q1 = bool(dataApp["option"]["settlingTime"])
        Q2 = bool(dataApp["option"]["overshoot"])
        Q3 = bool(dataApp["option"]["steadyStateError"])
        if Q1 or Q2 or Q3: 
            check = True
            checkML = False
            print ("***Step 2: Begin tuning by Machine Learning")
            Kp = float(dataApp["PID"]["kp"])
            Ki = float(dataApp["PID"]["ki"])
            Kd = float(dataApp["PID"]["kd"])
            
            K1 = float(dataDevice["quality"]["settlingTime"])
            K2 = float(dataDevice["quality"]["overshoot"])
            K3 = float(dataDevice["quality"]["steadyStateError"] )
            storePID.append([Kp,Ki,Kd,cuKp,cuKi,cuKd])
            k=0.5
            count = 0 

            while(1):
                count +=1 
                
                setpoint = setpointCalc()

                print (f"Kp: {Kp}, Ki: {Ki}, Kd: {Kd}, K1: {K1}, K2: {K2}, K3: {K3}, Q1: {Q1}, Q2: {Q2}, Q3: {Q3}, ID: {idDevice}, setpoint: {setpoint}")
                
                #---------Begin tuining--------------------
                cloud.sendData(table="App",
                               id=1,name="Motor",
                               online=True, 
                               kp=Kp,ki=Ki,kd=Kd,
                               ZN=False,ML=False,status="MLBegin",
                               cvMax = 3, cvMin=3, sp1 = 3, sp2 =3,
                               q1= False, q2= False, q3= False
                               )
                
                #mlKp,mlKi,mlKd = PID.beginTuning(kp=Kp,ki=Ki,kd=Kd,k1=K1,k2=K2,k3=K3,q1=Q1, q2=Q2, q3=Q3)
                #print ( mlKp, mlKi, mlKd )
                print ( count )
                if count == timeOut: 
                    value = bestPID(storePID, q1=Q1, q2=Q2, q3=Q3)
                else:
                    value = cluPID.beginTuning(K1=K1,K2=K2,K3=K3,q1=Q1,q2=Q2,q3=Q3,k=k)
                k+=0.25

                storePID.append([Kp,Ki,Kd,K1,K2,K3])
                print (f"storePID {storePID}")
                print ( f"that is value predict {value}" )
                mlKp = value[0]
                mlKi = value[1]
                mlKd = value[2]
                mlK1 = value[3]
                mlK2 = value[4]
                mlK3 = value[5]

                cloud.sendData(table="ML",
                               id=1, currentID=idDevice+1 , name="Motor_1",
                               online=True, 
                               kp=mlKp,ki=mlKi,kd=mlKd,
                               movePara=True,moveToPos=False,stop=False, autoTune=False,
                               setpoint=setpoint)
                print ("***Step 3: Control IoT2050")
                time.sleep(2)
                
                cloud.sendData(table="ML",
                               id=1, currentID=idDevice +1  , name="Motor_1",
                               online=True, 
                               kp=mlKp,ki=mlKi,kd=mlKd,
                               movePara=False,moveToPos=False,stop=False, autoTune=False,
                               setpoint=setpoint)

                time.sleep(0.1)

                
                data3 = cloud.receiveData(table="Device",id=1)

                K13 = float(data3["quality"]["settlingTime"])
                K23 = float(data3["quality"]["overshoot"])

                while True:
                    data4 = cloud.receiveData(table="Device",id=1)

                    K14 = float(data4["quality"]["settlingTime"])
                    K24 = float(data4["quality"]["overshoot"])
                    K34 = float(data3["quality"]["overshoot"])

                    if K13 != K14 or K23 != K24:
                        checkML= checkCondML(K1,K2,K3,K14,K24,K34,q1=Q1,q2=Q2,q3=Q3)
                        print ( f"print checkml {checkML}" )
                        if checkML:

                            cloud.sendData(table="App",
                                           id=1,name="Motor",
                                           online=True, 
                                           kp=Kp,ki=Ki,kd=Kd,
                                           ZN=False,ML=False,status="Done",
                                           cvMax = 3, cvMin=3, sp1 = 3, sp2 =3,
                                           q1= False, q2= False, q3= False
                                           )

                        break 

                if checkML:
                    print ("**Step 4: Send status")
                    print ( "Done" )
                    print (f"count {count}")
                    break 
                
                else :
                    if count == timeOut: 
                        print ("**Step 4: Send status")
                        print ( "Done" )
                        print (f"count {count}")
                        break 


    elif runZN == True and runML == False: 
        setpoint = setpointCalc()
        if check:
            print("***Step 2:Begin tuning PID by ZN")
            print (f"ID: {idDevice}, setpoint: {setpoint}")

        print("\r\n***step 3: ZN Begin...")
        sendDataAutotune(idDevice,"ZNTime0",cuKp,cuKi,cuKd)


        check = False
        while statusZN0: 
            data0 = cloud.receiveData(table="Device",id=1)

            K10 = float(data0["quality"]["settlingTime"])
            K20 = float(data0["quality"]["overshoot"])

            kp0 = float( data0["PID"]["kp"])
            ki0 = float( data0["PID"]["ki"])
            kd0 = float( data0["PID"]["kd"])

            if cuKd != kd0 and cuKi != ki0:
                print("\r\n***step 3: ZN time 0 ...")

                cloud.sendData(table="App",
                               id=1,name="Motor",
                               online=True, 
                               kp=kp0,ki=ki0,kd=kd0,
                               ZN=False,ML=False,status="ZNBegin",
                               cvMax = 3, cvMin=3, sp1 = 3, sp2 =3,
                               q1= False, q2= False, q3= False)

                time.sleep(1)

                sendDataAutotune(idDevice,"ZNTime0",kp0,ki0,kd0,pid=True)
                #run
                break

        while statusZN1: 
            data1 = cloud.receiveData(table="Device",id=1)

            K11 = float(data1["quality"]["settlingTime"])
            K21 = float(data1["quality"]["overshoot"])

            kp1 = float( data1["PID"]["kp"])
            ki1 = float( data1["PID"]["ki"])
            kd1 = float( data1["PID"]["kd"])

            if K11 != K10 or K21 != K20:
                print("\r\n***step 4: ZN time 1 ...")

                cloud.sendData(table="App",
                               id=1,name="Motor",
                               online=True, 
                               kp=kp0,ki=ki0,kd=kd0,
                               ZN=False,ML=False,status="ZNTime0",
                               cvMax = 3, cvMin=3, sp1 = 3, sp2 =3,
                               q1= False, q2= False, q3= False)

                time.sleep(1)


                Ku = kp1/0.6
                Tu = 1.2*Ku/ki1

                Kp_PI = 0.7*Ku
                Ki_PI = 1.75*Ku/Tu
                Td_PI = 3*Tu/20
                Kd_PI = Kp_PI/Td_PI

                sendDataAutotune(idDevice,"ZNTime0",Kp_PI,Ki_PI,Kd_PI,pid=True)
                #run 
                break 
        while statusZN2: 
            data2 = cloud.receiveData(table="Device",id=1)

            K12 = float(data2["quality"]["settlingTime"])
            K22 = float(data2["quality"]["overshoot"])


            if K11 != K12 or K21 != K22:

                cloud.sendData(table="App",
                               id=1,name="Motor",
                               online=True, 
                               kp=kp1,ki=ki1,kd=kd1,
                               ZN=False,ML=False,status="ZNTime1",
                               cvMax = 3, cvMin=3, sp1 = 3, sp2 =3,
                               q1= False, q2= False, q3= False)

                time.sleep(1)

                print("\r\n***step 5: ZN time 2 ...")

                kp2 = float( data2["PID"]["kp"])
                ki2 = float( data2["PID"]["ki"])
                kd2 = float( data2["PID"]["kd"])

                Ku = kp2/0.6
                Tu = 1.2*Ku/ki2

                #Kp_SO = Ku/3
                Kp_SO = Ku*0.55
                Ki_SO = ((2/3)*Ku/Tu)*1.25
                #Ki_SO = (2/3)*Ku/Tu
                Td_SO = Tu/3
                #Kd_SO = Kp_SO/Td_SO
                Kd_SO = (Kp_SO/Td_SO)*1.8

                sendDataAutotune(idDevice,"ZNTime2",Kp_SO,Ki_SO,Kd_SO,pid=True)
                break  

        while statusZN3: 
            data3 = cloud.receiveData(table="Device",id=1)

            K13 = float(data3["quality"]["settlingTime"])
            K23 = float(data3["quality"]["overshoot"])

            
            if K12 != K13 or K22 != K23:
                print("\r\n***step 6: ZN time 3 ...")


                cloud.sendData(table="App",
                               id=1,name="Motor",
                               online=True, 
                               kp=kp2,ki=ki2,kd=kd2,
                               ZN=False,ML=False,status="ZNTime2",
                               cvMax = 3, cvMin=3, sp1 = 3, sp2 =3,
                               q1= False, q2= False, q3= False)

                time.sleep(1)


                kp3 = float( data3["PID"]["kp"])
                ki3 = float( data3["PID"]["ki"])
                kd3 = float( data3["PID"]["kd"])

                #run 
                Ku = kp3/0.6
                Tu = 1.2*Ku/ki3

                #Kp_NO = 0.2*Ku
                Kp_NO = 0.5*Ku
                Ki_NO = ((2/3)*Ku/Tu)*1.1
                Td_NO = Tu/3
                Kd_NO = (Kp_NO/Td_NO)*1.6
                #Ki_NO = (2/5)*Ku/Tu
                #Td_NO = Tu/3
                #Kd_NO = Kp_NO/Td_NO

                sendDataAutotune(idDevice,"ZNTime3",Kp_NO,Ki_NO,Kd_NO,pid=True)
                break 

        while statusZN4:
            data4 = cloud.receiveData(table="Device",id=1)

            K14 = float(data4["quality"]["settlingTime"])
            K24 = float(data4["quality"]["overshoot"])

            if K13 != K14 or K23 != K24:

                cloud.sendData(table="App",
                               id=1,name="Motor",
                               online=True, 
                               kp=kp3,ki=ki3,kd=kd3,
                               ZN=False,ML=False,status="ZNTime3",
                               cvMax = 3, cvMin=3, sp1 = 3, sp2 =3,
                               q1= False, q2= False, q3= False)

                time.sleep(1)

                kp4 = float( data4["PID"]["kp"])
                ki4 = float( data4["PID"]["ki"])
                kd4 = float( data4["PID"]["kd"])
                cloud.sendData(table="App",
                               id=1,name="Motor",
                               online=True, 
                               kp=kp4,ki=ki4,kd=kd4,
                               ZN=False,ML=False,status="ZNDone",
                               cvMax = 3, cvMin=3, sp1 = 3, sp2 =3,
                               q1= False, q2= False, q3= False)

                print("\r\n***Done!")

                print("\r\n----------------------------------------------------------\r\n")

                check = True
                break

    else: 
        if check : 
            print("Please chose method to tuining PID!")

        check = False



#cloud.sendData(table="App",
#               id=1,name="Motor",
#               online=True, 
#               kp=Kp,ki=Ki,kd=Kd,
#               ZN=False,ML=False,status="ML Runing...",
#               cvMax = 3, cvMin=3, sp1 = 3, sp2 =3,
#               q1= False, q2= False, q3= False
#               )
#

## get the final ID in the cloud 
#finalID = cloud.getFinalID(table="Device") 
#print (finalID)
#
#Kp = 0.03999999910593033
#Kd = 0.03999999910593033
#Ki = 0.001500000013038516
#count = 0
#check=False
#while True: 
#    setpoint = randint(100,250)
#    x=random.rand(3)/2
#    Kp = Kp + Kp*x[0]
#    Ki = Ki + Ki*x[1]
#    Kd = Kd + Ki*x[2]
#    print (f"Current ID: {count}, Kp = {Kp}, Ki = {Ki}, Kd = {Kd}, setpoint: {setpoint}")
#    
#    settlingTime =  cloud.receiveData(table="Device",id=1)["quality"]["settlingTime"]
#    
#    time.sleep(1)
#    
#    cloud.sendData(table="ML",
#                   id=1, currentID=count , name="Motor_1",
#                   online=True, 
#                   kp=Kp,ki=Ki,kd=Kd,
#                   movePara=True,moveToPos=False,stop=False, autoTune=False,
#                   setpoint=setpoint)
#    print ("---------------send step 1---------------")
#    time.sleep(2)
#
#    cloud.sendData(table="ML",
#                   id=1, currentID=count , name="Motor_1",
#                   online=True, 
#                   kp=Kp,ki=Ki,kd=Kd,
#                   movePara=False,moveToPos=False,stop=False, autoTune=False,
#                   setpoint=setpoint)
#    
#    time.sleep(2)
#
#    print ("---------------send step 2---------------")
#    time.sleep(2)
#    if setpoint >= 266 : 
#        setpoint = 126
#
#    
#    while check == False: 
#        dataDevice =  cloud.receiveData(table="Device",id=1)
#        
#        idDevice = int(dataDevice["currentID"]) 
#        settlingDevice = dataDevice["quality"]["settlingTime"]
#        print (f"---------------check currentID=={count} and settling time != {settlingTime} step 3---------------")
#        print ( idDevice, settlingDevice )
#        if  settlingDevice != settlingTime : 
#            check == True 
#            print ("---------------step 3 is OK---------------")
#            time.sleep(1)
#
#            cloud.sendData(table="ML",
#                           id=1, currentID=count , name="Motor_1",
#                           online=True, 
#                           kp=Kp,ki=Ki,kd=Kd,
#                           movePara=False,moveToPos=False,stop=False, autoTune=False,
#                           setpoint=setpoint)
#            count +=1 
#            break 
#    print ( f"Done {count}" )
