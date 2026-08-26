# Arquitetura — Padaria-System

Documentação técnica completa do projeto: contexto, regras de negócio, modelagem, arquitetura, plano de desenvolvimento e roadmap.

Este documento é a especificação inicial e contexto-base do projeto. Deve ser atualizado conforme decisões técnicas e necessidades reais da padaria forem descobertas durante o desenvolvimento.

---

## 1. Visão geral

O Padaria-System é um sistema de automação criado para resolver um problema real de operação de uma padaria.

Atualmente, os clientes fazem encomendas principalmente pelo WhatsApp. Os pedidos precisam ser interpretados, organizados, produzidos e posteriormente entregues. Durante o dia, parte dos pedidos pode ser entregue em diferentes horários, tornando necessário controlar exatamente:

- quem pediu;
- o que foi pedido;
- para qual data;
- quantos pães foram pedidos;
- quantos foram produzidos;
- quantos foram enviados em cada remessa;
- quanto ainda falta entregar;
- quanto foi vendido;
- quanto foi recebido;
- quanto ainda está pendente.

O sistema deve transformar esse processo em um fluxo organizado e rastreável.

A ideia principal é que o banco de dados seja a fonte oficial de verdade. O WhatsApp, o painel administrativo e o Excel serão diferentes formas de interagir ou visualizar os mesmos dados.

## 2. Objetivo principal

Construir um sistema completo de gestão da operação da padaria, começando por um núcleo simples e confiável e evoluindo posteriormente para automação através do WhatsApp e inteligência artificial.

O sistema deverá permitir:

1. cadastrar clientes;
2. registrar pedidos;
3. calcular a quantidade necessária de produção;
4. considerar que uma pesada possui 30 pães;
5. registrar remessas parciais;
6. saber exatamente quanto cada cliente recebeu;
7. saber quanto ainda falta entregar;
8. acompanhar a produção;
9. controlar valores financeiros;
10. visualizar tudo através de um painel administrativo;
11. gerar relatórios e planilhas Excel;
12. futuramente receber pedidos diretamente pelo WhatsApp;
13. futuramente interpretar mensagens de texto e áudios;
14. futuramente utilizar IA para transformar mensagens naturais em pedidos estruturados.

## 3. Princípio fundamental do projeto

O sistema não deve considerar um pedido simplesmente como `ENTREGUE` ou `NÃO ENTREGUE`. Um pedido pode ser entregue em várias partes.

Exemplo:

```
Pedido: 500 pães
11:00 → 300 pães
15:30 → 100 pães
17:00 →  50 pães

Resultado:
Pedido:       500
Entregue:     450
Pendente:      50
Status:     PARCIAL
```

Cada entrega deve ser registrada como uma **Remessa** independente. Isso permite manter histórico e reconstruir exatamente o que aconteceu durante o dia.

## 4. Conceito de Remessa

Uma remessa representa uma quantidade de pães efetivamente enviada/entregue referente a um pedido.

```
Cliente: Padaria A
Pedido: 500 pães
Remessa #1: 300 pães — 24/08/2026 às 11:00
Remessa #2: 200 pães — 24/08/2026 às 15:30

500 - (300 + 200) = 0 → Pedido completo
```

Outro exemplo:

```
Pedido: 700
Remessa #1: 200

Pedido:       700
Entregue:     200
Pendente:     500
Status:     PARCIAL
```

## 5. Conceito de produção

```
1 pesada = 30 pães
pesadas = ceil(total_de_pães / 30)
```

Exemplo:

```
235 pães pedidos
235 / 30 = 7,83 → 8 pesadas
Produção: 8 × 30 = 240 pães
Sobra prevista: 240 - 235 = 5 pães
```

O sistema deve realizar esse cálculo automaticamente.

## 6. Entidades principais

```
Cliente (1:N) → Pedido (1:N) → Remessa
```

Posteriormente outras entidades poderão ser adicionadas, principalmente relacionadas a pagamentos e usuários administrativos.

