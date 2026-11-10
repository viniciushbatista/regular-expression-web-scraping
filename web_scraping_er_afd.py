import urllib.request
import re
import string

# =========================================================
# VALIDAÇÃO DO LINK POR AFD (Autômato Finito Determinístico)
# ---------------------------------------------------------
# Em vez de validar só com re.match, construímos AQUI, à mão, o AFD
# que reconhece EXATAMENTE a mesma linguagem da expressão regular:
#
#     ^https://pt\.wikipedia\.org/wiki/[A-Za-z0-9_()%\-]+$
#
# A linguagem é: a cadeia fixa "https://pt.wikipedia.org/wiki/"
# seguida de UM OU MAIS caracteres válidos de artigo.
#
# O AFD é simulado como o professor descreve um simulador de AFD:
#   - guardamos o ESTADO ATUAL
#   - lemos a cadeia símbolo a símbolo
#   - a FUNÇÃO DE TRANSIÇÃO (delta) decide o próximo estado
# Isso liga o conceito (autômato / linguagem regular) à aplicação.
# =========================================================

PREFIXO = "https://pt.wikipedia.org/wiki/"   # cadeia fixa (30 símbolos)
N = len(PREFIXO)                             # 30
PREFIXO_COMPLETO = N                         # estado 30: leu todo o prefixo
ACEITA = N + 1                               # estado 31: estado de aceitação
TRAP = -1                                    # estado de erro (poço)

# classe de caractere [A-Za-z0-9_()%\-]
CHARS_ARTIGO = set(string.ascii_letters + string.digits + "_()%-")


def eh_char_artigo(c):
    return c in CHARS_ARTIGO


def delta(estado, c):
    # função de transição do AFD
    if estado == TRAP:                      # erro é poço: nunca sai dele
        return TRAP
    if estado < N:                          # consumindo o prefixo, char a char
        return estado + 1 if c == PREFIXO[estado] else TRAP
    if estado == PREFIXO_COMPLETO:          # precisa de >= 1 caractere de artigo
        return ACEITA if eh_char_artigo(c) else TRAP
    if estado == ACEITA:                    # auto-laço nos demais caracteres
        return ACEITA if eh_char_artigo(c) else TRAP
    return TRAP


def validar_link_afd(link):
    estado = 0                              # estado inicial q0
    for c in link:
        estado = delta(estado, c)
        if estado == TRAP:
            return False
    return estado == ACEITA                 # aceita só se terminar no estado final


def validar_link_regex(link):
    # validação equivalente com a ER do Python (usada só para conferência)
    padrao = r"^https://pt\.wikipedia\.org/wiki/[A-Za-z0-9_()%\-]+$"
    return re.match(padrao, link) is not None


def _rotulo(estado):
    if estado == TRAP:
        return "ERRO(trap)"
    if estado == ACEITA:
        return "q31 ACEITA"
    if estado == PREFIXO_COMPLETO:
        return "q30 (prefixo completo)"
    return f"q{estado}"


def mostrar_trace(link):
    # mostra o AFD "andando" pela cadeia (ótimo para a apresentação)
    print("\nSIMULAÇÃO DO AFD (estado a estado):\n")
    estado = 0
    print(f"  inicio -> {_rotulo(estado)}")
    for c in link:
        novo = delta(estado, c)
        print(f"  le {c!r:5} : {_rotulo(estado)} -> {_rotulo(novo)}")
        estado = novo
        if estado == TRAP:
            print("\n  Caiu no estado de ERRO: a cadeia e REJEITADA.")
            return
    print(f"\n  Terminou em {_rotulo(estado)} -> " +
          ("ACEITA" if estado == ACEITA else "REJEITA"))


