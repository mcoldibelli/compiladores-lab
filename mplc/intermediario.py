"""
Entrega 4, primeira metade — codigo de tres enderecos.

A propriedade que define a representacao, e a unica que o verificador mede:
cada linha de operacao tem NO MAXIMO UM OPERADOR. Uma expressao como
a + b * c vira duas linhas, com um temporario no meio.

O formato do despejo e de voces. A propriedade nao e.

Leiam antes: CONTRATOS.md secao 5.
"""

# O valor de uma variavel declarada sem inicializar (LINGUAGEM.md 4.1).
PADRAO = {'inteiro': '0', 'real': '0.0', 'logico': 'falso', 'texto': '""'}


class Funcao:
    def __init__(self, nome, tipo):
        self.nome = nome
        self.tipo = tipo
        self.parametros = []    # (nome no codigo, tipo), na ordem
        # Cada instrucao e uma tupla (linha do fonte, tipo, argumentos...).
        # A linha e a do comando: e a que a VM relata num erro de execucao.
        self.instrucoes = []


def gerar(arvore, tabela):
    """Devolve o codigo de tres enderecos: uma lista de Funcao."""
    gerador = Gerador()
    return [gerador.funcao(f) for f in arvore.filhos]


def despejar(codigo):
    """Devolve as linhas do --ir."""
    linhas = []
    for f in codigo:
        parametros = ', '.join(f'{nome} {tipo}' for nome, tipo in f.parametros)
        linhas.append(f'funcao {f.nome} {f.tipo} ({parametros})')
        for _, tipo, *a in f.instrucoes:
            linhas.append(formatar(tipo, a))
        linhas.append('fim')
    return linhas


def formatar(tipo, a):
    if tipo == 'copia':
        return f'  {a[0]} = {a[1]}'
    if tipo == 'binaria':
        return f'  {a[0]} = {a[1]} {a[2]} {a[3]}'
    if tipo == 'unaria':
        return f'  {a[0]} = {a[1]} {a[2]}'
    if tipo == 'real':
        return f'  {a[0]} = real {a[1]}'
    if tipo == 'rotulo':
        return f'{a[0]}:'
    if tipo == 'desvie':
        return f'  desvie {a[0]}'
    if tipo == 'seFalso':
        return f'  seFalso {a[0]} desvie {a[1]}'
    if tipo == 'chama':
        destino = f'{a[0]} = ' if a[0] is not None else ''
        return f"  {destino}chama {a[1]} {', '.join(a[2])}".rstrip()
    if tipo == 'retorne':
        return '  retorne' + (f' {a[0]}' if a[0] is not None else '')
    if tipo == 'escreva':
        return f'  escreva {a[0]}'


