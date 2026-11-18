# Sistema Especialista com Aprendizado Supervisionado: Recomendação de Investimentos

Projeto didático em Python que combina **aprendizado de máquina** e **regras**. Um classificador (árvore de decisão) aprende a prever o **perfil de investidor** a partir de exemplos rotulados. Essa previsão entra como um fato em um sistema especialista, cujas regras, escritas pela equipe, geram a recomendação e **explicam o porquê** de cada conclusão.

> **Aviso:** projeto educacional, com dados fictícios. Não substitui a orientação de um consultor financeiro.

## Requisitos

- Python 3.8 ou superior
- Bibliotecas: `pandas` e `scikit-learn`

```bash
pip install pandas scikit-learn
```

## Como executar

```bash
python sistema_especialista_investimentos.py
```

O programa treina o modelo, mostra a avaliação e depois faz as perguntas. Responda digitando o **número** da opção (e, no prazo, o número de anos).

## Como funciona

```
dados rotulados -> [treino] -> modelo (árvore de decisão)
                                   |
respostas do usuário --------------+--> fatos --> [motor de inferência + regras] --> recomendação + explicação
```

| Componente | Onde está no código | O que faz |
|---|---|---|
| Dataset rotulado | `dados` | 30 exemplos fictícios com o perfil já definido |
| Treino e avaliação | `treinar_modelo()` | Separa treino e teste, treina a árvore e mostra as métricas |
| Previsão | `prever_perfil()` | Usa o modelo para prever o perfil de uma nova pessoa |
| Base de conhecimento | `REGRAS` | Regras SE... ENTÃO... escritas pela equipe |
| Motor de inferência | `motor_de_inferencia()` | Dispara regras até nenhuma regra nova poder ser usada (encadeamento para frente) |
| Interface | `perguntar()`, `perguntar_anos()`, `main()` | Faz as perguntas e mostra o resultado |
| Explicação | final de `main()` | Lista o perfil previsto e as regras utilizadas |

### O que vem do modelo e o que vem das regras

- **Do modelo:** apenas o **perfil do investidor** (conservador, moderado ou arrojado), previsto a partir do prazo e da reação a uma queda.
- **Das regras da equipe:** a verificação de dívidas e reserva, a liberação para investir e **todas as recomendações de investimento**.

## Aprendizado de máquina

### Dataset (dados fictícios)

São 30 exemplos inventados para demonstração, divididos em 10 por perfil. Eles não vêm de pessoas reais e **não validam uma ferramenta real**.

| Atributo | Significado |
|---|---|
| `horizonte_anos` | Por quantos anos a pessoa pretende investir |
| `reacao_queda` | `1` = venderia, `2` = manteria, `3` = compraria mais (queda de 10%) |
| **`perfil` (rótulo)** | `conservador`, `moderado` ou `arrojado` |

**Critério de rotulagem** (definido manualmente pela equipe):

- **conservador:** prazo de até 2 anos **ou** venderia numa queda
- **moderado:** manteria numa queda (prazo acima de 2 anos) **ou** compraria mais, mas com prazo de 3 a 4 anos
- **arrojado:** compraria mais numa queda **e** prazo de 5 anos ou mais

### Treino e teste

- 75% dos exemplos para treino (22) e 25% para teste (8), com `stratify` para manter a proporção das classes e `random_state=42` para a divisão ser reproduzível.
- Modelo: `DecisionTreeClassifier(max_depth=4)`.
- O rótulo nunca entra nos atributos usados para prever.

### Resultado obtido

```
Acurácia no teste: 87.5%
             conservador  moderado  arrojado
conservador            3         0         0
moderado               1         2         0
arrojado               0         0         2
```

O modelo errou um exemplo (um perfil moderado foi previsto como conservador). Com apenas 8 exemplos de teste, **essa acurácia não prova eficácia em situações reais**, e o programa deixa esse aviso na tela.

## Perguntas feitas

