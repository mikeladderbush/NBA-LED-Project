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

    @server.route("/")
    def index(request: Request):
        html = """
        <html>
        <head>
            <title>Scoreboard Control</title>
        </head>
        <body style="font-family:sans-serif;text-align:center;margin-top:40px">

            <h2>Scoreboard Control</h2>

            <button onclick="fetch('/on')">Power On</button>
            <button onclick="fetch('/off')">Power Off</button>

            <br><br>

            <input id="teamBox" placeholder="Enter Team (ex: BOS)">
            <button onclick="setTeam()">Set Team</button>

            <script>
            function setTeam(){
                let t = document.getElementById("teamBox").value;
                fetch("/team?name=" + t);
            }
            </script>

        </body>
        </html>
        """
        return Response(request, html, content_type="text/html")

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
        name = name.upper()
        server_state["team"] = name
        return Response(request, f"Team set to {name}")


    # ---------- START SERVER ----------
    server.start(str(wifi.radio.ipv4_address))

    print("Server running:", wifi.radio.ipv4_address)

    return server, server_state