"""
Entrega 1 — analise lexica.

Transformar o texto do programa numa lista de tokens.

O que voces tem que devolver: uma lista de Token. O ultimo elemento e sempre
um token FIM_ARQUIVO. A regra de posicao dele esta em CONTRATOS.md, secao 7.

Leiam antes: LINGUAGEM.md secao 2, e CONTRATOS.md secao 2.
"""
from mplc.erros import ErroMPL


class Token:
    __slots__ = ('tipo', 'lexema', 'linha', 'coluna')

    def __init__(self, tipo, lexema, linha, coluna):
        self.tipo = tipo          # 'ID', 'INTEIRO', 'MAIS', ... (a lista esta no contrato)
        self.lexema = lexema      # o texto exato como apareceu no fonte
        self.linha = linha
        self.coluna = coluna      # a coluna do PRIMEIRO caractere do token

    def __str__(self):
        # esta e a linha que o --tokens imprime; nao mexam no formato
        return f"{self.linha},{self.coluna},{self.tipo},{self.lexema}"


PALAVRAS_RESERVADAS = {
    'funcao': 'FUNCAO', 'retorne': 'RETORNE', 'se': 'SE', 'senao': 'SENAO',
    'enquanto': 'ENQUANTO', 'escreva': 'ESCREVA',
    'inteiro': 'TIPO_INTEIRO', 'real': 'TIPO_REAL', 'logico': 'TIPO_LOGICO',
    'texto': 'TIPO_TEXTO', 'vazio': 'TIPO_VAZIO',
    'verdadeiro': 'LOGICO', 'falso': 'LOGICO',
    'e': 'E', 'ou': 'OU', 'nao': 'NAO',
}

# Os simbolos de dois caracteres sao testados antes dos de um.
# Na ordem contraria, '<=' vira '<' seguido de '='.
SIMBOLOS_DUPLOS = {'==': 'IGUAL', '!=': 'DIFERENTE', '<=': 'MENOR_IGUAL', '>=': 'MAIOR_IGUAL'}
SIMBOLOS = {
    '+': 'MAIS', '-': 'MENOS', '*': 'VEZES', '/': 'DIVIDE', '%': 'RESTO',
    '<': 'MENOR', '>': 'MAIOR', '=': 'ATRIBUI',
    '(': 'ABRE_PAR', ')': 'FECHA_PAR', '{': 'ABRE_CHAVE', '}': 'FECHA_CHAVE',
    ',': 'VIRGULA', ';': 'PONTO_VIRGULA',
}
DIGITOS = '0123456789'
ESCAPES = 'nt"\\'      # o caractere que pode vir depois de '\' num texto


def eh_letra(c):
    # So ASCII. 'c' com cedilha passa em isalpha(), mas a MPL nao aceita (LINGUAGEM.md 2.2).
    return c == '_' or 'a' <= c <= 'z' or 'A' <= c <= 'Z'


def analisar(fonte):
    """Recebe o texto do programa. Devolve a lista de Token."""
    tokens = []
    n = len(fonte)
    i = 0               # indice do proximo caractere a ler
    linha = 1
    inicio_linha = 0    # indice do primeiro caractere da linha atual

    def coluna(j):
        return j - inicio_linha + 1

    def erro(j, mensagem):
        raise ErroMPL('lexico', linha, coluna(j), mensagem)

    while i < n:
        c = fonte[i]
        ini = i

        # O que separa tokens e nao gera token: espaco, quebra de linha, comentario.
        if c == '\n':
            i += 1
            linha += 1
            inicio_linha = i
            continue
        if c in ' \t\r':
            i += 1
            continue
        if fonte.startswith('//', i):
            while i < n and fonte[i] != '\n':
                i += 1
            continue
        if fonte.startswith('/*', i):
            fim = fonte.find('*/', i + 2)     # o primeiro '*/' fecha: nao aninha
            if fim == -1:
                erro(i, 'comentario de bloco aberto aqui e nunca fechado')
            quebras = fonte.count('\n', i, fim)
            if quebras:
                linha += quebras
                inicio_linha = fonte.rfind('\n', i, fim) + 1
            i = fim + 2
            continue

        # Cada ramo abaixo avanca i ate o fim do token e decide o tipo.
        if eh_letra(c):
            while i < n and (eh_letra(fonte[i]) or fonte[i] in DIGITOS):
                i += 1
            tipo = PALAVRAS_RESERVADAS.get(fonte[ini:i], 'ID')

        elif c in DIGITOS:
            while i < n and fonte[i] in DIGITOS:
                i += 1
            tipo = 'INTEIRO'
            if i < n and fonte[i] == '.':
                if i + 1 >= n or fonte[i + 1] not in DIGITOS:
                    erro(i, 'numero real sem digito depois do ponto (escreva 3.0, nao 3.)')
                i += 1
                while i < n and fonte[i] in DIGITOS:
                    i += 1
                tipo = 'REAL'

        elif c == '"':
            i += 1
            while i < n and fonte[i] not in '"\n':
                if fonte[i] == '\\':
                    if i + 1 >= n or fonte[i + 1] not in ESCAPES:
                        erro(i, 'escape invalido: os aceitos sao \\n, \\t, \\" e \\\\')
                    i += 2
                else:
                    i += 1
            if i >= n or fonte[i] == '\n':
                erro(ini, 'texto aberto aqui e nao fechado na mesma linha')
            i += 1
            tipo = 'TEXTO'

        elif fonte[i:i + 2] in SIMBOLOS_DUPLOS:
            i += 2
            tipo = SIMBOLOS_DUPLOS[fonte[ini:i]]

        elif c in SIMBOLOS:
            i += 1
            tipo = SIMBOLOS[c]

        elif c == '.' and i + 1 < n and fonte[i + 1] in DIGITOS:
            erro(i, 'numero real sem digito antes do ponto (escreva 0.5, nao .5)')

        else:
            erro(i, f'caractere inesperado {c!r}')

        tokens.append(Token(tipo, fonte[ini:i], linha, coluna(ini)))

    tokens.append(Token('FIM_ARQUIVO', '', linha, coluna(i)))
    return tokens
