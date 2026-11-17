"""
Sistema Especialista: Recomendação de Investimentos (projeto didático)

Como funciona:
  1. Base de conhecimento -> lista de REGRAS (SE ... ENTÃO ...)
  2. Fatos                -> respostas do usuário (e fatos novos que as regras geram)
  3. Motor de inferência  -> encadeamento para frente: repete até nenhuma regra nova disparar
  4. Explicação           -> mostra quais regras dispararam e por quê
"""

# =====================================================================
# 1) BASE DE CONHECIMENTO
# Cada regra tem:
#   id       -> nome da regra
#   se       -> condições (todas precisam ser verdadeiras)
#               valor simples  = igual a esse valor
#               valor em set   = igual a QUALQUER um dos valores do set
#   entao    -> fatos novos que a regra adiciona
#   mensagem -> (opcional) recomendação mostrada ao usuário
#   porque   -> texto usado na explicação
#
# Conflitos: as regras de perfil (R4, R5, R6 e R7) foram escritas com
# condições que NUNCA se sobrepõem, então um usuário só recebe um perfil.
# =====================================================================
REGRAS = [
    # --- Camada 1: prioridades (bloqueiam o investimento) ---
    {
        "id": "R1",
        "se": {"tem_dividas": "sim"},
        "entao": {"bloqueado": True},
        "mensagem": "Quite suas dívidas antes de investir.",
        "porque": "Os juros de dívidas (cartão, cheque especial) costumam ser maiores que qualquer rendimento.",
    },
    {
        "id": "R2",
        "se": {"tem_dividas": "nao", "tem_reserva": "nao"},
        "entao": {"bloqueado": True},
        "mensagem": "Monte sua reserva de emergência (Tesouro Selic ou CDB com liquidez diária).",
        "porque": "Sem reserva, qualquer imprevisto força a venda de investimentos na hora errada.",
    },
    {
        "id": "R3",
        "se": {"tem_dividas": "nao", "tem_reserva": "sim"},
        "entao": {"pode_investir": True},
        "porque": "Sem dívidas e com reserva, você está pronto para investir.",
    },

    # --- Camada 2: descobrir o perfil (gera o fato 'perfil') ---
    {
        "id": "R4",
        "se": {"pode_investir": True, "horizonte": {"medio", "longo"}, "reacao_queda": "vende"},
        "entao": {"perfil": "conservador"},
        "porque": "Quem venderia numa queda de 10% tem baixa tolerância a risco.",
    },
    {
        "id": "R5",
        "se": {"pode_investir": True, "horizonte": {"medio", "longo"}, "reacao_queda": "mantem"},
        "entao": {"perfil": "moderado"},
        "porque": "Quem mantém a calma numa queda tem tolerância média a risco.",
    },
    {
        "id": "R6",
        "se": {"pode_investir": True, "horizonte": {"medio", "longo"}, "reacao_queda": "compra_mais"},
        "entao": {"perfil": "arrojado"},
        "porque": "Quem aproveitaria a queda para comprar mais tem alta tolerância a risco.",
    },
    {
        "id": "R7",
        "se": {"pode_investir": True, "horizonte": "curto"},
        "entao": {"perfil": "conservador"},
        "porque": "Com prazo curto não há tempo para se recuperar de quedas, então o perfil é conservador.",
    },

    # --- Camada 3: recomendações (usam o fato 'perfil') ---
    {
        "id": "R8",
        "se": {"perfil": "conservador"},
        "entao": {},
        "mensagem": "Tesouro Selic, CDB e LCI/LCA.",
        "porque": "Perfil conservador prioriza segurança e liquidez.",
    },
    {
        "id": "R9",
        "se": {"perfil": "moderado"},
        "entao": {},
        "mensagem": "Maior parte em renda fixa, com uma parcela em fundos imobiliários (FIIs) e fundos multimercado.",
        "porque": "Perfil moderado equilibra segurança e rentabilidade.",
    },
    {
        "id": "R10",
        "se": {"perfil": "arrojado", "experiencia": "iniciante"},
        "entao": {},
        "mensagem": "ETFs diversificados (por exemplo, de Ibovespa) em vez de ações individuais.",
        "porque": "Iniciantes ficam menos expostos ao risco de uma única empresa com ETFs.",
    },
    {
        "id": "R11",
        "se": {"perfil": "arrojado", "experiencia": {"intermediario", "avancado"}, "horizonte": "longo"},
        "entao": {},
        "mensagem": "Ações, ETFs e FIIs.",
        "porque": "Perfil arrojado, com experiência e prazo longo, comporta renda variável.",
    },
    {
        "id": "R12",
        "se": {"perfil": "arrojado", "experiencia": {"intermediario", "avancado"}, "horizonte": "medio"},
        "entao": {},
        "mensagem": "Combinação de ETFs, FIIs e renda fixa (prazo médio pede mais cautela).",
        "porque": "O prazo médio limita a exposição a renda variável.",
    },
]

