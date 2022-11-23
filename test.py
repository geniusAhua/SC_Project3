import time 

def main():
    command_name = ['truck/speed', 'truck/proximity', 'truck/light-on', 'truck/wiper-on', 'truck/passengers-count', 'truck/fuel', 'truck/engine-temperature',
                    'bike/speed', 'bike/proximity', 'bike/light-on', 'bike/wiper-on', 'bike/passengers-count', 'bike/fuel', 'bike/engine-temperature']

    while True:
        for c in command_name:
            print('Press enter to send next interest packet')
            input()
            print(c)
            # print('\n')
        time.sleep(20)

if __name__ == '__main__':
    main()