### Cliente

Campos iniciais: `id`, `nome`, `local_entrega`.

Um cliente pode possuir vários pedidos.

### Pedido

Campos iniciais: `id`, `cliente_id` (FK → clients.id), `data`, `quantidade_pedida`, `preco_unitario`, `valor_total`.

Um pedido pertence a um cliente; um cliente pode possuir vários pedidos.

### Remessa

Campos: `id`, `pedido_id` (FK → orders.id), `quantidade`, `data_hora`.

Um pedido pode possuir várias remessas.

## 7. Modelagem do banco

```
clients
├── id
├── name
└── delivery_location

orders
├── id
├── client_id → clients.id
├── date
├── quantity
├── unit_price
└── total_price

shipments
├── id
├── order_id → orders.id
├── quantity
└── date_time
```

O projeto deverá inicialmente utilizar um único banco PostgreSQL, com várias tabelas relacionadas, e não bancos separados para clientes, pedidos e remessas.

## 8. Financeiro

O valor financeiro do pedido deve ser separado da quantidade física entregue. O sistema deve conseguir distinguir: valor do pedido, valor referente ao que foi entregue, valor recebido e valor pendente.

No início, o controle financeiro pode ser simples. Posteriormente poderá existir uma entidade separada `Payment`, permitindo múltiplos pagamentos por pedido (ex.: pedido de R$400 pago em duas parcelas de R$200). O pagamento não deve ser tratado como um simples campo do pedido.

## 9. Painel administrativo

Interface web responsiva, pensada principalmente para uso pelo responsável pela padaria através do celular — será a principal interface de operação diária.

**Dashboard** — exemplo:

```
HOJE
Pedidos:          2.340 pães
Pesadas:             78
Produção:          2.340 pães
Entregues:         1.800
Pendentes:           540
Valor vendido:   R$ 1.872
```

**Tela de pedidos** — a quantidade entregue é sempre calculada a partir da soma das remessas; nunca alterada manualmente.

**Registro de remessa** — deve ser extremamente rápido: selecionar pedido → informar quantidade → confirmar. O sistema registra automaticamente pedido, quantidade, data e horário atual.

**Histórico de remessas** — cada remessa é guardada individualmente; nunca apagar ou sobrescrever o histórico para atualizar a quantidade entregue.

## 10. Produção

O sistema deve calcular a produção necessária para uma data com base nos pedidos registrados. Posteriormente poderá existir controle real: produção planejada, produção realizada, sobra, perdas.

## 11. Excel

O Excel não é a fonte principal dos dados (essa é o PostgreSQL). Será usado para relatórios, exportação, análise, impressão, histórico e visualização financeira — ex.: planilha de pedidos e planilha de remessas.

## 12. WhatsApp

Fase posterior. Objetivo: permitir que o cliente faça pedidos sem acessar o sistema.

```
WhatsApp → Webhook → FastAPI → Interpretação → Pedido estruturado → PostgreSQL
```

## 13. Áudio

Clientes também poderão enviar mensagens de voz. O sistema poderá usar Speech-to-Text (Whisper) para converter áudio em texto, que depois será interpretado.

## 14. Inteligência artificial

A IA não deve ser responsável pelas regras fundamentais do sistema — ela deve apenas interpretar linguagem humana e transformar em dados estruturados (ex.: `"duas pesadas e mais cinco"` → `{"quantidade": 65}`). A regra de negócio (cálculo de pesadas, etc.) continua sempre no backend.

### Confirmação de pedidos interpretados

O sistema não deve confiar cegamente na interpretação da IA. Deve solicitar confirmação ao cliente antes de consolidar o pedido (`SIM` / `CORRIGIR`), reduzindo erros de interpretação.

## 15. Arquitetura geral

