"""
Entrega 4, segunda metade — geracao do codigo executavel.

Traduz o codigo de tres enderecos para o formato que a VM de voces executa.
O formato do .mplb e de voces, com uma exigencia: tem que ser TEXTO legivel.
Na apresentacao a gente vai abrir um .mplb e ler junto.

Leiam antes: CONTRATOS.md secao 6.
"""

BINARIAS = {
    '+': 'SOME', '-': 'SUBTRAIA', '*': 'MULTIPLIQUE', '/': 'DIVIDA', '%': 'RESTO',
    '==': 'IGUAL', '!=': 'DIFERENTE', '<': 'MENOR', '<=': 'MENOR_IGUAL',
    '>': 'MAIOR', '>=': 'MAIOR_IGUAL', 'e': 'E', 'ou': 'OU',
}
UNARIAS = {'-': 'NEGUE', 'nao': 'NAO'}

CABECALHO = [
    '; .mplb: codigo de pilha da MPL (o conjunto de instrucoes esta no README).',
    '; "funcao <nome> <parametros>" abre uma funcao e "fim" fecha.',
    '; Em cada instrucao, o primeiro numero e a linha do fonte, para os erros de execucao.',
]


def eh_nome(operando):
    """Operando do codigo de tres enderecos: nome (variavel ou $t) ou constante."""
    return operando not in ('verdadeiro', 'falso') and (operando[0].isalpha() or operando[0] in '_$')


def gerar(codigo_intermediario):
    """Devolve as linhas do arquivo .mplb."""
    saida = list(CABECALHO)
    for f in codigo_intermediario:
        saida.append(' '.join(['funcao', f.nome] + [nome for nome, _ in f.parametros]))
        for linha, tipo, *a in f.instrucoes:
            if tipo == 'rotulo':
                saida.append(f'{a[0]}:')
            else:
                saida += [f'{linha:5}  {i}' for i in traduzir(tipo, a)]
        saida.append('fim')
    return saida


def traduzir(tipo, a):
    """Uma instrucao de tres enderecos vira algumas instrucoes de pilha."""
    def empilhe(operando):
        return f'CARREGUE {operando}' if eh_nome(operando) else f'EMPILHE {operando}'

    if tipo == 'copia':                     # x = a
        return [empilhe(a[1]), f'GUARDE {a[0]}']
    if tipo == 'binaria':                   # x = a op b
        return [empilhe(a[1]), empilhe(a[3]), BINARIAS[a[2]], f'GUARDE {a[0]}']
    if tipo == 'unaria':                    # x = op a
        return [empilhe(a[2]), UNARIAS[a[1]], f'GUARDE {a[0]}']
    if tipo == 'real':                      # x = real a
        return [empilhe(a[1]), 'REAL', f'GUARDE {a[0]}']
    if tipo == 'desvie':
        return [f'DESVIE {a[0]}']
    if tipo == 'seFalso':
        return [empilhe(a[0]), f'SE_FALSO {a[1]}']
    if tipo == 'chama':                     # [x =] chama f args
        destino, nome, argumentos = a
        guarda = [f'GUARDE {destino}'] if destino is not None else []
        return [empilhe(arg) for arg in argumentos] + [f'CHAME {nome} {len(argumentos)}'] + guarda
    if tipo == 'retorne':
        return ([empilhe(a[0])] if a[0] is not None else []) + ['RETORNE']
    if tipo == 'escreva':
        return [empilhe(a[0]), 'ESCREVA']
