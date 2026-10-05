"""
Entrega 2 — analise sintatica.

Transformar a lista de tokens numa arvore.

Sugestao forte: descida recursiva, uma funcao por nivel de precedencia, na
ordem da secao 3.3 da especificacao. E como voces vao enxergar a precedencia
virar formato de arvore.

Gerador de parser (ANTLR, PLY, yacc) esta proibido nesta entrega e na
anterior — o objetivo e entender, e o gerador esconde exatamente a parte
que esta sendo ensinada.

Leiam antes: LINGUAGEM.md secoes 3 a 5, e CONTRATOS.md secao 3.
"""
from mplc.erros import ErroMPL


class No:
    """Um no da arvore. O rotulo e o que sai no --ast."""

    def __init__(self, rotulo, filhos=None, linha=0, coluna=0, **extra):
        self.rotulo = rotulo      # 'binario +', 'literal inteiro 1', 'bloco', ...
        self.filhos = filhos or []
        self.linha = linha
        self.coluna = coluna
        self.extra = extra        # o que a semantica quiser pendurar depois


TIPOS = ('TIPO_INTEIRO', 'TIPO_REAL', 'TIPO_LOGICO', 'TIPO_TEXTO')
LITERAIS = {'INTEIRO': 'inteiro', 'REAL': 'real', 'LOGICO': 'logico', 'TEXTO': 'texto'}


def analisar(tokens):
    """Recebe a lista de Token. Devolve a raiz da arvore (um No 'programa')."""
    return Parser(tokens).programa()


