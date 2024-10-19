import os
import sys
import qrcode
import socket
import threading
import socketserver
from server import FileServer
from context_menu import menus


def run_server_(filenames, _):
    IP = get_ip()
    print(f"SERVER IP: {IP}")
    QR = input("qr show (yes / no) >>> ") or "now"
    run_server(IP, filenames[0], QR)


def add_context_menu():
    cm = menus.ContextMenu('Локальная сеть', type='FILES')
    cm.add_items([menus.ContextCommand('Запустить сервер...', python=run_server_)])
    cm.compile()

    cm = menus.ContextMenu('Локальная сеть', type='DIRECTORY')
    cm.add_items([menus.ContextCommand('Запустить сервер...', python=run_server_)])
    cm.compile()


def get_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as google:
        google.connect(('8.8.8.8', 80))
        return google.getsockname()[0]
    
    
def get_user_data(path: str | None):
    PATH = path or input(f"path (file or folder) ({os.environ['USERPROFILE']}\\Desktop) >>> ") or f"{os.environ['USERPROFILE']}\\Desktop"
    QR = input("qr show (yes / no) >>> ") or "now"
    
    return PATH, QR


def run_server(IP, PATH, QR):
    for PORT in range(2**16-1, 2**15 - 1, -1):
        try:
            with socketserver.TCPServer(("", PORT), FileServer) as server:
                if os.path.isfile(PATH):
                    os.chdir(os.path.dirname(PATH))
                    if QR == "yes":
                        threading.Thread(target=qrcode.make(f"http://{IP}:{PORT}/{os.path.basename(PATH)}").get_image().show).start()
                    print(f"Сервер запущен! -> http://{IP}:{PORT}/{os.path.basename(PATH)}")
                else:
                    os.chdir(PATH)
                    if QR == "yes":
                        threading.Thread(target=qrcode.make(f"http://{IP}:{PORT}").get_image().show).start()
                    print(f"Сервер запущен! -> http://{IP}:{PORT}")
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    print("Сервер закрыт!")
                    return
        except OSError:
            pass
        
        
def main():
    path = None
    if sys.argv.__len__() >= 4 and (os.path.isfile(sys.argv[3]) or os.path.isdir(sys.argv[3])):
        path = sys.argv[3]

    add_context_menu()
    IP = get_ip()
    print(f"SERVER IP: {IP}")
    PATH, QR = get_user_data(path)
    run_server(IP, PATH, QR)
    
        
if __name__ == '__main__':
    main()
