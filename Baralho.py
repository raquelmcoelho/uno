import random
from Card import *


# criando baralho
BARALHO = []
for cor in range(4):
    for content in range(13):
        BARALHO.append(Carta(CardColor(cor), CardContent(content)).__str__())

for black_content in range(13, 15):
    BARALHO.append(Carta(CardColor(4), CardContent(black_content)).__str__())
    BARALHO.append(Carta(CardColor(4), CardContent(black_content)).__str__())


class Baralho:
    def __init__(self):
        self.baralho = self._embaralhar()

    @staticmethod
    def _embaralhar():
        embaralhado = 2 * BARALHO.copy()
        random.shuffle(embaralhado)
        # embaralhado.reverse()
        return embaralhado

    def dividir(self, qtd_players):
        cartas_por_jogador = []
        inicio = 0
        qtd = 7
        for _ in range(qtd_players):
            cartas_por_jogador.append(self.baralho[inicio:inicio+qtd])
            inicio += qtd
        resto = self.baralho[inicio:-1]
        return cartas_por_jogador, resto
