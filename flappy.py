import pygame #pip install pygame
import os
import random
import neat #pip install neat-python

TELA_LARGURA = 500
TELA_ALTURA = 800

ia_jogando = True
geracao = 0

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_imgs = os.path.join(diretorio_atual, 'imgs')

IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join(caminho_imgs, 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join(caminho_imgs, 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join(caminho_imgs, 'bg.png')))
IMAGENS_PASSARO = [pygame.transform.scale2x(pygame.image.load(os.path.join(caminho_imgs, 'bird1.png'))),
                pygame.transform.scale2x(pygame.image.load(os.path.join(caminho_imgs, 'bird2.png'))),
                pygame.transform.scale2x(pygame.image.load(os.path.join(caminho_imgs, 'bird3.png')))]

pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('Arial', 25)


class Passaro:
    IMGS = IMAGENS_PASSARO

    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    def __init__ (self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo
        #Restringir deslocamento
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= -2

        self.y += deslocamento

        #Ângulo do pássaro

        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -=self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
            #Definir a imagem que vai utilizar
            self.contagem_imagem += 1

            if self.contagem_imagem < self.TEMPO_ANIMACAO:
                self.imagem = self.IMGS[0]
            elif self.contagem_imagem < self.TEMPO_ANIMACAO*2:
                self.imagem = self.IMGS[1]
            elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
                self.imagem = self.IMGS[2]
            elif self.contagem_imagem < self.TEMPO_ANIMACAO*4:
                self.imagem = self.IMGS[1]
            elif self.contagem_imagem < self.TEMPO_ANIMACAO*5:
                self.imagem = self.IMGS[0]

                self.contagem_imagem = 0

            #Próximo passo: queda do pássaro

            if self.angulo <= -80:
                self.imagem = self.IMGS[1]
                self.contagem_imagem = self.TEMPO_ANIMACAO*2

            imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
            pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
            retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
            tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)

class Cano:
    #Distância entre o cano de cima e o cano debaixo
    DISTANCIA = 200
    VELOCIDADE = 5
    VELOCIDADE_VERTICAL = 2
    subindo = True

    def __init__ (self, x):
        self.x = x
        self.altura = 0
        self.pos_top = 0
        self.pos_base = 0
        #Não flipa em relação ao x, apenas ao y
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50,450)
        self.pos_base = self.altura + self.DISTANCIA
        self.pos_top = self.altura - self.CANO_TOPO.get_height()

    def mover(self):
        self.x -= self.VELOCIDADE

        if self.subindo:
            self.altura -= self.VELOCIDADE_VERTICAL
            if self.altura < 50:
                self.subindo = False
        else:
            self.altura += self.VELOCIDADE_VERTICAL
            if self.altura > 450:
                self.subindo = True
        self.pos_top = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_top))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, Passaro):
        passaro_mask = Passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - Passaro.x, self.pos_top - round(Passaro.y))
        distancia_base = (self.x - Passaro.x, self.pos_base - round(Passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False

class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()
    imagem = IMAGEM_CHAO

    def __init__ (self, y):
        self.y = y
        self.x0 = 0
        self.x1 = self.LARGURA

    def mover(self):
        self.x0 -= self.VELOCIDADE
        self.x1 -= self.VELOCIDADE

        if self.x0 + self.LARGURA < 0:
            self.x0 = self.x1 + self.LARGURA
        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x0 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.imagem, (self.x0, self.y))
        tela.blit(self.imagem, (self.x1, self.y))

#Vários pássaros na IA, guardaremos o melhor resultado e executamos novamente

def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))

    for passaro in passaros:
        passaro.desenhar(tela)
    
    for cano in canos:
        cano.desenhar(tela)

    chao.desenhar(tela)

    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))

    if ia_jogando:
        texto = FONTE_PONTOS.render(f"Geração: {geracao}", 1, (255, 255, 255))
        tela.blit(texto, (10,10))

    pygame.display.update()

def main(genomas, config):
    global geracao
    geracao += 1

    if ia_jogando:
        redes = []
        lista_genoma = []
        passaros = []

        for _, genoma in genomas:
            rede = neat.nn.FeedForwardNetwork.create(genoma,config)
            redes.append(rede)
            genoma.fitness = 0
            lista_genoma.append(genoma)
            passaros.append(Passaro(230,250))
    else:
        passaros = [Passaro(230,250)]


    chao = Chao(730)
    canos = [Cano(700)]

    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0

    relogio = pygame.time.Clock()

    rodando = True
    while rodando:
        relogio.tick(70) #Define o tick do game

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if not ia_jogando: #Caso a IA não esteja rodando
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        for passaro in passaros:
                            passaro.pular()

        indice_cano = 0
        if len(passaros) > 0:
            if len(canos) > 1 and passaros[0].x > (canos[0].x + canos[0].CANO_TOPO.get_width()):
                indice_cano = 1
        else:
            rodando = False
            break

        for i, passaro in enumerate(passaros):
            passaro.mover()
            lista_genoma[i].fitness += 0.1 #Cada vez que o pássaro se mover, ele ganha um bônus de 0.1 (treat)
            output = redes[i].activate((passaro.y,
                                        abs(passaro.y - canos [indice_cano].altura),
                                        abs(passaro.y - canos[indice_cano].pos_base)))
            if output[0] > 0.5:
                passaro.pular()

        chao.mover()

        adicionar_canos = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)
                    if ia_jogando:
                        lista_genoma[i].fitness -= 1
                        lista_genoma.pop()
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_canos = True
            cano.mover()

            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_canos:
            pontos += 1
            for genoma in lista_genoma:
                genoma.fitness += 5
            canos.append(Cano(600))

        for cano in remover_canos:
            canos.remove(cano)

        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)
                if ia_jogando:
                        lista_genoma.pop()
                        redes.pop(i)

        desenhar_tela(tela, passaros, canos, chao, pontos)

def rodar(caminho_config):
    config = neat.config.Config(
                        neat.DefaultGenome,
                        neat.DefaultReproduction,
                        neat.DefaultSpeciesSet,
                        neat.DefaultStagnation,
                        caminho_config
                    )
    populacao = neat.Population(config)

    if ia_jogando:
        populacao.run(main, 50)
    else:
        main(None, None)

if __name__ == '__main__':
    caminho_config =  "config.txt"
    rodar(caminho_config)