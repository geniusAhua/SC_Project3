truck_interest_packets = ['truck/speed', 'truck/proximity', 'truck/light-on', 'truck/wiper-on', 'truck/passengers-count', 'truck/fuel', 'truck/engine-temperature']
bike_interest_packets = ['bike/speed', 'bike/proximity', 'bike/light-on', 'bike/wiper-on', 'bike/passengers-count', 'bike/fuel', 'bike/engine-temperature']
car_interest_packets = ['car/speed', 'car/proximity', 'car/light-on', 'car/wiper-on', 'car/passengers-count', 'car/fuel', 'car/engine-temperature']
    
while True:
        print('\n')
        print('Press 1 to send truck interest packets')
        print('Press 2 to send bike interest packets')
        print('Press 3 to send car interest packets\n')
        val = input()

        if val == '1':
            for c in truck_interest_packets:
                print('press 1 to send next packet, press 2 to change vehicle type')
                inp = input()
                if inp != '1':
                    break
                print(c)
                print('\n')
        elif val == '2':
            for c in bike_interest_packets:
                print('press 1 to send next packet, press 2 to change vehicle type')
                inp = input()
                if inp != '1':
                    break
                print(c)
                print('\n')
        elif val == '3':
            for c in car_interest_packets:
                print('press 1 to send next packet, press 2 to change vehicle type')
                inp = input()
                if inp != '1':
                    break
                print(c)
                print('\n')
