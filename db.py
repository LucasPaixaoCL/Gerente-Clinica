import psycopg2

DB = {
    "database": "clinica_db",
    "host": "127.0.0.1",
    "user": "postgres",
    "password": "Limonada01",
    "port": 5432,
}


def main():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    # -------------------------
    # CLIENTES
    # -------------------------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(120) NOT NULL,
            telefone VARCHAR(40),
            email VARCHAR(120),
            criado_em TIMESTAMP DEFAULT NOW()
        );
    """
    )

    # -------------------------
    # PRODUTOS
    # -------------------------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(120) NOT NULL,
            preco NUMERIC(12,2) NOT NULL,
            estoque INT DEFAULT 0,
            criado_em TIMESTAMP DEFAULT NOW()
        );
    """
    )

    # -------------------------
    # CONSULTAS
    # -------------------------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS consultas (
            id SERIAL PRIMARY KEY,
            cliente_id INT NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
            descricao VARCHAR(200),
            valor NUMERIC(12,2) NOT NULL,
            data DATE NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'agendada',
            criado_em TIMESTAMP DEFAULT NOW()
        );
        """
    )

    # garante a coluna status caso a tabela já exista antiga (SEM status)
    cur.execute(
        """
        ALTER TABLE consultas
        ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'agendada';
        """
    )

    # -------------------------
    # VENDAS
    # -------------------------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS vendas (
            id SERIAL PRIMARY KEY,
            cliente_id INT REFERENCES clientes(id) ON DELETE SET NULL,
            produto_id INT NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
            quantidade INT NOT NULL,
            valor_total NUMERIC(12,2) NOT NULL,
            data DATE NOT NULL,
            criado_em TIMESTAMP DEFAULT NOW()
        );
    """
    )

    # -------------------------
    # TRANSAÇÕES FINANCEIRAS
    # -------------------------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            kind VARCHAR(10) NOT NULL CHECK (kind IN ('receita', 'despesa')),
            category VARCHAR(50) NOT NULL,
            description VARCHAR(200) NOT NULL,
            amount NUMERIC(12,2) NOT NULL
        );
    """
    )

    # -------------------------
    # SEED (apenas se vazio)
    # -------------------------
    cur.execute("SELECT COUNT(*) FROM transactions;")
    (count_tx,) = cur.fetchone()

    if count_tx == 0:
        cur.execute(
            """
            INSERT INTO transactions (date, kind, category, description, amount) VALUES
            ('2025-11-01', 'receita', 'Salário', 'Salário Novembro', 5000.00),
            ('2025-11-02', 'despesa', 'Moradia', 'Aluguel', 1800.00),
            ('2025-11-03', 'despesa', 'Alimentação', 'Supermercado', 650.50),
            ('2025-11-04', 'despesa', 'Transporte', 'Combustível', 300.00),
            ('2025-10-10', 'receita', 'Freelancer', 'Projeto site', 1200.00),
            ('2025-10-15', 'despesa', 'Lazer', 'Cinema e lanches', 150.00);
        """
        )

    # seeds auxiliares
    cur.execute("SELECT COUNT(*) FROM clientes;")
    (count_cli,) = cur.fetchone()
    if count_cli == 0:
        cur.execute(
            """
            INSERT INTO clientes (nome, telefone, email) VALUES
            ('João Pedro', '99999-1111', 'joao@email.com'),
            ('Maria Clara', '99999-2222', 'maria@email.com');
        """
        )

    cur.execute("SELECT COUNT(*) FROM produtos;")
    (count_prod,) = cur.fetchone()
    if count_prod == 0:
        cur.execute(
            """
            INSERT INTO produtos (nome, preco, estoque) VALUES
            ('Livro A', 59.90, 30),
            ('Curso Online X', 199.00, 100),
            ('Livro B', 79.90, 20);
        """
        )

    conn.commit()
    cur.close()
    conn.close()
    print("Tabelas criadas e seeds aplicados com sucesso.")


if __name__ == "__main__":
    main()
