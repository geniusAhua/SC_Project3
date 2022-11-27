import socket
import time
import base64
import random

ROUTER_IP = '10.35.70.28'
ROUTER_PORT = 33310

def bencode(toEncode):
    ascii_encoded = toEncode.encode("ascii")
    base64_bytes = base64.b64encode(ascii_encoded)
    base64_string = base64_bytes.decode("ascii")
    return base64_string

def bdecode(toDecode):
    base64_bytes = toDecode.encode("ascii")
    sample_string_bytes = base64.b64decode(base64_bytes)
    sample_string = sample_string_bytes.decode("ascii")
    return sample_string

vehicleStatus={}
vehicleStatus2={}
vehicleStatus3={}



#DESERT HEALTH CHECK USE CASE
def actuate(interest_packet, data_packet):
    

   # print("Data packet received: ", data_packet, ' for interest packet ', interest_packet)
 
       
   if interest_packet == 'truck/speed':
       vehicleStatus['vehicletype']=1
       feature = interest_packet.split("/")[1]
       vehicleStatus[feature]=int(data_packet)
       data_packet_int = int(data_packet)
       if data_packet_int > 40:
         print('WARNING: Truck approaching at speed ', data_packet ,' km/h Please slow down for vehicle health checkup before long run :)')
       else:
          print('Stop for Truck Health Checkup, Current Speed: ', data_packet)
            
   elif interest_packet == 'truck/proximity':
        feature = interest_packet.split("/")[1]
        vehicleStatus[feature]=int(data_packet)
        print('Truck is  ', data_packet ,'metres away from last garage/gas station')
        
   elif interest_packet == 'truck/pressure':
     feature = interest_packet.split("/")[1]
     vehicleStatus[feature]=int(data_packet)
     data_packet_int = int(data_packet)
     if data_packet_int < 125:
       print('WARNING: Truck tyre pressure is low ( ', data_packet,' psi) , get your tyre some air ----\n *STOP AT THE GARAGE(Truck)*:)')
     else:
       print ('Truck tyre pressure is in good condition')
            
   elif interest_packet == 'truck/light-on':
     feature = interest_packet.split("/")[1]
     if data_packet=='on':
       vehicleStatus[feature]=0
       print("Truck Light is on")
     elif data_packet=='off':
       vehicleStatus[feature]=1
       print("Truck Light is off")
     else:
       vehicleStatus[feature]=2
       print("WARNING: Truck Light is faulty")
          
          
   elif interest_packet == 'truck/wiper-on':
     feature = interest_packet.split("/")[1]
     if data_packet=='on':
       vehicleStatus[feature]=0
       print('Truck wiper is ', data_packet)
     elif data_packet=='off':
       vehicleStatus[feature]=1
       print('Truck wiper is ', data_packet)
     else:
       vehicleStatus[feature]=2
       print('WARNING: Truck wiper is ', data_packet)
            
        
   elif interest_packet == 'truck/passengers-count':
     feature = interest_packet.split("/")[1]
     vehicleStatus[feature]=int(data_packet)
     print('Truck is approaching with ', data_packet, ' number of passengers')
      
   elif interest_packet == 'truck/fuel':
     feature = interest_packet.split("/")[1]
     if data_packet=='low':
       vehicleStatus[feature]=0
       print('WARNING: this is the last gas station, Truck fuel level: ', data_packet.upper(),' Kindly refill your fuel tank')
     elif data_packet=='medium':
       vehicleStatus[feature]=1
       print('WARNING: this is the last gas station, Truck fuel level: ', data_packet.upper() ,' Kindly refill your fuel tank')
     else:
       vehicleStatus[feature]=2
       print('truck fuel is ',data_packet.upper(), ':Good to go')
        
   elif interest_packet == 'truck/engine-temperature':
     feature = interest_packet.split("/")[1]
     vehicleStatus[feature]=int(data_packet)
     data_packet_int=int(data_packet)
     if int(data_packet_int) > 200:
       print('WARNING: Truck engine is heating up, current engine temperature: ', data_packet,' degree Celcius, Please head towards garage(Truck) before long run :)')
     else:
       print('Truck engine teperature is normal')
