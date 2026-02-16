import wifi
import socketpool
import board
import digitalio
from adafruit_httpserver import Server, Request, Response

server_state = {"power": "off", "team":None}

def run_server():

    print("Starting Server")

    pool = socketpool.SocketPool(wifi.radio)
    server = Server(pool, "/static", debug=True)

    # ---------- ROUTES ----------

    @server.route("/on")
    def on(request: Request):
        server_state["power"] = "on"
        return Response(request, "OK")


    @server.route("/off")
    def off(request: Request):
        server_state["power"] = "off"
        return Response(request, "OK")


    @server.route("/team")
    def team(request: Request):
        name = request.query_params.get("name")
        server_state["team"] = name
        return Response(request, f"Team set to {name}")


    # ---------- START SERVER ----------
    server.start(str(wifi.radio.ipv4_address))

    print("Server running:", wifi.radio.ipv4_address)

    return server, server_state