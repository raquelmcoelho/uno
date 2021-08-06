from SocketFunctions import *
from Baralho import *
from Estado import *


class Partida:
    salas = 0

    def __init__(self, idjogadores):
        # each player: [socket, nick, cards]
        self.jogadores = idjogadores
        self.baralho = Baralho()
        self.pilha_puxar = self.distribuir()
        self.pilha_jogar = []
        self.vez = 0
        self.estado = Estado.parado
        self.cor_carta_cima = ""
        self.puxar_acumuladas = 0
        self.idsala = Partida.salas
        Partida.salas += 1
        self.iniciar()

    @staticmethod
    def pick_card(player):
        jogada = None

        while not jogada:
            try:
                jogada = player[2][int(receber(player[0])) - 1]
                color_jogada = jogada[0]
                conteudo_jogada = jogada[1]
                return jogada, color_jogada, conteudo_jogada

            except ValueError:
                mandar(player[0], "Posição inválida, digite números")

            except IndexError:
                mandar(player[0], "Número não existente dentre suas cartas")

    @staticmethod
    def colorir_carta(carta):
        # vermelho, amarelo, azul, verde, preto
        cores_format = [91, 93, 94, 92, 97]
        cor_correspondente = CardColor[carta[0]].value
        return "\033[{}m {}  \033[97m {}".format(cores_format[cor_correspondente], carta[0], carta[1])

    def print_cartas(self, cards):
        txt = ""
        for n, card in enumerate(cards):
            txt += f"{n+1} - {self.colorir_carta(card)}\n"

        return txt

    def set_cor(self, socket):
        mandar(socket, "A carta é preta então escolha a cor, digite o nome em maiúsculo")
        cor_escolhida = receber(socket)

        while cor_escolhida not in ["GREEN", "YELLOW", "RED", "BLUE"]:
            mandar(socket, "cor inválida")
            cor_escolhida = receber(socket)

        else:
            self.cor_carta_cima = cor_escolhida

    def distribuir(self):
        cartas_por_jogador, resto = self.baralho.dividir(len(self.jogadores))

        for num, jogador in enumerate(self.jogadores):
            jogador.append(cartas_por_jogador[num])
            mandar(jogador[0], "Essas são suas cartas\n" + self.print_cartas(jogador[2]))

        return resto

    def iniciar(self):
        self.estado = Estado.playing

        # por a primeira carta na roda
        self.puxar(self.pilha_jogar, 1)

        if self.pilha_jogar[-1][0] != "BLACK":
            self.cor_carta_cima = self.pilha_jogar[-1][0]

        else:
            socket_primeiro_jogador = self.checar_vez()[0]
            self.set_cor(socket_primeiro_jogador)

        # não acabar até alguém ganhar
        while self.estado != Estado.ganhou:
            self.jogada()

        # fechar clientes
        for client in self.jogadores:
            mandar(client[0], "aperte enter para sair")
            receber(client[0])
            sair(client[0])

    def puxar(self, who, num):
        # se vazia, mistura as duas pilhas embaralha e continua o jogo
        if len(self.pilha_puxar) == 0:
            broadcast(self.jogadores, "Pilha de puxar acabou, vou embaralhar todo o baralho novamente")

            ultima_carta = self.pilha_jogar.pop(-1)  # salvar para depois
            self.pilha_puxar += self.pilha_jogar
            random.shuffle(self.pilha_puxar)
            self.pilha_jogar.clear()
            self.pilha_jogar.append(ultima_carta)

        # puxar num vezes
        for i in range(num):
            who.append(self.pilha_puxar.pop(-1))

    def atualizar_player(self, player):
        for jogador in self.jogadores:
            if jogador[0] == player[0]:
                index = self.jogadores.index(jogador)
                self.jogadores.pop(index)
                self.jogadores.insert(index, player)

    def jogar(self, player, carta):
        self.pilha_jogar.append(carta)
        player[2].remove(carta)       # remove das cartas dele
        self.atualizar_player(player)
        if carta[0] != "BLACK":
            self.cor_carta_cima = carta[0]
        self.vez += 1

    def checar_vez(self):
        return self.jogadores[self.vez % len(self.jogadores)]

    def check_state(self, player_cards, color, conteudo):
        # checar se ganhou
        if not player_cards:
            self.estado = Estado.ganhou

        else:
            # checar se travou
            for card in player_cards:
                if card[0] == color or card[1] == conteudo or card[0] == "BLACK":
                    self.estado = Estado.playing
                    return 0
                else:
                    self.estado = Estado.travado
            return 0

    def puxar_tudo(self, puxar_comeco, player):
        # checar se rebateu as cartas de puxar
        if puxar_comeco == self.puxar_acumuladas and self.puxar_acumuladas != 0:
            mandar(player[0], "Já que você não rebateu os puxar cartas, agora terá que puxar :(")
            self.puxar(player[2], self.puxar_acumuladas)
            self.puxar_acumuladas = 0
            mandar(player[0], f"Suas cartas agora estão assim \n{self.print_cartas(player[2])}")

    def jogada(self):

        player = self.checar_vez()    # Player[socket, name, cards]
        socket = player[0]
        name = player[1]
        other_players = self.jogadores.copy()
        other_players.remove(player)
        carta_de_cima = self.pilha_jogar[-1]
        color = self.cor_carta_cima
        conteudo = carta_de_cima[1]
        puxar_comeco = self.puxar_acumuladas

        mandar(socket, "É a sua vez e essas são suas Cartas\n" + self.print_cartas(player[2]))
        broadcast(self.jogadores, f"A carta do meio é:\n " + self.colorir_carta([color, conteudo]))
        broadcast(other_players, f"é a vez de {name}")
        lock_players(other_players)

        # checar se ta travado
        for tentativa in range(2):
            self.check_state(player[2], color, conteudo)
            if self.estado == Estado.playing:
                break
            else:
                if tentativa == 1:
                    self.puxar_tudo(puxar_comeco, player)
                    broadcast(other_players, f"{name} foi pulado a vez")
                    mandar(socket, "Infelizmente você foi pulada a vez")
                    self.vez += 1
                    return 0

                self.puxar(player[2], 1)
                mandar(socket, "Você tem que puxar :((")
                mandar(socket, "Suas cartas agora estão assim\n" + self.print_cartas(player[2]))
                broadcast(other_players, f"O {name} puxou uma carta")

        # jogar
        print("\n-----------------------------------------"
              + f"\n     INFORMAÇÕES SALA {self.idsala}"
              + f"\ncarta_de_cima : {self.colorir_carta(carta_de_cima)}"
              + f"\ncolor : {self.colorir_carta([color, ''])}"
              + f"\nestado : {self.estado}"
              + "\n-----------------------------------------")

        mandar(socket, "Digite a posição da sua carta (número sem vírgula e letras)")
        jogada, color_jogada, conteudo_jogada = self.pick_card(player)

        if color_jogada != "BLACK":

            # checar jogada
            while color_jogada != color and conteudo_jogada != conteudo:
                mandar(socket, "carta inválida tente novamente")
                jogada, color_jogada, conteudo_jogada = self.pick_card(player)
            else:

                if conteudo_jogada == "plustwo":
                    self.puxar_acumuladas += 2
                    broadcast(self.jogadores, f"O próximo jogador deverá puxar {self.puxar_acumuladas} cartas")

                elif conteudo_jogada == "block":
                    broadcast(self.jogadores, f"O próximo jogador foi bloqueado pelo {name}")
                    self.vez += 1

                elif conteudo_jogada == "revert":
                    broadcast(self.jogadores, f"O jogador {name} reverteu o jogo")
                    posicao = int((self.vez % len(self.jogadores)))
                    print("posicao, vez, len", posicao, self.vez, len(self.jogadores))
                    substituto = []
                    for i in range(len(self.jogadores)):
                        substituto.append(self.jogadores[posicao - 1])
                        print("substituto", substituto)
                        posicao -= 1
                    self.jogadores.clear()
                    self.jogadores = substituto
                    print("agora os jogador tão assim oh", self.jogadores)
                    self.vez = -1

        else:
            self.set_cor(socket)
            broadcast(self.jogadores, f"{name} ESCOLHEU A COR {self.colorir_carta([self.cor_carta_cima, ''])}")

            if conteudo_jogada == "plusfour":
                self.puxar_acumuladas += 4
                broadcast(self.jogadores, f"O próximo jogador deverá puxar {self.puxar_acumuladas} cartas")

        self.jogar(player, jogada)

        # checar se rebateu as cartas de puxar
        self.puxar_tudo(puxar_comeco, player)

        # checar se ganhou
        self.check_state(player[2], color, conteudo)
        if self.estado == Estado.ganhou:
            print(f"SALA {self.idsala} FINALIZADA")
            broadcast(self.jogadores, f"Jogador(a) {name} ganhou!!!")
