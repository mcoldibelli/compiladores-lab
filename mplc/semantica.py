"""
Entrega 3 — analise semantica.

Tabela de simbolos, escopos aninhados e verificacao de tipos.

Tres coisas que costumam ser esquecidas e valem nota:
  - o corpo de uma funcao abre DOIS escopos (o dos parametros e o do bloco);
  - uma funcao pode ser chamada antes de aparecer no arquivo, entao a
    primeira passada so coleta assinaturas;
  - funcao com retorno declarado precisa garantir o retorno em TODOS os
    caminhos.

Leiam antes: LINGUAGEM.md secoes 3 a 5, e CONTRATOS.md secao 4.
"""
from mplc.erros import ErroMPL

NUMERICOS = ('inteiro', 'real')


class Simbolo:
    def __init__(self, nome, categoria, tipo, linha, parametros=None):
        self.nome = nome
        self.categoria = categoria    # 'funcao', 'parametro' ou 'variavel'
        self.tipo = tipo              # para funcao, o tipo de retorno
        self.linha = linha
        self.parametros = parametros  # so funcao: a lista dos tipos dos parametros


class Escopo:
    def __init__(self, numero, descricao, pai):
        self.numero = numero
        self.descricao = descricao    # 'global', 'funcao <nome>' ou 'bloco'
        self.pai = pai
        self.simbolos = {}            # nome -> Simbolo, na ordem de declaracao

    def buscar(self, nome):
        """Procura do escopo atual para fora. O primeiro que achar esconde os de fora."""
        escopo = self
        while escopo is not None:
            if nome in escopo.simbolos:
                return escopo.simbolos[nome]
            escopo = escopo.pai
        return None


def analisar(arvore):
    """Percorre a arvore, monta a tabela e confere os tipos. Devolve a tabela."""
    return Analisador().programa(arvore)


def despejar(tabela):
    """Devolve as linhas do --tabela, no formato da secao 4 do contrato."""
    linhas = []
    for escopo in tabela:
        pai = f' pai {escopo.pai.numero}' if escopo.pai else ''
        linhas.append(f'escopo {escopo.numero} {escopo.descricao}{pai}')
        for s in escopo.simbolos.values():
            tipo = f"{s.tipo}({','.join(s.parametros)})" if s.categoria == 'funcao' else s.tipo
            linhas.append(f'  {s.nome}|{s.categoria}|{tipo}|{s.linha}')
    return linhas


def erro(no, mensagem):
    raise ErroMPL('semantico', no.linha, no.coluna, mensagem)


def cabe(origem, destino):
    """A unica conversao implicita: inteiro vira real (LINGUAGEM.md 3.1)."""
    return origem == destino or (origem == 'inteiro' and destino == 'real')


def garante_retorno(bloco):
    """Olha so a estrutura, nunca o valor da condicao: 'se' sem 'senao' nunca garante."""
    for c in bloco.filhos:
        tipo = c.rotulo.split()[0]
        if tipo == 'retorne':
            return True
        if tipo == 'bloco' and garante_retorno(c):
            return True
        if tipo == 'se' and len(c.filhos) == 3 and garante_retorno(c.filhos[1]) \
                and garante_retorno(c.filhos[2]):
            return True
    return False


