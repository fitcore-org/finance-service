# Finance Service

Microserviço para gerenciar cargos, salários e gastos dentro do sistema FitCore.

## Tecnologias

- Python 3.11
- FastAPI
- SQLAlchemy (async) com PostgreSQL
- aio-pika (RabbitMQ)
- Pydantic
- Uvicorn

## Funcionalidades

- Gerenciamento de cargos e salários
- Controle de gastos manuais
- Controle de status de pagamento de funcionários
- Integração RabbitMQ para sincronização com sistema de usuários

## Configuração

### Variáveis de Ambiente

```bash
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=fitcore
POSTGRES_PASSWORD=fitcorepass
POSTGRES_DB=auth

RABBITMQ_HOST=rabbitmq
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin
```

## Docker

Construir e executar usando Docker Compose:
```bash
docker-compose up -d
```

## Endpoints da API

### Cargos
- `GET /positions` - Listar cargos
- `POST /positions` - Criar cargo
- `PUT /positions/{id}` - Atualizar cargo
- `DELETE /positions/{id}` - Excluir cargo

### Salários
- `GET /salaries` - Listar salários de funcionários
- `POST /salaries` - Registrar/atualizar salário personalizado

### Gastos
- `GET /expenses/manual` - Listar gastos manuais
- `POST /expenses/manual` - Registrar gasto manual

### Pagamentos
- `GET /payments/status` - Status de pagamentos
- `PATCH /payments/{employeeId}/pay` - Confirmar pagamento
- `POST /payments/{employeeId}/dismiss` - Demitir funcionário

## Filas RabbitMQ

### Consumidas
- `cadastro-funcionario-queue` - Novos funcionários
- `employee-deleted-queue` - Funcionários excluídos
- `employee-role-changed-queue` - Mudanças de cargo
- `employee-status-changed-queue` - Mudanças de status

### Publicadas
- `finance.expense.registered` - Gasto registrado
- `finance.employee.paid` - Funcionário pago
- `employee-dismissed-queue` - Funcionário demitido

## Testes

### Testes Automatizados

Executar conjunto completo de testes:

**Windows:**
```powershell
.\start_and_test.ps1
```

**Linux/Mac:**
```bash
chmod +x start_and_test.sh
./start_and_test.sh
```

### Testes Manuais

**Testes da API:**
```bash
python test_complete.py
```

**Testes do RabbitMQ:**
```bash
python test_rabbitmq.py
```

## Execução Local

### Pré-requisitos
- Python 3.7+
- PostgreSQL (porta 5432)
- RabbitMQ (porta 5672)

### Início Rápido

**Windows:**
```powershell
.\run.ps1
```

### Configuração Manual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Definir variáveis de ambiente (opcional)
set POSTGRES_HOST=localhost
set RABBITMQ_HOST=localhost

# Executar do diretório raiz
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

### Health Check

```bash
curl http://localhost:8004/health
```

## Banco de Dados

O serviço cria automaticamente as seguintes tabelas:
- `positions` - Cargos e salários base
- `manual_expenses` - Gastos manuais
- `employee_payment_status` - Status de pagamento de funcionários
