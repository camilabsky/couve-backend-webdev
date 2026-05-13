import sqlite3
import os

DB_NAME = "horta_game.db"

def criar_banco():
    # Remove o banco antigo se existir (opcional)
    # if os.path.exists(DB_NAME):
    #     os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Ativa suporte a chaves estrangeiras no SQLite
    cursor.execute("PRAGMA foreign_keys = ON")

    # --------------------------------
    # TABELA USUARIO
    # --------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nome            VARCHAR(100)  NOT NULL,
            email           VARCHAR(150)  UNIQUE NOT NULL,
            senha           VARCHAR(255)  NOT NULL,
            nivel           INT           DEFAULT 1  CHECK (nivel >= 1),
            xp              INT           DEFAULT 0  CHECK (xp >= 0),
            moedas          INT           DEFAULT 0  CHECK (moedas >= 0),
            pontos_ranking  INT           DEFAULT 0  CHECK (pontos_ranking >= 0),
            tipo            VARCHAR(20)   NOT NULL    -- 'comum' ou 'responsavel'
        )
    """)

    # --------------------------------
    # TABELA HORTA
    # --------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS horta (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            nome             VARCHAR(100) NOT NULL,
            localizacao      VARCHAR(255),
            responsavel_id   INT NOT NULL,
            FOREIGN KEY (responsavel_id) REFERENCES usuario(id) ON DELETE CASCADE
        )
    """)

    # --------------------------------
    # TABELA MISSAO
    # --------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS missao (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo             VARCHAR(100) NOT NULL,
            descricao          TEXT,
            nivel_minimo       INT NOT NULL CHECK (nivel_minimo >= 1),
            recompensa_moedas  INT NOT NULL CHECK (recompensa_moedas >= 0),
            pontos_ranking     INT NOT NULL DEFAULT 0,
            tipo               VARCHAR(50),
            horta_id           INT NOT NULL,
            FOREIGN KEY (horta_id) REFERENCES horta(id) ON DELETE CASCADE
        )
    """)

    # --------------------------------
    # TABELA USUARIO_MISSAO
    # --------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuario_missao (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id      INT NOT NULL,
            missao_id       INT NOT NULL,
            status          VARCHAR(20) NOT NULL, -- 'aceita', 'concluida'
            data_conclusao  TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,
            FOREIGN KEY (missao_id)  REFERENCES missao(id)  ON DELETE CASCADE,
            UNIQUE (usuario_id, missao_id)
        )
    """)

    # --------------------------------
    # TABELA CONQUISTA
    # --------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conquista (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nome      VARCHAR(100) NOT NULL,
            descricao TEXT
        )
    """)

    # --------------------------------
    # TABELA USUARIO_CONQUISTA
    # --------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuario_conquista (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id       INT NOT NULL,
            conquista_id     INT NOT NULL,
            data_desbloqueio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id)   REFERENCES usuario(id)   ON DELETE CASCADE,
            FOREIGN KEY (conquista_id) REFERENCES conquista(id) ON DELETE CASCADE,
            UNIQUE (usuario_id, conquista_id)
        )
    """)

    # --------------------------------
    # TABELA ITEM_LOJA
    # --------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS item_loja (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            nome          VARCHAR(100) NOT NULL,
            descricao     TEXT,
            custo_moedas  INT NOT NULL CHECK (custo_moedas >= 0),
            horta_id      INT NOT NULL,
            FOREIGN KEY (horta_id) REFERENCES horta(id) ON DELETE CASCADE
        )
    """)

    # --------------------------------
    # TABELA COMPRA
    # --------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compra (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id  INT NOT NULL,
            item_id     INT NOT NULL,
            quantidade  INT       DEFAULT 1 CHECK (quantidade > 0),
            data_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuario(id)    ON DELETE CASCADE,
            FOREIGN KEY (item_id)    REFERENCES item_loja(id)  ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

    print(f"✅ Banco '{DB_NAME}' criado com sucesso!")
    print("📋 Tabelas criadas:")
    print("   • usuario")
    print("   • horta")
    print("   • missao")
    print("   • usuario_missao")
    print("   • conquista")
    print("   • usuario_conquista")
    print("   • item_loja")
    print("   • compra")


def listar_tabelas():
    """Exibe as tabelas existentes no banco."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tabelas = cursor.fetchall()
    conn.close()

    print("\n📂 Tabelas no banco:")
    for t in tabelas:
        print(f"   - {t[0]}")


if __name__ == "__main__":
    criar_banco()
    listar_tabelas()
