import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DB = {
    "database": "clinica_db",
    "host": "127.0.0.1",
    "user": "postgres",
    "password": "Limonada01",
    "port": 5432,
}


def db_conn():
    return psycopg2.connect(**DB)


# =======================================================
# DASHBOARD / PÁGINA ÚNICA
# =======================================================


@app.get("/")
def index():
    conn = db_conn()
    cur = conn.cursor()

    # LISTAGEM DE LANÇAMENTOS
    cur.execute(
        """
        SELECT
            id,
            to_char(date, 'YYYY-MM-DD') AS date_str,
            kind,
            category,
            description,
            amount,
            ROW_NUMBER() OVER (ORDER BY date DESC, id DESC) AS pos
        FROM transactions
        ORDER BY date DESC, id DESC;
        """
    )
    data = cur.fetchall()

    # RESUMO DO MÊS ATUAL (cards)
    cur.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN kind = 'receita' THEN amount END), 0) AS total_receitas,
            COALESCE(SUM(CASE WHEN kind = 'despesa' THEN amount END), 0) AS total_despesas
        FROM transactions
        WHERE date >= date_trunc('month', CURRENT_DATE)
          AND date <  date_trunc('month', CURRENT_DATE) + INTERVAL '1 month';
        """
    )
    total_rec, total_desp = cur.fetchone()

    # CLIENTES
    cur.execute(
        """
        SELECT id, nome, telefone, email
        FROM clientes
        ORDER BY id DESC
        LIMIT 50;
        """
    )
    clientes = cur.fetchall()

    # PRODUTOS
    cur.execute(
        """
        SELECT id, nome, preco, estoque
        FROM produtos
        ORDER BY id DESC
        LIMIT 50;
        """
    )
    produtos = cur.fetchall()

    # CONSULTAS AGENDADAS (ainda não realizadas)
    cur.execute(
        """
        SELECT
            con.id,
            to_char(con.data, 'YYYY-MM-DD') AS data_str,
            con.descricao,
            con.valor,
            con.status,
            con.cliente_id,
            COALESCE(cli.nome, '') AS cliente_nome
        FROM consultas con
        LEFT JOIN clientes cli ON cli.id = con.cliente_id
        WHERE con.status = 'agendada'
        ORDER BY con.data, con.id;
        """
    )
    consultas = cur.fetchall()

    cur.close()
    conn.close()

    total_rec = float(total_rec or 0)
    total_desp = float(total_desp or 0)
    saldo = total_rec - total_desp

    return render_template(
        "index.html",
        data=data,
        total_receitas_mes=total_rec,
        total_despesas_mes=total_desp,
        saldo_mes=saldo,
        clientes=clientes,
        produtos=produtos,
        consultas=consultas,
    )


# =======================================================
# TRANSAÇÕES (LANÇAMENTOS FINANCEIROS)
# =======================================================


@app.post("/create")
def create():
    description = request.form.get("description", "").strip()
    date_str = request.form.get("date")
    kind = request.form.get("kind")
    category = request.form.get("category", "").strip()
    amount_str = request.form.get("amount", "").strip()

    if not (
        description
        and date_str
        and kind in ("receita", "despesa")
        and category
        and amount_str
    ):
        return redirect(url_for("index"))

    amount_str = amount_str.replace(",", ".")
    try:
        amount = float(amount_str)
    except ValueError:
        return redirect(url_for("index"))

    conn = db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO transactions (date, kind, category, description, amount)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (date_str, kind, category, description, amount),
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


@app.post("/update")
def update():
    trans_id = request.form.get("id")
    description = request.form.get("description", "").strip()
    date_str = request.form.get("date")
    kind = request.form.get("kind")
    category = request.form.get("category", "").strip()
    amount_str = request.form.get("amount", "").strip()

    if not (
        trans_id
        and description
        and date_str
        and kind in ("receita", "despesa")
        and category
        and amount_str
    ):
        return redirect(url_for("index"))

    amount_str = amount_str.replace(",", ".")
    try:
        amount = float(amount_str)
    except ValueError:
        return redirect(url_for("index"))

    conn = db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE transactions
        SET date = %s,
            kind = %s,
            category = %s,
            description = %s,
            amount = %s
        WHERE id = %s;
        """,
        (date_str, kind, category, description, amount, trans_id),
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


