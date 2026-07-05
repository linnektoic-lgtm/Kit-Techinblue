# ===================================================
# KIT TECHINBLUE - VERSÃO CUSTOMTKINTER GUI (2026)
# Criado por: Linnek Fernandes
# Contato Comercial: (81)98797-2730 - Contato Particular (81)98433-0974 👈😘
# ===================================================

#====== Próxima melhoria: Ajuste do monitor de temperatura e novos programas e funções na Versão 3.0 😘

# ⚠️ AVISO AOS DEVS
# NOTA: O código ainda precisa de mais comentários.
# Estou documentando função por função para melhor aprendizado.
# Se quiser ajudar, fique à vontade!

# ===================================================
# BIBLIOTECAS PADRÃO DO PYTHON
# ===================================================
import os              # Manipulação de arquivos e pastas
import sys             # Acesso a variáveis e funções do sistema
import ctypes          # Acesso a DLLs do Windows - Usado pra rodar como Admin
import subprocess      # Execução de comandos CMD/PowerShell
import threading       # Rodar tarefas em segundo plano sem travar a GUI
from datetime import datetime # Data e Hora pro log e relatório

# ===================================================
# BIBLIOTECAS DE INTERFACE GRÁFICA
# ===================================================
import tkinter as tk                   # Base do Tkinter
from tkinter import messagebox         # Caixas de alerta e confirmação
import customtkinter as ctk            # GUI Moderna e escura do Kit-Techinblue

# ===================================================
# BIBLIOTECAS DE HARDWARE E SISTEMA
# ===================================================
import psutil          # Monitoramento de CPU, RAM, Disco
import platform        # Informações do Sistema Operacional
import webbrowser      # Abrir links de suporte: Dell, Google


# ===================================================
# CONFIGURAÇÕES GLOBAIS DE TEMA DO CUSTOMTKINTER
# ===================================================
ctk.set_appearance_mode("dark")  # Define tema Dark para todo o sistema
ctk.set_default_color_theme("green")  # Tema Verde Techinblue - Identidade visual


