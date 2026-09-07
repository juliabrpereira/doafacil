"""Interface web mínima para criar e confirmar doações.

Execute com ``python -m app.web`` e abra http://localhost:8000.
Os dados são mantidos apenas em memória, como no escopo atual do MVP.
"""

from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from app.domain import DomainError, EstadoDoacao, ONG, confirmar_doacao, criar_doacao


def criar_doacao_demo():
    """Cria o registro exibido pela interface de demonstração."""
    return criar_doacao(
        nome_doador="Ana Silva",
        email_doador="ana@example.com",
        ong=ONG(nome="Instituto Esperança"),
        valor="25.00",
    )


def criar_doacao_por_formulario(dados):
    """Cria uma doação a partir dos dados enviados pelo formulário web."""
    return criar_doacao(
        nome_doador=dados.get("nome_doador", [""])[0],
        email_doador=dados.get("email_doador", [""])[0],
        ong=ONG(nome=dados.get("ong", [""])[0]),
        valor=dados.get("valor", [""])[0],
    )


def renderizar_layout(titulo, conteudo):
    """Aplica a estrutura HTML comum às páginas da interface."""
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>{escape(titulo)} — DOA FÁCIL</title>
  <style>
    body {{ font-family: sans-serif; max-width: 42rem; margin: 3rem auto; padding: 0 1rem; }}
    button, .button {{
      display: inline-block;
      padding: .65rem 1rem;
      cursor: pointer;
      background: #166534;
      color: white;
      border: 0;
      border-radius: .25rem;
      font: inherit;
      text-decoration: none;
    }}
    button:hover, .button:hover {{ background: #14532d; }}
    .success {{ color: #16723a; }} .message {{ color: #9a3412; }}
    .doacao {{ border: 1px solid #ccc; border-radius: .25rem; margin: 1rem 0; padding: 1rem; }}
  </style>
</head>
<body>
  <h1>DOA FÁCIL</h1>
  {conteudo}
</body>
</html>""".encode("utf-8")


def renderizar_landing():
    """Gera a página inicial com os atalhos de navegação."""
    return renderizar_layout(
        "Início",
        '''<p>Conectamos doadores e ONGs.</p>
  <p>
    <a class="button" href="/criar">Criar doação</a>
    <a class="button" href="/doacoes">Ver doações</a>
  </p>''',
    )


def renderizar_formulario(mensagem=""):
    """Gera a página para criar uma nova doação."""
    aviso = f'<p class="message">{escape(mensagem)}</p>' if mensagem else ""
    return renderizar_layout(
        "Criar doação",
        f'''<h2>Criar doação</h2>
  {aviso}
  <form method="post" action="/criar">
    <p><label>Nome do doador: <input name="nome_doador" required></label></p>
    <p><label>E-mail do doador: <input type="email" name="email_doador" required></label></p>
    <p><label>ONG: <input name="ong" required></label></p>
    <p><label>Valor: <input type="number" name="valor" min="0.01" step="0.01" required></label></p>
    <button type="submit">Criar doação</button>
  </form>
  <p><a href="/">Voltar ao início</a></p>''',
    )


def renderizar_doacoes(doacoes, mensagem=""):
    """Gera a página que lista as doações mantidas em memória."""
    aviso = f'<p class="message">{escape(mensagem)}</p>' if mensagem else ""
    itens = []
    for indice, doacao in enumerate(doacoes):
        acao = (
            '<p class="success">Doação confirmada.</p>'
            if doacao.estado is EstadoDoacao.CONFIRMADA
            else f'''<form method="post" action="/confirmar/{indice}">
  <button type="submit">Confirmar doação</button>
</form>'''
        )
        itens.append(f'''<section class="doacao">
  <p><strong>Doador:</strong> {escape(doacao.nome_doador)}</p>
  <p><strong>ONG:</strong> {escape(doacao.ong.nome)}</p>
  <p><strong>Valor:</strong> R$ {doacao.valor:.2f}</p>
  <p><strong>Status:</strong> {doacao.estado.value}</p>
  {acao}
</section>''')

    conteudo = "<p>Nenhuma doação cadastrada.</p>" if not itens else "\n".join(itens)
    return renderizar_layout(
        "Doações",
        f'''<h2>Doações</h2>
  {aviso}
  {conteudo}
  <p><a href="/criar">Criar doação</a> · <a href="/">Voltar ao início</a></p>''',
    )


def renderizar_pagina(doacao, mensagem=""):
    """Mantém a renderização de uma doação para os consumidores existentes."""
    return renderizar_doacoes([doacao], mensagem)


class DoaFacilHandler(BaseHTTPRequestHandler):
    """Manipulador HTTP das doações de demonstração em memória."""

    doacoes = [criar_doacao_demo()]

    def responder_html(self, corpo, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        if self.path == "/":
            self.responder_html(renderizar_landing())
            return
        if self.path == "/criar":
            self.responder_html(renderizar_formulario())
            return
        if self.path == "/doacoes":
            self.responder_html(renderizar_doacoes(self.doacoes))
            return
        self.send_error(404)

    def do_POST(self):
        if self.path == "/criar":
            tamanho = int(self.headers.get("Content-Length", "0"))
            dados = parse_qs(self.rfile.read(tamanho).decode("utf-8"), keep_blank_values=True)
            try:
                type(self).doacoes.append(criar_doacao_por_formulario(dados))
            except DomainError as erro:
                self.responder_html(renderizar_formulario(str(erro)), status=400)
                return

            self.send_response(303)
            self.send_header("Location", "/doacoes")
            self.end_headers()
            return

        if not self.path.startswith("/confirmar/"):
            self.send_error(404)
            return

        try:
            indice = int(self.path.removeprefix("/confirmar/"))
            if indice < 0:
                raise IndexError
            doacao = self.doacoes[indice]
            confirmar_doacao(doacao)
        except (DomainError, IndexError, ValueError) as erro:
            if not isinstance(erro, DomainError):
                self.send_error(404)
                return
            self.responder_html(renderizar_doacoes(self.doacoes, str(erro)), status=400)
            return

        self.send_response(303)
        self.send_header("Location", "/doacoes")
        self.end_headers()


def executar_servidor(porta=8000):
    """Inicia a aplicação local."""
    servidor = HTTPServer(("localhost", porta), DoaFacilHandler)
    print(f"DOA FÁCIL disponível em http://localhost:{porta}")
    servidor.serve_forever()


if __name__ == "__main__":
    executar_servidor()