def descrever_afd():
    # definição formal M = (Q, Sigma, delta, q0, F)
    print("\nDEFINICAO FORMAL DO AFD  M = (Q, Sigma, delta, q0, F)\n")
    print("  Q  (estados):   q0, q1, ..., q31 e ERRO(trap)")
    print("  Sigma (alfabeto): caracteres ASCII imprimiveis")
    print("  q0 (inicial):   q0")
    print("  F  (aceitacao): { q31 }")
    print("\n  delta (funcao de transicao):")
    print('   - qi --PREFIXO[i]--> q(i+1)      para i = 0..29   (le a cadeia fixa)')
    print('     cadeia fixa = "https://pt.wikipedia.org/wiki/"')
    print("   - q30 --[A-Za-z0-9_()%-]--> q31  (1o caractere do artigo)")
    print("   - q31 --[A-Za-z0-9_()%-]--> q31  (auto-laco: demais caracteres)")
    print("   - qualquer outra transicao --> ERRO(trap)")


# =========================================================
# BAIXAR HTML
# =========================================================
def baixar_html(link):
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(link, headers=headers)
    response = urllib.request.urlopen(req)
    html = response.read().decode("utf-8")
    return html


# =========================================================
# EXTRAIR TÓPICOS DO ÍNDICE
# =========================================================
def extrair_topicos(html):
    padrao_blocos = r'<div class="vector-toc-text".*?>[\s\S]*?</div>'
    blocos = re.findall(padrao_blocos, html)

    print("\nTOPICOS DO ARTIGO:\n")
    topicos = []
    for bloco in blocos:
        padrao_titulo = r'<span>(.*?)</span>'
        resultado = re.findall(padrao_titulo, bloco)
        for r in resultado:
            topicos.append(r)
            print("-", r)
    print("\nTotal de topicos:", len(topicos))


# =========================================================
# EXTRAIR IMAGENS
# =========================================================
def extrair_imagens(html):
    imagens = []

    figuras = re.findall(r'<figure[\s\S]*?</figure>', html)
    for f in figuras:
        imgs = re.findall(r'src="[^"]*/([^/]+\.(?:jpg|png|svg|jpeg))"', f)
        for i in imgs:
            imagens.append(i)

    tabelas = re.findall(r'<table class="infobox[\s\S]*?</table>', html)
    for t in tabelas:
        imgs = re.findall(r'src="[^"]*/([^/]+\.(?:jpg|png|svg|jpeg))"', t)
        for i in imgs:
            imagens.append(i)

    imagens = list(set(imagens))

    print("\nIMAGENS DO ARTIGO:\n")
    for img in imagens:
        print("-", img)
    print("\nTotal de imagens:", len(imagens))


# =========================================================
# EXTRAIR LINKS DE OUTROS ARTIGOS
# =========================================================
def extrair_links(html):
    padrao = r'href="(/wiki/[^":#]+)"'
    links = re.findall(padrao, html)
    links = list(set(links))

    print("\nLINKS PARA OUTROS ARTIGOS:\n")
    for l in links:
        print("https://pt.wikipedia.org" + l)
    print("\nTotal de links encontrados:", len(links))


# =========================================================
# PROGRAMA PRINCIPAL
# =========================================================
if __name__ == "__main__":
    link = input("Digite o link do artigo da Wikipedia: ")

    valido_afd = validar_link_afd(link)         # validação pelo AFD (à mão)
    valido_regex = validar_link_regex(link)     # conferência com o re do Python

    if valido_afd:
        print("\nLink valido! (reconhecido pelo AFD construido a mao)")
        print(f"Conferencia -> AFD={valido_afd} | regex={valido_regex} | "
              + ("concordam" if valido_afd == valido_regex else "DIVERGEM!"))

        html = baixar_html(link)

        while True:
            print("\nMENU")
            print("1 - Listar topicos do artigo")
            print("2 - Listar imagens")
            print("3 - Listar links para outros artigos")
            print("4 - Mostrar o AFD da validacao (definicao + simulacao)")
            print("0 - Sair")

            opcao = input("Escolha uma opcao: ")

            if opcao == "1":
                extrair_topicos(html)
            elif opcao == "2":
                extrair_imagens(html)
            elif opcao == "3":
                extrair_links(html)
            elif opcao == "4":
                descrever_afd()
                mostrar_trace(link)
            elif opcao == "0":
                break
            else:
                print("Opcao invalida")
    else:
        print("\nLink invalido da Wikipedia (rejeitado pelo AFD).")
        mostrar_trace(link)