```
WHATSAPP → WEBHOOK → FASTAPI → (SERVICES, SCHEMAS, AUTH)
                                     │
                                     ▼
                                SQLALCHEMY
                                     │
                                     ▼
                                POSTGRESQL
                              ┌──────┼───────┐
                              ▼      ▼       ▼
                          CLIENTS ORDERS SHIPMENTS
                                     │
                                     ▼
                                FINANCEIRO

FASTAPI → PAINEL WEB → USUÁRIO ADMINISTRATIVO
POSTGRESQL → RELATÓRIOS EXCEL
```

## 16. Organização de pastas

```
Padaria-System/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/          (clients.py, orders.py, shipments.py, auth.py)
│   │   ├── models/       (client.py, order.py, shipment.py)
│   │   ├── schemas/      (client.py, order.py, shipment.py)
│   │   ├── services/     (order_service.py, production_service.py, shipment_service.py)
│   │   ├── database/     (connection.py, base.py)
│   │   └── config/       (settings.py)
│   └── tests/            (test_clients.py, test_orders.py, test_shipments.py)
├── frontend/
│   ├── templates/        (dashboard.html, clients.html, orders.html, shipments.html)
│   └── static/           (css/, js/, images/)
├── integrations/
│   ├── whatsapp/         (whatsapp_client.py)
│   ├── transcription/    (whisper.py)
│   └── ai/               (order_interpreter.py)
├── reports/              (excel.py)
├── docs/                 (architecture.md)
├── .gitignore
└── README.md
```

A estrutura completa não precisa existir desde o primeiro dia — as pastas devem ser criadas conforme as funcionalidades forem implementadas.

## 17. Responsabilidade de cada camada

| Camada | Pergunta que responde | Exemplos |
|---|---|---|
| `models/` | O que existe no banco? | Client, Order, Shipment |
| `database/` | Como o sistema acessa o banco? | engine, session, Base |
| `schemas/` | Que formato de dados a API recebe/devolve? | CreateOrder, OrderResponse |
| `services/` | O que o sistema deve fazer? | calcular pendente, produção, validar entrega |
| `api/` | Como o mundo externo conversa com o sistema? | GET/POST /clients, /orders, /shipments |
| `integrations/` | Serviços externos | WhatsApp, Whisper, IA |
| `reports/` | Geração de arquivos/relatórios | Excel |

## 18. Fluxo interno de uma operação

Exemplo: registrar uma remessa de 300 pães.

```
Frontend → HTTP POST → api/shipments.py → Shipment Schema
   → shipment_service.py → valida pedido → verifica quantidade pendente
   → cria Shipment → SQLAlchemy → PostgreSQL
```

Resposta da API:

```json
{
  "order_id": 153,
  "ordered": 500,
  "delivered": 300,
  "pending": 200,
  "status": "partial"
}
```

## 19. Regras de negócio fundamentais

As regras importantes devem estar no backend, nunca no frontend.

| Regra | Fórmula |
|---|---|
| Pesada | `1 pesada = 30 pães` |
| Produção | `pesadas = ceil(pães_pedidos / 30)` |
| Entregue | `entregue = SUM(remessas.quantidade)` |
| Pendente | `pendente = quantidade_pedida - entregue` |
| Status | `entregue = 0` → `PENDING`; `0 < entregue < pedido` → `PARTIAL`; `entregue = pedido` → `COMPLETED` |

A implementação final deve também definir o comportamento para quantidades inválidas, cancelamentos e outras exceções.

## 20. Tecnologias

- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic, Alembic
- **Banco:** PostgreSQL
- **Frontend:** HTML, CSS, JavaScript (inicialmente)
- **Relatórios:** openpyxl / Excel
- **Integrações futuras:** WhatsApp Business Platform, Speech-to-Text/Whisper, LLM/IA

## 21. Conhecimento prévio do desenvolvedor

Já domina: Python, Programação Orientada a Objetos, SQL, SQLite, ORM do Django, REST API, HTTP.

