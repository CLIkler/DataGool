"""Punto de entrada DATAGOOL (MVC): servidor HTTP, inicialización de BD y programador de momios."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import config
from controllers import router
from models import db, log, partido
from services import odds_service


class Handler(BaseHTTPRequestHandler):
    def _enviar(self, status, ctype, body):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._enviar(*router.manejar_get(self.path))

    def do_POST(self):
        n = min(int(self.headers.get("Content-Length") or 0), 500_000)
        self._enviar(*router.manejar_post(self.path, self.rfile.read(n)))

    def log_message(self, *a):
        pass


def main():
    db.iniciar()
    r = partido.importar_csv_dir(config.HISTORICO_DIR)
    print(f"Histórico: +{r['insertados']} partidos ({r['duplicados']} ya existían, {r['invalidos']} inválidos)")
    if odds_service.iniciar_programador():
        print(f"Momios: actualización automática cada {config.ODDS_INTERVALO_HORAS} h")
    srv = ThreadingHTTPServer((config.HOST, config.PORT), Handler)
    print(f"DATAGOOL en http://{config.HOST}:{config.PORT}/")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.server_close()


if __name__ == "__main__":
    main()
