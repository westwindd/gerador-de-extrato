# Receipt Service (FastAPI + Docker + PostgreSQL)

Este projeto é um exemplo de microserviço Python que gera comprovantes/recibos em formato de imagem (estilo Magie), armazena-os criptografados no banco de dados PostgreSQL, e os disponibiliza via um endpoint.

## Sumário
- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Uso](#instalação-e-uso)
- [Exemplo de Requisição](#exemplo-de-requisição)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Endpoints Principais](#endpoints-principais)
- [Licença](#licença)

---

## Visão Geral

O serviço expõe duas rotas principais:

1. `POST /generate`: Recebe um JSON com dados do recibo (como data, hora, dados de remetente e destinatário, etc.) e retorna um `id` e uma `url` onde a imagem pode ser acessada.
2. `GET /receipt/{id}`: Retorna a imagem PNG correspondente, recuperada e descriptografada do banco PostgreSQL.

O projeto inclui:
- **FastAPI** para construção da API.
- **Pillow** para geração e manipulação de imagens.
- **cryptography** para criptografia simétrica com Fernet.
- **psycopg2** para conexão com PostgreSQL.
- **qrcode** para gerar QR codes incorporados no comprovante.
- **Docker** e **docker-compose** para empacotamento e execução consistentes.

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado.
- [Docker Compose](https://docs.docker.com/compose/install/) instalado.
- (Opcional) Python 3.11+ se quiser rodar localmente sem containers.

---

## Instalação e Uso

1. **Clonar** este repositório:
   ```bash
   git clone https://github.com/seu-usuario/receipt-service.git
   cd receipt-service
   ```

2. **Gere** uma chave Fernet para criptografia e coloque-a no `docker-compose.yml`:
   ```bash
   python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
   # Cole a chave no lugar de FERNET_KEY
   ```

3. **Suba os containers**:
   ```bash
   docker-compose up --build
   ```

4. **Acesse** o serviço em `http://localhost:8000`.

---

## Exemplo de Requisição

Para gerar um comprovante, envie um `POST /generate` com JSON no seguinte formato:

```json
{
    "date": "07/04/2025",
    "time": "15:23",
    "from": {
        "name": "Luiz Guilherme Ramalho De Souza",
        "document": "824.317.***",
        "bank": "CELCOIN IP S.A.",
        "agency": "0001",
        "account": "300541298142"
    },
    "to": {
        "name": "Joao Vitor Camargo Silva",
        "document": "806.641.***",
        "bank": "CELCOIN IP S.A.",
        "agency": "0001",
        "account": "30054219875"
    },
    "amount": "R$ 100,00",
    "qr_payload": "https://magie.com.br/share/abc123",
    "transaction_id": "e27e039-8c96-4b6b-9cb3-8bdd85441f5f"
}
```

Retorno esperado:

```json
{
  "id": 1,
  "url": "http://localhost:8000/receipt/1"
}
```

---

## Estrutura de Pastas

```
receipt-service/
├── app.py                # Código principal (FastAPI)
├── Dockerfile            # Dockerfile para build da imagem
├── docker-compose.yml    # Orquestração com Postgres e o receipt
├── requirements.txt      # Dependências Python
└── magie_logo.png        # Logotipo usado na geração do comprovante
```

---

## Variáveis de Ambiente

| Variável      | Descrição                                                                              | Padrão     |
|---------------|------------------------------------------------------------------------------------------|------------|
| `PG_HOST`     | Host do banco PostgreSQL                                                                 | `db`       |
| `PG_PORT`     | Porta do banco PostgreSQL                                                                | `5432`     |
| `PG_DB`       | Nome do banco de dados                                                                   | `receipts` |
| `PG_USER`     | Usuário do banco                                                                         | `user`     |
| `PG_PASSWORD` | Senha do banco                                                                           | `password` |
| `FERNET_KEY`  | Chave Fernet (32 bytes em base64). Necessária p/ criptografia (não pode ser aleatória). | Nenhum     |

---

## Endpoints Principais

- `POST /generate`
  - **Body**: JSON com os campos `date`, `time`, `from`, `to`, `amount`, `qr_payload` e `transaction_id`.
  - **Retorno**: `{"id": <int>, "url": "http://<host>:<port>/receipt/<id>"}`.

- `GET /receipt/{id}`
  - **Retorno**: PNG criptografado armazenado no banco, descriptografado em runtime.

---

## Licença

Este projeto é fornecido "como está" para fins educacionais/demonstração. Sinta-se livre para adaptar e usar como desejar.