class Analisador:
    def __init__(self):
        self.escopos = []       # todos os escopos, na ordem em que abrem: e a tabela
        self.atual = None       # o escopo onde o proximo nome sera declarado
        self.funcao = None      # o Simbolo da funcao em analise, para conferir o retorne

    def abrir(self, descricao):
        self.atual = Escopo(len(self.escopos), descricao, self.atual)
        self.escopos.append(self.atual)

    def fechar(self):
        self.atual = self.atual.pai

    def declarar(self, no, categoria, tipo, parametros=None):
        nome = no.extra['nome']
        anterior = self.atual.simbolos.get(nome)
        if anterior:
            erro(no, f"'{nome}' ja foi declarado neste escopo, na linha {anterior.linha}")
        simbolo = Simbolo(nome, categoria, tipo, no.linha, parametros)
        self.atual.simbolos[nome] = simbolo
        no.extra['simbolo'] = simbolo
        return simbolo

    # ---- programa e funcoes ------------------------------------------------

    def programa(self, arvore):
        self.abrir('global')

        # 1a passada: so as assinaturas. Assim uma funcao pode ser chamada
        # antes de aparecer no arquivo.
        for f in arvore.filhos:
            parametros = [p.extra['tipo'] for p in f.filhos[0].filhos]
            self.declarar(f, 'funcao', f.extra['tipo'], parametros)

        principal = self.atual.simbolos.get('principal')
        if principal is None:
            raise ErroMPL('semantico', 1, 1, "falta a funcao 'principal'")
        if principal.parametros or principal.tipo != 'vazio':
            raise ErroMPL('semantico', principal.linha, 1,
                          "'principal' tem que ser 'funcao vazio principal()', sem parametros")

        # 2a passada: os corpos.
        for f in arvore.filhos:
            self.funcao_corpo(f)
        return self.escopos

    def funcao_corpo(self, no):
        self.funcao = no.extra['simbolo']
        self.abrir(f'funcao {self.funcao.nome}')
        for p in no.filhos[0].filhos:
            self.declarar(p, 'parametro', p.extra['tipo'])
        corpo = no.filhos[1]
        self.bloco(corpo)
        self.fechar()
        if self.funcao.tipo != 'vazio' and not garante_retorno(corpo):
            erro(no, f"a funcao '{self.funcao.nome}' pode terminar sem 'retorne' "
                     "(um 'se' sem 'senao' nao garante o retorno)")

    def bloco(self, no):
        self.abrir('bloco')
        for c in no.filhos:
            self.comando(c)
        self.fechar()

    # ---- comandos ----------------------------------------------------------

    def comando(self, no):
        tipo = no.rotulo.split()[0]

        if tipo == 'declaracao':
            # A expressao vem antes do declarar: em 'inteiro x = x + 1;' o x da
            # direita e o de fora, porque o de dentro ainda nao existe.
            if no.filhos:
                self.confere(no.filhos[0], no.extra['tipo'], f"o valor inicial de '{no.extra['nome']}'")
            self.declarar(no, 'variavel', no.extra['tipo'])

        elif tipo == 'atribuicao':
            variavel = self.variavel(no)
            self.confere(no.filhos[0], variavel.tipo, f"o valor atribuido a '{variavel.nome}'")

        elif tipo in ('se', 'enquanto'):
            t = self.expressao(no.filhos[0])
            if t != 'logico':
                erro(no.filhos[0], f"a condicao do '{tipo}' tem que ser logico, mas e {t}")
            for b in no.filhos[1:]:
                self.bloco(b)

        elif tipo == 'escreva':
            self.expressao(no.filhos[0])    # vazio ja e recusado dentro de expressao

        elif tipo == 'retorne':
            esperado = self.funcao.tipo
            if esperado == 'vazio':
                if no.filhos:
                    erro(no, "funcao vazio nao devolve valor: use 'retorne;'")
            elif not no.filhos:
                erro(no, f"esta funcao devolve {esperado}: falta o valor depois de 'retorne'")
            else:
                self.confere(no.filhos[0], esperado, 'o valor do retorne')

        elif tipo == 'bloco':
            self.bloco(no)

        elif tipo == 'chamada':             # como comando, funcao vazio e permitida
            self.chamada(no)

    def confere(self, no, destino, o_que):
        t = self.expressao(no)
        if not cabe(t, destino):
            erro(no, f'{o_que} tem que ser {destino}, mas e {t}')

    def variavel(self, no):
        nome = no.extra['nome']
        simbolo = self.atual.buscar(nome)
        if simbolo is None:
            erro(no, f"'{nome}' nao foi declarado")
        if simbolo.categoria == 'funcao':
            erro(no, f"'{nome}' e uma funcao, nao uma variavel")
        no.extra['simbolo'] = simbolo
        return simbolo

    def chamada(self, no):
        """Confere a chamada e devolve o tipo de retorno (pode ser vazio)."""
        nome = no.extra['nome']
        funcao = self.escopos[0].simbolos.get(nome)    # funcoes so existem no global
        if funcao is None:
            erro(no, f"a funcao '{nome}' nao existe")
        if len(no.filhos) != len(funcao.parametros):
            erro(no, f"'{nome}' recebe {len(funcao.parametros)} argumento(s), "
                     f"mas a chamada passa {len(no.filhos)}")
        for i, (arg, tipo) in enumerate(zip(no.filhos, funcao.parametros), 1):
            self.confere(arg, tipo, f"o argumento {i} de '{nome}'")
        no.extra['simbolo'] = funcao
        return funcao.tipo

    # ---- expressoes --------------------------------------------------------

    def expressao(self, no):
        """Devolve o tipo da expressao e o guarda em no.extra['tipo'] para a Entrega 4."""
        t = self.tipo_de(no)
        no.extra['tipo'] = t
        return t

    def tipo_de(self, no):
        tipo = no.rotulo.split()[0]

        if tipo == 'literal':
            return no.extra['tipo']

        if tipo == 'variavel':
            return self.variavel(no).tipo

        if tipo == 'chamada':
            t = self.chamada(no)
            if t == 'vazio':
                erro(no, f"'{no.extra['nome']}' e vazio e nao devolve valor: "
                         "so pode ser chamada como comando")
            return t

        op = no.extra['op']
        if tipo == 'unario':
            t = self.expressao(no.filhos[0])
            if op == 'nao' and t == 'logico':
                return 'logico'
            if op == '-' and t in NUMERICOS:
                return t
            erro(no, f"o operador '{op}' nao aceita {t}")

        a = self.expressao(no.filhos[0])
        b = self.expressao(no.filhos[1])
        numericos = a in NUMERICOS and b in NUMERICOS

        if op == '+' and a == b == 'texto':
            return 'texto'
        if op in ('+', '-', '*', '/'):
            if numericos:
                return 'real' if 'real' in (a, b) else 'inteiro'
        elif op == '%':
            if a == b == 'inteiro':
                return 'inteiro'
        elif op in ('==', '!='):
            if a == b or numericos:
                return 'logico'
        elif op in ('<', '<=', '>', '>='):
            if numericos:
                return 'logico'
        elif op in ('e', 'ou'):
            if a == b == 'logico':
                return 'logico'
        erro(no, f"o operador '{op}' nao aceita {a} e {b}")
