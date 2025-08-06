# Sistema de Ciclo de Pagamentos

## Visão Geral

O sistema de ciclo de pagamentos foi implementado para automatizar o processo de reset mensal dos status de pagamento dos funcionários, garantindo que todos os funcionários precisem ser marcados como pagos manualmente a cada mês.

## Funcionalidades

### 1. Configuração do Ciclo de Pagamentos

**Endpoint:** `GET /payments/cycle/config`
- Retorna a configuração atual do ciclo de pagamentos
- Inclui o dia do mês configurado para reset e a data do último reset

**Endpoint:** `PUT /payments/cycle/config`
- Atualiza o dia do mês para reset automático
- Aceita valores de 1 a 31
- Valor padrão: dia 10

### 2. Verificação de Próximo Reset

**Endpoint:** `GET /payments/cycle/next-reset`
- Retorna a próxima data de reset programada
- Inclui informações sobre a configuração atual

### 3. Reset Manual

**Endpoint:** `POST /payments/cycle/reset`
- Executa o reset manual de todos os status de pagamento
- Retorna quantos funcionários foram afetados
- Publica evento no RabbitMQ para notificar outros serviços

### 4. Verificação e Reset Automático

**Endpoint:** `POST /payments/cycle/check-auto-reset`
- Verifica se um reset automático deve ser executado
- Executa o reset se necessário
- Pode ser usado em cronjobs ou verificações manuais

## Lógica de Funcionamento

### Reset Automático

O sistema verifica automaticamente se um reset deve ser executado baseado nas seguintes regras:

1. **Primeiro Reset:** Se nunca houve um reset e já passou do dia configurado no mês atual
2. **Resets Subsequentes:** Se o último reset foi em um mês anterior e já passou do dia configurado no mês atual

### Inicialização Automática

Na inicialização da aplicação, o sistema:
1. Verifica se existe uma configuração de ciclo
2. Cria uma configuração padrão (dia 10) se não existir
3. Executa automaticamente o reset se necessário

## Eventos RabbitMQ

### payment-cycle-reset-queue

Quando um reset é executado, o sistema publica um evento com as seguintes informações:

```json
{
  "type": "payment.cycle.reset",
  "payload": {
    "reset_date": "2025-08-05",
    "employees_affected": 15,
    "reset_day": 10
  }
}
```

## Casos de Uso

### 1. Configuração Inicial
- A aplicação é inicializada
- Sistema cria configuração padrão (dia 10)
- Se já é dia 10 ou depois, executa o primeiro reset

### 2. Mudança do Dia de Reset
- Administrador decide mudar o dia de reset de 10 para 5
- Faz PUT /payments/cycle/config com {"reset_day": 5}
- Próximo reset será no dia 5 do próximo mês

### 3. Reset Manual de Emergência
- Necessidade de reset fora do cronograma
- Faz POST /payments/cycle/reset
- Todos os funcionários voltam para status "não pago"

### 4. Verificação via Cronjob
- Cronjob diário chama POST /payments/cycle/check-auto-reset
- Sistema verifica se deve executar reset
- Executa automaticamente se necessário

## Logs e Monitoramento

O sistema registra logs para:
- Configurações criadas/atualizadas
- Resets executados (manual e automático)
- Número de funcionários afetados
- Erros durante o processo

## Integração com Outros Serviços

O evento `payment-cycle-reset-queue` pode ser consumido por outros microserviços para:
- Notificar administradores
- Atualizar dashboards
- Gerar relatórios mensais
- Sincronizar com sistemas externos