# =====================================================================
# 2) PERGUNTAS (cada resposta vira um fato)
# formato: (nome_do_fato, texto_da_pergunta, [(valor, rótulo), ...])
# =====================================================================
PERGUNTAS = [
    ("tem_dividas", "Você possui dívidas (cartão, cheque especial, empréstimos)?",
     [("sim", "Sim"), ("nao", "Não")]),
    ("tem_reserva", "Você tem reserva de emergência (cerca de 6 meses de gastos)?",
     [("sim", "Sim"), ("nao", "Não")]),
    ("horizonte", "Por quanto tempo pretende deixar o dinheiro investido?",
     [("curto", "Até 2 anos"), ("medio", "De 2 a 5 anos"), ("longo", "Mais de 5 anos")]),
    ("reacao_queda", "Se seu investimento caísse 10% em um mês, o que você faria?",
     [("vende", "Venderia tudo"), ("mantem", "Manteria"), ("compra_mais", "Compraria mais")]),
    ("experiencia", "Qual sua experiência com investimentos?",
     [("iniciante", "Iniciante"), ("intermediario", "Intermediário"), ("avancado", "Avançado")]),
]


def perguntar(texto, opcoes):
    """Mostra um menu numerado e repete até o usuário digitar uma opção válida."""
    print(f"\n{texto}")
    for i, (_, rotulo) in enumerate(opcoes, start=1):
        print(f"  {i}) {rotulo}")
    while True:
        resposta = input("Escolha: ").strip()
        if resposta.isdigit() and 1 <= int(resposta) <= len(opcoes):
            return opcoes[int(resposta) - 1][0]
        print("Opção inválida, tente novamente.")


# =====================================================================
# 3) MOTOR DE INFERÊNCIA (encadeamento para frente)
# =====================================================================
def condicao_ok(condicoes, fatos):
    """Verifica se TODAS as condições da regra batem com os fatos atuais."""
    for fato, esperado in condicoes.items():
        valor = fatos.get(fato)
        if isinstance(esperado, set):      # "qualquer um destes valores"
            if valor not in esperado:
                return False
        elif valor != esperado:            # igual a um valor específico
            return False
    return True


def motor_de_inferencia(fatos):
    """Dispara regras até que nenhuma regra nova possa ser disparada."""
    disparadas = []                        # regras já usadas, em ordem
    ids_disparados = set()
    mudou = True
    while mudou:                           # novos fatos podem liberar novas regras
        mudou = False
        for regra in REGRAS:
            if regra["id"] in ids_disparados:
                continue                   # cada regra dispara só uma vez
            if condicao_ok(regra["se"], fatos):
                fatos.update(regra["entao"])   # adiciona os fatos novos
                disparadas.append(regra)
                ids_disparados.add(regra["id"])
                mudou = True
    return disparadas


# =====================================================================
# 4) PROGRAMA PRINCIPAL
# =====================================================================
def main():
    print("=== Sistema Especialista: Recomendação de Investimentos ===")

    # Coleta os fatos iniciais
    fatos = {}
    for nome, texto, opcoes in PERGUNTAS:
        fatos[nome] = perguntar(texto, opcoes)

    # Roda o motor de inferência
    disparadas = motor_de_inferencia(fatos)

    # Mostra o resultado (regras que têm mensagem)
    print("\n=== RESULTADO ===")
    if "perfil" in fatos:
        print(f"Seu perfil de investidor: {fatos['perfil']}")
    for regra in disparadas:
        if "mensagem" in regra:
            print(f"-> {regra['mensagem']}")

    # Módulo de explicação (mostra todas as regras usadas)
    print("\n=== POR QUE? (regras utilizadas) ===")
    for regra in disparadas:
        print(f"[{regra['id']}] {regra['porque']}")

    print("\nAviso: sistema didático, não substitui um consultor financeiro.")


if __name__ == "__main__":
    main()
