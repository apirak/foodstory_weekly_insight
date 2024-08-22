from http.server import HTTPServer, SimpleHTTPRequestHandler
import json


class APIHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/sales-data":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            with open("processed_sales_data.json", "rb") as file:
                self.wfile.write(file.read())
        else:
            super().do_GET()


def run(server_class=HTTPServer, handler_class=APIHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving on port {port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
