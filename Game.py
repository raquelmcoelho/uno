from threading import *
from Partida import *
from socket import *

Uno = socket(AF_INET, SOCK_STREAM)
Uno.bind(("26.52.80.182", 9997))
Uno.listen()

print("\033[40m{}".format(""))


def sala_de_espera(cliente, index, sala):
    global clientes, permissao

    mandar(cliente, f"""Seja Bem Vindo ao UNO ONLINE\nSala {sala}\nqual seu nickname? """)
    nick = receber(cliente)
    print(nick, " é o nome do jogador ", index)
    clientes[index].append(nick)
    mandar(cliente, "Clique enter para iniciar a partida, se quiser sair digite q:")
    resposta = receber(cliente)

    if resposta != "q":
        permissao.append("ok")
        game(cliente)

    else:
        sair(cliente)
        cliente.close()
        clientes.pop(index)
        broadcast(clientes, f"{nick} saiu")


def game(cliente):
    global clientes, permissao, qtdsalas
    if len(clientes) < 2 or len(permissao) != len(clientes):
        mandar(cliente, "Esperando a confirmação de todos os jogadores para iniciar")
    else:
        qtdsalas += 1
        mandar(cliente, "Você iniciou a partida")
        txt = "A partida foi iniciada, e estes serão os jogadores:\n"
        for client in clientes:
            txt += f"{client[1]}\n"
        broadcast(clientes, txt)
        players = clientes.copy()
        clientes.clear()
        permissao.clear()
        Partida(players)


print("servidor aberto")
qtdsalas = 0
clientes = []
permissao = []
while True:
    clientesocket, adrr = Uno.accept()
    print("Conectado a jogador ", len(clientes))
    if len(clientes) > 6:
        mandar(clientesocket, "SALA CHEIA")
        sair(clientesocket)
        clientesocket.close()

    else:
        t = Thread(target=sala_de_espera, args=(clientesocket, len(clientes), qtdsalas))
        clientes.append([clientesocket])
        t.start()
