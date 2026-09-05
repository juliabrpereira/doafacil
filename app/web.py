"""Interface web mínima para demonstrar a confirmação de uma doação.

Execute com ``python -m app.web`` e abra http://localhost:8000.
Os dados são mantidos apenas em memória, como no escopo atual do MVP.
"""

from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.domain import DomainError, EstadoDoacao, ONG, confirmar_doacao, criar_doacao


def criar_doacao_demo():
    """Cria o registro exibido pela interface de demonstração."""
    return criar_doacao(
        nome_doador="Ana Silva",
        email_doador="ana@example.com",
        ong=ONG(nome="Instituto Esperança"),
        valor="25.00",
    )


def renderizar_pagina(doacao, mensagem=""):
    """Gera a página com o estado da doação e sua ação disponível."""
    confirmada = doacao.estado is EstadoDoacao.CONFIRMADA
    acao = (
        '<p class="success">Doação confirmada.</p>'
        if confirmada
        else '''<form method="post" action="/confirmar">
  <button type="submit">Confirmar doação</button>
</form>'''
    )
    aviso = f'<p class="message">{escape(mensagem)}</p>' if mensagem else ""
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>DOA FÁCIL</title>
  <style>
    body {{ font-family: sans-serif; max-width: 42rem; margin: 3rem auto; padding: 0 1rem; }}
    button {{ padding: .65rem 1rem; cursor: pointer; }}
    .success {{ color: #16723a; }} .message {{ color: #9a3412; }}
  </style>
</head>
<body>
  <h1>DOA FÁCIL</h1>
  <h2>Doação</h2>
  <p><strong>Doador:</strong> {escape(doacao.nome_doador)}</p>
  <p><strong>ONG:</strong> {escape(doacao.ong.nome)}</p>
  <p><strong>Valor:</strong> R$ {doacao.valor:.2f}</p>
  <p><strong>Status:</strong> {doacao.estado.value}</p>
  {aviso}
  {acao}
</body>
</html>""".encode("utf-8")


class DoaFacilHandler(BaseHTTPRequestHandler):
    """Manipulador HTTP da única doação de demonstração."""

    doacao = criar_doacao_demo()

    def responder_html(self, corpo, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return
        self.responder_html(renderizar_pagina(self.doacao))

    def do_POST(self):
        if self.path != "/confirmar":
            self.send_error(404)
            return

        try:
            confirmar_doacao(self.doacao)
        except DomainError as erro:
            self.responder_html(renderizar_pagina(self.doacao, str(erro)), status=400)
            return

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


def executar_servidor(porta=8000):
    """Inicia a aplicação local."""
    servidor = HTTPServer(("localhost", porta), DoaFacilHandler)
    print(f"DOA FÁCIL disponível em http://localhost:{porta}")
    servidor.serve_forever()


if __name__ == "__main__":
    executar_servidor()
