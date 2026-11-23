# BiblioTauá — Projeto Prático do Aluno (Sprint 04 - Aula 27)
## TASK-204 (Etapa 4 — Final): Garantia de Qualidade (Pytest), CLI e Fechamento da Sprint

Bem-vindo(a) ao **Encontro 4 (Fechamento)** da Sprint 04 do sistema **BiblioTauá Livraria Web**!

Nas Aulas 24, 25 e 26, você projetou e implementou o domínio de cupons (`models/cupom.py`), a hierarquia de exceções de negócio (`exceptions.py`), a persistência relacional no SQLite (`repositories/cupom_repository.py`), o serviço de cálculo (`services/calculadora_desconto.py`) e o orquestrador transacional de checkout (`services/checkout_service.py`).

Hoje, nossa missão é **garantir a qualidade** de todo o módulo através de **testes automatizados com Pytest**, homologar o sistema no **CLI interativo** e submeter o **Pull Request** formal no GitHub para encerrar a `TASK-204`!

---

## 🌿 Fluxo Git & GitHub do Estudante

Você segue desenvolvendo no seu **próprio repositório no GitHub** (fork):

*   **Opção A (Continuar da Aula 26):**
    ```bash
    git checkout feature/task-204-motor-cupons
    ```
*   **Opção B (Ponto Homologado da Aula 27):**
    ```bash
    git fetch upstream
    git checkout -b feature/task-204-aula27 upstream/aula-27
    ```

---

## 🎯 Suas Tarefas Hoje

1. **`bibliotaua/tests/test_cupons.py` (Suíte de Testes Automatizados com Pytest):**
   - Utilizar as fixtures isoladas em memória (`conexao_memoria`, `cliente_teste`, `livro_teste`).
   - Implementar os testes unitários do **Caminho Feliz** (desconto percentual e valor fixo, além do teto em R$ 0,00).
   - Implementar os testes de **Fluxos de Exceção** da DUC UC04 (`FE01` a `FE04`) utilizando `pytest.raises(...)`.
   - Implementar os testes de **Integração SQLite** validando `CupomRepository`, `CupomInexistenteError` e `CheckoutService.realizar_checkout` (baixa de estoque + incremento de usos).

2. **`bibliotaua/main.py` (Homologação no CLI Interativo):**
   - Executar o sistema interativo no terminal, consultar o acervo e os cupons e simular uma compra aplicando um cupom válido (ex: `VOLTAAULAS10`) e um cupom inválido.

3. **Versionamento e Pull Request (PR) no GitHub:**
   - Consolidar os commits semânticos e enviar para o seu fork (`git push origin HEAD`).
   - Abrir o Pull Request formal no GitHub utilizando o template do `guia_desenvolvedor.md`.

---

## 🚀 Como Executar

### 1. Rodar a Suíte de Testes (Pytest)
```bash
PYTHONPATH=. pytest bibliotaua/tests/test_cupons.py -v
```

### 2. Executar o CLI Interativo
```bash
python3 -m bibliotaua.main
```

**Critério de Aceite:**
Todos os **10 casos de teste** em `test_cupons.py` devem passar com 100% de sucesso (`10 passed`), e a simulação no CLI deve exibir o cálculo correto do desconto, atualização de estoque e gravação no banco SQLite.

---

## 💾 Versionamento e Entrega Final no GitHub

Ao concluir os testes com sucesso, envie o código para seu repositório pessoal e abra o Pull Request:

```bash
git add bibliotaua/tests/test_cupons.py
git commit -m "test(pytest): implementa suite completa de testes do motor de cupons (Aula 27)"
git push origin HEAD
```
