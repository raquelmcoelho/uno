import pickle
import time

linha = f"{ 120 * '-'}"


# funcoes auxiliares do socket
def sair(client):
    time.sleep(0.2)
    client.send(pickle.dumps([0]))


def mandar(client, txt):
    time.sleep(0.2)
    client.sendall(pickle.dumps([1, linha + "\n" + str(txt) + "\n" + linha]))


def receber(client):
    time.sleep(0.2)
    client.send(pickle.dumps([2]))
    return pickle.loads(client.recv(4096))


def broadcast(clients, conteudo):
    for client in clients:
        mandar(client[0], conteudo)


def lock_players(clients):
    for client in clients:
        time.sleep(0.2)
        client[0].send(pickle.dumps([3]))