class KitTechinblueGUI:
    def __init__(self, root):
        """
        FUNÇÃO: Construtor da Classe Principal
        OBJETIVO: Configura janela, pastas, banco de dados e inicia a interface
        """
        self.root = root
        self.root.title("Kit Techinblue - Painel de Controle 2.0")

        # ===================================================
        # BLOCO: CONFIGURAÇÃO DO ÍCONE DA JANELA
        # DESC: Detecta se está rodando como .py ou .exe PyInstaller
        # ===================================================
        try:
            # [FIX] PyInstaller extrai arquivos em uma pasta temporária _MEIPASS
            if getattr(sys, 'frozen', False):
                base_dir = sys._MEIPASS  # Caminho do executável compilado
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))  # Caminho do .py

            icon_path = os.path.join(base_dir, "techinblue.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)  # Aplica o ícone se encontrar
        except Exception:
            pass  # Falha silenciosa pra não travar se não achar o .ico
        # --- FIM BLOCO ÍCONE ---

        # Vincula o botão "X" da janela a função de confirmação de saída
        self.root.protocol("WM_DELETE_WINDOW", self.confirmar_saida)

        # ===================================================
        # BLOCO: GEOMETRIA E POSICIONAMENTO DA JANELA
        # DESC: Define tamanho e cola a janela no topo central do monitor
        # ===================================================
        largura, altura = 1000, 720
        self.root.update_idletasks()  # Atualiza pra pegar resolução real

        x = (self.root.winfo_screenwidth() // 2) - (largura // 2)  # Centraliza na horizontal
        y = 0  # Cola no topo da tela

        self.root.geometry(f"{largura}x{altura}+{x}+{y}")
        self.root.configure(fg_color="#121212")  # Fundo cinza escuro

        # ===================================================
        # BLOCO: VARIÁVEIS DE CONTROLE GLOBAIS
        # DESC: Usadas para cancelar processos e travar a GUI
        # ===================================================
        self.cancelar_operacao = False  # Flag para cancelar instalação/otimização
        self.processo_atual = None  # Guarda o subprocess.Popen atual

        # ===================================================
        # BLOCO: CONFIGURAÇÃO DE PASTAS E LOGS
        # DESC: Cria pasta de downloads e arquivo de log. Funciona em .py e .exe
        # ===================================================
        # [FIX] Portabilidade: Pega caminho correto se for executável ou script
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)  # Pasta do .exe
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))  # Pasta do .py

        self.pasta_downloads = os.path.join(base_dir, "Downloads_Kit_Techinblue")
        if not os.path.exists(self.pasta_downloads):
            os.makedirs(self.pasta_downloads)  # Cria pasta se não existir

        self.relatorio_path = os.path.join(self.pasta_downloads, "Log_Relatorio_Instalacao.txt")
        self.inicializar_relatorio()  # Zera/Cria o arquivo de log

        # ===================================================
        # BLOCO: BANCO DE DADOS DE PROGRAMAS
        # DESC: Lista todos os programas do "Plano 1, 2 e 3". Link + Nome do Arq + Parâmetros Silent
        #  - Adicionar novos programas aqui seguindo o padrão
        # ===================================================
        self.banco_programas = {
            # --- PLANO 1: ESSENCIAIS ---
            "7ZIP": {"link": "https://www.7-zip.org/a/7z2408-x64.exe", "arq": "7zip.exe", "params": "/S"},
            "JAVA": {"link": "https://download.oracle.com/java/21/latest/jdk-21_windows-x64_bin.exe", "arq": "Java.exe",
                     "params": "/s"},
            "CHROME": {"link": "https://dl.google.com/chrome/install/latest/chrome_installer.exe", "arq": "Chrome.exe",
                       "params": "/silent /install"},
            "EDGE": {"link": "https://go.microsoft.com/fwlink/?linkid=2109147", "arq": "Edge.exe",
                     "params": "/silent /install"},

            # --- PLANO 2: COMUNICAÇÃO / PRODUTIVIDADE ---
            "FIREFOX": {"link": "https://download.mozilla.org/?product=firefox-msi-latest-ssl&os=win64&lang=pt-BR",
                        "arq": "Firefox.msi", "params": "/passive /norestart"},
            "ADOBE": {
                "link": "https://ftp.adobe.com/pub/adobe/reader/win/AcrobatDC/2400220300/AcroRdrDC2400220300_pt_BR.exe",
                "arq": "Adobe.exe", "params": "/sAll /msi /norestart"},
            "OFFICE 365/2021": {
                "link": "https://c2rsetup.officeapps.live.com/c2r/download.aspx?ProductreleaseID=O365ProPlusRetail&platform=x64&language=pt-br",
                "arq": "OfficeSetup.exe", "params": ""},

            # --- PLANO 3: SUPORTE / ESPECÍFICOS ---
            "TEAMVIEWER": {"link": "https://download.teamviewer.com/pub/tv/TeamViewer_Host.msi",
                           "arq": "TeamViewer.msi", "params": "/passive /norestart"},
            "ANYDESK": {"link": "https://download.anydesk.com/AnyDesk.exe", "arq": "AnyDesk.exe",
                        "params": '--install "C:\\Program Files\\AnyDesk" --start-with-win --silent'},
            "WINRAR": {"link": "https://www.win-rar.com/fileadmin/winrar-versions/winrar-x64-631br.exe",
                       "arq": "WinRAR.exe", "params": "/S"},
            "MILVUS AGENTE": {"link": "https://update.milvus.com.br/downloads/110.0.0.4/x64/Setup_Milvus.exe",
                              "arq": "Setup_Milvus.exe", "params": "/S"}
        }

        # ===================================================
        # BLOCO: VARIÁVEIS DAS CHECKBOXES
        # DESC: Cria um BooleanVar para cada programa, já marcado como True
        # ===================================================
        self.check_vars = {prog: tk.BooleanVar(value=True) for prog in self.banco_programas}

        # Inicia a montagem da interface
        self.criar_interface()

        # --- BLOQUEIO APÓS CARREGAR ---
        # Chama a verificação de senha 100ms após a janela carregar
        self.root.after(100, self.verificar_senha_interface)

    def confirmar_saida(self):
        # Cria uma mini janela filha customizada
        janela_confirma = ctk.CTkToplevel(self.root)
        janela_confirma.title("Sair")
        janela_confirma.geometry("300x150")
        janela_confirma.resizable(False, False)
        janela_confirma.transient(self.root)
        janela_confirma.grab_set()

        # Centralização rápida
        janela_confirma.update_idletasks()
        p_x, p_y = self.root.winfo_x(), self.root.winfo_y()
        p_w, p_h = self.root.winfo_width(), self.root.winfo_height()
        janela_confirma.geometry(f"300x150+{p_x + (p_w // 2) - 150}+{p_y + (p_h // 2) - 75}")

        lbl = ctk.CTkLabel(janela_confirma, text="Deseja realmente fechar o sistema?", font=("Consolas", 12))
        lbl.pack(pady=20)

        frame_btn = ctk.CTkFrame(janela_confirma, fg_color="transparent")
        frame_btn.pack(fill=ctk.X, padx=20)

        btn_sim = ctk.CTkButton(frame_btn, text="Sim", fg_color="#3d1f1f", text_color="#FF3333", width=100,
                                command=self.root.quit)  # Ou self.root.destroy
        btn_sim.pack(side=ctk.LEFT, expand=True, padx=5)

        btn_nao = ctk.CTkButton(frame_btn, text="Não", fg_color="#2b2b2b", text_color="#ffffff", width=100,
                                command=janela_confirma.destroy)
        btn_nao.pack(side=ctk.RIGHT, expand=True, padx=5)

    def verificar_senha_interface(self):
        # Cria um frame que cobre a tela toda
        self.frame_bloqueio = ctk.CTkFrame(self.root, fg_color="#000000")
        self.frame_bloqueio.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Centraliza o pedido de senha
        frame_login = ctk.CTkFrame(self.frame_bloqueio, fg_color="#1a1a1a")
        frame_login.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame_login, text="🔐 TECHINBLUE - ACESSO RESTRITO", font=("Consolas", 18, "bold")).pack(pady=20, padx=40)

        self.entry_senha = ctk.CTkEntry(frame_login, placeholder_text="Senha do Técnico", show="*")
        self.entry_senha.pack(pady=10, padx=20)

        btn_entrar = ctk.CTkButton(frame_login, text="DESBLOQUEAR", command=self.validar_senha)
        btn_entrar.pack(pady=20, padx=20)

        self.entry_senha.bind('<Return>', lambda event: self.validar_senha())

    def validar_senha(self):
        if self.entry_senha.get() == "SuaSenhaAqui!": # Defina sua senha aqui 👈🫡
            self.frame_bloqueio.destroy()
            self.log("[SISTEMA] Acesso liberado pelo técnico da Techinblue.")
        else:
            messagebox.showerror("Acesso Negado", "Senha incorreta! Verifique a senha com a Techinblue!")
            self.entry_senha.delete(0, 'end')

    def aplicar_config_rede_admin(self):
        self.log("=== Iniciando Configurações de Rede e Acesso ===")
        self.cancelar_operacao = False

        # 1. DESATIVAR IPV6
        try:
            self.log("[1/3] Desativando IPv6 nas interfaces de rede...")
            cmd_ipv6 = 'Get-NetAdapterBinding -ComponentID ms_tcpip6 | Disable-NetAdapterBinding -PassThru'
            self.processo_atual = subprocess.Popen(["powershell", "-Command", cmd_ipv6], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.processo_atual.wait()
            if self.processo_atual.returncode == 0:
                self.log("[OK] IPv6 desativado com sucesso.")
            else:
                self.log("[AVISO] Falha ao desativar IPv6. Rode como Admin.")
        except Exception as e:
            self.log(f"[ERRO] IPv6: {str(e)}")

        if self.cancelar_operacao: return

        # 2. CRIAR GRUPO LOCAL E ADICIONAR EM ADMINISTRADORES
        try:
            self.log("[2/3] Criando grupo 'G_SupLocal' e adicionando aos Administradores...")
            # Comando cria o grupo se não existir e já joga nos admins locais
            cmd_grupo = """
            if (-not (Get-LocalGroup -Name "G_SupLocal" -ErrorAction SilentlyContinue)) { 
                New-LocalGroup -Name "G_SupLocal" -Description "Grupo Suporte Techinblue" 
            }; 
            Add-LocalGroupMember -Group "Administradores" -Member "G_SupLocal" -ErrorAction SilentlyContinue
            """
            self.processo_atual = subprocess.Popen(["powershell", "-Command", cmd_grupo], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.processo_atual.wait()
            if self.processo_atual.returncode == 0:
                self.log("[OK] Grupo 'G_SupLocal' criado e adicionado em Administradores.")
            else:
                self.log("[AVISO] Falha ao criar grupo. Verifique se já existe.")
        except Exception as e:
            self.log(f"[ERRO] Grupo: {str(e)}")

        if self.cancelar_operacao: return

        # 3. ATIVAR RDP - ACESSO REMOTO
        try:
            self.log("[3/3] Ativando Acesso Remoto RDP e liberando no Firewall...")
            cmd_rdp = """
            Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -name "fDenyTSConnections" -Value 0;
            Enable-NetFirewallRule -DisplayGroup "Área de Trabalho Remota"
            """
            self.processo_atual = subprocess.Popen(["powershell", "-Command", cmd_rdp], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.processo_atual.wait()
            if self.processo_atual.returncode == 0:
                self.log("[OK] RDP ativado e regra de firewall liberada.")
            else:
                self.log("[AVISO] Falha ao ativar RDP.")
        except Exception as e:
            self.log(f"[ERRO] RDP: {str(e)}")

        self.processo_atual = None
        self.log("=== Configurações de Rede e Acesso Finalizadas ===")

    def abrir_usuarios(self):
        self.log("Abrindo gerenciador de usuários...")
        subprocess.run("lusrmgr.msc", shell=True)

    def resetar_dns(self):
        self.log("Resetando cache de DNS e renovando IP...")
        comandos = ["ipconfig /flushdns", "ipconfig /release", "ipconfig /renew"]
        for cmd in comandos:
            subprocess.run(cmd, shell=True)
        self.log("[OK] DNS resetado e IP renovado.")


    def ingressar_dominio(self):
        # Abre o menu de sistema para o técnico digitar o domínio manualmente
        self.log("Abrindo configurações de Domínio...")
        subprocess.run("sysdm.cpl", shell=True)
        messagebox.showinfo("Domínio", "Digite o domínio e as credenciais na janela que se abriu.")

    def abrir_janela_monitoramento(self):
        janela_monitor = ctk.CTkToplevel(self.root)
        janela_monitor.title("Monitoramento e Suporte Techinblue")
        janela_monitor.geometry("480x620")  # Aumentado para acomodar as informações de memória onboard sem quebras

        # --- BLOQUEIO DA TELA PRINCIPAL (MODAL) ---
        janela_monitor.transient(self.root)  # Define como janela filha (vinculada à principal)
        janela_monitor.grab_set()  # Bloqueia cliques e interações na janela principal

        # --- CENTRALIZAÇÃO ---
        janela_monitor.update_idletasks()
        p_x, p_y = self.root.winfo_x(), self.root.winfo_y()
        p_w, p_h = self.root.winfo_width(), self.root.winfo_height()
        janela_monitor.geometry(f"480x620+{p_x + (p_w // 2) - 240}+{p_y + (p_h // 2) - 310}")

        janela_monitor.focus()

        ctk.CTkLabel(janela_monitor, text="STATUS DO SISTEMA", font=("Consolas", 16, "bold"),
                     text_color="#00FF66").pack(pady=20)

        # Aviso de cores dos HDs Principal - Secundário
        ctk.CTkLabel(janela_monitor, text="Informação de Disco: Verde: Principal | Azul: Secundário",
                     font=("Consolas", 10), text_color="#aaaaaa").pack()

        self.lbl_info = ctk.CTkLabel(janela_monitor, text="Coletando dados...", font=("Consolas", 12), justify="left")
        self.lbl_info.pack(pady=10)

        # --- BOTÃO EXTRA: TOP 8 CONSUMIDORES DE MEMÓRIA (AMPLIADO) ---
        btn_maior_ram = ctk.CTkButton(janela_monitor, text="Ver Top 8 Consumidores de RAM", fg_color="#2b2b2b",
                                      text_color="#00FF66",
                                      hover_color="#333333", font=("Consolas", 11, "bold"), height=28,
                                      command=lambda: self.mostrar_maior_consumidor_ram(janela_monitor))
        btn_maior_ram.pack(pady=(0, 10))

        # Container para a lista de discos colorida
        self.frame_discos = ctk.CTkFrame(janela_monitor, fg_color="transparent")
        self.frame_discos.pack(fill=ctk.X, padx=40, pady=5)

        # Links
        ctk.CTkLabel(janela_monitor, text="LINKS ÚTEIS", font=("Consolas", 14, "bold"), text_color="#00FF66").pack(
            pady=(20, 10))
        ctk.CTkButton(janela_monitor, text="Suporte DELL", fg_color="#333",
                      command=lambda: webbrowser.open("https://www.dell.com/support/home/pt-br")).pack(fill=ctk.X,
                                                                                                       padx=40, pady=5)
        ctk.CTkButton(janela_monitor, text="Google", fg_color="#333",
                      command=lambda: webbrowser.open("https://google.com")).pack(fill=ctk.X, padx=40, pady=5)

        # --- COLETAR INFORMAÇÕES DE HARDWARE QUE NÃO MUDAM (Roda uma única vez) ---
        # 1. Pega o modelo comercial exato do processador direto pelo Registro do Windows (Leve e nativo)
        self.modelo_cpu = "Desconhecido"
        if platform.system() == "Windows":
            try:
                comando = 'reg query "HKLM\\HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0" /v ProcessorNameString'
                saida = subprocess.check_output(comando, shell=True).decode('utf-8', errors='ignore')
                for linha in saida.splitlines():
                    if "ProcessorNameString" in linha:
                        self.modelo_cpu = linha.split("REG_SZ")[-1].strip()
                        break
            except:
                pass
        if self.modelo_cpu == "Desconhecido":
            self.modelo_cpu = platform.processor()

        # 2. Pega detalhes da memória RAM (Velocidade individual, Slots, Dual Channel e Tipo Integrado)
        self.velocidade_ram = "Desconhecida"
        self.slots_ram = "Desconhecido"
        self.canal_ram = "Single Channel"
        self.onboard_ram = "Não Detectada (Pentes Removíveis)"

        if platform.system() == "Windows":
            try:
                # Coleta velocidades individuais de cada chip/pente ativo
                comando_ram = "wmic memorychip get speed"
                resultado = subprocess.check_output(comando_ram, shell=True).decode('utf-8').strip().split()
                if len(resultado) > 1:
                    # Filtra apenas os números das velocidades encontradas
                    frequencias = [f"{v} MHz" for v in resultado[1:] if v.isdigit()]
                    if frequencias:
                        # Exibe separado por "+" caso encontre múltiplos pentes (ex: 3200 + 3200 MHz)
                        self.velocidade_ram = " + ".join([v.split()[0] for v in frequencias]) + " MHz"

                    pentes_ativos = len(resultado) - 1
                    self.slots_ram = f"{pentes_ativos} ocupado(s)"

                    if pentes_ativos >= 2:
                        self.canal_ram = "Dual Channel (Ativo)"

                # Coleta estendida para garantir a detecção Onboard
                comando_onboard = "wmic memorychip get formfactor, banklabel, devicelocator"
                saida_onboard = subprocess.check_output(comando_onboard, shell=True).decode('utf-8',
                                                                                            errors='ignore').strip().lower().splitlines()

                # Termos de engenharia comuns para pentes soldados
                termos_onboard = ["onboard", "embedded", "soldered", "integrated", "system board", "u3e1", "bank 0",
                                  "bank0"]

                for linha in saida_onboard[1:]:
                    partes = linha.split()
                    if partes:
                        # Se o formfactor for 0 (Unknown) ou contiver qualquer nomenclatura Onboard no mapeamento físico
                        if "0" in partes or any(termo in linha for termo in termos_onboard):
                            self.onboard_ram = "Sim (Memória Integrada na Placa)"
                            break
            except:
                pass

        # 3. Pega as informações da Placa de Vídeo (Integrada ou Dedicada PCI Express)
        self.modelo_gpu = "Não possui"
        if platform.system() == "Windows":
            try:
                command_gpu = "wmic path win32_videocontroller get name"
                resultado_gpu = subprocess.check_output(command_gpu, shell=True).decode('utf-8',
                                                                                        errors='ignore').strip().splitlines()
                gpus_encontradas = [linha.strip() for linha in resultado_gpu[1:] if linha.strip()]
                if gpus_encontradas:
                    self.modelo_gpu = " / ".join(gpus_encontradas)
            except:
                pass

        self.atualizar_monitor(janela_monitor)

    def mostrar_maior_consumidor_ram(self, janela_pai):
        processos = []

        # Faz uma varredura rápida coletando nome e consumo de memória
        for proc in psutil.process_iter(['name', 'memory_percent']):
            try:
                percentual = proc.info['memory_percent']
                nome = proc.info['name']
                if percentual and percentual > 0.1:  # Ignora processos irrelevantes (< 0.1%)
                    processos.append((nome, percentual))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Ordena do maior consumo para o menor e isola os 8 primeiros
        top_8 = sorted(processos, key=lambda x: x[1], reverse=True)[:8]

        if top_8:
            # Cria uma subjanela para listar o ranking de forma organizada
            janela_top = ctk.CTkToplevel(self.root)
            janela_top.title("Top 8 Consumo de RAM")
            janela_top.geometry("360x340")
            janela_top.resizable(False, False)

            # Bloqueia a janela de monitoramento enquanto o Top 8 estiver aberto
            janela_top.transient(janela_top.master)
            janela_top.grab_set()

            # --- RETORNA O BLOQUEIO EXPLICITAMENTE PARA A JANELA DE MONITORAMENTO AO FECHAR ---
            def fechar_sub_monitor():
                janela_top.destroy()
                if janela_pai.winfo_exists():
                    janela_pai.grab_set()

            janela_top.protocol("WM_DELETE_WINDOW", fechar_sub_monitor)

            # Centraliza a nova janela em relação à janela principal
            janela_top.update_idletasks()
            p_x, p_y = self.root.winfo_x(), self.root.winfo_y()
            p_w, p_h = self.root.winfo_width(), self.root.winfo_height()
            janela_top.geometry(f"360x340+{p_x + (p_w // 2) - 180}+{p_y + (p_h // 2) - 170}")

            janela_top.focus()

            ctk.CTkLabel(janela_top, text="RANKING DE CONSUMO (RAM)", font=("Consolas", 14, "bold"),
                         text_color="#00FF66").pack(pady=15)

            # Container interno estilizado para a lista
            frame_lista = ctk.CTkFrame(janela_top, fg_color="#1e1e1e", border_width=1, border_color="#333")
            frame_lista.pack(fill=ctk.BOTH, expand=True, padx=20, pady=(0, 20))

            for i, (nome, pct) in enumerate(top_8, start=1):
                # Formata e limita o tamanho do nome para não quebrar o alinhamento
                nome_formatado = nome if len(nome) <= 22 else f"{nome[:19]}..."
                texto_linha = f"{i}. {nome_formatado:<22} -> {pct:>5.1f}%"

                # Destaca o primeiro colocado em verde e o resto em branco
                cor_linha = "#00FF66" if i == 1 else "#ffffff"

                ctk.CTkLabel(frame_lista, text=texto_linha, font=("Consolas", 12),
                             text_color=cor_linha, justify="left").pack(anchor="w", padx=20, pady=4)
        else:
            messagebox.showwarning("Aviso", "Não foi possível coletar os dados dos processos no momento.")

    def atualizar_monitor(self, janela):
        if janela.winfo_exists():
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()

            # --- CAPTURA DA TEMPERATURA DA CPU EM TEMPO REAL ---
            temp_cpu = "N/A"
            if platform.system() == "Windows":
                try:
                    cmd_temp = "wmic /namespace:\\\\root\\wmi PATH MSAcpi_ThermalZoneTemperature get CurrentTemperature"
                    saida_temp = subprocess.check_output(cmd_temp, shell=True).decode('utf-8').strip().splitlines()
                    if len(saida_temp) > 1 and saida_temp[1].strip().isdigit():
                        # Converte de Kelvin (padrão ACPI) para Celsius
                        temp_celsius = (int(saida_temp[1].strip()) / 10.0) - 273.15
                        temp_cpu = f"{temp_celsius:.1f} °C"
                except:
                    temp_cpu = "Incompatível"

            # CPU, RAM e GPU organizadas (com frequências, canais e detecção de onboard isolados)
            info_txt = (f"PROCESSADOR: {self.modelo_cpu}\n"
                        f"CPU USO:     {cpu:>6.1f}%\n"
                        #f"CPU TEMP:    {temp_cpu}\n"  # <--- TEMPERATURA ADICIONADA AQUI / Só na V3 🫡 Falta aplicar umas Dll e ajustar o codigo 🙏🏼
                        f"RAM TOTAL:   {round(mem.total / (1024 ** 3))} GB\n"
                        f"RAM FREQ:    {self.velocidade_ram}\n"
                        f"RAM SLOTS:   {self.slots_ram}\n"
                        f"RAM MODO:    {self.canal_ram}\n"
                        f"RAM PLACA:   {self.onboard_ram}\n"
                        f"RAM EM USO:  {mem.percent:>6.1f}%\n"
                        f"VÍDEO / GPU: {self.modelo_gpu}")
            self.lbl_info.configure(text=info_txt)

            # Limpa o frame de discos antes de redesenhar
            for widget in self.frame_discos.winfo_children():
                widget.destroy()

            # Itera sobre os discos fixos
            for particao in psutil.disk_partitions():
                if 'fixed' in particao.opts:
                    try:
                        uso = psutil.disk_usage(particao.mountpoint)

                        # Cálculo dos valores em GB
                        total_gb = round(uso.total / (1024 ** 3))
                        livre_gb = round(uso.free / (1024 ** 3))
                        ocupado_perc = uso.percent

                        # Define cor: Verde para C:, Azul para os outros
                        cor = "#00FF66" if particao.device.startswith("C:") else "#3399FF"

                        # Formata o texto: ex: C: 476GB (120GB livre) | 74.8% ocupado
                        txt = f"{particao.device} {total_gb}GB ({livre_gb}GB livre) | {ocupado_perc:.1f}% ocupado"

                        ctk.CTkLabel(self.frame_discos, text=txt, text_color=cor,
                                     font=("Consolas", 11, "bold")).pack(anchor="w")
                    except:
                        continue

            janela.after(2000, lambda: self.atualizar_monitor(janela))




    def inicializar_relatorio(self):
        if not os.path.exists(self.relatorio_path):
            with open(self.relatorio_path, "w", encoding="utf-8") as f:
                f.write("========================================\n")
                f.write("     RELATORIO DE INSTALACAO - TECHINBLUE   \n")
                f.write(f"     Data: {datetime.now().strftime('%d/%m/%Y as %H:%M:%S')}\n")
                f.write("========================================\n")

    def log(self, mensagem):
        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        texto_completo = f"{timestamp}{mensagem}\n"
        self.txt_console.insert("end", texto_completo)
        self.txt_console.see("end")

        with open(self.relatorio_path, "a", encoding="utf-8") as f:
            f.write(texto_completo)

    def alternar_selecao_todos(self):
        # Verifica o estado do "Selecionar Todos" e aplica nas outras variáveis
        estado = self.var_selecionar_todos.get()
        for nome in self.check_vars:
            self.check_vars[nome].set(estado)

    def criar_interface(self):
        # --- ESTILIZAÇÃO DO HEADER ---
        header_frame = ctk.CTkFrame(self.root, fg_color="#1a1a1a", corner_radius=8)
        header_frame.pack(fill=ctk.X, padx=15, pady=10)

        lbl_titulo = ctk.CTkLabel(header_frame, text="KIT TECHINBLUE", font=("Consolas", 20, "bold"),
                                  text_color="#00FF66")
        lbl_titulo.pack(pady=(5, 2))
        lbl_autor = ctk.CTkLabel(header_frame, text="Criado por: Linnek Fernandes | Contato: (81)98797-2730",
                                 font=("Consolas", 11), text_color="#aaaaaa")
        lbl_autor.pack(pady=(0, 5))

        # --- CORPO PRINCIPAL ---
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=5)

        # Coluna Esquerda: Programas e Lotes
        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=(0, 10))

        # --- NOVO BLOCO PROGRAMAS INDIVIDUAIS COM SELEÇÃO TOTAL ---
        prog_lf = ctk.CTkFrame(left_frame, fg_color="#1a1a1a", corner_radius=8)
        prog_lf.pack(fill=ctk.BOTH, expand=True, pady=(0, 10))

        # Header com o Checkbox Mestre
        header_prog_frame = ctk.CTkFrame(prog_lf, fg_color="transparent")
        header_prog_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=10)

        lbl_section1 = ctk.CTkLabel(header_prog_frame, text=" Programas Individuais ",
                                    font=("Consolas", 13, "bold"), text_color="#00FF66")
        lbl_section1.pack(side=ctk.LEFT)

        self.var_selecionar_todos = tk.BooleanVar(value=True)
        chk_todos = ctk.CTkCheckBox(header_prog_frame, text="Marcar Todos",
                                    variable=self.var_selecionar_todos,
                                    command=self.alternar_selecao_todos,
                                    font=("Consolas", 11, "bold"), text_color="#00FF66",
                                    checkbox_height=18, checkbox_width=18)
        chk_todos.pack(side=ctk.RIGHT)

        # Loop de criação dos checkboxes individuais
        row = 1
        for nome in self.banco_programas.keys():
            chk = ctk.CTkCheckBox(prog_lf, text=nome, variable=self.check_vars[nome], font=("Consolas", 12),
                                  text_color="#ffffff")
            chk.grid(row=row, column=0, sticky="w", padx=20, pady=4)

            btn_instalar = ctk.CTkButton(prog_lf, text="Instalar",
                                         command=lambda n=nome: self.acao_async(self.instalar_programa, n),
                                         font=("Consolas", 11, "bold"), fg_color="#2b2b2b", text_color="#00FF66",
                                         hover_color="#333333", width=90, height=26)
            btn_instalar.grid(row=row, column=1, padx=20, pady=4, sticky="e")
            row += 1

        prog_lf.grid_columnconfigure(0, weight=1)
        prog_lf.grid_columnconfigure(1, weight=0)

        # Bloco de Ações em Lote
        lote_lf = ctk.CTkFrame(left_frame, fg_color="#1a1a1a", corner_radius=8)
        lote_lf.pack(fill=ctk.X, pady=(0, 5))

        lbl_section2 = ctk.CTkLabel(lote_lf, text=" Instalação em Lote ", font=("Consolas", 13, "bold"),
                                    text_color="#00FF66")
        lbl_section2.pack(anchor="w", padx=15, pady=(8, 4))

        btn_lote_soft = ctk.CTkButton(lote_lf, text="19 - INSTALAR SELECIONADOS",
                                      command=lambda: self.acao_async(self.instalar_lote, False), fg_color="#1f3d24",
                                      text_color="#00FF66", height=38)
        btn_lote_soft.pack(fill=ctk.X, padx=15, pady=5)

        btn_lote_tudo = ctk.CTkButton(lote_lf, text="20 - INSTALAR TUDO + REPAROS",
                                      command=lambda: self.acao_async(self.instalar_lote, True), fg_color="#3d1f1f",
                                      text_color="#FF3333", height=38)
        btn_lote_tudo.pack(fill=ctk.X, padx=15, pady=(5, 12))

        # Coluna Direita: Ferramentas e Console
        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)

        # Bloco Ferramentas (CRIADO PRIMEIRO PARA RECEBER OS BOTÕES)
        ferramentas_lf = ctk.CTkFrame(right_frame, fg_color="#1a1a1a", corner_radius=8)
        ferramentas_lf.pack(fill=ctk.X, pady=(0, 10))

        lbl_section3 = ctk.CTkLabel(ferramentas_lf, text=" Reparos e Ferramentas ", font=("Consolas", 13, "bold"),
                                    text_color="#00FF66")
        lbl_section3.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(8, 4))

        # Grid de botões
        botoes = [
            ("SFC + DISM", lambda: self.acao_async(self.rodar_sfc_dism)),
            ("Limpeza de Disco", lambda: self.acao_async(self.rodar_limpeza)),
            ("CHKDSK (Boot)", lambda: self.acao_async(self.rodar_chkdsk)),
            ("Otimizar SSD/HD", lambda: self.acao_async(self.rodar_defrag)),
            ("Desativar IPv6 + Ativar RDP + G_SupLocal", lambda: self.acao_async(self.aplicar_config_rede_admin)),
            ("Resetar DNS", lambda: self.acao_async(self.resetar_dns)),
            ("Atualizar via Winget", lambda: self.acao_async(self.rodar_winget)),
            ("Apagar Downloads", self.apagar_pasta_downloads),
            ("Gerenciar Usuários", self.abrir_usuarios),
            ("Ingressar Domínio", self.ingressar_dominio)
        ]

        for i, (texto, cmd) in enumerate(botoes):
            btn = ctk.CTkButton(ferramentas_lf, text=texto, command=cmd, fg_color="#2b2b2b", text_color="#ffffff",
                                height=30)
            btn.grid(row=(i // 2) + 1, column=i % 2, padx=10, pady=5, sticky="ew")

        # Monitoramento no final (Linha 7)
        btn_monitor = ctk.CTkButton(ferramentas_lf, text="Monitoramento HW", command=self.abrir_janela_monitoramento,
                                    fg_color="#1f3d24", text_color="#00FF66", height=30)
        btn_monitor.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Entrada para renomear Computador posicionado abaixo do monitoramento (Linha 8)
        rename_frame = ctk.CTkFrame(ferramentas_lf, fg_color="transparent")
        rename_frame.grid(row=8, column=0, columnspan=2, padx=10, pady=(8, 12), sticky="ew")

        lbl_rename = ctk.CTkLabel(rename_frame, text="Novo nome do PC:", text_color="#ffffff", font=("Consolas", 11))
        lbl_rename.pack(side=ctk.LEFT, padx=(5, 5))

        self.ent_nome_pc = ctk.CTkEntry(rename_frame, fg_color="#222222", border_color="#333333", text_color="#00FF66",
                                        font=("Consolas", 12), height=28, width=150)
        self.ent_nome_pc.pack(side=ctk.LEFT, padx=5, fill=ctk.X, expand=True)

        btn_renomear = ctk.CTkButton(rename_frame, text="Renomear", command=lambda: self.acao_async(self.renomear_pc),
                                     fg_color="#2b2b2b", text_color="#00FF66", hover_color="#333333",
                                     font=("Consolas", 11, "bold"), width=90, height=28)
        btn_renomear.pack(side=ctk.LEFT, padx=(5, 5))

        ferramentas_lf.grid_columnconfigure(0, weight=1)
        ferramentas_lf.grid_columnconfigure(1, weight=1)

        # Bloco Console de Saída (Log)
        console_lf = ctk.CTkFrame(right_frame, fg_color="#1a1a1a", corner_radius=8)
        console_lf.pack(fill=ctk.BOTH, expand=True)

        lbl_section4 = ctk.CTkLabel(console_lf, text=" Console de Saída / Progresso ", font=("Consolas", 13, "bold"),
                                    text_color="#00FF66")
        lbl_section4.pack(anchor="w", padx=15, pady=(8, 4))

        # --- BOTÃO DE INTERRUPÇÃO CUSTOMIZADO ---
        btn_cancelar = ctk.CTkButton(console_lf, text="🛑 CANCELAR OPERAÇÃO / INSTALAÇÕES EM ANDAMENTO",
                                     command=self.cancelar_tudo, fg_color="#5a1c1c", text_color="#ff6666",
                                     hover_color="#732424", font=("Consolas", 11, "bold"), height=32)
        btn_cancelar.pack(fill=ctk.X, padx=15, pady=4)

        self.txt_console = ctk.CTkTextbox(console_lf, fg_color="#050505", text_color="#00FF66", border_color="#222222",
                                          font=("Consolas", 11))
        self.txt_console.pack(fill=ctk.BOTH, expand=True, padx=15, pady=(5, 15))
        self.log("Sistema Pronto. Aguardando comandos...")

    def acao_async(self, funcao, *args):
        threading.Thread(target=funcao, args=args, daemon=True).start()

    # ========== MECANISMO DE INTERRUPÇÃO ATIVA ==========
    def cancelar_tudo(self):
        if messagebox.askyesno("Cancelar Processos",
                               "Tem certeza de que deseja interromper todas as tarefas, downloads e instalações ativas?"):
            self.cancelar_operacao = True
            self.log("[CANCELANDO] Solicitação de interrupção enviada pelo técnico.")
            if self.processo_atual:
                try:
                    subprocess.run(f"taskkill /F /T /PID {self.processo_atual.pid}", shell=True, capture_output=True)
                    self.log("[INTERROMPIDO] O subprocesso ativo no Windows foi finalizado.")
                except Exception as e:
                    self.log(f"[ERRO] Falha ao encerrar processo: {str(e)}")
                self.processo_atual = None

    # ========== FUNÇÃO UNIVERSAL DE DOWNLOAD E INSTALAÇÃO ==========
    def instalar_programa(self, nome):
        if self.cancelar_operacao:
            self.log(f"[IGNORADO] {nome} pulado devido ao cancelamento do lote.")
            return False

        prog = self.banco_programas[nome]
        link = prog["link"]
        arq_nome = prog["arq"]
        params = prog["params"]
        caminho_completo = os.path.join(self.pasta_downloads, arq_nome)

        self.log(f"=== Processando: {nome} ===")

        if os.path.exists(caminho_completo):
            self.log(f"[INFO] {arq_nome} ja existe localmente. Pulando Download.")
        else:
            self.log(f"Iniciando download em cascata de {arq_nome}...")

            if not self.cancelar_operacao:
                cmd_bits = f"Start-BitsTransfer -Source '{link}' -Destination '{caminho_completo}'"
                self.processo_atual = subprocess.Popen(["powershell", "-Command", cmd_bits], stdout=subprocess.PIPE,
                                                       stderr=subprocess.PIPE)
                self.processo_atual.wait()

            if not os.path.exists(caminho_completo) and not self.cancelar_operacao:
                self.log("[AVISO] BITS falhou. Tentando Plano B (WebClient TLS 1.2)...")
                cmd_webclient = f"[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('{link}', '{caminho_completo}')"
                self.processo_atual = subprocess.Popen(["powershell", "-Command", cmd_webclient],
                                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.processo_atual.wait()

            if not os.path.exists(caminho_completo) and not self.cancelar_operacao:
                self.log("[AVISO] WebClient falhou. Tentando Plano C (Invoke-WebRequest)...")
                cmd_webreq = f"Invoke-WebRequest -Uri '{link}' -OutFile '{caminho_completo}' -UserAgent 'Mozilla/5.0' -UseBasicParsing"
                self.processo_atual = subprocess.Popen(["powershell", "-Command", cmd_webreq], stdout=subprocess.PIPE,
                                                       stderr=subprocess.PIPE)
                self.processo_atual.wait()

        self.processo_atual = None

        if self.cancelar_operacao:
            self.log(f"[CANCELADO] Operação parada antes da instalação de {nome}.")
            return False

        if not os.path.exists(caminho_completo):
            self.log(f"[FALHOU] Não foi possível baixar o instalador de {nome}.")
            return False

            # --- LINHA PRA DESTRAVAR WIN 25H2 ---
        self.log(f"Desbloqueando {arq_nome} para o Windows 25H2...")
        subprocess.run(f'powershell -Command "Unblock-File -Path \'{caminho_completo}\'"', shell=True)

        self.log(f"Instalando {nome} de forma silenciosa...")
        try:
            # --- FIX 25H2 PARA MSI ---
            if arq_nome.endswith(".msi"):
                self.log(f"Detectado MSI. Usando msiexec para instalação silenciosa...")
                cmd_exec = f'msiexec.exe /i "{caminho_completo}" {params} /qn /norestart'
            else:
                cmd_exec = f'Start-Process -FilePath "{caminho_completo}" -ArgumentList "{params}" -Wait -NoNewWindow'
            # --- FIM FIX ---

            self.processo_atual = subprocess.Popen(["powershell", "-Command", cmd_exec], stdout=subprocess.PIPE,
                                                   stderr=subprocess.PIPE, text=True)
            self.processo_atual.wait()

            return_code = self.processo_atual.returncode
            self.processo_atual = None

            if return_code == 0:
                self.log(f"[SUCESSO] {nome} instalado perfeitamente!")
                return True
            elif return_code == 3010:  # Codigo de sucesso mas precisa reiniciar
                self.log(f"[SUCESSO] {nome} instalado! Reinicialização necessária.")
                return True
            else:
                self.log(f"[FALHOU] {nome} retornou código de erro: {return_code}")
                return False
        except Exception as e:
            self.processo_atual = None
            self.log(f"[ERRO] Falha crítica na execução do instalador: {str(e)}")
            return False

    # ========== SEQUÊNCIAS EM LOTE ==========
    def instalar_lote(self, incluir_reparos=False):
        self.cancelar_operacao = False
        selecionados = [nome for nome, var in self.check_vars.items() if var.get()]
        if not selecionados:
            messagebox.showwarning("Aviso", "Nenhum programa foi selecionado para instalação em lote!")
            return

        self.log("=========================================")
        self.log("   INICIANDO INSTALAÇÃO EM LOTE DO KIT   ")
        self.log("=========================================")

        for programa in selecionados:
            if self.cancelar_operacao:
                self.log("[INTERROMPIDO] Instalação em lote cancelada pelo operador.")
                break
            self.instalar_programa(programa)

        if incluir_reparos and not self.cancelar_operacao:
            self.log("\nIniciando esteira automatizada de manutenção...")
            self.rodar_sfc_dism()
            if not self.cancelar_operacao: self.rodar_limpeza()
            if not self.cancelar_operacao: self.rodar_defrag()

        self.log("=========================================")
        self.log("   PROCESSO EM LOTE FINALIZADO           ")
        self.log("=========================================")

        if not self.cancelar_operacao:
            subprocess.Popen(["notepad.exe", self.relatorio_path])

    # ========== REPAROS E FERRAMENTAS DO WINDOWS ==========
    def rodar_sfc_dism(self):
        self.cancelar_operacao = False
        self.log("=== [1/2] Executando SFC Scannow (Pode demorar)... ===")
        self.processo_atual = subprocess.Popen("sfc /scannow", shell=True, stdout=subprocess.PIPE,
                                               stderr=subprocess.STDOUT, text=True, errors="ignore")
        for linha in iter(self.processo_atual.stdout.readline, ""):
            if self.cancelar_operacao: break
            self.txt_console.insert("end", linha)
            self.txt_console.see("end")
        self.processo_atual.wait()

        if self.cancelar_operacao:
            self.processo_atual = None
            self.log("[INTERROMPIDO] Manutenção do sistema cancelada.")
            return

        self.log("=== [2/2] Executando DISM RestoreHealth... ===")
        self.processo_atual = subprocess.Popen("DISM /Online /Cleanup-Image /RestoreHealth", shell=True,
                                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                               errors="ignore")
        for linha in iter(self.processo_atual.stdout.readline, ""):
            if self.cancelar_operacao: break
            self.txt_console.insert("end", linha)
            self.txt_console.see("end")
        self.processo_atual.wait()
        self.processo_atual = None

        if not self.cancelar_operacao:
            self.log("[OK] Rotina SFC + DISM Concluída!")

    def rodar_limpeza(self):
        self.log("Iniciando varredura e limpeza de arquivos temporários...")
        comandos = [
            'del /s /f /q %TEMP%\\*.* >nul 2>&1',
            'del /s /f /q C:\\Windows\\Temp\\*.* >nul 2>&1',
            'del /s /f /q C:\\Windows\\Prefetch\\*.* >nul 2>&1',
            'del /s /f /q C:\\Windows\\Logs\\*.log >nul 2>&1'
        ]
        for cmd in comandos:
            if self.cancelar_operacao: break
            subprocess.run(cmd, shell=True)

        if not self.cancelar_operacao:
            subprocess.run(["powershell", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
                           capture_output=True)
            self.log("[OK] Limpeza de arquivos inúteis e caches executada com sucesso!")

    def rodar_chkdsk(self):
        self.log("Agendando verificação CHKDSK profunda para a inicialização...")
        proc = subprocess.Popen("chkdsk C: /f /r", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True)
        saida, _ = proc.communicate(input="S\n")
        self.log("[INFO] Resposta do sistema:\n" + saida.strip())
        self.log("[OK] CHKDSK agendado. O disco será analisado ao reiniciar a máquina.")


    # Detecta SSD vs HD e roda o comando certo pra cada
    def rodar_defrag(self):
        self.cancelar_operacao = False
        self.log("=== INICIANDO OTIMIZAÇÃO INTELIGENTE DE DISCOS ===")

        for particao in psutil.disk_partitions():
            if 'fixed' in particao.opts and not self.cancelar_operacao:
                letra = particao.device
                self.processo_atual = None  # [FIX] Zera sempre
                try:
                    # Detecta se é SSD ou HD via PowerShell
                    cmd_check = f'powershell "Get-PhysicalDisk | Where-Object DeviceId -eq {letra[0]} | Select-Object -ExpandProperty MediaType"'
                    tipo_disco = subprocess.check_output(cmd_check, shell=True,
                                                         stderr=subprocess.DEVNULL).decode().strip()

                    if "SSD" in tipo_disco:
                        self.log(f"[SSD] {letra} -> Executando TRIM / ReTrim")
                        cmd = f"defrag {letra} /L /O /U"
                    elif "HDD" in tipo_disco:
                        self.log(f"[HD] {letra} -> Executando Desfragmentação")
                        cmd = f"defrag {letra} /O /U"
                    else:
                        # [FIX] Se não detectar, deixa o Windows decidir com /O
                        self.log(f"[AUTO] {letra} -> Tipo não detectado. Deixando Windows decidir")
                        cmd = f"defrag {letra} /O /U"

                    # [FIX] Só roda se não foi cancelado
                    if not self.cancelar_operacao:
                        self.processo_atual = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                                               stderr=subprocess.STDOUT, text=True, errors="ignore")

                        # Mostra o progresso no console
                        for linha in iter(self.processo_atual.stdout.readline, ""):
                            if self.cancelar_operacao: break
                            self.txt_console.insert("end", linha)
                            self.txt_console.see("end")
                        self.processo_atual.wait()

                except Exception as e:
                    self.log(f"[AVISO] Não consegui otimizar {letra}: {str(e)}")

        self.processo_atual = None
        if not self.cancelar_operacao:
            self.log("[OK] Otimização de todos os discos concluída!")

    def renomear_pc(self):
        novo_nome = self.ent_nome_pc.get().strip()
        if not novo_nome:
            messagebox.showwarning("Aviso", "Digite um nome válido para o computador.")
            return

        self.log(f"Tentando alterar o nome do Host para: {novo_nome}...")
        cmd = f"Rename-Computer -NewName '{novo_nome}' -Force"
        proc = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)

        if proc.returncode == 0:
            self.log(f"[SUCESSO] Computador renomeado para {novo_nome}!")
            if messagebox.askyesno("Reiniciar",
                                   f"O computador foi renomeado para {novo_nome}. Deseja reiniciar agora de forma segura?"):
                subprocess.run("shutdown /r /t 5", shell=True)
        else:
            self.log("[ERRO] Erro ao renomear. Verifique caracteres inválidos.")
            messagebox.showerror("Erro", "Não foi possível renomear. Veja o console de saída.")

    # ========== CONFIRMAÇÃO REVISADA DO WINGET (SISTEMA EM DUAS ETAPAS) ==========
    def rodar_winget(self):
        self.cancelar_operacao = False
        self.log("Buscando atualizações de pacotes via Winget...")

        # Etapa 1: Listar na tela o que tem para atualizar
        self.processo_atual = subprocess.Popen("winget upgrade", shell=True, stdout=subprocess.PIPE,
                                               stderr=subprocess.STDOUT, text=True, errors="ignore")
        for linha in iter(self.processo_atual.stdout.readline, ""):
            if self.cancelar_operacao: break
            self.txt_console.insert("end", linha)
            self.txt_console.see("end")
        self.processo_atual.wait()
        self.processo_atual = None

        if self.cancelar_operacao:
            self.log("[CANCELADO] Operação via Winget interrompida.")
            return

        # Etapa 2: Chama a caixa de diálogo na thread principal do tkinter
        self.root.after(0, self.confirmar_upgrade_winget)

    def confirmar_upgrade_winget(self):
        if messagebox.askyesno("Confirmar Upgrade",
                               "As atualizações foram listadas no console. Deseja aplicar os upgrades globais no sistema agora?"):
            self.acao_async(self.executar_upgrade_total_winget)
        else:
            self.log("[INFO] Atualização massiva via Winget cancelada pelo operador.")

    def executar_upgrade_total_winget(self): # [FIX] Era 'ejecutar'
        self.log("Iniciando instalação de todos os upgrades encontrados...")
        cmd_upgrade = "winget upgrade --all --include-unknown --accept-package-agreements --accept-source-agreements"
        self.processo_atual = subprocess.Popen(cmd_upgrade, shell=True, stdout=subprocess.PIPE,
                                               stderr=subprocess.STDOUT, text=True, errors="ignore")
        for linha in iter(self.processo_atual.stdout.readline, ""):
            if self.cancelar_operacao: break
            self.txt_console.insert("end", linha)
            self.txt_console.see("end")
        self.processo_atual.wait()
        self.processo_atual = None
        if not self.cancelar_operacao:
            self.log("[SUCESSO] Todos os pacotes compatíveis foram atualizados via Winget!")

    def apagar_pasta_downloads(self):
        if messagebox.askyesno("Confirmação",
                               "Tem certeza que deseja limpar e apagar todos os instaladores salvos em cache?"):
            try:
                for arquivo in os.listdir(self.pasta_downloads):
                    caminho_arq = os.path.join(self.pasta_downloads, arquivo)
                    if os.path.isfile(caminho_arq):
                        os.remove(caminho_arq)
                self.log("[OK] Cache da pasta local de downloads foi completamente zerado.")
            except Exception as e:
                self.log(f"[ERRO] Erro ao limpar repositório: {str(e)}")


# ========== CONTROLE DE PRIVILÉGIOS ELEVADOS ==========
def checar_privilegios_administrador():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == "__main__": # Só roda esse bloco se o arquivo for executado diretamente
    # Verifica se o programa já está rodando como Administrador
    if checar_privilegios_administrador():
        # Se SIM: Inicia a interface gráfica normalmente
        root = ctk.CTk() # Cria a janela principal do CustomTkinter
        app = KitTechinblueGUI(root) # Instancia a classe da nossa interface
        root.mainloop() # Mantém a janela aberta até o usuário fechar
    else:
        # Se NÃO: Precisa pedir privilégios de Administrador
        print("Solicitando privilégios elevados de Administrador...")

        # Pega o caminho completo do arquivo.py/.exe que está rodando
        script_executavel = os.path.abspath(sys.argv[0])
        # Pega os parâmetros que foram passados na execução, se tiver
        parametros = " ".join(sys.argv[1:])

        # Usa o Windows para reabrir o próprio programa como Admin
        # "runas" = comando do Windows pra "Executar como Administrador"
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script_executavel}" {parametros}', None, 1)

        # Fecha a instância atual sem privilégios
        sys.exit()