#--------------------------------------------------------------------------------------------------------------------------
   elif interest_packet == 'car/speed':
       vehicleStatus2['vehicletype']=2
       feature = interest_packet.split("/")[1]
       vehicleStatus2[feature]=int(data_packet)
       data_packet_int = int(data_packet)
       if data_packet_int > 40:
         print('WARNING: Car approaching at speed ', data_packet ,' km/h Please slow down for vehicle health checkup before long run :)')
       else:
          print('Stop for Car Health Checkup, Current Speed: ', data_packet)
            
   elif interest_packet == 'car/proximity':
       feature = interest_packet.split("/")[1]
       vehicleStatus2[feature]=int(data_packet)
       print('Car is ', data_packet ,' metres away from last garage/gas station')
        
   elif interest_packet == 'car/pressure':
      feature = interest_packet.split("/")[1]
      vehicleStatus2[feature]=int(data_packet)
      data_packet_int = int(data_packet)
      if data_packet_int < 32:
        print('WARNING: Car tyre pressure is LOW ( ', data_packet,' psi) , get your tyre some air ----\n *STOP AT THE GARAGE(Car)*:)')
      else:
        print ('Car tyre pressure is in good condition')
        
   elif interest_packet == 'car/light-on':
     feature = interest_packet.split("/")[1]
     if data_packet=='on':
       vehicleStatus2[feature]=0
       print("Car Light is on")
     elif data_packet=='off':
       vehicleStatus2[feature]=1
       print("Car Light is off")
     else:
       vehicleStatus2[feature]=2
       print("WARNING: Car Light is faulty")
          
             
   elif interest_packet == 'car/wiper-on':
     feature = interest_packet.split("/")[1]
     if data_packet=='on':
       vehicleStatus2[feature]=0
       print('Car wiper is ', data_packet)
     elif data_packet=='off':
       vehicleStatus2[feature]=1
       print('Car wiper is ', data_packet)
     else:
       vehicleStatus2[feature]=2
       print('WARNING: Car wiper is ', data_packet)
        
   elif interest_packet == 'car/passengers-count':
     feature = interest_packet.split("/")[1]
     vehicleStatus2[feature]=int(data_packet)
     print('Car is approaching with ', data_packet, ' number of passengers')
        
   elif interest_packet == 'car/fuel':
     feature = interest_packet.split("/")[1]
     if data_packet=='low':
       vehicleStatus2[feature]=0
       print('WARNING: this is the last gas station, Car fuel level: ', data_packet.upper(),' Kindly refill your fuel tank')
     elif data_packet=='medium':
       vehicleStatus2[feature]=1
       print('WARNING: this is the last gas station, Car fuel level: ', data_packet.upper() ,' Kindly refill your fuel tank')
     else:
       vehicleStatus2[feature]=2
       print('Car fuel is ',data_packet.upper(), ':Good to go')
        
   elif interest_packet == 'car/engine-temperature':
       feature = interest_packet.split("/")[1]
       vehicleStatus2[feature]=int(data_packet)
       data_packet_int=int(data_packet)
       if data_packet_int > 200:
        print('WARNING: Car engine is heating up, current engine temperature: ', data_packet,'degree Celcius, Please head towards garage(Car) before long run :)')
       else:
        print('Car engine temperature is normal:',data_packet_int,' degree celcius')

