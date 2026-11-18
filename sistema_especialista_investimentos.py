"""
Sistema Especialista com Aprendizado Supervisionado
Recomendação de Investimentos (projeto didático)

Visão geral:
  1. Um CLASSIFICADOR (árvore de decisão) aprende, com exemplos rotulados,
     a prever o perfil do investidor (conservador, moderado ou arrojado).
  2. A previsão do modelo vira um FATO ("perfil_ml").
  3. As REGRAS, escritas pela equipe, usam esse fato junto com as respostas
     do usuário para chegar à recomendação.
  4. O MOTOR DE INFERÊNCIA (encadeamento para frente) dispara as regras
     e a seção "POR QUE?" explica o resultado.

Requisitos: pip install pandas scikit-learn
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import accuracy_score, confusion_matrix

# =====================================================================
# 1) DATASET ROTULADO (DADOS FICTÍCIOS)
# São 30 exemplos inventados para demonstração: não validam uma ferramenta real.
#
# Atributos:
#   horizonte_anos -> por quantos anos a pessoa pretende investir
#   reacao_queda   -> 1 = venderia, 2 = manteria, 3 = compraria mais (queda de 10%)
# Rótulo: perfil
#
# Critério de rotulagem (definido pela equipe, de forma manual):
#   conservador -> prazo de até 2 anos OU venderia numa queda
#   moderado    -> manteria numa queda (prazo acima de 2 anos)
#                  OU compraria mais, mas com prazo de apenas 3 a 4 anos
#   arrojado    -> compraria mais numa queda E prazo de 5 anos ou mais
# =====================================================================
dados = pd.DataFrame({
    "horizonte_anos": [1, 1, 1, 2, 2, 2, 3, 5, 8, 12,       # conservador
                       3, 4, 5, 6, 7, 10, 12, 15, 3, 4,     # moderado
                       5, 6, 7, 8, 9, 10, 12, 15, 20, 25],  # arrojado
    "reacao_queda":   [1, 2, 3, 1, 2, 3, 1, 1, 1, 1,
                       2, 2, 2, 2, 2, 2, 2, 2, 3, 3,
                       3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    "perfil": ["conservador"] * 10 + ["moderado"] * 10 + ["arrojado"] * 10,
})

# Tradução das respostas do menu para o número que o modelo usa
CODIGO_REACAO = {"vende": 1, "mantem": 2, "compra_mais": 3}


# =====================================================================
# 2) TREINO E AVALIAÇÃO DO MODELO
# =====================================================================
def treinar_modelo():
    """Treina a árvore de decisão, mostra a avaliação e devolve o modelo."""
    X = dados[["horizonte_anos", "reacao_queda"]]   # atributos (o rótulo NÃO entra aqui)
    y = dados["perfil"]                             # rótulo

    # 75% para treino e 25% para teste. O teste serve para medir o modelo
    # em exemplos que ele não viu. stratify mantém a proporção das classes
    # e random_state torna a divisão reproduzível.
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    # max_depth limita o tamanho da árvore (evita decorar os dados de treino)
    modelo = DecisionTreeClassifier(max_depth=4, random_state=42)
    modelo.fit(X_treino, y_treino)                  # aprende SOMENTE com o treino

    # Avaliação no conjunto de teste
    previsoes = modelo.predict(X_teste)
    classes = ["conservador", "moderado", "arrojado"]
    matriz = confusion_matrix(y_teste, previsoes, labels=classes)

    print("=== TREINAMENTO DO MODELO (dados fictícios) ===")
    print(f"Treino: {len(X_treino)} exemplos | Teste: {len(X_teste)} exemplos")
    print(f"Acurácia no teste: {accuracy_score(y_teste, previsoes):.1%}")
    print("Matriz de confusão (linhas = real, colunas = previsto):")
    print(pd.DataFrame(matriz, index=classes, columns=classes))
    print("Condições aprendidas pela árvore:")
    print(export_text(modelo, feature_names=list(X.columns)))
    print("Atenção: com poucos exemplos de teste, a acurácia não prova eficácia real.")

    # Guardamos o intervalo visto no treino para avisar sobre entradas fora dele
    intervalo = (X_treino["horizonte_anos"].min(), X_treino["horizonte_anos"].max())
    return modelo, intervalo


def prever_perfil(modelo, anos, reacao_codigo):
    """Usa o modelo treinado para prever o perfil de uma nova pessoa."""
    novo_caso = pd.DataFrame([{"horizonte_anos": anos, "reacao_queda": reacao_codigo}])
    return modelo.predict(novo_caso)[0]


# =====================================================================
# 3) BASE DE CONHECIMENTO (regras escritas pela equipe)
# Cada regra tem:
#   id       -> nome da regra
#   se       -> condições (todas precisam ser verdadeiras)
#               valor simples = igual a esse valor
#               valor em set  = igual a QUALQUER um dos valores do set
#   entao    -> fatos novos que a regra adiciona
#   mensagem -> (opcional) recomendação mostrada ao usuário
#   porque   -> texto usado na explicação
#
# O fato "perfil_ml" vem do MODELO. Todo o resto vem das regras da equipe.
# =====================================================================
REGRAS = [
    # --- Camada 1: prioridades (bloqueiam ou liberam o investimento) ---
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

    # --- Camada 2: perfil (usa a previsão do modelo, mas só se puder investir) ---
    {
        "id": "R4",
        "se": {"pode_investir": True, "perfil_ml": "conservador"},
        "entao": {"perfil": "conservador"},
        "porque": "O modelo de aprendizado de máquina previu perfil conservador (a partir do prazo e da reação a quedas).",
    },
    {
        "id": "R5",
        "se": {"pode_investir": True, "perfil_ml": "moderado"},
        "entao": {"perfil": "moderado"},
        "porque": "O modelo de aprendizado de máquina previu perfil moderado (a partir do prazo e da reação a quedas).",
    },
    {
        "id": "R6",
        "se": {"pode_investir": True, "perfil_ml": "arrojado"},
        "entao": {"perfil": "arrojado"},
        "porque": "O modelo de aprendizado de máquina previu perfil arrojado (a partir do prazo e da reação a quedas).",
    },

    # --- Camada 3: recomendações (usam o fato 'perfil' e outros fatos) ---
    {
        "id": "R7",
        "se": {"perfil": "conservador"},
        "entao": {},
        "mensagem": "Tesouro Selic, CDB e LCI/LCA.",
        "porque": "Perfil conservador prioriza segurança e liquidez.",
    },
    {
        "id": "R8",
        "se": {"perfil": "moderado"},
        "entao": {},
        "mensagem": "Maior parte em renda fixa, com uma parcela em fundos imobiliários (FIIs) e fundos multimercado.",
        "porque": "Perfil moderado equilibra segurança e rentabilidade.",
    },
    {
        "id": "R9",
        "se": {"perfil": "arrojado", "experiencia": "iniciante"},
        "entao": {},
        "mensagem": "ETFs diversificados (por exemplo, de Ibovespa) em vez de ações individuais.",
        "porque": "Iniciantes ficam menos expostos ao risco de uma única empresa com ETFs.",
    },
    {
        "id": "R10",
        "se": {"perfil": "arrojado", "experiencia": {"intermediario", "avancado"}, "horizonte": "longo"},
        "entao": {},
        "mensagem": "Ações, ETFs e FIIs.",
        "porque": "Perfil arrojado, com experiência e prazo longo, comporta renda variável.",
    },
    {
        "id": "R11",
        "se": {"perfil": "arrojado", "experiencia": {"intermediario", "avancado"}, "horizonte": "medio"},
        "entao": {},
        "mensagem": "Combinação de ETFs, FIIs e renda fixa (prazo médio pede mais cautela).",
        "porque": "O prazo médio limita a exposição a renda variável.",
    },
]

# =====================================================================
# 4) PERGUNTAS DE MENU (cada resposta vira um fato)
# formato: fato -> (texto da pergunta, [(valor, rótulo), ...])
# O prazo (em anos) é perguntado à parte, porque é um número.
# =====================================================================
PERGUNTAS = {
    "tem_dividas": ("Você possui dívidas (cartão, cheque especial, empréstimos)?",
                    [("sim", "Sim"), ("nao", "Não")]),
    "tem_reserva": ("Você tem reserva de emergência (cerca de 6 meses de gastos)?",
                    [("sim", "Sim"), ("nao", "Não")]),
    "reacao_queda": ("Se seu investimento caísse 10% em um mês, o que você faria?",
                     [("vende", "Venderia tudo"), ("mantem", "Manteria"),
                      ("compra_mais", "Compraria mais")]),
    "experiencia": ("Qual sua experiência com investimentos?",
                    [("iniciante", "Iniciante"), ("intermediario", "Intermediário"),
                     ("avancado", "Avançado")]),
}


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


def perguntar_anos(texto, minimo=1, maximo=60):
    """Pergunta um número inteiro de anos e valida os limites."""
    print(f"\n{texto}")
    while True:
        resposta = input(f"Digite um número entre {minimo} e {maximo}: ").strip()
        if resposta.isdigit() and minimo <= int(resposta) <= maximo:
            return int(resposta)
        print("Valor inválido, tente novamente.")


def categoria_horizonte(anos):
    """Converte anos em categoria, usada pelas regras R10 e R11."""
    if anos <= 2:
        return "curto"
    if anos <= 5:
        return "medio"
    return "longo"


# =====================================================================
# 5) MOTOR DE INFERÊNCIA (encadeamento para frente)
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
# 6) PROGRAMA PRINCIPAL
# =====================================================================
def main():
    print("=== Sistema Especialista: Recomendação de Investimentos ===\n")
    modelo, (min_anos, max_anos) = treinar_modelo()

    # Coleta os fatos informados pelo usuário
    fatos = {}
    fatos["tem_dividas"] = perguntar(*PERGUNTAS["tem_dividas"])
    fatos["tem_reserva"] = perguntar(*PERGUNTAS["tem_reserva"])
    anos = perguntar_anos("Por quantos anos pretende deixar o dinheiro investido?")
    fatos["horizonte"] = categoria_horizonte(anos)
    fatos["reacao_queda"] = perguntar(*PERGUNTAS["reacao_queda"])
    fatos["experiencia"] = perguntar(*PERGUNTAS["experiencia"])

    # O modelo prevê o perfil e a previsão entra como um fato para as regras
    fatos["perfil_ml"] = prever_perfil(modelo, anos, CODIGO_REACAO[fatos["reacao_queda"]])

    # Roda o motor de inferência
    disparadas = motor_de_inferencia(fatos)

    # Mostra o resultado
    print("\n=== RESULTADO ===")
    if "perfil" in fatos:
        print(f"Seu perfil de investidor: {fatos['perfil']}")
    mensagens = [r["mensagem"] for r in disparadas if "mensagem" in r]
    for mensagem in mensagens:
        print(f"-> {mensagem}")
    if fatos.get("pode_investir") and not mensagens:
        # Segurança: nenhuma regra cobriu esta combinação de fatos
        print("-> Nenhuma regra cobre o seu caso; procure orientação profissional.")

    # Avisos de confiabilidade
    if not min_anos <= anos <= max_anos:
        print(f"Aviso: prazo fora do intervalo visto no treino ({min_anos} a {max_anos} anos); "
              "a previsão do modelo pode ser menos confiável.")

    # Módulo de explicação (mostra todas as regras usadas)
    print("\n=== POR QUE? (regras utilizadas) ===")
    if "perfil_ml" in fatos and fatos.get("pode_investir"):
        print(f"[Modelo] Perfil previsto pelo modelo: {fatos['perfil_ml']}")
    for regra in disparadas:
        print(f"[{regra['id']}] {regra['porque']}")

    print("\nAviso: sistema didático (dados fictícios), sujeito a revisão humana; "
          "não substitui um consultor financeiro.")


if __name__ == "__main__":
    main()