class Parser:
    """Descida recursiva: um metodo por regra da gramatica (README, Entrega 2)."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0          # indice do token atual; nunca passa do FIM_ARQUIVO

    # ---- ferramentas -------------------------------------------------------

    def atual(self):
        return self.tokens[self.i]

    def seguinte(self):
        return self.tokens[self.i + 1]

    def aceitar(self, tipo):
        """Consome o token atual se ele for do tipo pedido."""
        if self.atual().tipo == tipo:
            self.i += 1
            return True
        return False

    def esperar(self, tipo, o_que):
        """Consome e devolve o token atual. Se nao for do tipo pedido, e erro nele."""
        tok = self.atual()
        if tok.tipo != tipo:
            self.erro(o_que)
        self.i += 1
        return tok

    def erro(self, o_que):
        # O erro fica no token que apareceu, nao no fim do anterior (CONTRATOS.md 7).
        tok = self.atual()
        veio = 'o fim do arquivo' if tok.tipo == 'FIM_ARQUIVO' else repr(tok.lexema)
        raise ErroMPL('sintatico', tok.linha, tok.coluna, f'esperava {o_que}, mas veio {veio}')

    def tipo(self, o_que, aceita_vazio=False):
        tok = self.atual()
        if tok.tipo in TIPOS or (aceita_vazio and tok.tipo == 'TIPO_VAZIO'):
            self.i += 1
            return tok.lexema
        self.erro(o_que)

    # ---- programa, funcao, bloco -------------------------------------------

    def programa(self):
        funcoes = []
        while self.atual().tipo != 'FIM_ARQUIVO':
            funcoes.append(self.funcao())
        return No('programa', funcoes, 1, 1)

    def funcao(self):
        self.esperar('FUNCAO', "'funcao'")
        tipo = self.tipo('o tipo de retorno', aceita_vazio=True)
        nome = self.esperar('ID', 'o nome da funcao')
        self.esperar('ABRE_PAR', "'('")
        parametros = []
        if self.atual().tipo != 'FECHA_PAR':
            parametros.append(self.parametro())
            while self.aceitar('VIRGULA'):
                parametros.append(self.parametro())
        self.esperar('FECHA_PAR', "')'")
        corpo = self.bloco()
        return No(f'funcao {nome.lexema} {tipo}', [No('parametros', parametros), corpo],
                  nome.linha, nome.coluna, nome=nome.lexema, tipo=tipo)

    def parametro(self):
        tipo = self.tipo('o tipo do parametro')
        nome = self.esperar('ID', 'o nome do parametro')
        return No(f'parametro {nome.lexema} {tipo}', [], nome.linha, nome.coluna,
                  nome=nome.lexema, tipo=tipo)

    def bloco(self):
        abre = self.esperar('ABRE_CHAVE', "'{'")
        comandos = []
        while self.atual().tipo not in ('FECHA_CHAVE', 'FIM_ARQUIVO'):
            comandos.append(self.comando())
        self.esperar('FECHA_CHAVE', "'}'")
        return No('bloco', comandos, abre.linha, abre.coluna)

    # ---- comandos ----------------------------------------------------------

    def comando(self):
        tok = self.atual()
        t = tok.tipo

        if t in TIPOS:
            tipo = self.tipo('um tipo')
            nome = self.esperar('ID', 'o nome da variavel')
            filhos = [self.expressao()] if self.aceitar('ATRIBUI') else []
            self.esperar('PONTO_VIRGULA', "';'")
            return No(f'declaracao {nome.lexema} {tipo}', filhos, nome.linha, nome.coluna,
                      nome=nome.lexema, tipo=tipo)

        if t == 'ID':
            if self.seguinte().tipo == 'ABRE_PAR':     # chamada usada como comando
                no = self.chamada()
                self.esperar('PONTO_VIRGULA', "';'")
                return no
            self.i += 1
            self.esperar('ATRIBUI', f"'=' ou '(' depois de '{tok.lexema}'")
            valor = self.expressao()
            self.esperar('PONTO_VIRGULA', "';'")
            return No(f'atribuicao {tok.lexema}', [valor], tok.linha, tok.coluna, nome=tok.lexema)

        if t == 'SE':
            self.i += 1
            filhos = [self.condicao(), self.bloco()]
            if self.aceitar('SENAO'):
                filhos.append(self.bloco())
            return No('se', filhos, tok.linha, tok.coluna)

        if t == 'ENQUANTO':
            self.i += 1
            return No('enquanto', [self.condicao(), self.bloco()], tok.linha, tok.coluna)

        if t == 'ESCREVA':
            self.i += 1
            self.esperar('ABRE_PAR', "'('")
            valor = self.expressao()
            self.esperar('FECHA_PAR', "')'")
            self.esperar('PONTO_VIRGULA', "';'")
            return No('escreva', [valor], tok.linha, tok.coluna)

        if t == 'RETORNE':
            self.i += 1
            filhos = [] if self.atual().tipo == 'PONTO_VIRGULA' else [self.expressao()]
            self.esperar('PONTO_VIRGULA', "';'")
            return No('retorne', filhos, tok.linha, tok.coluna)

        if t == 'ABRE_CHAVE':
            return self.bloco()

        self.erro('um comando')

    def condicao(self):
        self.esperar('ABRE_PAR', "'('")
        no = self.expressao()
        self.esperar('FECHA_PAR', "')'")
        return no

    # ---- expressoes: um metodo por nivel, do mais fraco para o mais forte --

    def expressao(self):
        return self.ou()

    def ou(self):
        return self.binario_esquerda(self.e, 'OU')

    def e(self):
        return self.binario_esquerda(self.igualdade, 'E')

    def igualdade(self):
        return self.binario_esquerda(self.relacional, 'IGUAL', 'DIFERENTE')

    def relacional(self):
        return self.binario_esquerda(self.aditiva, 'MENOR', 'MENOR_IGUAL', 'MAIOR', 'MAIOR_IGUAL')

    def aditiva(self):
        return self.binario_esquerda(self.multiplicativa, 'MAIS', 'MENOS')

    def multiplicativa(self):
        return self.binario_esquerda(self.unaria, 'VEZES', 'DIVIDE', 'RESTO')

    def binario_esquerda(self, proximo, *operadores):
        # Um laco, e nao recursao a direita: o no ja montado vira o filho da
        # esquerda do proximo. Assim 10 - 4 - 3 fica (10 - 4) - 3.
        no = proximo()
        while self.atual().tipo in operadores:
            op = self.atual()
            self.i += 1
            no = No(f'binario {op.lexema}', [no, proximo()], op.linha, op.coluna, op=op.lexema)
        return no

    def unaria(self):
        # Recursao a direita de proposito: nao e '- - x' fica - (- x).
        op = self.atual()
        if op.tipo in ('NAO', 'MENOS'):
            self.i += 1
            return No(f'unario {op.lexema}', [self.unaria()], op.linha, op.coluna, op=op.lexema)
        return self.primaria()

    def primaria(self):
        tok = self.atual()
        if tok.tipo in LITERAIS:
            self.i += 1
            tipo = LITERAIS[tok.tipo]
            if tipo == 'inteiro':
                valor = str(int(tok.lexema))
            elif tipo == 'real':
                valor = f'{float(tok.lexema):.6f}'
            else:
                valor = tok.lexema
            return No(f'literal {tipo} {valor}', [], tok.linha, tok.coluna, tipo=tipo)
        if tok.tipo == 'ID':
            if self.seguinte().tipo == 'ABRE_PAR':
                return self.chamada()
            self.i += 1
            return No(f'variavel {tok.lexema}', [], tok.linha, tok.coluna, nome=tok.lexema)
        if self.aceitar('ABRE_PAR'):
            no = self.expressao()
            self.esperar('FECHA_PAR', "')'")
            return no
        self.erro('uma expressao')

    def chamada(self):
        nome = self.esperar('ID', 'o nome da funcao')
        self.esperar('ABRE_PAR', "'('")
        argumentos = []
        if self.atual().tipo != 'FECHA_PAR':
            argumentos.append(self.expressao())
            while self.aceitar('VIRGULA'):
                argumentos.append(self.expressao())
        self.esperar('FECHA_PAR', "')'")
        return No(f'chamada {nome.lexema}', argumentos, nome.linha, nome.coluna, nome=nome.lexema)


def despejar(no, nivel=0, saida=None):
    """Imprime a arvore no formato do --ast. Ja esta pronto: dois espacos por nivel."""
    saida = saida if saida is not None else []
    saida.append('  ' * nivel + no.rotulo)
    for f in no.filhos:
        despejar(f, nivel + 1, saida)
    return saida