@app.post("/delete")
def delete():
    trans_id = request.form.get("id")
    if not trans_id:
        return redirect(url_for("index"))

    conn = db_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM transactions WHERE id = %s;", (trans_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


# =======================================================
# CLIENTES
# =======================================================


@app.post("/clientes/add")
def clientes_add():
    nome = request.form.get("nome", "").strip()
    telefone = request.form.get("telefone", "").strip() or None
    email = request.form.get("email", "").strip() or None

    if not nome:
        return redirect(url_for("index"))

    conn = db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO clientes (nome, telefone, email)
        VALUES (%s, %s, %s);
        """,
        (nome, telefone, email),
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


@app.post("/clientes/update")
def clientes_update():
    cliente_id = request.form.get("id")
    nome = request.form.get("nome", "").strip()
    telefone = request.form.get("telefone", "").strip() or None
    email = request.form.get("email", "").strip() or None

    if not (cliente_id and nome):
        return redirect(url_for("index"))

    conn = db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE clientes
        SET nome = %s,
            telefone = %s,
            email = %s
        WHERE id = %s;
        """,
        (nome, telefone, email, cliente_id),
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


@app.post("/clientes/delete")
def clientes_delete():
    cliente_id = request.form.get("id")
    if not cliente_id:
        return redirect(url_for("index"))

    conn = db_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE id = %s;", (cliente_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


# =======================================================
# PRODUTOS
# =======================================================


@app.post("/produtos/add")
def produtos_add():
    nome = request.form.get("nome", "").strip()
    preco_str = request.form.get("preco", "").strip()
    estoque_str = request.form.get("estoque", "").strip() or "0"

    if not (nome and preco_str):
        return redirect(url_for("index"))

    preco_str = preco_str.replace(",", ".")
    try:
        preco = float(preco_str)
    except ValueError:
        return redirect(url_for("index"))

    try:
        estoque = int(estoque_str)
    except ValueError:
        estoque = 0

    conn = db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO produtos (nome, preco, estoque)
        VALUES (%s, %s, %s);
        """,
        (nome, preco, estoque),
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


@app.post("/produtos/update")
def produtos_update():
    produto_id = request.form.get("id")
    nome = request.form.get("nome", "").strip()
    preco_str = request.form.get("preco", "").strip()
    estoque_str = request.form.get("estoque", "").strip() or "0"

    if not (produto_id and nome and preco_str):
        return redirect(url_for("index"))

    preco_str = preco_str.replace(",", ".")
    try:
        preco = float(preco_str)
    except ValueError:
        return redirect(url_for("index"))

    try:
        estoque = int(estoque_str)
    except ValueError:
        estoque = 0

    conn = db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE produtos
        SET nome = %s,
            preco = %s,
            estoque = %s
        WHERE id = %s;
        """,
        (nome, preco, estoque, produto_id),
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


@app.post("/produtos/delete")
def produtos_delete():
    produto_id = request.form.get("id")
    if not produto_id:
        return redirect(url_for("index"))

    conn = db_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM produtos WHERE id = %s;", (produto_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


# =======================================================
# CONSULTAS
# =======================================================


