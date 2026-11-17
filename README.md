# Sistema Especialista: Recomendação de Investimentos

Projeto didático em Python que simula o raciocínio de um consultor de investimentos. O programa faz algumas perguntas ao usuário, descobre o **perfil de investidor** dele e recomenda tipos de investimento, **explicando o porquê** de cada conclusão.

> **Aviso:** projeto educacional. Não substitui a orientação de um consultor financeiro.

## Requisitos

- Python 3.8 ou superior
- Nenhuma biblioteca externa

## Como executar

```bash
python sistema_especialista_investimentos.py
```

Responda às perguntas digitando o **número** da opção desejada.

## Como funciona

O sistema segue a arquitetura clássica de um sistema especialista:

| Componente | Onde está no código | O que faz |
|---|---|---|
| Base de conhecimento | `REGRAS` | Lista de regras no formato SE... ENTÃO... |
| Fatos | `fatos` (dicionário) | Respostas do usuário e fatos gerados pelas regras |
| Motor de inferência | `motor_de_inferencia()` | Dispara regras repetidamente até nenhuma regra nova poder ser usada |
| Interface | `perguntar()` e `main()` | Faz as perguntas e mostra o resultado |
| Módulo de explicação | final de `main()` | Lista as regras utilizadas e o motivo de cada uma |

### Encadeamento para frente

O motor usa **encadeamento para frente** (*forward chaining*): parte dos fatos conhecidos e aplica as regras. Uma regra pode gerar um fato novo, que libera outras regras:

```
respostas do usuário -> R3 (pode_investir) -> R4..R7 (perfil) -> R8..R12 (recomendação)
```

## Perguntas feitas

| Fato | Pergunta | Valores |
|---|---|---|
| `tem_dividas` | Possui dívidas? | `sim`, `nao` |
| `tem_reserva` | Tem reserva de emergência (cerca de 6 meses de gastos)? | `sim`, `nao` |
| `horizonte` | Por quanto tempo vai investir? | `curto` (até 2 anos), `medio` (2 a 5), `longo` (mais de 5) |
| `reacao_queda` | O que faria se o investimento caísse 10% em um mês? | `vende`, `mantem`, `compra_mais` |
| `experiencia` | Qual sua experiência com investimentos? | `iniciante`, `intermediario`, `avancado` |

## Regras

**Camada 1: prioridades** (bloqueiam ou liberam o investimento)

| Regra | SE | ENTÃO |
|---|---|---|
| R1 | `tem_dividas = sim` | Quitar as dívidas antes de investir |
| R2 | `tem_dividas = nao` E `tem_reserva = nao` | Montar a reserva de emergência |
| R3 | `tem_dividas = nao` E `tem_reserva = sim` | `pode_investir = True` |

**Camada 2: perfil** (geram o fato `perfil`)

| Regra | SE | ENTÃO |
|---|---|---|
| R4 | pode investir, horizonte médio/longo, `reacao_queda = vende` | `perfil = conservador` |
| R5 | pode investir, horizonte médio/longo, `reacao_queda = mantem` | `perfil = moderado` |
| R6 | pode investir, horizonte médio/longo, `reacao_queda = compra_mais` | `perfil = arrojado` |
| R7 | pode investir, `horizonte = curto` | `perfil = conservador` |

**Camada 3: recomendação** (usam o fato `perfil`)

| Regra | SE | ENTÃO |
|---|---|---|
| R8 | `perfil = conservador` | Tesouro Selic, CDB e LCI/LCA |
| R9 | `perfil = moderado` | Renda fixa + parte em FIIs e fundos multimercado |
| R10 | `perfil = arrojado` E `experiencia = iniciante` | ETFs diversificados |
| R11 | `perfil = arrojado` E experiência intermediária/avançada E `horizonte = longo` | Ações, ETFs e FIIs |
| R12 | `perfil = arrojado` E experiência intermediária/avançada E `horizonte = medio` | ETFs, FIIs e renda fixa |

### Resolução de conflitos

As regras de perfil (R4 a R7) foram escritas com condições que **nunca se sobrepõem**. Por isso, cada usuário recebe apenas um perfil. Em especial, o horizonte curto (R7) sempre resulta em perfil conservador, pois não há tempo de recuperar perdas.

## Exemplo de execução

Entradas: sem dívidas, com reserva, horizonte longo, compraria mais numa queda, experiência intermediária.

```
=== RESULTADO ===
Seu perfil de investidor: arrojado
-> Ações, ETFs e FIIs.

=== POR QUE? (regras utilizadas) ===
[R3] Sem dívidas e com reserva, você está pronto para investir.
[R6] Quem aproveitaria a queda para comprar mais tem alta tolerância a risco.
[R11] Perfil arrojado, com experiência e prazo longo, comporta renda variável.
```

## Como adicionar novas regras

Basta incluir um novo dicionário na lista `REGRAS`, sem mexer no motor:

```python
{
    "id": "R13",
    "se": {"perfil": "moderado", "experiencia": "avancado"},   # condições
    "entao": {},                                                # fatos novos (opcional)
    "mensagem": "Texto da recomendação.",                       # mostrado ao usuário
    "porque": "Texto usado na explicação.",                     # mostrado em "POR QUE?"
}
```

- Valor simples nas condições significa "igual a".
- Um `set` (por exemplo, `{"medio", "longo"}`) significa "igual a qualquer um destes".

Para criar uma nova pergunta, adicione uma tupla em `PERGUNTAS` com o nome do fato, o texto e as opções.

## Limitações

- As regras são fixas e escritas manualmente; o sistema não aprende com dados.
- Não considera valores em reais, renda, objetivos específicos nem a situação do mercado.
- Funciona apenas no domínio de investimentos para pessoa física no contexto brasileiro.

## Estrutura do projeto

```
.
├── sistema_especialista_investimentos.py
└── README.md
```
