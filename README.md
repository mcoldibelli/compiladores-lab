# Minha pequena linguagem

Trabalho semestral de **Compiladores** — Ciência da Computação, UNISAGRADO.
Prof. Luiz Ricardo Mantovani da Silva · 2026-2

Cada grupo escreve um **compilador completo** para a MPL, uma linguagem
pequena de palavras-chave em português. O compilador de vocês vai ler um
programa em `.mpl`, atravessar as quatro fases da disciplina e produzir um
arquivo que **roda de verdade** numa máquina virtual que vocês também vão
escrever.

No fim do semestre vocês executam um programa escrito por vocês, numa
linguagem compilada por vocês.

---

## Comece por aqui

```bash
git clone https://github.com/LuizRMSilva1973/compiladores-lab.git
cd compiladores-lab
```

```bash
make verificar E=1
```

Vai dar vermelho — é para dar. O esqueleto responde à linha de comando mas
ainda não tem nenhuma fase escrita. O vermelho é o seu ponto de partida, e
ele vai virando verde conforme vocês preenchem `mplc/`.

Não precisa instalar nada além do Python 3. Se o notebook de vocês der
trabalho, o [Google Cloud Shell](https://shell.cloud.google.com) já vem com
Python 3.12, Java 21 e git — e é o mesmo ambiente da correção.

---

## Os três documentos que mandam

| Arquivo | O que decide |
|---|---|
| [LINGUAGEM.md](LINGUAGEM.md) | **o que** o compilador aceita: a sintaxe e as regras de tipo da MPL |
| [CONTRATOS.md](CONTRATOS.md) | **como** ele se comunica: a linha de comando e o formato de cada despejo |
| [entregas/](entregas/) | o enunciado de cada entrega, com o que vale nota |

Quando a sua intuição discordar de um deles, é o arquivo que vale. Se o
arquivo estiver errado, me procurem — já aconteceu de eu escrever um exemplo
errado no contrato e só descobrir rodando.

---

## As entregas

| # | Entrega | Turma A (quarta) | Turma B (segunda) | Vale |
|---|---|---|---|---|
| [E1](entregas/E1.md) | Analisador léxico | 02/09 | 31/08 | 0,8 |
| [E2](entregas/E2.md) | Analisador sintático e árvore | 30/09 | 28/09 | 1,2 |
| [E3](entregas/E3.md) | Tabela de símbolos e tipos | 28/10 | 26/10 | 1,2 |
| [E4](entregas/E4.md) | Código intermediário, geração e VM | 18/11 | 16/11 | 1,8 |
| [Apres.](entregas/APRESENTACAO.md) | Demonstração e defesa | 25/11 | 23/11 | 1,0 |

São **quatro entregas sobre o mesmo compilador**, não quatro trabalhos. O que
vocês escreverem na E1 continua rodando na E4 — e o verificador da E4 confere
tudo o que veio antes. Deixar a E1 pela metade custa caro em novembro.

---

## Regras do jogo

**A entrega é o repositório, nunca a máquina de vocês.** A correção clona o
repositório numa máquina limpa e roda `make verificar E=n`. Se não passar
lá, não conta como entregue. Testem antes de entregar — de preferência na
Cloud Shell, que é o ambiente da correção.

**Grupos de até 3.** O mesmo grupo do começo ao fim. Mudança de grupo só até
a E1.

**Gerador de parser proibido nas Entregas 1 e 2.** ANTLR, PLY, yacc, lark e
parentes escondem exatamente a parte que está sendo ensinada. Da E3 em diante
o assunto é outro, e aí não faz diferença. Na apresentação vocês podem — e
devem — comparar o parser de vocês com o que um gerador produziria.

**A linguagem de implementação é de vocês, entre as que o ambiente da correção
já tem:** Python 3.12, Java 21, C e C++ (gcc 13), Ruby 3.2 ou PHP 8.3. O
verificador não olha para dentro — ele roda `./compilar` e `./executar` e
compara o que sai. O esqueleto em `mplc/` é Python porque é o caminho mais
curto, mas ninguém é obrigado a usá-lo.

A lista existe por um motivo prático: a correção roda numa Cloud Shell limpa, e
o que não estiver lá não roda. Querem outra linguagem? Falem comigo **antes** de
começar — o critério é ela existir no ambiente sem instalação. Em nenhum caso
dependam de biblioteca externa: só a biblioteca padrão.

**Escrever o compilador é a tarefa.** Usar IA para explicar um conceito,
revisar uma mensagem de erro ou entender um trecho é bem-vindo, e eu faço
isso também. Entregar um compilador que vocês não sabem alterar é outra
coisa — e a apresentação foi desenhada para separar os dois casos: cada grupo
recebe **uma alteração pequena na linguagem, na hora, com 10 minutos para
fazer**. Quem escreveu o compilador faz. Não é desconfiança; é o formato.

---

## O verificador

```bash
make verificar E=2      # confere a Entrega 2 e, junto, a 1
make verificar          # confere as quatro
make evidencias E=2     # grava evidencias/verificacao-2.txt, que vai na entrega
```

**Antes de entregar, rodem `make prova`.** Ele clona o repositório de vocês num
diretório limpo e verifica lá — que é exatamente o que a correção faz. É o
teste que pega o defeito mais comum de todos, e que não tem nada a ver com
compiladores: *funciona aqui e não no clone*. Arquivo esquecido fora do commit,
caminho absoluto, passo de compilação que ninguém roda. Vale para qualquer
linguagem, e é a única prova que realmente antecipa a correção.

Ele não lê o código de vocês. Ele roda o compilador e compara a saída com um
corpus de **10 programas válidos**, **26 programas que precisam ser
recusados na compilação** e **3 que precisam falhar na execução** — com a
fase e a linha do erro conferidas.

Os programas recusados são metade da nota escondida do trabalho. Um
compilador que aceita tudo passa em todos os testes positivos e não vale
nada: é por isso que o corpus tem mais programas errados do que certos.

**A correção usa um segundo corpus, que vocês não têm.** Mesma linguagem,
mesmas regras, programas diferentes. Um compilador de verdade passa nos dois
sem que vocês precisem fazer nada; um programa que apenas reproduza as saídas
esperadas deste corpus passa aqui e reprova lá. Estou dizendo isto abertamente
para ninguém perder tempo pelo caminho errado.

---

## Como entregar

1. `git push` no repositório do grupo.
2. Abram a [página do trabalho](https://profluiz.mantovanitec.com/disciplinas/aulas/compiladores/trabalho.html).
3. No formulário do fim da página: escolham a entrega, identifiquem os
   integrantes (nome, RA e e-mail), colem a URL do repositório e anexem o
   `evidencias/verificacao-N.txt`.
4. Cada integrante recebe uma cópia por e-mail. **Guardem esse e-mail**: é o
   comprovante.

---

## Nosso compilador

### Entrega 1: tabela de tokens

O analisador léxico (`mplc/lexico.py`) é escrito à mão: um laço lê o fonte da
esquerda para a direita e, olhando o caractere atual, escolhe um ramo. Cada
ramo é um autômato pequeno que avança até o fim do token. A coluna de um token
é `indice - inicio_da_linha + 1`.

| Tipo | Expressão regular | Observação |
|---|---|---|
| `ID` | `[A-Za-z_][A-Za-z0-9_]*` | só ASCII; se o lexema for palavra reservada, o tipo é o da linha abaixo |
| palavras reservadas | `funcao` `retorne` `se` `senao` `enquanto` `escreva` | tipos `FUNCAO` `RETORNE` `SE` `SENAO` `ENQUANTO` `ESCREVA` |
| tipos | `inteiro` `real` `logico` `texto` `vazio` | `TIPO_INTEIRO` `TIPO_REAL` `TIPO_LOGICO` `TIPO_TEXTO` `TIPO_VAZIO` |
| `E` `OU` `NAO` | `e` `ou` `nao` | operadores lógicos escritos como palavra |
| `LOGICO` | `verdadeiro\|falso` | reconhecido pelo mesmo ramo do `ID` |
| `INTEIRO` | `[0-9]+` | |
| `REAL` | `[0-9]+\.[0-9]+` | o ramo do número só aceita o ponto se vier dígito depois |
| `TEXTO` | `"([^"\\\n]\|\\[nt"\\])*"` | o lexema guarda as aspas e os escapes como estão no fonte |
| `IGUAL` `DIFERENTE` `MENOR_IGUAL` `MAIOR_IGUAL` | `==` `!=` `<=` `>=` | testados **antes** dos símbolos de um caractere |
| `MAIS` `MENOS` `VEZES` `DIVIDE` `RESTO` | `+` `-` `*` `/` `%` | |
| `MENOR` `MAIOR` `ATRIBUI` | `<` `>` `=` | |
| `ABRE_PAR` `FECHA_PAR` `ABRE_CHAVE` `FECHA_CHAVE` `VIRGULA` `PONTO_VIRGULA` | `(` `)` `{` `}` `,` `;` | |
| `FIM_ARQUIVO` | fim do fonte | lexema vazio; linha seguinte e coluna 1 se o fonte termina em quebra de linha, senão logo depois do último caractere |

Não geram token: espaço, `\t`, `\r`, `\n`, `//[^\n]*` e `/\*` até o primeiro
`*/` (o comentário de bloco não aninha).

Os erros léxicos, e para onde cada um aponta:

| Erro | Exemplo | Posição relatada |
|---|---|---|
| escape inválido | `"a\qb"` | a `\` |
| texto não fechado na linha | `"sem fim` | a `"` de abertura |
| comentário de bloco não fechado | `/* ...` | o `/` de abertura |
| real sem dígito depois do ponto | `3.` | o `.` |
| real sem dígito antes do ponto | `.5` | o `.` |
| caractere fora da linguagem | `@`, `!` sozinho, `ç` | o próprio caractere |

### Entrega 2: gramática

O analisador sintático (`mplc/sintatico.py`) é uma descida recursiva escrita à
mão. Cada regra abaixo é um método da classe `Parser` com o mesmo nome. Os
terminais estão entre aspas; `{ x }` é zero ou mais vezes, `[ x ]` é opcional.

```ebnf
programa       = { funcao } FIM_ARQUIVO ;
funcao         = "funcao" ( tipo | "vazio" ) ID "(" [ parametro { "," parametro } ] ")" bloco ;
parametro      = tipo ID ;
tipo           = "inteiro" | "real" | "logico" | "texto" ;
bloco          = "{" { comando } "}" ;

comando        = tipo ID [ "=" expressao ] ";"                 (* declaracao *)
               | ID "=" expressao ";"                          (* atribuicao *)
               | chamada ";"                                   (* chamada como comando *)
               | "se" condicao bloco [ "senao" bloco ]
               | "enquanto" condicao bloco
               | "escreva" "(" expressao ")" ";"
               | "retorne" [ expressao ] ";"
               | bloco ;
condicao       = "(" expressao ")" ;

expressao      = ou ;
ou             = e { "ou" e } ;
e              = igualdade { "e" igualdade } ;
igualdade      = relacional { ( "==" | "!=" ) relacional } ;
relacional     = aditiva { ( "<" | "<=" | ">" | ">=" ) aditiva } ;
aditiva        = multiplicativa { ( "+" | "-" ) multiplicativa } ;
multiplicativa = unaria { ( "*" | "/" | "%" ) unaria } ;
unaria         = ( "nao" | "-" ) unaria | primaria ;
primaria       = INTEIRO | REAL | LOGICO | TEXTO
               | chamada | ID
               | "(" expressao ")" ;
chamada        = ID "(" [ expressao { "," expressao } ] ")" ;
```

**Como a precedência está codificada:** cada nível de precedência é uma regra,
e cada regra só chama a regra do nível seguinte, mais forte. Por isso um
operador mais forte sempre fica mais fundo na árvore: em `1 + 2 * 3`, o `*` é
montado dentro de `multiplicativa`, antes de `aditiva` montar o `+`.

**Como a associatividade está codificada:** a repetição `{ ... }` dos níveis
binários é um laço (`binario_esquerda`) em que o nó já montado vira o filho da
esquerda do próximo. Por isso `10 - 4 - 3` fica `(10 - 4) - 3`. A regra
`unaria` chama a si mesma à direita, então `nao` e o `-` unário associam à
direita.

**Como o parser escolhe o comando:** pelo primeiro token. Só o `ID` precisa
olhar um token a mais: `ID "("` é chamada, e qualquer outro é atribuição.

**Onde fica o erro sintático:** no token que apareceu no lugar do esperado.
Faltando o `;` no fim de uma linha, o erro fica no primeiro token da linha
seguinte.

### Entrega 3: estrutura dos escopos

Os escopos formam uma árvore: cada escopo é um dicionário (`nome -> Simbolo`)
com um ponteiro para o escopo pai (`Escopo` em `mplc/semantica.py`). A busca
de um nome começa no escopo atual e sobe pela cadeia de pais; o primeiro que achar
vence, e é isso que faz o sombreamento sem nenhum código extra. Ao fechar um
bloco, o analisador só volta o ponteiro `atual` para o pai, então a variável de
dentro some da busca e a de fora volta. O escopo fechado **não** é apagado:
todos ficam numa lista, na ordem em que abriram, porque o `--tabela` imprime
todos e a Entrega 4 vai precisar deles para dar uma posição de memória a cada
variável.

Escolhemos a árvore de dicionários, e não uma pilha que descarta o escopo ao
fechar, por esse motivo: a pilha responde "o que é visível agora", mas perde o
escopo depois que ele fecha. O dicionário dá busca em tempo constante dentro
de cada escopo, e a profundidade da cadeia é pequena.

Outras decisões:

- **Duas passadas.** A primeira declara só as assinaturas das funções no
  escopo 0. A segunda analisa os corpos. Assim uma função pode chamar outra que
  aparece depois no arquivo (recursão indireta).
- **Funções são buscadas só no escopo 0.** Uma variável local com o nome de uma
  função não impede a chamada dessa função.
- **Em `inteiro x = x + 1;`** a expressão é analisada antes de declarar o novo
  `x`, então o `x` da direita é o de fora.
- **Retorno em todos os caminhos** é decidido pela estrutura: um bloco garante
  retorno se tem um `retorne`, um bloco interno que garante, ou um `se` com
  `senao` em que os dois lados garantem. `enquanto` nunca garante, porque a
  condição não é avaliada.
- O analisador grava em cada nó da árvore o tipo da expressão
  (`extra['tipo']`) e o símbolo do nome (`extra['simbolo']`). A Entrega 4 usa
  esses dados para saber onde converter `inteiro` em `real` e qual `x` cada uso
  significa.
