# 🕷️ Web Scraping da Wikipedia com Expressões Regulares e AFD

> **Projeto 1 — Linguagens Formais e Compiladores**  
> Curso de Ciência da Computação · 6º Período

---

## 📋 Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [Como Funciona](#-como-funciona)
- [Expressão Regular (ER)](#-expressão-regular-er)
- [Autômato Finito Determinístico (AFD)](#-autômato-finito-determinístico-afd)
- [Equivalência ER ↔ AFD](#-equivalência-er--afd)
- [Funcionalidades do Scraper](#-funcionalidades-do-scraper)
- [Como Usar](#-como-usar)
- [Exemplos de Execução](#-exemplos-de-execução)
- [Requisitos](#-requisitos)

---

## 🧠 Sobre o Projeto

Este projeto une **teoria de linguagens formais** com uma aplicação prática real: um **web scraper** da Wikipédia em português.

O grande diferencial é a validação do link informado pelo usuário: em vez de usar diretamente a biblioteca `re` do Python, construímos **manualmente** um **Autômato Finito Determinístico (AFD)** que reconhece exatamente a mesma linguagem que a expressão regular `^https://pt\.wikipedia\.org/wiki/[A-Za-z0-9_()\%\-]+$`.

Isso conecta os conceitos vistos em sala (ER, AFD, simulador de autômato, linguagens regulares) a um caso de uso real.

---

## ⚙️ Como Funciona

```
Usuário informa um link
        │
        ▼
┌─────────────────────────┐
│   Validação pelo AFD    │  ◄── construído à mão, símbolo a símbolo
│   (simulado em Python)  │
└────────────┬────────────┘
             │
      ┌──────┴──────┐
      │             │
   ACEITA        REJEITA
      │             │
      ▼             ▼
Baixa o HTML   Mostra trace
da Wikipedia   do AFD e encerra
      │
      ▼
┌─────────────────────────────────────┐
│              MENU                   │
│  1 - Tópicos do artigo              │
│  2 - Imagens                        │
│  3 - Links para outros artigos      │
│  4 - Definição + simulação do AFD   │
│  0 - Sair                           │
└─────────────────────────────────────┘
```

---

## 🔤 Expressão Regular (ER)

A ER utilizada para validar os links da Wikipédia é:

```
^https://pt\.wikipedia\.org/wiki/[A-Za-z0-9_()\%\-]+$
```

### Anatomia da ER

| Parte da ER | Significado |
|---|---|
| `^` | Início da cadeia |
| `https://pt\.wikipedia\.org/wiki/` | Prefixo literal obrigatório (os `.` são escapados) |
| `[A-Za-z0-9_()\%\-]` | **Classe de caracteres** válidos para o nome do artigo |
| `+` | Um ou mais caracteres da classe acima |
| `$` | Fim da cadeia |

### Classe de Caracteres do Artigo

```
[A-Za-z0-9_()\%\-]
 │      │  │││ │
 │      │  │││ └── hífen  (ex: Jean-Paul_Sartre)
 │      │  ││└──── percentual (ex: encoding %C3)
 │      │  │└───── parênteses (ex: Mercúrio_(planeta))
 │      │  └────── underscore (ex: São_Paulo)
 │      └───────── dígitos 0–9
 └──────────────── letras maiúsculas e minúsculas
```

### Exemplos

| Link | Válido? | Motivo |
|---|---|---|
| `https://pt.wikipedia.org/wiki/Python` | ✅ Sim | Formato correto |
| `https://pt.wikipedia.org/wiki/S%C3%A3o_Paulo` | ✅ Sim | % e _ permitidos |
| `https://pt.wikipedia.org/wiki/Mercurio_(planeta)` | ✅ Sim | Parênteses permitidos |
| `https://pt.wikipedia.org/wiki/` | ❌ Não | Nome do artigo vazio (`+` exige ≥ 1) |
| `https://en.wikipedia.org/wiki/Python` | ❌ Não | Domínio `en` em vez de `pt` |
| `http://pt.wikipedia.org/wiki/Python` | ❌ Não | `http` sem `s` |
| `https://pt.wikipedia.org/wiki/Python#Secao` | ❌ Não | `#` não está na classe |

---

## 🤖 Autômato Finito Determinístico (AFD)

### Definição Formal

```
M = (Q, Σ, δ, q₀, F)

  Q  = { q0, q1, ..., q30, q31, ERRO }
  Σ  = Caracteres ASCII imprimíveis
  q₀ = q0   (estado inicial)
  F  = { q31 }  (único estado de aceitação)
  δ  = função de transição (descrita abaixo)
```

### Lógica dos Estados

O AFD tem **33 estados** no total:

| Estado | Significado |
|---|---|
| `q0` | Estado inicial |
| `q1` a `q29` | Lendo o prefixo `https://pt.wikipedia.org/wiki/` caractere a caractere |
| `q30` | Prefixo completo lido — aguarda **1º caractere** do artigo |
| `q31` | **Estado de aceitação** — lendo os demais caracteres do artigo |
| `ERRO` | Estado poço (trap) — cadeia inválida, sem retorno |

### Diagrama do AFD

```
              'h'   't'   't'   'p'   's'  ':'  '/'  '/'  'p'  't'  '.'  ...  '/'
  ──► [q0] ──► [q1]──[q2]──[q3]──[q4]──[q5]──[q6]──[q7]──[q8]──[q9]──[q10]──...──[q30]
        │                                                                               │
        │ (qualquer                                                     [A-Za-z0-9_()%-]│
        │  símbolo                                                                      │
        │  inválido)                                                                    ▼
        └────────────────────────────────────────────────────────► ┌─────────────────────┐
                                                                    │       [q31]         │◄─┐
                   [ERRO] ◄──── (qualquer símbolo inválido) ────── │    (ACEITA ✅)      │  │
                  (trap)                                            └─────────────────────┘  │
                                                                              │               │
                                                                    [A-Za-z0-9_()%-]         │
                                                                              └───────────────┘
                                                                            (auto-laço)
```

### Função de Transição δ

```
δ(qᵢ,  PREFIXO[i])        = q(i+1)    para i = 0..29   (lê a cadeia fixa char a char)
δ(qᵢ,  outro símbolo)     = ERRO      para i = 0..29

δ(q30, [A-Za-z0-9_()\%-]) = q31       ← 1º char do artigo (obrigatório)
δ(q30, outro símbolo)      = ERRO

δ(q31, [A-Za-z0-9_()\%-]) = q31       ← auto-laço nos demais caracteres
δ(q31, outro símbolo)      = ERRO

δ(ERRO, qualquer)          = ERRO      ← poço (trap state): sem retorno
```

> **Estado poço (trap state):** uma vez atingido o estado `ERRO`, nenhum símbolo consegue sair dele. Isso garante que qualquer prefixo inválido descarta a cadeia inteiramente.

### Simulação Passo a Passo

#### ✅ Link válido — `https://pt.wikipedia.org/wiki/Python`

```
SIMULAÇÃO DO AFD (estado a estado):

  inicio -> q0
  le 'h' : q0  -> q1
  le 't' : q1  -> q2
  le 't' : q2  -> q3
  le 'p' : q3  -> q4
  le 's' : q4  -> q5
  le ':' : q5  -> q6
  le '/' : q6  -> q7
  le '/' : q7  -> q8
  le 'p' : q8  -> q9
  le 't' : q9  -> q10
  le '.' : q10 -> q11
  le 'w' : q11 -> q12
  le 'i' : q12 -> q13
  le 'k' : q13 -> q14
  le 'i' : q14 -> q15
  le 'p' : q15 -> q16
  le 'e' : q16 -> q17
  le 'd' : q17 -> q18
  le 'i' : q18 -> q19
  le 'a' : q19 -> q20
  le '.' : q20 -> q21
  le 'o' : q21 -> q22
  le 'r' : q22 -> q23
  le 'g' : q23 -> q24
  le '/' : q24 -> q25
  le 'w' : q25 -> q26
  le 'i' : q26 -> q27
  le 'k' : q27 -> q28
  le 'i' : q28 -> q29
  le '/' : q29 -> q30   ◄── prefixo completo!
  le 'P' : q30 -> q31   ◄── 1º char do artigo → entra em ACEITA
  le 'y' : q31 -> q31
  le 't' : q31 -> q31
  le 'h' : q31 -> q31
  le 'o' : q31 -> q31
  le 'n' : q31 -> q31

  Terminou em q31 ACEITA -> ✅ ACEITA
```

#### ❌ Link inválido — `https://en.wikipedia.org/wiki/Python`

```
SIMULAÇÃO DO AFD (estado a estado):

  inicio -> q0
  le 'h' : q0  -> q1
  le 't' : q1  -> q2
  le 't' : q2  -> q3
  le 'p' : q3  -> q4
  le 's' : q4  -> q5
  le ':' : q5  -> q6
  le '/' : q6  -> q7
  le '/' : q7  -> q8
  le 'e' : q8  -> ERRO   ◄── esperava 'p' (de "pt."), recebeu 'e'

  Caiu no estado de ERRO: a cadeia é ❌ REJEITADA.
```

---

## 🔄 Equivalência ER ↔ AFD

Pelo **Teorema de Kleene**, toda linguagem regular pode ser descrita tanto por uma **Expressão Regular** quanto por um **Autômato Finito**. Este projeto demonstra isso na prática:

| Expressão Regular | AFD equivalente |
|---|---|
| `^https://pt\.wikipedia\.org/wiki/` | `q0 → q1 → ... → q30` (prefixo lido char a char) |
| `[A-Za-z0-9_()\%\-]+` | `q30 → q31` (1º char) + auto-laço `q31 → q31` |
| Rejeição de tudo mais | Qualquer transição não definida → `ERRO` |

No código, os dois métodos são executados e comparados — e **sempre concordam**:

```python
valido_afd   = validar_link_afd(link)    # AFD construído à mão
valido_regex = validar_link_regex(link)  # re.match() do Python
# resultado: sempre concordam ✅
```

---

## 🕵️ Funcionalidades do Scraper

Após a validação bem-sucedida do link, o programa oferece:

### 1. Tópicos do Artigo
Extrai os títulos do índice da página usando as ERs:
```python
r'<div class="vector-toc-text".*?>[\s\S]*?</div>'  # bloco do índice
r'<span>(.*?)</span>'                               # título de cada tópico
```

### 2. Imagens
Coleta os nomes de arquivo de todas as imagens do artigo (figuras e infoboxes):
```python
r'<figure[\s\S]*?</figure>'                                   # elementos figure
r'src="[^"]*/([^/]+\.(?:jpg|png|svg|jpeg))"'                  # nome do arquivo
```

### 3. Links para Outros Artigos
Encontra todos os links internos da Wikipédia presentes no artigo:
```python
r'href="(/wiki/[^":#]+)"'   # links internos sem âncoras ou namespaces
```

### 4. Definição + Simulação do AFD
Exibe a definição formal `M = (Q, Σ, δ, q₀, F)` e simula a execução do AFD no link informado, estado a estado.

---

## 🚀 Como Usar

### Pré-requisitos

- Python 3.x (sem dependências externas — apenas bibliotecas padrão)

### Executando

```bash
python web_scraping_er_afd.py
```

### Fluxo de uso

```
Digite o link do artigo da Wikipedia: https://pt.wikipedia.org/wiki/Linguagem_formal

Link valido! (reconhecido pelo AFD construido a mao)
Conferencia -> AFD=True | regex=True | concordam

MENU
1 - Listar topicos do artigo
2 - Listar imagens
3 - Listar links para outros artigos
4 - Mostrar o AFD da validacao (definicao + simulacao)
0 - Sair

Escolha uma opcao:
```

---

## 📌 Exemplos de Execução

### Tópicos — Artigo sobre Linguagem Formal

```
TOPICOS DO ARTIGO:

- Definição
- Palavras e linguagens
- Operações sobre linguagens
- Linguagens formais e máquinas abstratas
- Complexidade de linguagens formais
- Aplicações
- Ver também
- Referências

Total de topicos: 8
```

### Imagens — Artigo sobre Python

```
IMAGENS DO ARTIGO:

- Python-logo-notext.svg
- Guido_van_Rossum_OSCON_2006.jpg
- ...

Total de imagens: 5
```

---

## 📦 Requisitos

| Item | Versão |
|---|---|
| Python | ≥ 3.6 |
| `urllib` | padrão (built-in) |
| `re` | padrão (built-in) |
| `string` | padrão (built-in) |

Nenhuma instalação extra necessária. ✅

---

## 📚 Conceitos de LFC Aplicados

| Conceito | Onde aparece no código |
|---|---|
| Expressão Regular | `validar_link_regex()` — padrão `r"^https://..."` |
| AFD (definição formal) | `descrever_afd()` — imprime Q, Σ, δ, q₀, F |
| Função de transição δ | `delta(estado, c)` — implementada como função Python |
| Estado poço (trap) | Constante `TRAP = -1`, retorno imediato em `validar_link_afd()` |
| Simulador de AFD | `mostrar_trace(link)` — percorre a cadeia e exibe cada transição |
| Teorema de Kleene | Comparação entre AFD e `re.match()` — sempre concordam |

---

<div align="center">

Feito com 🧠 teoria e 🐍 Python  

**Linguagens Formais e Compiladores — 2026**

</div>