from socket import *
import pickle
from threading import *

player = socket(AF_INET, SOCK_STREAM)
player.connect(("26.52.80.182", 9997))


lock = Lock()
print("\033[40m{}".format(""))


def mutar():
    global lock
    lock.acquire()
    print("ESPERE A VEZ DO OUTRO JOGADOR E NÃO DIGITE NADA")
    while True:
        msg = pickle.loads(player.recv(4096))
        if msg[0] == 1:
            print(msg[1])
        elif msg[0] == 2:
            player.send(pickle.dumps(input()))
            break
        elif msg[0] == 3:
            print("ESPERE A VEZ DO OUTRO JOGADOR E NÃO DIGITE NADA")
        elif msg[0] == 0:
            player.close()

    lock.release()


def handle_request(req):
    if req[0] == 1:
        print(req[1])

    elif req[0] == 2:
        player.send(pickle.dumps(input()))


while True:
    request = pickle.loads(player.recv(4096))

    if request[0] == 0:
        player.close()
        print("Foi bom tê-lo conosco ☺")
        break

    elif request[0] == 3:
        t2 = Thread(target=mutar())
        t2.start()
        t2.join()

    t = Thread(target=handle_request(request))
    t.start()