| Fato | Pergunta | Valores |
|---|---|---|
| `tem_dividas` | Possui dívidas? | `sim`, `nao` |
| `tem_reserva` | Tem reserva de emergência (cerca de 6 meses de gastos)? | `sim`, `nao` |
| `horizonte_anos` | Por quantos anos vai investir? | número inteiro de 1 a 60 |
| `reacao_queda` | O que faria se o investimento caísse 10% em um mês? | `vende`, `mantem`, `compra_mais` |
| `experiencia` | Qual sua experiência com investimentos? | `iniciante`, `intermediario`, `avancado` |

O prazo em anos é convertido em categoria para as regras: `curto` (até 2 anos), `medio` (3 a 5) e `longo` (mais de 5).

## Regras

**Camada 1: prioridades** (bloqueiam ou liberam o investimento)

| Regra | SE | ENTÃO |
|---|---|---|
| R1 | `tem_dividas = sim` | Quitar as dívidas antes de investir |
| R2 | `tem_dividas = nao` E `tem_reserva = nao` | Montar a reserva de emergência |
| R3 | `tem_dividas = nao` E `tem_reserva = sim` | `pode_investir = True` |

**Camada 2: perfil** (usam a previsão do modelo, `perfil_ml`)

| Regra | SE | ENTÃO |
|---|---|---|
| R4 | pode investir E `perfil_ml = conservador` | `perfil = conservador` |
| R5 | pode investir E `perfil_ml = moderado` | `perfil = moderado` |
| R6 | pode investir E `perfil_ml = arrojado` | `perfil = arrojado` |

**Camada 3: recomendação** (usam o fato `perfil` e as respostas do usuário)

| Regra | SE | ENTÃO |
|---|---|---|
| R7 | `perfil = conservador` | Tesouro Selic, CDB e LCI/LCA |
| R8 | `perfil = moderado` | Renda fixa + parte em FIIs e fundos multimercado |
| R9 | `perfil = arrojado` E `experiencia = iniciante` | ETFs diversificados |
| R10 | `perfil = arrojado` E experiência intermediária/avançada E `horizonte = longo` | Ações, ETFs e FIIs |
| R11 | `perfil = arrojado` E experiência intermediária/avançada E `horizonte = medio` | ETFs, FIIs e renda fixa |

### Origem das regras

As regras foram definidas pela equipe a partir de princípios básicos de educação financeira: quitar dívidas caras e formar reserva de emergência antes de investir, e adequar o risco ao perfil, ao prazo e à experiência do investidor.

## Exemplo de execução

Entradas: sem dívidas, com reserva, 10 anos, compraria mais numa queda, experiência avançada.

```
=== RESULTADO ===
Seu perfil de investidor: arrojado
-> Ações, ETFs e FIIs.

=== POR QUE? (regras utilizadas) ===
[Modelo] Perfil previsto pelo modelo: arrojado
[R3] Sem dívidas e com reserva, você está pronto para investir.
[R6] O modelo de aprendizado de máquina previu perfil arrojado (a partir do prazo e da reação a quedas).
[R10] Perfil arrojado, com experiência e prazo longo, comporta renda variável.
```

## Como evoluir o projeto

- **Nova regra:** inclua um dicionário em `REGRAS`, sem mexer no motor. Valor simples nas condições significa "igual a"; um `set` significa "igual a qualquer um destes".
- **Mais dados:** acrescente linhas ao `dados` e treine de novo. Em um projeto real, documente quem rotulou os exemplos e com quais evidências.
- **Nova pergunta:** adicione uma entrada em `PERGUNTAS` (ou uma pergunta numérica, como a do prazo).

## Limitações

- O dataset é fictício, pequeno e rotulado manualmente; o modelo reflete o critério da equipe, não o comportamento de pessoas reais.
- A acurácia foi medida em apenas 8 exemplos de teste e não prova eficácia real.
- As regras são fixas e escritas à mão (por exemplo, a exigência de reserva de 6 meses).
- Não considera valores em reais, renda, objetivos pessoais nem a situação do mercado.
- Prazos fora do intervalo visto no treino (1 a 25 anos) geram um aviso de menor confiabilidade.
- As recomendações são sugestões e devem passar por revisão humana.

## Estrutura do projeto

```
.
├── sistema_especialista_investimentos.py
├── README.md
└── ETICA_E_IMPACTOS.md
```