@app.post("/consultas/add")
def consultas_add():
    cliente_id_str = request.form.get("cliente_id", "").strip()
    data = request.form.get("data")
    descricao = request.form.get("descricao", "").strip()
    valor_str = request.form.get("valor", "").strip() or "0"

    if not (cliente_id_str and data and descricao):
        return redirect(url_for("index"))

    try:
        cliente_id = int(cliente_id_str)
    except ValueError:
        return redirect(url_for("index"))

    valor_str = valor_str.replace(",", ".")
    try:
        valor = float(valor_str)
    except ValueError:
        valor = 0.0

    conn = db_conn()
    cur = conn.cursor()

    # garante que o cliente existe para não estourar ForeignKeyViolation
    cur.execute("SELECT 1 FROM clientes WHERE id = %s;", (cliente_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    # registra consulta apenas como "agendada"
    cur.execute(
        """
        INSERT INTO consultas (cliente_id, descricao, valor, data, status)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (cliente_id, descricao, valor, data, "agendada"),
    )

    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


@app.post("/consultas/done")
def consultas_done():
    consulta_id = request.form.get("id")
    if not consulta_id:
        return redirect(url_for("index"))

    conn = db_conn()
    cur = conn.cursor()

    # pega dados da consulta
    cur.execute(
        """
        SELECT c.data, c.descricao, c.valor, c.cliente_id, cli.nome
        FROM consultas c
        LEFT JOIN clientes cli ON cli.id = c.cliente_id
        WHERE c.id = %s;
        """,
        (consulta_id,),
    )
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    data, descricao, valor, cliente_id, cliente_nome = row
    valor = float(valor or 0)

    # marca como realizada
    cur.execute(
        """
        UPDATE consultas
        SET status = 'realizada'
        WHERE id = %s;
        """,
        (consulta_id,),
    )

    # se tiver valor, gerar lançamento de receita
    if valor > 0:
        desc_tx = f"Consulta: {descricao}"
        if cliente_nome:
            desc_tx += f" (cliente: {cliente_nome})"

        cur.execute(
            """
            INSERT INTO transactions (date, kind, category, description, amount)
            VALUES (%s, 'receita', 'Consulta', %s, %s);
            """,
            (data, desc_tx, valor),
        )

    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


@app.post("/consultas/delete")
def consultas_delete():
    consulta_id = request.form.get("id")
    if not consulta_id:
        return redirect(url_for("index"))

    conn = db_conn()
    cur = conn.cursor()
    # pode só deletar; se preferir manter histórico, trocaria para status = 'cancelada'
    cur.execute("DELETE FROM consultas WHERE id = %s;", (consulta_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


# =======================================================
# (opcional) VENDAS - mantive caso queira usar depois
# =======================================================


@app.post("/vendas/add")
def vendas_add():
    cliente_id_str = request.form.get("cliente_id", "").strip()
    produto_id_str = request.form.get("produto_id", "").strip()
    quantidade_str = request.form.get("quantidade", "").strip() or "1"
    data = request.form.get("data")

    if not (produto_id_str and data):
        return redirect(url_for("index"))

    try:
        produto_id = int(produto_id_str)
    except ValueError:
        return redirect(url_for("index"))

    try:
        quantidade = int(quantidade_str)
    except ValueError:
        quantidade = 1

    cliente_id = None
    if cliente_id_str:
        try:
            cliente_id = int(cliente_id_str)
        except ValueError:
            cliente_id = None

    conn = db_conn()
    cur = conn.cursor()

    cur.execute("SELECT nome, preco FROM produtos WHERE id = %s;", (produto_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    produto_nome, preco = row
    valor_total = float(preco) * quantidade

    cur.execute(
        """
        INSERT INTO vendas (cliente_id, produto_id, quantidade, valor_total, data)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (cliente_id, produto_id, quantidade, valor_total, data),
    )

    descricao_venda = f"Venda: {produto_nome} (x{quantidade})"
    cur.execute(
        """
        INSERT INTO transactions (date, kind, category, description, amount)
        VALUES (%s, 'receita', 'Venda', %s, %s);
        """,
        (data, descricao_venda, valor_total),
    )

    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


# =======================================================
# RUN
# =======================================================

if __name__ == "__main__":
    app.run(debug=True)
