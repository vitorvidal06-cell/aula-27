"""
Suíte de Testes Automatizados: TASK-204 (Motor de Cupons da BiblioTauá)
Base do Aluno (Aula 27) — Implemente os casos de teste marcados com TODO.
"""
from datetime import date, timedelta
import pytest
import sqlite3

from bibliotaua.database import SCHEMA_SQL
from bibliotaua.models.cliente import Cliente
from bibliotaua.models.livro import Livro
from bibliotaua.models.item_pedido import ItemPedido
from bibliotaua.models.pedido import Pedido
from bibliotaua.models.cupom import Cupom, TipoDesconto
from bibliotaua.repositories.cupom_repository import CupomRepository
from bibliotaua.services.checkout_service import CheckoutService
from bibliotaua.exceptions import (
    CupomInexistenteError,
    CupomInativoError,
    CupomExpiradoError,
    CupomEsgotadoError,
    ValorMinimoNaoAtingidoError
)


@pytest.fixture
def conexao_memoria():
    """Cria uma base de dados SQLite isolada em memória para cada teste."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    conn.execute("""
        INSERT INTO clientes (id, nome, email, matricula)
        VALUES (1, 'Carlos Eduardo', 'carlos@aluno.ifce.edu.br', '2024101')
    """)
    conn.execute("""
        INSERT INTO livros (id, titulo, autor, isbn, preco, estoque, categoria)
        VALUES (1, 'UML 2 Prática', 'Gilleanes Guedes', '978-8575222812', 100.0, 10, 'Didático')
    """)
    yield conn
    conn.close()


@pytest.fixture
def cliente_teste():
    return Cliente(id=1, nome="Carlos Eduardo", email="carlos@aluno.ifce.edu.br", matricula="2024101")


@pytest.fixture
def livro_teste():
    return Livro(id=1, titulo="UML 2 Prática", autor="Gilleanes Guedes", isbn="978-8575222812", preco=100.0, estoque=10)


class TestMotorCuponsRegrasNegocio:
    """Testes unitários puros das regras de negócio especificadas na DUC UC04."""

    def test_fluxo_principal_cupom_percentual(self, cliente_teste, livro_teste):
        """Valida aplicação de 15% de desconto em um pedido de R$ 100,00."""
        cupom = Cupom(
            codigo="PROMO15",
            tipo_desconto=TipoDesconto.PERCENTUAL,
            valor_desconto=15.0,
            valor_minimo_pedido=50.0,
            validade_ate="2027-12-31"
        )
        pedido = Pedido(cliente=cliente_teste)
        pedido.adicionar_item(ItemPedido(livro=livro_teste, quantidade=1, preco_unitario=100.0))

        pedido.aplicar_cupom(cupom)

        assert pedido.subtotal == 100.0
        assert pedido.desconto_aplicado == 15.0
        assert pedido.total == 85.0

    def test_fluxo_alternativo_cupom_valor_fixo(self, cliente_teste, livro_teste):
        """FA01: valida aplicação de R$ 25,00 de desconto fixo."""
        cupom = Cupom(
            codigo="FIXO25",
            tipo_desconto=TipoDesconto.VALOR_FIXO,
            valor_desconto=25.0,
            valor_minimo_pedido=50.0,
            validade_ate="2027-12-31"
        )
        pedido = Pedido(cliente=cliente_teste)
        pedido.adicionar_item(ItemPedido(livro=livro_teste, quantidade=1, preco_unitario=100.0))

        pedido.aplicar_cupom(cupom)

        assert pedido.subtotal == 100.0
        assert pedido.desconto_aplicado == 25.0
        assert pedido.total == 75.0

    def test_desconto_fixo_maior_que_subtotal_nao_gera_saldo_negativo(self, cliente_teste, livro_teste):
        """Garante que desconto fixo superior ao subtotal não gere total negativo."""
        cupom = Cupom(
            codigo="DESCONTO200",
            tipo_desconto=TipoDesconto.VALOR_FIXO,
            valor_desconto=200.0,
            validade_ate="2027-12-31"
        )
        pedido = Pedido(cliente=cliente_teste)
        pedido.adicionar_item(ItemPedido(livro=livro_teste, quantidade=1, preco_unitario=100.0))

        pedido.aplicar_cupom(cupom)

        assert pedido.desconto_aplicado == 100.0
        assert pedido.total == 0.0
        assert pedido.total >= 0.0

    def test_excecao_cupom_inativo(self, cliente_teste, livro_teste):
        """FE01: cupom inativo deve lançar CupomInativoError."""
        cupom = Cupom(
            codigo="INATIVO",
            tipo_desconto=TipoDesconto.PERCENTUAL,
            valor_desconto=10.0,
            validade_ate="2027-12-31",
            ativo=False
        )
        pedido = Pedido(cliente=cliente_teste)
        pedido.adicionar_item(ItemPedido(livro=livro_teste, quantidade=1, preco_unitario=100.0))

        with pytest.raises(CupomInativoError):
            pedido.aplicar_cupom(cupom)

    def test_excecao_cupom_expirado(self, cliente_teste, livro_teste):
        """FE02: cupom com validade anterior à data atual deve lançar exceção."""
        ontem = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        cupom = Cupom(
            codigo="EXPIRADO",
            tipo_desconto=TipoDesconto.PERCENTUAL,
            valor_desconto=10.0,
            validade_ate=ontem
        )
        pedido = Pedido(cliente=cliente_teste)
        pedido.adicionar_item(ItemPedido(livro=livro_teste, quantidade=1, preco_unitario=100.0))

        with pytest.raises(CupomExpiradoError):
            pedido.aplicar_cupom(cupom)

    def test_excecao_cupom_esgotado(self, cliente_teste, livro_teste):
        """FE03: cupom que atingiu o limite de usos deve lançar exceção."""
        cupom = Cupom(
            codigo="ESGOTADO",
            tipo_desconto=TipoDesconto.PERCENTUAL,
            valor_desconto=10.0,
            limite_usos=5,
            usos_realizados=5,
            validade_ate="2027-12-31"
        )
        pedido = Pedido(cliente=cliente_teste)
        pedido.adicionar_item(ItemPedido(livro=livro_teste, quantidade=1, preco_unitario=100.0))

        with pytest.raises(CupomEsgotadoError):
            pedido.aplicar_cupom(cupom)

    def test_excecao_subtotal_inferior_ao_minimo(self, cliente_teste, livro_teste):
        """FE04: subtotal abaixo do mínimo deve lançar exceção."""
        cupom = Cupom(
            codigo="MINIMO150",
            tipo_desconto=TipoDesconto.PERCENTUAL,
            valor_desconto=10.0,
            valor_minimo_pedido=150.0,
            validade_ate="2027-12-31"
        )
        pedido = Pedido(cliente=cliente_teste)
        pedido.adicionar_item(ItemPedido(livro=livro_teste, quantidade=1, preco_unitario=100.0))

        with pytest.raises(ValorMinimoNaoAtingidoError):
            pedido.aplicar_cupom(cupom)


class TestIntegracaoSQLite:
    """Testes de integração com SQLite para repositório e serviço de checkout."""

    def test_cupom_repository_crud_e_incremento(self, conexao_memoria):
        """Testa criação, leitura, listagem e incremento de uso no SQLite em memória."""
        repo = CupomRepository(conexao_memoria)
        cupom = Cupom(
            codigo="IFCE20",
            tipo_desconto=TipoDesconto.VALOR_FIXO,
            valor_desconto=20.0,
            valor_minimo_pedido=50.0,
            limite_usos=10,
            validade_ate="2027-12-31"
        )

        salvo = repo.salvar(cupom)
        encontrado = repo.buscar_por_codigo("ifce20")

        assert salvo.id is not None
        assert encontrado.codigo == "IFCE20"
        assert encontrado.usos_realizados == 0
        assert len(repo.listar_todos()) == 1

        repo.registrar_uso("IFCE20")
        atualizado = repo.buscar_por_codigo("IFCE20")
        assert atualizado.usos_realizados == 1

    def test_cupom_inexistente_lanca_excecao(self, conexao_memoria):
        """Código inexistente deve lançar CupomInexistenteError."""
        repo = CupomRepository(conexao_memoria)

        with pytest.raises(CupomInexistenteError):
            repo.buscar_por_codigo("NAO_EXISTE")

    def test_checkout_completo_com_cupom_e_baixa_de_estoque(self, conexao_memoria, cliente_teste):
        """Valida checkout, desconto, baixa de estoque e incremento de uso do cupom."""
        cupom_repo = CupomRepository(conexao_memoria)
        cupom_repo.salvar(Cupom(
            codigo="IFCE20",
            tipo_desconto=TipoDesconto.VALOR_FIXO,
            valor_desconto=20.0,
            valor_minimo_pedido=50.0,
            limite_usos=10,
            validade_ate="2027-12-31"
        ))

        checkout_service = CheckoutService(conexao_memoria)
        pedido = checkout_service.realizar_checkout(
            cliente=cliente_teste,
            itens_solicitados=[(1, 2)],
            codigo_cupom="IFCE20"
        )

        estoque = conexao_memoria.execute(
            "SELECT estoque FROM livros WHERE id = 1"
        ).fetchone()[0]
        cupom_atualizado = cupom_repo.buscar_por_codigo("IFCE20")

        assert pedido.subtotal == 200.0
        assert pedido.desconto_aplicado == 20.0
        assert pedido.total == 180.0
        assert estoque == 8
        assert cupom_atualizado.usos_realizados == 1