class Gerador:
    def __init__(self):
        self.rotulos = 0        # contador global: os rotulos nao se repetem entre funcoes

    def funcao(self, no):
        self.f = Funcao(no.extra['nome'], no.extra['tipo'])
        self.nomes = {}         # Simbolo -> nome no codigo
        self.usados = set()
        self.temporarios = 0
        self.linha = no.linha
        for p in no.filhos[0].filhos:
            self.f.parametros.append((self.nome(p.extra['simbolo']), p.extra['tipo']))
        self.bloco(no.filhos[1])
        if self.f.tipo == 'vazio':
            self.linha = no.linha
            self.emitir('retorne', None)    # funcao vazio pode acabar sem 'retorne'
        return self.f

    # ---- ferramentas -------------------------------------------------------

    def emitir(self, tipo, *argumentos):
        self.f.instrucoes.append((self.linha, tipo, *argumentos))

    def temporario(self):
        # '$' nao existe num identificador da MPL, entao nao colide com variavel.
        t = f'$t{self.temporarios}'
        self.temporarios += 1
        return t

    def rotulo(self):
        r = f'L{self.rotulos}'
        self.rotulos += 1
        return r

    def nome(self, simbolo):
        """Um nome por variavel da funcao. O primeiro 'x' fica 'x'; um 'x' que
        sombreia outro vira 'x#2', 'x#3'. '#' tambem nao existe na MPL."""
        if simbolo not in self.nomes:
            nome, n = simbolo.nome, 1
            while nome in self.usados:
                n += 1
                nome = f'{simbolo.nome}#{n}'
            self.usados.add(nome)
            self.nomes[simbolo] = nome
        return self.nomes[simbolo]

    def converter(self, valor, de, para):
        """A unica conversao: inteiro vira real. Fica explicita no codigo."""
        if de == 'inteiro' and para == 'real':
            t = self.temporario()
            self.emitir('real', t, valor)
            return t
        return valor

    def valor(self, expressao, tipo_destino):
        """Gera a expressao e converte para o tipo de quem vai guardar o valor."""
        return self.converter(self.expressao(expressao), expressao.extra['tipo'], tipo_destino)

    # ---- comandos ----------------------------------------------------------

    def bloco(self, no):
        for c in no.filhos:
            self.comando(c)

    def comando(self, no):
        self.linha = no.linha
        tipo = no.rotulo.split()[0]

        if tipo == 'declaracao':
            # Sempre emite a copia: dentro de um enquanto, a declaracao
            # reinicia a variavel a cada volta.
            t = no.extra['tipo']
            valor = self.valor(no.filhos[0], t) if no.filhos else PADRAO[t]
            self.emitir('copia', self.nome(no.extra['simbolo']), valor)

        elif tipo == 'atribuicao':
            simbolo = no.extra['simbolo']
            self.emitir('copia', self.nome(simbolo), self.valor(no.filhos[0], simbolo.tipo))

        elif tipo == 'se':
            condicao = self.expressao(no.filhos[0])
            senao = self.rotulo()
            self.emitir('seFalso', condicao, senao)
            self.bloco(no.filhos[1])
            if len(no.filhos) == 3:
                fim = self.rotulo()
                self.emitir('desvie', fim)
                self.emitir('rotulo', senao)
                self.bloco(no.filhos[2])
                self.emitir('rotulo', fim)
            else:
                self.emitir('rotulo', senao)

        elif tipo == 'enquanto':
            inicio, fim = self.rotulo(), self.rotulo()
            self.emitir('rotulo', inicio)
            condicao = self.expressao(no.filhos[0])
            self.emitir('seFalso', condicao, fim)
            self.bloco(no.filhos[1])
            self.emitir('desvie', inicio)
            self.emitir('rotulo', fim)

        elif tipo == 'escreva':
            self.emitir('escreva', self.expressao(no.filhos[0]))

        elif tipo == 'retorne':
            valor = self.valor(no.filhos[0], self.f.tipo) if no.filhos else None
            self.emitir('retorne', valor)

        elif tipo == 'bloco':
            self.bloco(no)

        elif tipo == 'chamada':
            self.chamada(no)

    # ---- expressoes --------------------------------------------------------

    def expressao(self, no):
        """Gera o codigo da expressao. Devolve onde o valor ficou: um nome ou uma constante."""
        tipo = no.rotulo.split()[0]

        if tipo == 'literal':
            return no.extra['lexema']

        if tipo == 'variavel':
            return self.nome(no.extra['simbolo'])

        if tipo == 'chamada':
            return self.chamada(no)

        if tipo == 'unario':
            a = self.expressao(no.filhos[0])
            t = self.temporario()
            self.emitir('unaria', t, no.extra['op'], a)
            return t

        # binario: os dois lados sao sempre gerados, entao 'e' e 'ou' avaliam
        # os dois (sem curto-circuito, LINGUAGEM.md 3.2).
        esquerda, direita = no.filhos
        a = self.expressao(esquerda)
        b = self.expressao(direita)
        if 'real' in (esquerda.extra['tipo'], direita.extra['tipo']):
            a = self.converter(a, esquerda.extra['tipo'], 'real')
            b = self.converter(b, direita.extra['tipo'], 'real')
        t = self.temporario()
        self.emitir('binaria', t, a, no.extra['op'], b)
        return t

    def chamada(self, no):
        funcao = no.extra['simbolo']
        argumentos = [self.valor(a, tipo) for a, tipo in zip(no.filhos, funcao.parametros)]
        # Funcao com valor sempre guarda o resultado, mesmo chamada como comando:
        # assim a pilha da VM fica limpa.
        destino = None if funcao.tipo == 'vazio' else self.temporario()
        self.emitir('chama', destino, funcao.nome, argumentos)
        return destino
