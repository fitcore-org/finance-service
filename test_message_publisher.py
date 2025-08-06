"""
Script para simular mensagens de outros microserviços nas filas do RabbitMQ
Usado para testar os consumers do finance-service

IMPORTANTE: Este serviço apenas CONSOME mensagens de funcionários.
Este script simula outros microserviços publicando eventos.
"""
import asyncio
import json
import uuid
from datetime import datetime, timezone
from app.messaging import init_rabbitmq, close_rabbitmq, publish_message


async def simulate_other_services_messages():
    """Simula mensagens de outros microserviços para testar os consumers"""
    
    print("🚀 Simulando mensagens de outros microserviços...")
    print("💡 O finance-service apenas CONSOME essas mensagens")
    
    # Inicializar conexão RabbitMQ
    await init_rabbitmq()
    print("✅ Conexão RabbitMQ estabelecida")
    
    try:
        # 1. Simular funcionário registrado pelo microserviço de funcionários
        print("\n📝 Simulando: Funcionário registrado (por outro microserviço)...")
        employee_1_id = str(uuid.uuid4())
        employee_registered = {
            "id": employee_1_id,
            "name": "João Silva Teste",
            "cpf": "12345678901",
            "email": "joao.teste@fitcore.com",
            "phone": "11999999999",
            "birthDate": [1990, 5, 15],
            "hireDate": [2025, 8, 5],
            "role": "PERSONAL_TRAINER",
            "roleDescription": "Personal Trainer Especializado",
            "profile_url": None,
            "profileUrl": None,
            "registrationDate": [2025, 8, 5, 14, 30, 0, 0],
            "active": True,
            "terminationDate": None
        }
        await publish_message("cadastro-funcionario-queue", employee_registered)
        print("✅ Funcionário registrado simulado (consumido pelo finance-service)")
        
        # 2. Simular mudança de cargo pelo microserviço de funcionários
        print("\n🔄 Simulando: Mudança de cargo (por outro microserviço)...")
        role_changed = {
            "id": employee_1_id,
            "name": "João Silva Teste",
            "cpf": "12345678901",
            "email": "joao.teste@fitcore.com",
            "phone": "11999999999",
            "birthDate": [1990, 5, 15],
            "hireDate": [2025, 8, 5],
            "role": "MANAGER",
            "roleDescription": "Manager da Academia",
            "profile_url": None,
            "profileUrl": None,
            "registrationDate": [2025, 8, 5, 14, 30, 0, 0],
            "active": True,
            "terminationDate": None
        }
        await publish_message("employee-role-changed-queue", role_changed)
        print("✅ Mudança de cargo simulada (consumida pelo finance-service)")
        
        # 3. Simular funcionário demitido pelo microserviço de funcionários
        print("\n❌ Simulando: Funcionário demitido (por outro microserviço)...")
        status_changed = {
            "id": employee_1_id,
            "active": False
        }
        await publish_message("employee-status-changed-queue", status_changed)
        print("✅ Status de demissão publicado")
        
        # 4. Teste de funcionário deletado
        print("\n🗑️ Publicando: Funcionário deletado...")
        employee_deleted = {
            "id": employee_1_id
        }
        await publish_message("employee-deleted-queue", employee_deleted)
        print("✅ Funcionário deletado publicado")
        
        # 5. Registrar outro funcionário para testes
        print("\n📝 Publicando: Segundo funcionário...")
        employee_2_id = str(uuid.uuid4())
        employee_registered_2 = {
            "id": employee_2_id,
            "name": "Maria Santos Teste",
            "cpf": "98765432100",
            "email": "maria.teste@fitcore.com",
            "phone": "11888888888",
            "birthDate": [1985, 10, 20],
            "hireDate": [2025, 8, 5],
            "role": "RECEPTIONIST",
            "roleDescription": "Recepcionista",
            "profile_url": None,
            "profileUrl": None,
            "registrationDate": [2025, 8, 5, 14, 35, 0, 0],
            "active": True,
            "terminationDate": None
        }
        await publish_message("cadastro-funcionario-queue", employee_registered_2)
        print("✅ Segundo funcionário registrado")
        
        # 6. Registrar terceiro funcionário
        print("\n📝 Publicando: Terceiro funcionário...")
        employee_3_id = str(uuid.uuid4())
        employee_registered_3 = {
            "id": employee_3_id,
            "name": "Carlos Oliveira Teste",
            "cpf": "11122233344",
            "email": "carlos.teste@fitcore.com",
            "phone": "11777777777",
            "birthDate": [1992, 3, 8],
            "hireDate": [2025, 8, 5],
            "role": "CLEANER",
            "roleDescription": "Auxiliar de Limpeza",
            "profile_url": None,
            "profileUrl": None,
            "registrationDate": [2025, 8, 5, 14, 40, 0, 0],
            "active": True,
            "terminationDate": None
        }
        await publish_message("cadastro-funcionario-queue", employee_registered_3)
        print("✅ Terceiro funcionário registrado")
        
        print("\n🎉 Todas as mensagens de funcionários foram simuladas!")
        
        # Aguardar um pouco antes de simular outros eventos
        await asyncio.sleep(1)
        
        # 7. Simular eventos de gastos (que o finance-service publica)
        print("\n� Simulando eventos de gastos...")
        
        # Gasto registrado
        expense_registered = {
            "type": "expense.registered",
            "payload": {
                "amount": 150.75,
                "category": "Material de Limpeza",
                "description": "Produtos de higienização",
                "date": "2025-08-05",
                "responsible": "Admin Teste"
            }
        }
        await publish_message("finance.expense.registered", expense_registered)
        print("✅ Evento de gasto registrado simulado")
        
        # Múltiplos gastos adicionais
        expense_2_id = str(uuid.uuid4())
        expense_3_id = str(uuid.uuid4())
        expense_4_id = str(uuid.uuid4())
        
        gastos_adicionais = [
            {
                "id": expense_2_id, 
                "amount": 2500.00,
                "category": "Equipamentos",
                "description": "Esteiras para academia",
                "date": "2025-08-04",
                "responsible": "Gerente Operacional",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": expense_3_id,
                "amount": 85.30,
                "category": "Manutenção",
                "description": "Reparo do ar condicionado",
                "date": "2025-08-03",
                "responsible": "Técnico Terceirizado",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": expense_4_id,
                "amount": 320.00,
                "category": "Marketing",
                "description": "Impressão de panfletos promocionais",
                "date": "2025-08-02",
                "responsible": "Marketing",
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        for gasto in gastos_adicionais:
            expense_event = {
                "type": "expense.registered",
                "payload": gasto
            }
            await publish_message("finance.expense.registered", expense_event)
            print(f"✅ Gasto registrado: {gasto['description']} - R$ {gasto['amount']}")
            await asyncio.sleep(0.2)  # Pequena pausa entre mensagens
        
        # Gasto deletado
        expense_deleted = {
            "type": "expense.deleted",
            "payload": {
                "id": expense_3_id,
                "deleted_at": datetime.now(timezone.utc),
                "reason": "Gasto duplicado"
            }
        }
        await publish_message("finance.expense.deleted", expense_deleted)
        print("✅ Evento de gasto deletado simulado")
        
        # 8. Simular eventos de pagamentos (que o finance-service publica)
        print("\n💳 Simulando eventos de pagamentos...")
        
        # Funcionários pagos (usando fila employee-paid-queue)
        pagamentos_simulados = [
            {
                "id": employee_2_id,
                "amount": 1800.0,
                "month": 8,
                "year": 2025,
                "paid_at": datetime.now(timezone.utc)
            },
            {
                "id": employee_3_id,
                "amount": 1200.0,
                "month": 8,
                "year": 2025,
                "paid_at": datetime.now(timezone.utc)
            }
        ]
        
        for pagamento in pagamentos_simulados:
            await publish_message("employee-paid-queue", pagamento)
            print(f"✅ Funcionário pago: {pagamento['id']} - R$ {pagamento['amount']}")
            await asyncio.sleep(0.2)
        
        # Mudança de status de funcionário (usando employee-status-changed-queue)
        print("\n🔄 Simulando mudanças de status de funcionários...")
        status_updates = [
            {
                "id": employee_2_id,
                "active": True,
                "updated_at": datetime.now(timezone.utc)
            },
            {
                "id": employee_3_id, 
                "active": False,  # Inativando funcionário
                "updated_at": datetime.now(timezone.utc)
            }
        ]
        
        for status_update in status_updates:
            await publish_message("employee-status-changed-queue", status_update)
            status_text = "ativo" if status_update["active"] else "inativo"
            print(f"✅ Status atualizado: {status_update['id']} - {status_text}")
            await asyncio.sleep(0.2)
        
        # Funcionário demitido (usando employee-dismissed-queue)
        print("\n❌ Simulando funcionário demitido...")
        employee_dismissed = {
            "id": employee_1_id,
            "dismissed_at": datetime.now(timezone.utc),
            "final_payment": 2100.0,
            "reason": "Término de contrato"
        }
        await publish_message("employee-dismissed-queue", employee_dismissed)
        print("✅ Funcionário demitido simulado")
        
        print("\n🎉 Todas as mensagens de teste foram publicadas com sucesso!")
        print("\n💡 O que foi simulado:")
        print("   📋 Mensagens CONSUMIDAS pelo finance-service:")
        print("      - Funcionários registrados, mudança de cargo, demissões, exclusões")
        print("   📤 Mensagens PUBLICADAS pelo finance-service:")
        print("      - 4 gastos registrados (Material, Equipamentos, Manutenção, Marketing)")
        print("      - 1 gasto deletado")
        print("      - 2 funcionários pagos")
        print("      - 2 mudanças de status de funcionários")
        print("      - 1 funcionário demitido")
        print("\n🔍 Filas utilizadas para publicação:")
        print("   - finance.expense.registered")
        print("   - finance.expense.deleted")
        print("   - employee-paid-queue")
        print("   - employee-status-changed-queue")
        print("   - employee-dismissed-queue")
        print("\n🔍 Dicas para verificar:")
        print("   - Verifique os logs da aplicação para ver os consumers")
        print("   - Use GET /payments/status para ver os funcionários")
        print("   - Use GET /expenses/manual para ver gastos")
        print(f"   - Os funcionários {employee_2_id[:8]}... e {employee_3_id[:8]}... devem estar ativos")
        print("   - Configure consumers nos outros microserviços para as filas específicas")
        
    except Exception as e:
        print(f"❌ Erro ao publicar mensagens: {e}")
        
    finally:
        # Fechar conexão
        await close_rabbitmq()
        print("\n🔌 Conexão RabbitMQ fechada")


async def simulate_payments_and_expenses_only():
    """Simula apenas pagamentos e gastos (sem funcionários)"""
    
    print("💰 Simulando apenas pagamentos e gastos...")
    
    # Inicializar conexão RabbitMQ
    await init_rabbitmq()
    print("✅ Conexão RabbitMQ estabelecida")
    
    try:
        # 1. Simular eventos de gastos
        print("\n💸 Simulando eventos de gastos...")
        
        expense_1_id = str(uuid.uuid4())
        expense_2_id = str(uuid.uuid4())
        expense_3_id = str(uuid.uuid4())
        
        gastos_simulados = [
            {
                "type": "expense.registered",
                "payload": {
                    "id": expense_1_id,
                    "amount": 450.75,
                    "category": "Material de Escritório",
                    "description": "Papéis, canetas e materiais diversos",
                    "date": "2025-08-05",
                    "responsible": "Admin Sistema",
                    "created_at": datetime.now(timezone.utc)
                }
            },
            {
                "type": "expense.registered", 
                "payload": {
                    "id": expense_2_id,
                    "amount": 1200.00,
                    "category": "Equipamentos",
                    "description": "Halteres e anilhas",
                    "date": "2025-08-04",
                    "responsible": "Gerente Operacional",
                    "created_at": datetime.now(timezone.utc)
                }
            },
            {
                "type": "expense.registered",
                "payload": {
                    "id": expense_3_id, 
                    "amount": 285.50,
                    "category": "Manutenção",
                    "description": "Manutenção preventiva esteiras",
                    "date": "2025-08-03",
                    "responsible": "Técnico Especializado",
                    "created_at": datetime.now(timezone.utc)
                }
            }
        ]
        
        for gasto in gastos_simulados:
            await publish_message("finance.expense.registered", gasto)
            payload = gasto["payload"]
            print(f"✅ Gasto registrado: {payload['description']} - R$ {payload['amount']}")
            await asyncio.sleep(0.3)
        
        # Deletar um gasto
        expense_deleted = {
            "type": "expense.deleted",
            "payload": {
                "id": expense_2_id,
                "deleted_at": datetime.now(timezone.utc),
                "reason": "Cancelamento da compra"
            }
        }
        await publish_message("finance.expense.deleted", expense_deleted)
        print(f"✅ Gasto deletado: {expense_2_id[:8]}...")
        
        # 2. Simular pagamentos de funcionários
        print("\n💳 Simulando pagamentos de funcionários...")
        
        emp_uuid_1 = str(uuid.uuid4())
        emp_uuid_2 = str(uuid.uuid4())
        emp_uuid_3 = str(uuid.uuid4())
        
        pagamentos = [
            {
                "id": emp_uuid_1,
                "amount": 2500.0,
                "month": 8,
                "year": 2025,
                "paid_at": datetime.now(timezone.utc)
            },
            {
                "id": emp_uuid_2, 
                "amount": 1800.0,
                "month": 8,
                "year": 2025,
                "paid_at": datetime.now(timezone.utc)
            },
            {
                "id": emp_uuid_3,
                "amount": 2200.0,
                "month": 8,
                "year": 2025,
                "paid_at": datetime.now(timezone.utc)
            }
        ]
        
        for pagamento in pagamentos:
            await publish_message("employee-paid-queue", pagamento)
            print(f"✅ Funcionário pago: {pagamento['id']} - R$ {pagamento['amount']}")
            await asyncio.sleep(0.3)
        
        # 3. Simular mudanças de status
        print("\n🔄 Simulando mudanças de status...")
        
        status_changes = [
            {
                "id": emp_uuid_1,
                "active": True,
                "updated_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "active": False,
                "updated_at": datetime.now(timezone.utc)
            }
        ]
        
        for status in status_changes:
            await publish_message("employee-status-changed-queue", status)
            status_text = "ativo" if status["active"] else "inativo"
            print(f"✅ Status atualizado: {status['id']} - {status_text}")
            await asyncio.sleep(0.3)
        
        # 4. Simular demissão
        print("\n❌ Simulando demissão...")
        
        demissao = {
            "id": str(uuid.uuid4()),
            "dismissed_at": datetime.now(timezone.utc),
            "final_payment": 3500.0,
            "reason": "Fim do período de experiência"
        }
        
        await publish_message("employee-dismissed-queue", demissao)
        print(f"✅ Funcionário demitido: {demissao['id']} - Pagamento final: R$ {demissao['final_payment']}")
        
        print("\n🎉 Simulação de pagamentos e gastos concluída!")
        print("\n📊 Resumo:")
        print("   💸 3 gastos registrados, 1 deletado")
        print("   💳 3 funcionários pagos")
        print("   🔄 2 mudanças de status")
        print("   ❌ 1 demissão")
        
    except Exception as e:
        print(f"❌ Erro ao publicar mensagens: {e}")
        
    finally:
        await close_rabbitmq()
        print("\n🔌 Conexão RabbitMQ fechada")


async def publish_custom_message():
    """Permite publicar uma mensagem customizada"""
    
    print("\n🛠️ Modo personalizado:")
    print("Filas que o finance-service CONSOME:")
    print("1. cadastro-funcionario-queue")
    print("2. employee-deleted-queue") 
    print("3. employee-role-changed-queue")
    print("4. employee-status-changed-queue")
    print("\nFilas que o finance-service PUBLICA:")
    print("5. finance.expense.registered")
    print("6. finance.expense.deleted")
    print("7. employee-paid-queue")
    print("8. employee-status-changed-queue")
    print("9. employee-dismissed-queue")
    
    queue_name = input("\nDigite o nome da fila: ")
    
    print("\nExemplos de payload:")
    if "cadastro-funcionario" in queue_name:
        example = {
            "id": str(uuid.uuid4()),
            "name": "Nome do Funcionário",
            "cpf": "12345678901",
            "email": "email@teste.com",
            "phone": "11999999999",
            "birthDate": [1990, 1, 1],
            "hireDate": [2025, 8, 5],
            "role": "PERSONAL_TRAINER",
            "roleDescription": "Descrição do cargo",
            "profile_url": None,
            "profileUrl": None,
            "registrationDate": [2025, 8, 5, 14, 0, 0, 0],
            "active": True,
            "terminationDate": None
        }
    elif "deleted" in queue_name:
        example = {"id": str(uuid.uuid4())}
    elif "role-changed" in queue_name:
        example = {
            "id": str(uuid.uuid4()),
            "role": "MANAGER",
            "active": True
        }
    elif "status-changed" in queue_name:
        example = {"id": str(uuid.uuid4()), "active": False}
    elif "expense.registered" in queue_name:
        example = {
            "type": "expense.registered",
            "payload": {
                "id": str(uuid.uuid4()),
                "amount": 150.75,
                "category": "Material",
                "description": "Compra de produtos",
                "date": "2025-08-05",
                "responsible": "Admin",
                "created_at": datetime.now(timezone.utc)
            }
        }
    elif "expense.deleted" in queue_name:
        example = {
            "type": "expense.deleted",
            "payload": {
                "id": str(uuid.uuid4()),
                "deleted_at": datetime.now(timezone.utc),
                "reason": "Cancelamento"
            }
        }
    elif "finance.employee.paid" in queue_name:
        example = {
            "id": str(uuid.uuid4()),
            "amount": 3500.0,
            "month": 8,
            "year": 2025,
            "paid_at": datetime.now(timezone.utc)
        }
    elif "payroll.processed" in queue_name:
        example = {
            "id": str(uuid.uuid4()),
            "active": True,
            "updated_at": datetime.now(timezone.utc)
        }
    elif "employee-paid" in queue_name:
        example = {
            "id": str(uuid.uuid4()),
            "amount": 3500.0,
            "month": 8,
            "year": 2025,
            "paid_at": datetime.now(timezone.utc)
        }
    elif "employee-status-changed" in queue_name:
        example = {
            "id": str(uuid.uuid4()),
            "active": True,
            "updated_at": datetime.now(timezone.utc)
        }
    elif "employee-dismissed" in queue_name:
        example = {
            "id": str(uuid.uuid4()),
            "dismissed_at": datetime.now(timezone.utc),
            "final_payment": 2100.0,
            "reason": "Término de contrato"
        }
    else:
        example = {"id": str(uuid.uuid4()), "data": "exemplo"}
    
    print(f"Exemplo: {json.dumps(example, indent=2)}")
    
    payload_str = input("\nDigite o payload JSON (ou ENTER para usar o exemplo): ").strip()
    
    if not payload_str:
        payload = example
    else:
        try:
            payload = json.loads(payload_str)
        except json.JSONDecodeError:
            print("❌ JSON inválido!")
            return
    
    await init_rabbitmq()
    
    try:
        await publish_message(queue_name, payload)
        print(f"✅ Mensagem publicada na fila '{queue_name}'")
    except Exception as e:
        print(f"❌ Erro ao publicar: {e}")
    finally:
        await close_rabbitmq()


async def main():
    """Menu principal"""
    
    print("🎯 PUBLISHER DE MENSAGENS TESTE - FINANCE SERVICE")
    print("=" * 50)
    print("1. Publicar conjunto completo de testes")
    print("2. Publicar apenas pagamentos e gastos")
    print("3. Publicar mensagem customizada")
    print("4. Sair")
    
    choice = input("\nEscolha uma opção (1-4): ").strip()
    
    if choice == "1":
        await simulate_other_services_messages()
    elif choice == "2":
        await simulate_payments_and_expenses_only()
    elif choice == "3":
        await publish_custom_message()
    elif choice == "4":
        print("👋 Saindo...")
    else:
        print("❌ Opção inválida!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
