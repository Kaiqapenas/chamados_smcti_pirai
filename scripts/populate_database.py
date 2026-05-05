"""
populate_database.py
====================
Popula o banco de desenvolvimento com dados fictícios para testes.

Uso:
    python scripts/populate_database.py
    python scripts/populate_database.py --clean
    python scripts/populate_database.py --usuarios 20 --itens 30 --chamados 15
    python scripts/populate_database.py --clean --usuarios 10 --itens 20 --chamados 10

Argumentos:
    --clean         Limpa os dados antes de popular (exceto superusuários)
    --usuarios N    Quantidade de usuários a criar por perfil (default: 5)
    --itens N       Quantidade de itens de estoque a criar (default: 20)
    --chamados N    Quantidade de chamados a criar (default: 10)
"""

import os
import sys
import django
import argparse
import logging
import random
from pathlib import Path

# ─── Setup Django ────────────────────────────────────────────────────────────
# Adiciona a raiz do projeto ao sys.path para que os imports funcionem
# independente de onde o script é chamado.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

# ─── Imports dos models (sempre APÓS django.setup()) ─────────────────────────
from django.db import transaction
from faker import Faker

from apps.core.models import User
from apps.estoque.models import CategoriaItem, ItemEstoque, MovimentacaoEstoque
from apps.chamados.models import Chamado, ItemChamado

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(BASE_DIR / "scripts" / "populate.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

fake = Faker("pt_BR")

# ─── Dados fixos de referência 

PERFIS = {
    "solicitante": "Solicitante",
    "tecnico":     "Técnico",
    "almoxarife":  "Almoxarife",
    "secretario":  "Secretário",
    "admin":       "Administrador",
}

SETORES = [
    "TI", "Infraestrutura", "Administrativo", "Financeiro",
    "RH", "Manutenção", "Almoxarifado", "Diretoria",
]

CATEGORIAS = [
    ("Climatização",   "Ar-condicionados, ventiladores e exaustores"),
    ("Informática",    "Computadores, periféricos e componentes"),
    ("Redes",          "Switches, roteadores, cabos e conectores"),
    ("Elétrica",       "Cabos, tomadas, disjuntores e fios"),
    ("Ferramentas",    "Ferramentas manuais e elétricas"),
    ("Segurança",      "Câmeras, alarmes e controle de acesso"),
]

ITENS_POR_CATEGORIA = {
    "Climatização":  ["Ar-condicionado Split 9000 BTU", "Ventilador de Teto", "Filtro para Ar-condicionado", "Controle Remoto Universal", "Suporte para Ar-condicionado"],
    "Informática":   ["Mouse USB", "Teclado ABNT2", "Monitor 24\"", "Cabo HDMI 2m", "Memória RAM 8GB DDR4", "SSD 240GB", "Fonte ATX 500W", "Webcam Full HD"],
    "Redes":         ["Switch 8 portas", "Cabo de Rede Cat6 (metro)", "Roteador Wi-Fi", "Patch Panel 24 portas", "Conector RJ45", "Alicate de Crimpagem"],
    "Elétrica":      ["Cabo PP 2x2,5mm (metro)", "Tomada 2P+T", "Disjuntor 20A", "Régua de Tomadas", "Fita Isolante", "Multímetro Digital"],
    "Ferramentas":   ["Chave de Fenda Cruz", "Chave de Fenda Reta", "Alicate Universal", "Furadeira de Impacto", "Trena 5m", "Nível de Bolha"],
    "Segurança":     ["Câmera IP 1080p", "DVR 8 canais", "Cabo Coaxial (metro)", "Bateria Nobreak 7Ah", "Sensor de Presença"],
}

MARCAS = ["Dell", "HP", "Intelbras", "Positivo", "TP-Link", "Samsung", "LG", "Multilaser", "Elgin", "Schneider"]

DESTINOS_CHAMADO = [
    "TI - Suporte Técnico",
    "Infraestrutura",
    "Manutenção Predial",
    "Almoxarifado Central",
    "Secretaria Geral",
]

TITULOS_CHAMADO = [
    "Computador não liga",
    "Impressora offline",
    "Sem acesso à internet",
    "Ar-condicionado com defeito",
    "Troca de lâmpada queimada",
    "Teclado com teclas travando",
    "Monitor sem imagem",
    "Cabo de rede danificado",
    "Nobreak emitindo alarme",
    "Mouse com defeito",
    "Tomada sem energia",
    "Solicitar equipamento para novo colaborador",
    "Câmera de segurança fora do ar",
    "Switch com porta queimada",
    "Solicitação de peças para manutenção",
]


# ─── Limpeza

def clean_data():
    """Remove todos os dados de teste (mantém superusuários)."""
    log.warning("⚠️  Limpando dados do banco...")
    with transaction.atomic():
        # Ordem: filhos antes dos pais
        ItemChamado.objects.all().delete()
        Chamado.objects.all().delete()           # AlteracaoChamado em CASCADE
        MovimentacaoEstoque.objects.all().delete()
        ItemEstoque.objects.all().delete()
        CategoriaItem.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
    log.info("✅  Dados limpos com sucesso.")


# ─── Usuários

def gerar_matricula():
    """Gera uma matrícula única no formato MAT-XXXXXX."""
    while True:
        matricula = f"MAT-{random.randint(100000, 999999)}"
        if not User.objects.filter(matricula=matricula).exists():
            return matricula


def create_usuarios(quantidade_por_perfil: int) -> dict[str, list[User]]:
    """
    Cria usuários para cada perfil.
    Retorna um dicionário {perfil: [lista de User]}.
    """
    log.info(f"👤  Criando {quantidade_por_perfil} usuário(s) por perfil...")
    usuarios_por_perfil: dict[str, list[User]] = {p: [] for p in PERFIS}
    senha_padrao = "Teste@1234"

    for perfil_key, perfil_nome in PERFIS.items():
        for i in range(quantidade_por_perfil):
            try:
                matricula = gerar_matricula()
                nome = fake.first_name()
                sobrenome = fake.last_name()
                email = fake.unique.email()
                setor = random.choice(SETORES)

                is_staff = perfil_key in ("admin", "secretario")

                user = User.objects.create_user(
                    matricula=matricula,
                    password=senha_padrao,
                    first_name=nome,
                    last_name=sobrenome,
                    email=email,
                    telefone=fake.phone_number(),
                    setor=setor,
                    ativo=True,
                    is_staff=is_staff,
                )
                usuarios_por_perfil[perfil_key].append(user)
                log.info(f"   [{perfil_nome}] {matricula} - {nome} {sobrenome} | senha: {senha_padrao}")

            except Exception:
                log.exception(f"   Erro ao criar usuário ({perfil_key} #{i+1})")

    total = sum(len(v) for v in usuarios_por_perfil.values())
    log.info(f"✅  {total} usuário(s) criado(s).")
    return usuarios_por_perfil


# ─── Estoque 

def create_categorias(usuario: User) -> dict[str, CategoriaItem]:
    """Cria as categorias fixas e retorna {nome: objeto}."""
    log.info("🗂️   Criando categorias...")
    categorias = {}
    for nome, descricao in CATEGORIAS:
        cat, created = CategoriaItem.objects.get_or_create(
            nome=nome,
            defaults={"descricao": descricao,
            "usuario": usuario},
        )
        categorias[nome] = cat
        if created:
            log.info(f"   + Categoria: {nome}")
    log.info(f"✅  {len(categorias)} categoria(s) prontas.")
    return categorias


def create_itens_estoque(quantidade: int, categorias: dict[str, CategoriaItem], usuario: User) -> list[ItemEstoque]:
    """Cria itens de estoque distribuídos entre as categorias."""
    log.info(f"📦  Criando {quantidade} item(ns) de estoque...")
    itens_criados = []

    nomes_usados = set()

    for _ in range(quantidade):
        try:
            cat_nome = random.choice(list(categorias.keys()))
            categoria = categorias[cat_nome]

            # Escolhe um nome base e garante unicidade (nome + número)
            nome_base = random.choice(ITENS_POR_CATEGORIA[cat_nome])
            nome = nome_base
            sufixo = 2
            while nome in nomes_usados:
                nome = f"{nome_base} #{sufixo}"
                sufixo += 1
            nomes_usados.add(nome)

            qtd = random.randint(0, 50)
            qtd_minima = random.randint(2, 10)
            unidade = random.choice([ItemEstoque.UnidadeMedida.UNIDADE, ItemEstoque.UnidadeMedida.METRO])

            item = ItemEstoque.objects.create(
                nome=nome,
                categoria=categoria,
                quantidade=qtd,
                quantidade_minima=qtd_minima,
                unidade_medida=unidade,
                descricao=fake.sentence(nb_words=10),
                marca=random.choice(MARCAS + [None, None]),   # ~33% sem marca
                modelo=f"Modelo-{fake.bothify('??-####')}",
                serie=fake.bothify("SN-#########") if random.random() > 0.4 else None,
                patrimonio=fake.bothify("PAT-######") if random.random() > 0.5 else None,
                ativo=random.choices([True, False], weights=[90, 10])[0],
                usuario=usuario,
            )
            itens_criados.append(item)
            estoque_label = "⚠️  BAIXO" if item.estoque_baixo else "OK"
            log.info(f"   + {item.nome} | qtd: {qtd} (mín {qtd_minima}) [{estoque_label}]")

        except Exception:
            log.exception("   Erro ao criar item de estoque")

    log.info(f"✅  {len(itens_criados)} item(ns) criado(s).")
    return itens_criados


def create_movimentacoes(itens: list[ItemEstoque], usuario: User, quantidade: int = 30):
    """Cria movimentações de estoque (entradas e saídas) para simular histórico."""
    log.info(f"🔄  Criando {quantidade} movimentação(ões) de estoque...")
    criadas = 0

    for _ in range(quantidade):
        item = random.choice(itens)
        tipo = random.choice([
            MovimentacaoEstoque.TipoMovimentacao.ENTRADA,
            MovimentacaoEstoque.TipoMovimentacao.SAIDA,
        ])
        qtd = random.randint(1, 5)

        try:
            with transaction.atomic():
                # Para saída, garante que tem saldo
                item.refresh_from_db()
                if tipo == MovimentacaoEstoque.TipoMovimentacao.SAIDA and item.quantidade < qtd:
                    # Faz entrada antes para ter saldo
                    MovimentacaoEstoque.objects.create(
                        item=item,
                        tipo=MovimentacaoEstoque.TipoMovimentacao.ENTRADA,
                        quantidade=qtd + 5,
                        observacao="Entrada automática para viabilizar movimentação de teste",
                        usuario=usuario,
                    )
                    item.refresh_from_db()

                mov = MovimentacaoEstoque.objects.create(
                    item=item,
                    tipo=tipo,
                    quantidade=qtd,
                    observacao=fake.sentence(nb_words=6),
                    usuario=usuario,
                )
                criadas += 1
                log.info(f"   {mov.get_tipo_display()} | {item.nome} | qtd: {qtd}")
        except Exception:
            log.exception(f"   Erro na movimentação ({item.nome})")

    log.info(f"✅  {criadas} movimentação(ões) criada(s).")


# ─── Chamados 

def create_chamados(
    quantidade: int,
    usuarios_por_perfil: dict[str, list[User]],
    itens: list[ItemEstoque],
):
    """Cria chamados com itens associados e histórico de status."""
    log.info(f"🎫  Criando {quantidade} chamado(s)...")
    criados = 0

    solicitantes = usuarios_por_perfil.get("solicitante", [])
    if not solicitantes:
        log.warning("   Nenhum usuário com perfil 'solicitante' encontrado. Chamados não serão criados.")
        return

    itens_ativos = [i for i in itens if i.ativo and i.quantidade > 0]

    for _ in range(quantidade):
        try:
            solicitante = random.choice(solicitantes)
            titulo = random.choice(TITULOS_CHAMADO)
            urgencia = random.choices(
                [Chamado.Urgencia.NORMAL, Chamado.Urgencia.URGENTE],
                weights=[75, 25],
            )[0]

            # Cria chamado no status ABERTO
            chamado = Chamado.objects.create(
                solicitante=f"{solicitante.first_name} {solicitante.last_name}",
                para_onde_solicitou=random.choice(DESTINOS_CHAMADO),
                titulo=titulo,
                descricao=fake.paragraph(nb_sentences=3),
                urgencia=urgencia,
                status=Chamado.Status.ABERTO,
                data_prevista=fake.date_between(start_date="today", end_date="+30d") if random.random() > 0.3 else None,
            )

            # Associa itens aleatoriamente (0 a 3 itens)
            if itens_ativos and random.random() > 0.3:
                num_itens = random.randint(1, min(3, len(itens_ativos)))
                itens_escolhidos = random.sample(itens_ativos, num_itens)
                for item in itens_escolhidos:
                    qtd_req = random.randint(1, min(3, item.quantidade))
                    ItemChamado.objects.get_or_create(
                        chamado=chamado,
                        item=item,
                        defaults={"quantidade": qtd_req},
                    )

            # Avança status de alguns chamados
            status_alvo = random.choices(
                [None, Chamado.Status.EM_ANDAMENTO, Chamado.Status.FINALIZADO],
                weights=[40, 35, 25],
            )[0]

            if status_alvo == Chamado.Status.EM_ANDAMENTO:
                chamado.mudar_status(Chamado.Status.EM_ANDAMENTO)

            elif status_alvo == Chamado.Status.FINALIZADO:
                chamado.mudar_status(Chamado.Status.EM_ANDAMENTO)
                # Garante estoque suficiente pra finalizar
                for item_chamado in chamado.itens.select_related("item").all():
                    item_chamado.item.refresh_from_db()
                    if item_chamado.item.quantidade < item_chamado.quantidade:
                        item_chamado.item.quantidade = item_chamado.quantidade + 5
                        item_chamado.item.save()
                chamado.mudar_status(Chamado.Status.FINALIZADO)

            status_display = chamado.get_status_display()
            urgencia_display = "🔴 URGENTE" if urgencia == Chamado.Urgencia.URGENTE else "🟢 Normal"
            log.info(f"   [{chamado.numero_protocolo}] {titulo} | {status_display} | {urgencia_display}")
            criados += 1

        except Exception:
            log.exception("   Erro ao criar chamado")

    log.info(f"✅  {criados} chamado(s) criado(s).")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Popula o banco de desenvolvimento com dados fictícios.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--clean", action="store_true", help="Limpa os dados antes de popular")
    parser.add_argument("--usuarios", type=int, default=5, metavar="N", help="Usuários por perfil (default: 5)")
    parser.add_argument("--itens", type=int, default=20, metavar="N", help="Itens de estoque (default: 20)")
    parser.add_argument("--chamados", type=int, default=10, metavar="N", help="Chamados (default: 10)")
    args = parser.parse_args()

    log.info("=" * 60)
    log.info("🚀  populate_database.py iniciado")
    log.info("=" * 60)

    if args.clean:
        clean_data()

    usuarios = create_usuarios(args.usuarios)

    usuario_sistema = next(
        user
        for lista in usuarios.values()
        if lista
        for user in lista
    )

    categorias = create_categorias(usuario_sistema)
    itens = create_itens_estoque(args.itens, categorias, usuario_sistema)

    create_movimentacoes(
        itens,
        usuario_sistema,
        quantidade=max(10, args.itens * 2),
    )

    create_chamados(args.chamados, usuarios, itens)

    log.info("=" * 60)
    log.info("🎉  Banco populado com sucesso!")
    log.info(f"    Categorias : {len(categorias)}")
    log.info(f"    Itens      : {len(itens)}")
    log.info(f"    Usuários   : {sum(len(v) for v in usuarios.values())} ({args.usuarios} por perfil)")
    log.info(f"    Chamados   : {args.chamados} (aprox.)")
    log.info("=" * 60)


if __name__ == "__main__":
    main()