O foco de aprendizado deste projeto é: PostgreSQL, SQLAlchemy, Alembic, arquitetura de backend, separação de responsabilidades, integração frontend/backend, autenticação, webhooks, integração com WhatsApp, processamento de áudio, integração com IA.

Ao explicar conceitos novos, priorizar conexões com o que já é conhecido:

```
Django ORM        → SQLAlchemy
Django model       → SQLAlchemy model
Django ForeignKey  → SQLAlchemy ForeignKey
Django migration   → Alembic
Django URL/view    → FastAPI router
```

## 22. Plano de desenvolvimento

Prioridade sempre: **funcionalidade funcionando → entendimento → refatoração → próxima funcionalidade.** Não tentar implementar tudo simultaneamente.

### Semana 1 — Fundação
Estrutura de pastas, ambiente virtual, Git, PostgreSQL, conexão básica, introdução ao SQLAlchemy (Engine, Session, Base), primeiro model.

### Semana 2 — Models e banco
Client, Order, Shipment com Foreign Keys, Relationships e Constraints. Aprender relacionamentos 1:N e Alembic (migrations).

### Semana 3 — CRUD e Services
CRUD de clientes/pedidos/remessas. Camada `services/` com as regras de entregue, pendente, status, produção e pesadas. Meta: rodar todo o fluxo principal sem frontend.

### Semana 4 — FastAPI
Endpoints REST (`/clients`, `/orders`, `/shipments`), routers, dependency injection, Pydantic, tratamento de erros, docs automáticas.

### Semana 5 — Painel administrativo
Dashboard, Clientes, Pedidos, Remessas — priorizando simplicidade, velocidade e uso via celular. Fluxo principal: selecionar pedido → registrar remessa → quantidade → confirmar.

### Semana 6 — Produção e relatórios
Produção diária, pesadas, sobra prevista, exportação Excel (pedidos, remessas, produção, financeiro).

### Semana 7 — Autenticação e refinamento
Login, usuário administrativo, autorização, proteção de endpoints, validações, logs, melhorias no dashboard.

### Semana 8 — WhatsApp
Webhook → FastAPI → Pedido, começando por mensagens de texto estruturadas/simples.

### Semana 9 — Áudio
Speech-to-Text de áudios do WhatsApp, testando português brasileiro, sotaques, ruído e expressões informais.

### Semana 10 — IA
Interpretação de linguagem natural em dados estruturados, com o backend sempre aplicando as regras de negócio.

## 23. MVP

```
PostgreSQL → Clientes → Pedidos → Remessas
  → Cálculo de pendências → Cálculo de produção → Painel administrativo
```

Sem WhatsApp, IA ou Áudio — essas integrações entram somente depois que o núcleo estiver sólido.

### Critério de sucesso do MVP

1. cadastrar um cliente;
2. criar um pedido para esse cliente;
3. visualizar o pedido;
4. registrar uma remessa;
5. registrar várias remessas para o mesmo pedido;
6. calcular automaticamente o total entregue;
7. calcular automaticamente o total pendente;
8. mostrar o status do pedido;
9. calcular quantas pesadas são necessárias;
10. visualizar as informações no painel administrativo;
11. exportar os dados para Excel.

## 24. Evoluções futuras (pós-MVP)

Controle de pagamentos, clientes inadimplentes, histórico financeiro, previsão de demanda, clientes recorrentes, pedidos "de sempre", notificações, confirmação automática, controle de estoque, perdas, produção real vs. planejada, relatórios mensais, gráficos, previsão de produção, múltiplos usuários administrativos, permissões diferentes, aplicativo/PWA.

## 25. Filosofia de desenvolvimento

Priorizar entendimento sobre velocidade. Para cada parte nova: entender o problema → entender a arquitetura → implementar uma versão simples → testar → corrigir → refatorar → documentar. Quando uma tecnologia nova aparecer, primeiro entender o conceito e depois utilizar no projeto (especialmente PostgreSQL, SQLAlchemy, Alembic, FastAPI, Webhooks, IA).