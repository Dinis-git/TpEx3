# Lógica Computacional – TP2, Exercício 3

## Multiplicação de Inteiros: verificação com SFOTS e k-indução

Resolução do exercício 3 do TP2 de Lógica Computacional. O problema é descrito no documento *Lógica Computacional: Multiplicação de Inteiros*, onde um **Control Flow Automaton** modela um programa imperativo que calcula a multiplicação de inteiros positivos representados por vetores de bits.

O trabalho está escrito como *notebook* [marimo](https://marimo.io/) (ficheiro `.py`), com o código em Z3 e explicações em *markdown* ao longo das células.

---

## Enunciado

Considere o problema descrito no documento *Lógica Computacional: Multiplicação de Inteiros*. Nesse documento usa-se um "Control Flow Automaton" como modelo do programa imperativo que calcula a multiplicação de inteiros positivos representados por vetores de bits.

1. Construir um SFOTS, usando `BitVec`'s de tamanho $n$, que descreva o comportamento deste autómato; para isso identifique e codifique em `Z3` as variáveis do modelo, o estado inicial, a relação de transição e o estado de erro.
2. Usando $k$-indução, verificar nesse SFOTS se a propriedade $(x \cdot y + z = a \cdot b)$ é um invariante do seu comportamento.
3. Usando $k$-indução no SFOTS acima e adicionando ao estado inicial a condição $(a < 2^{n/2}) \land (b < 2^{n/2})$, verificar a segurança do programa; nomeadamente, provar que, com tal estado inicial, o estado de erro nunca é acessível.
4. Codificar a propriedade de animação que exprime que o programa termina quaisquer que sejam os valores iniciais de $a$ e $b$ e provar que ela se verifica no SFOTS construído.

---

## O programa modelado

O programa multiplica `a` por `b` usando apenas somas e deslocamentos de bits:

```
1: x, y, z = a, b, 0
2: while y != 0
3:     if y é par:  x, y = x << 1, y >> 1     # duplica x, divide y por 2
4:     else:        y, z = y - 1, z + x       # tira 1 a y e acumula x em z
# no fim: z == a*b
```

Todas as variáveis são `BitVec` de tamanho `N`, logo as operações são feitas **módulo $2^N$**: um overflow não dá erro no Z3, apenas faz com que o resultado final seja incorreto.

---

## Estrutura da solução

### Alínea 1 – SFOTS

| Elemento | Função | Descrição |
|----------|--------|-----------|
| Estado | `declare(i)` | Estado número `i`: `pc` (2 bits, o local do autómato) e as variáveis `a`, `b`, `x`, `y`, `z` (`N` bits cada) |
| Auxiliar | `keep(atual, prox, vars)` | Impõe que as variáveis de `vars` mantêm o valor entre dois estados |
| Estado inicial | `init(s)` | `pc == 0`, `x == a`, `y == b`, `z == 0`, `x >= 0`, `y >= 0` |
| Estado inicial (alínea 3) | `init2(s)` | Igual a `init` com `a < 2**(N//2)` e `b < 2**(N//2)` |
| Transição | `trans(s, t)` | Disjunção de 5 casos (tabela abaixo) |
| Estado de erro | `erro(s)` | `pc == 2` (programa terminou) e `z != a*b` |

**Casos da relação de transição:**

| Caso | Local | Condição | Efeito |
|------|-------|----------|--------|
| `e0a` | 0 | `y != 0` | vai para o local 1; nada muda |
| `e0b` | 0 | `y == 0` | vai para o local 2; nada muda |
| `e1a` | 1 | `y` par | `x = x << 1`, `y = y >> 1` (`LShR`), volta ao local 0; `a`, `b`, `z` mantêm-se |
| `e1b` | 1 | `y` ímpar | `y = y - 1`, `z = z + x`, volta ao local 0; `a`, `b`, `x` mantêm-se |
| `e2` | 2 | – | estado final: fica no local 2 com as variáveis inalteradas (ciclo sobre si próprio, para a execução poder continuar indefinidamente) |

### Alíneas 2, 3 e 4 – Verificação

Em todos os verificadores o método é o mesmo: pedir ao Z3 um **contra-exemplo**. Se o solver responde `unsat`, não existe contra-exemplo e a propriedade fica provada; se responde `sat`, o modelo devolvido é o contra-exemplo.

| Alínea | Verificador | Aplicação |
|--------|-------------|-----------|
| 2 | `induction_always(declare, init, trans, inv)` | Indução simples (caso base + passo indutivo) com `init` e o invariante `inv`: $x \cdot y + z = a \cdot b$ |
| 3 | `kinduction_always(declare, init2, trans, inv2_forte, k)` | $k$-indução com `k = 10`, estado inicial `init2` e `inv2_forte`: `¬erro(s)` e $z + x \cdot y = a \cdot b$. Se for válido, o estado de erro é inacessível |
| 4 | `k_lookahead(declare, init, trans, V, k)` | Prova de terminação com a variante `var_simples` (`V = y`) e `k = 2`: ao fim de 2 transições (uma iteração do ciclo, local 0 → 1 → 0), `y` diminui ou já é 0 |

---

## Requisitos

- Python 3
- Z3 (`pip install z3-solver`)
- marimo (`pip install marimo`)

---

## Como usar

1. Ao executar o ficheiro, será pedido ao utilizador que digite um **inteiro $N$** (`digite o n:`), que corresponde ao número de bits dos vetores `BitVec`. Se o valor não for um inteiro, o pedido é repetido.
2. Usando esse valor de $N$, o código verifica, passo a passo, cada uma das condições do enunciado:
   - se a condição for provada, é impresso um resultado **válido** (`invariante valido` ou `Variante valida`);
   - caso contrário, é impresso o **contra-exemplo** que desprovou a condição (`Falhou o caso base`, `Falhou o passo indutivo`, `Caso base falhado`, `passo indutivo falhado` ou `Failed`, seguido do modelo do Z3).

### Exemplo de execução

```bash
python <nome_do_ficheiro>.py
```

```
digite o n: 8
invariante valido
invariante valido
Variante valida
```

---

## Notas

- O valor de $N$ influencia o tamanho do espaço de estados e, consequentemente, o tempo de verificação.
- Na alínea 3, a restrição $a, b < 2^{N/2}$ limita o tamanho dos inputs para que o produto $a \cdot b$ caiba em $N$ bits e o overflow não ocorra.
- Em `BitVec`, os operadores de comparação do Z3 (`>=`, `<`) são **com sinal**. Assim, `x >= 0` e `y >= 0` equivalem a exigir que o bit mais significativo seja 0.

---

## Utilização de LLMs neste trabalho

Foram usadas duas conversas com o Claude, cada uma com um papel diferente.

### Conversa 1 – compreensão do exercício e base do modelo

Ligação: https://claude.ai/share/90e28273-3836-42f1-b234-76e5afbe241b

- **Objetivo:** perceber como se traduz o programa (ciclo com `if` par/ímpar) para um SFOTS: estado, estado inicial, transição e estado de erro quando o Z3 trabalha módulo $2^n$.
- **Contributo para o código:** base das funções `declare`, `keep`, `init` e `trans`.
- **Adaptações:** `declare` e `keep` foram aproveitadas tal como surgiram; `init` foi adaptada ao enunciado e `init2` foi acrescentada (alínea 3); `trans`, `erro` e o invariante `inv2_forte` foram ajustados ao modelo. Os comentários `#codigo feito por llm` e `#codigo aproveitado da llm(codigo adaptado)` marcam estas partes.
- **Não veio desta conversa:** os verificadores `induction_always`, `kinduction_always` e `k_lookahead` foram aproveitados do material das aulas (comentários `# codigo aproveitado da aula`) e aplicados ao modelo.

### Conversa 2 – melhoria dos textos explicativos

Ligação: https://claude.ai/share/7a906a9a-f2f0-498b-9122-013b51aa05b6

- **Objetivo:** tornar mais claras as explicações em *markdown* que acompanham o código (alínea 1 e verificadores das alíneas 2, 3 e 4).
- **Contributo:** reformulação desses textos, como a tabela dos casos de `trans` e a explicação de cada verificador. **Não alterou o código.**
- **Como foi usada:** o texto gerado foi relido e confrontado com o código para confirmar que descreve o que as funções fazem.
