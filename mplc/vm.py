"""
Entrega 4, terceira metade (sim, sao tres) — a maquina virtual.

Le o .mplb e executa. Precisa de:
  - uma pilha de operandos;
  - um registro de ativacao por chamada, com os locais e o ponto de volta;
  - deteccao de divisao por zero e de estouro de pilha, com codigo de saida 2.

Essa e a materia da aula 11 virando codigo: sem registro de ativacao, a
recursao nao funciona.
"""
import operator
import re

from mplc.erros import ErroMPL

# Quantas chamadas podem estar abertas ao mesmo tempo. A VM nao usa a
# recursao do Python, entao este limite e nosso, e nao o do Python.
LIMITE_CHAMADAS = 100_000


def dividir(a, b):
    if isinstance(a, float) or isinstance(b, float):
        return a / b
    # Inteiros: trunca em direcao a zero. O // do Python arredonda para baixo.
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def resto(a, b):
    # O resto tem o sinal do dividendo. O % do Python segue o sinal do divisor.
    r = abs(a) % abs(b)
    return -r if a < 0 else r


BINARIAS = {
    'SOME': operator.add, 'SUBTRAIA': operator.sub, 'MULTIPLIQUE': operator.mul,
    'DIVIDA': dividir, 'RESTO': resto,
    'IGUAL': operator.eq, 'DIFERENTE': operator.ne,
    'MENOR': operator.lt, 'MENOR_IGUAL': operator.le,
    'MAIOR': operator.gt, 'MAIOR_IGUAL': operator.ge,
    'E': lambda a, b: a and b, 'OU': lambda a, b: a or b,
}
UNARIAS = {'NEGUE': operator.neg, 'NAO': operator.not_, 'REAL': float}

ESCAPES = {'n': '\n', 't': '\t', '"': '"', '\\': '\\'}


def constante(texto):
    if texto.startswith('"'):
        return re.sub(r'\\(.)', lambda m: ESCAPES[m[1]], texto[1:-1])
    if texto in ('verdadeiro', 'falso'):
        return texto == 'verdadeiro'
    if '.' in texto:
        return float(texto)
    return int(texto)


def formatar(valor):
    """A forma impressa de cada tipo (LINGUAGEM.md 4.5)."""
    if isinstance(valor, bool):         # antes do int: True tambem e int no Python
        return 'verdadeiro' if valor else 'falso'
    if isinstance(valor, float):
        return f'{valor:.6f}'
    return str(valor)


class Funcao:
    def __init__(self, nome, parametros):
        self.nome = nome
        self.parametros = parametros
        self.codigo = []        # (linha do fonte, instrucao, argumento)
        self.rotulos = {}       # rotulo -> indice em codigo


class Registro:
    """O registro de ativacao: uma chamada em andamento."""
    __slots__ = ('funcao', 'pc', 'locais')

    def __init__(self, funcao, locais):
        self.funcao = funcao
        self.pc = 0             # a proxima instrucao; para quem chamou, e o ponto de volta
        self.locais = locais    # nome -> valor, so desta chamada


def carregar(texto):
    funcoes = {}
    for linha in texto.splitlines():
        partes = linha.split(None, 2)
        if not partes or partes[0].startswith(';') or partes[0] == 'fim':
            continue
        if partes[0] == 'funcao':
            nomes = linha.split()
            f = funcoes[nomes[1]] = Funcao(nomes[1], nomes[2:])
        elif partes[0].isdigit():
            instrucao = partes[1]
            arg = partes[2] if len(partes) > 2 else None
            if instrucao == 'EMPILHE':
                arg = constante(arg)
            elif instrucao == 'CHAME':
                nome, n = arg.split()
                arg = (nome, int(n))
            f.codigo.append((int(partes[0]), instrucao, arg))
        else:                   # 'L3:'
            f.rotulos[partes[0][:-1]] = len(f.codigo)
    return funcoes


def executar(texto_mplb, saida):
    """Executa o bytecode. Escreve o que o programa imprimir em `saida`."""
    funcoes = carregar(texto_mplb)
    pilha = []                  # pilha de operandos, de todas as chamadas
    chamadas = []               # os registros de quem chamou e espera a volta
    atual = Registro(funcoes['principal'], {})

    while True:
        linha, instrucao, arg = atual.funcao.codigo[atual.pc]
        atual.pc += 1

        if instrucao == 'EMPILHE':
            pilha.append(arg)
        elif instrucao == 'CARREGUE':
            pilha.append(atual.locais[arg])
        elif instrucao == 'GUARDE':
            atual.locais[arg] = pilha.pop()

        elif instrucao in BINARIAS:
            b = pilha.pop()
            a = pilha.pop()
            if instrucao in ('DIVIDA', 'RESTO') and b == 0:
                raise ErroMPL('execucao', linha, 1, 'divisao por zero')
            pilha.append(BINARIAS[instrucao](a, b))
        elif instrucao in UNARIAS:
            pilha.append(UNARIAS[instrucao](pilha.pop()))

        elif instrucao == 'DESVIE':
            atual.pc = atual.funcao.rotulos[arg]
        elif instrucao == 'SE_FALSO':
            if not pilha.pop():
                atual.pc = atual.funcao.rotulos[arg]

        elif instrucao == 'CHAME':
            nome, n = arg
            if len(chamadas) >= LIMITE_CHAMADAS:
                raise ErroMPL('execucao', linha, 1,
                              f'estouro de pilha: mais de {LIMITE_CHAMADAS} chamadas abertas')
            funcao = funcoes[nome]
            argumentos = pilha[len(pilha) - n:]
            del pilha[len(pilha) - n:]
            chamadas.append(atual)
            atual = Registro(funcao, dict(zip(funcao.parametros, argumentos)))
        elif instrucao == 'RETORNE':
            # Se a funcao devolve valor, ele ja esta no topo da pilha.
            if not chamadas:
                return
            atual = chamadas.pop()

        elif instrucao == 'ESCREVA':
            saida.write(formatar(pilha.pop()) + '\n')