#--------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------

   elif interest_packet == 'bike/speed':
       vehicleStatus3['vehicletype']=3
       feature = interest_packet.split("/")[1]
       vehicleStatus3[feature]=int(data_packet)
       data_packet_int = int(data_packet)
       if data_packet_int > 40:
         print('WARNING: Bike approaching at speed ', data_packet ,' km/h Please slow down for vehicle health checkup before long run :)')
       else:
          print('Stop for Bike Health Checkup, Current Speed: ', data_packet)
            
   elif interest_packet == 'bike/proximity':
       feature = interest_packet.split("/")[1]
       vehicleStatus3[feature]=int(data_packet)
       print('Bike is ', data_packet ,' metres away from last garage/gas station')
        
   elif interest_packet == 'bike/pressure':
      feature = interest_packet.split("/")[1]
      vehicleStatus3[feature]=int(data_packet)
      data_packet_int = int(data_packet)
      if data_packet_int < 105:
        print('WARNING: Bike tyre pressure is LOW (', data_packet,' psi) , get your tyre some air ----\n *STOP AT THE GARAGE(Bike)*:)')
      else:
        print ('Bike tyre pressure is in good condition')
        
   elif interest_packet == 'bike/light-on':
     feature = interest_packet.split("/")[1]
     if data_packet=='on':
       vehicleStatus3[feature]=0
       print("Bike Light is on")
     elif data_packet=='off':
       vehicleStatus3[feature]=1
       print("Bike Light is off")
     else:
       vehicleStatus3[feature]=2
       print("WARNING: Bike Light is faulty")
          
             
   elif interest_packet == 'bike/wiper-on':
     feature = interest_packet.split("/")[1]
     if data_packet=='on':
       vehicleStatus3[feature]=0
       print('Bike wiper is ', data_packet)
     elif data_packet=='off':
       vehicleStatus3[feature]=1
       print('Bike wiper is ', data_packet)
     else:
       vehicleStatus3[feature]=2
       print('WARNING: Bike wiper is ', data_packet)
        
   elif interest_packet == 'bike/passengers-count':
     feature = interest_packet.split("/")[1]
     vehicleStatus3[feature]=int(data_packet)
     print('Bike is approaching with ', data_packet, ' number of passengers')
        
   elif interest_packet == 'bike/fuel':
     feature = interest_packet.split("/")[1]
     if data_packet=='low':
       vehicleStatus3[feature]=0
       print('WARNING: this is the last gas station, Bike fuel level: ', data_packet.upper(),' Kindly refill your fuel tank')
     elif data_packet=='medium':
       vehicleStatus3[feature]=1
       print('WARNING: this is the last gas station, Bike fuel level: ', data_packet.upper() ,' Kindly refill your fuel tank')
     else:
       vehicleStatus3[feature]=2
       print('Bike fuel is ',data_packet.upper(), ':Good to go')
        
   elif interest_packet == 'bike/engine-temperature':
       feature = interest_packet.split("/")[1]
       vehicleStatus3[feature]=int(data_packet)
       data_packet_int=int(data_packet)
       if data_packet_int > 200:
        print('WARNING: Bike engine is heating up, current engine temperature: ', data_packet,'degree Celcius, Please head towards garage(Bike) before long run :)')
       else:
        print('Bike engine temperature is normal:',data_packet_int,' degree celcius')

#--------------------------------------------------------------------------------------------------------------------------------------

def sendInterest(interest):
        routers = {(ROUTER_IP, ROUTER_PORT)}
        print('attempting to send interest packet: ', interest)
                
        for router in routers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(router)
                base64encoded = str(bencode(interest))
                s.send(base64encoded.encode())
                ack = s.recv(1024)
                print("WELCOME TO SAHARA DESSERT HIGHWAY,NO GARAGE/FUEL STATION FOR NEXT 150 KM \n ---------------------------------- \n VEHICLE HEALTH CHECKUP REPORT")
                actuate(interest, bdecode(ack.decode('utf-8')))
                s.close()
            except Exception:
                print("An exception occured")

def main():
    truck_interest_packets = ['truck/speed', 'interest/corrupted', 'truck/proximity', 'truck/pressure', 'truck/light-on', 'truck/wiper-on', 'truck/passengers-count', 'truck/fuel', 'truck/engine-temperature']
    bike_interest_packets = ['bike/speed', 'interest/corrupted', 'bike/proximity', 'bike/pressure', 'bike/light-on', 'bike/wiper-on', 'bike/passengers-count', 'bike/fuel', 'bike/engine-temperature']
    car_interest_packets = ['car/speed', 'interest/corrupted', 'car/proximity', 'car/pressure', 'car/light-on', 'car/wiper-on', 'car/passengers-count', 'car/fuel', 'car/engine-temperature']
    
    while True:
        print('\n')
        print('Press 1 to send truck interest packets')
        print('Press 2 to send car interest packets')
        print('Press 3 to send bike interest packets\n')
        val = input()

        if val == '1':
            for c in truck_interest_packets:
                print('press 1 to send next packet, press 2 to change vehicle type')
                inp = input()
                if inp != '1':
                    break
                sendInterest(c)
                print(vehicleStatus)
                print('\n')
        elif val == '2':
            for c in car_interest_packets:
                print('press 1 to send next packet, press 2 to change vehicle type')
                inp = input()
                if inp != '1':
                    break
                sendInterest(c)
                print(vehicleStatus2)
                print('\n')
        elif val == '3':
            for c in bike_interest_packets:
                print('press 1 to send next packet, press 2 to change vehicle type')
                inp = input()
                if inp != '1':
                    break
                sendInterest(c)
                print(vehicleStatus3)
                print('\n')

if __name__ == '__main__':
    main()

