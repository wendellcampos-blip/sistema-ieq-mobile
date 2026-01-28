import flet as ft
import psycopg2
import base64
from datetime import datetime

# =======================================================
# ⚙️ BANCO DE DADOS
# =======================================================
DB_HOST = "db.phqsoznnrrcjyebzyfht.supabase.co"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "Ieqcentral2026*"
DB_PORT = "5432"

# Cores do App
COLOR_PRIMARY = "#3B82F6"      # Azul
COLOR_BG = "#F3F4F6"           # Fundo Cinza Claro
COLOR_WHITE = "#FFFFFF"
COLOR_HEADER = "#1E293B"       # Azul Escuro

# Estado Global (Armazena usuário e aula atual)
class AppState:
    usuario = None
    aula_id = None
    temp_img = None 

state = AppState()

def get_conn():
    try:
        return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)
    except Exception as e:
        print(f"Erro DB: {e}")
        return None

def main(page: ft.Page):
    # Configurações da Janela
    page.title = "IEQ Mobile"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = COLOR_BG
    # Tamanho simulado de celular para teste no PC
    page.window_width = 375
    page.window_height = 700

    # ==============================================================================
    # 🛠️ UTILITÁRIOS
    # ==============================================================================
    def show_snack(msg, color="green"):
        page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    # Seletor de Arquivos (Funciona como Câmera/Galeria no Android)
    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            try:
                f = e.files[0]
                # Lê o arquivo e converte para base64
                with open(f.path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                    state.temp_img = encoded_string
                    show_snack("Imagem carregada com sucesso!", "blue")
            except Exception as err:
                show_snack(f"Erro ao ler imagem: {err}", "red")
        else:
            show_snack("Nenhuma imagem selecionada", "grey")

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    # ==============================================================================
    # 📱 TELAS (VIEWS)
    # ==============================================================================

    # --- 1. TELA DE LOGIN ---
    def view_login():
        user = ft.TextField(label="Usuário", width=300, border_radius=10, bgcolor="white")
        pwd = ft.TextField(label="Senha", password=True, width=300, border_radius=10, bgcolor="white")
        
        def logar(e):
            conn = get_conn()
            if not conn: return show_snack("Erro de conexão", "red")
            try:
                cur = conn.cursor()
                cur.execute("SELECT id, nome, role, foto FROM usuarios WHERE usuario=%s AND senha=%s", (user.value, pwd.value))
                res = cur.fetchone()
                conn.close()
                if res:
                    state.usuario = {"id": res[0], "nome": res[1], "role": res[2], "foto": res[3]}
                    page.go("/home")
                else:
                    show_snack("Login incorreto", "red")
            except: show_snack("Erro ao buscar usuário", "red")

        return ft.View(
            "/",
            [
                ft.Container(
                    content=ft.Column([
                        ft.Text("⛪", size=80),
                        ft.Text("IEQ KIDS", size=30, weight="bold", color=COLOR_HEADER),
                        ft.Container(height=20),
                        user, pwd,
                        ft.Container(height=20),
                        ft.ElevatedButton("ENTRAR", width=300, height=50, on_click=logar, style=ft.ButtonStyle(bgcolor=COLOR_HEADER, color="white"))
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    expand=True,
                    bgcolor="white"
                )
            ]
        )

    # --- 2. TELA HOME ---
    def view_home():
        if not state.usuario: page.go("/"); return ft.View("/", [])
        
        # Foto de Perfil
        img_src = state.usuario['foto'] if state.usuario['foto'] else ""
        avatar = ft.CircleAvatar(radius=30, src_base64=img_src) if img_src else ft.CircleAvatar(radius=30, content=ft.Icon(ft.icons.PERSON))
        
        header = ft.Container(
            padding=20, bgcolor="white",
            content=ft.Row([
                avatar,
                ft.Column([
                    ft.Text(f"Olá, {state.usuario['nome'].split()[0]}", weight="bold", size=18, color="black"),
                    ft.Text(state.usuario['role'].upper(), size=12, color="grey")
                ], spacing=2),
                ft.IconButton(ft.icons.LOGOUT, icon_color="red", on_click=lambda _: page.go("/"))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

        # Botões do Menu Principal
        def btn_menu(icon, text, color, route):
            return ft.Container(
                width=160, height=130, bgcolor=color, border_radius=15,
                padding=10, on_click=lambda _: page.go(route),
                content=ft.Column([
                    ft.Icon(icon, size=40, color="white"),
                    ft.Text(text, weight="bold", color="white", size=16)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        
        # Lógica inteligente para o botão de Aula
        def ir_aula(_):
            page.go("/chamada" if state.aula_id else "/nova_aula")

        # Grid de botões
        grid = ft.Column([
            ft.Row([btn_menu(ft.icons.DASHBOARD, "Mural", "#3B82F6", "/mural"), btn_menu(ft.icons.CHILD_CARE, "Alunos", "#F59E0B", "/alunos")], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([btn_menu(ft.icons.ROCKET_LAUNCH, "Aula", "#10B981", "FUNC_AULA"), btn_menu(ft.icons.GROUPS, "Equipe", "#8B5CF6", "/equipe")], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([btn_menu(ft.icons.HISTORY, "Histórico", "#64748B", "/historico")], alignment=ft.MainAxisAlignment.CENTER),
        ], spacing=15, scroll=ft.ScrollMode.AUTO)

        # Atribuir a função especial ao botão de Aula (índice 1 da lista, item 0 da linha)
        grid.controls[1].controls[0].on_click = ir_aula

        return ft.View(
            "/home",
            [header, ft.Container(content=grid, padding=10, expand=True)],
            bgcolor=COLOR_BG
        )

    # --- 3. MURAL (Rede Social) ---
    def view_mural():
        lv = ft.ListView(expand=True, spacing=10, padding=10)
        
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT mensagem, autor, data_criacao, fixado, imagem FROM avisos ORDER BY fixado DESC, data_criacao DESC")
        posts = cur.fetchall()
        conn.close()

        for msg, aut, dt, fix, img in posts:
            content_col = [
                ft.Row([
                    ft.Icon(ft.icons.PUSH_PIN if fix else ft.icons.CIRCLE, size=16, color="blue" if fix else "grey"),
                    ft.Text(f"{aut} • {dt.strftime('%d/%m')}", size=12, color="grey")
                ]),
                ft.Text(msg, size=15, color="#1E293B")
            ]
            if img:
                content_col.append(ft.Image(src_base64=img, fit=ft.ImageFit.COVER, border_radius=10))

            card = ft.Container(bgcolor="white", padding=15, border_radius=10, content=ft.Column(content_col))
            lv.controls.append(card)

        fab = ft.FloatingActionButton(icon=ft.icons.ADD, on_click=lambda _: page.go("/novo_aviso")) if state.usuario['role'] == 'admin' else None

        return ft.View("/mural", [
            ft.AppBar(title=ft.Text("Mural"), bgcolor=COLOR_HEADER, color="white"),
            lv
        ], floating_action_button=fab, bgcolor=COLOR_BG)

    def view_novo_aviso():
        txt = ft.TextField(label="Escreva aqui...", multiline=True, min_lines=5, bgcolor="white")
        state.temp_img = None
        
        def salvar(e):
            if not txt.value and not state.temp_img: return
            conn = get_conn(); c = conn.cursor()
            c.execute("INSERT INTO avisos (mensagem, data_criacao, autor, imagem) VALUES (%s,NOW(),%s,%s)", 
                     (txt.value, state.usuario['nome'], state.temp_img))
            conn.commit(); conn.close()
            page.go("/mural")

        return ft.View("/novo_aviso", [
            ft.AppBar(title=ft.Text("Novo Post"), bgcolor=COLOR_HEADER, color="white"),
            ft.Container(padding=20, content=ft.Column([
                txt,
                ft.ElevatedButton("📷 Adicionar Foto", icon=ft.icons.CAMERA_ALT, on_click=lambda _: file_picker.pick_files()),
                ft.ElevatedButton("PUBLICAR", on_click=salvar, bgcolor=COLOR_PRIMARY, color="white", width=300)
            ]))
        ], bgcolor=COLOR_BG)

    # --- 4. ALUNOS (CRUD Completo) ---
    def view_alunos():
        lv = ft.ListView(expand=True, spacing=5, padding=10)
        search = ft.TextField(prefix_icon=ft.icons.SEARCH, hint_text="Buscar criança...", bgcolor="white", border_radius=20, height=40)

        def carregar(termo=""):
            lv.controls.clear()
            conn = get_conn(); c = conn.cursor()
            c.execute("SELECT id, nome, responsavel, foto FROM alunos WHERE nome ILIKE %s ORDER BY nome", (f"%{termo}%",))
            for aid, nome, resp, foto in c.fetchall():
                av = ft.CircleAvatar(src_base64=foto) if foto else ft.CircleAvatar(content=ft.Text(nome[0]))
                
                # Funções de clique
                def edit_click(e, x=aid): page.go(f"/form_aluno?id={x}")
                def del_click(e, x=aid):
                    conn = get_conn(); c=conn.cursor(); c.execute("DELETE FROM alunos WHERE id=%s", (x,)); conn.commit(); conn.close()
                    carregar(search.value)

                card = ft.Container(
                    bgcolor="white", padding=10, border_radius=10,
                    content=ft.Row([
                        av,
                        ft.Column([ft.Text(nome, weight="bold", color="black"), ft.Text(resp, size=12, color="grey")], expand=True),
                        ft.IconButton(ft.icons.EDIT, icon_color="blue", on_click=edit_click),
                        ft.IconButton(ft.icons.DELETE, icon_color="red", on_click=del_click)
                    ])
                )
                lv.controls.append(card)
            page.update()

        search.on_change = lambda e: carregar(e.control.value)
        carregar()

        return ft.View("/alunos", [
            ft.AppBar(title=ft.Text("Alunos"), bgcolor=COLOR_HEADER, color="white"),
            ft.Container(content=search, padding=10),
            lv
        ], floating_action_button=ft.FloatingActionButton(icon=ft.icons.ADD, on_click=lambda _: page.go("/form_aluno")), bgcolor=COLOR_BG)

    def view_form_aluno(id_aluno=None):
        vals = [""]*10
        state.temp_img = None 
        
        if id_aluno:
            conn=get_conn(); c=conn.cursor()
            c.execute("SELECT nome, data_nascimento, responsavel, telefone, observacoes, autorizado_retirar, autorizado_2, autorizado_3, foto, imagem_ficha FROM alunos WHERE id=%s", (id_aluno,))
            vals = list(c.fetchone()); conn.close()
            state.temp_img = vals[8]

        nome = ft.TextField(label="Nome", value=vals[0], bgcolor="white")
        nasc = ft.TextField(label="Nascimento", value=vals[1], bgcolor="white")
        resp = ft.TextField(label="Responsável", value=vals[2], bgcolor="white")
        tel = ft.TextField(label="Telefone", value=vals[3], bgcolor="white")
        obs = ft.TextField(label="Alergias/Obs", value=vals[4], multiline=True, bgcolor="#FEF2F2")
        aut1 = ft.TextField(label="Autorizado 1", value=vals[5], bgcolor="white")
        aut2 = ft.TextField(label="Autorizado 2", value=vals[6], bgcolor="white")

        def salvar(e):
            conn = get_conn(); c = conn.cursor()
            v = [nome.value, nasc.value, resp.value, tel.value, obs.value, aut1.value, aut2.value, vals[7], state.temp_img, vals[9]]
            if id_aluno:
                c.execute("UPDATE alunos SET nome=%s, data_nascimento=%s, responsavel=%s, telefone=%s, observacoes=%s, autorizado_retirar=%s, autorizado_2=%s, autorizado_3=%s, foto=%s, imagem_ficha=%s WHERE id=%s", v + [id_aluno])
            else:
                c.execute("INSERT INTO alunos (nome, data_nascimento, responsavel, telefone, observacoes, autorizado_retirar, autorizado_2, autorizado_3, foto, imagem_ficha) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", v)
            conn.commit(); conn.close()
            page.go("/alunos")

        return ft.View("/form_aluno", [
            ft.AppBar(title=ft.Text("Cadastro Criança"), bgcolor=COLOR_HEADER, color="white"),
            ft.Column([
                nome, nasc, resp, tel, obs, aut1, aut2,
                ft.ElevatedButton("📷 Foto Perfil", icon=ft.icons.CAMERA_ALT, on_click=lambda _: file_picker.pick_files()),
                ft.ElevatedButton("SALVAR", on_click=salvar, bgcolor="green", color="white")
            ], scroll=ft.ScrollMode.AUTO, padding=20)
        ], bgcolor=COLOR_BG)

    # --- 5. EQUIPE ---
    def view_equipe():
        lv = ft.ListView(expand=True, spacing=5, padding=10)
        
        def carregar():
            lv.controls.clear()
            conn = get_conn(); c = conn.cursor()
            c.execute("SELECT id, nome, role, foto, telefone FROM usuarios ORDER BY nome")
            for uid, nome, role, foto, tel in c.fetchall():
                av = ft.CircleAvatar(src_base64=foto) if foto else ft.CircleAvatar(content=ft.Text(nome[0]))
                
                # Botão Excluir só pra admin
                del_btn = ft.IconButton(ft.icons.DELETE, icon_color="red", on_click=lambda e, x=uid: deletar(x)) if state.usuario['role'] == 'admin' else ft.Container()

                card = ft.Container(bgcolor="white", padding=10, border_radius=10, content=ft.Row([
                        av,
                        ft.Column([ft.Text(nome, weight="bold", color="black"), ft.Text(f"{role} | {tel}", size=12, color="grey")], expand=True),
                        del_btn
                    ]))
                lv.controls.append(card)
            page.update()

        def deletar(uid):
            conn = get_conn(); c=conn.cursor(); c.execute("DELETE FROM usuarios WHERE id=%s", (uid,)); conn.commit(); conn.close()
            carregar()

        carregar()
        fab = ft.FloatingActionButton(icon=ft.icons.ADD, on_click=lambda _: page.go("/form_equipe")) if state.usuario['role'] == 'admin' else None

        return ft.View("/equipe", [ft.AppBar(title=ft.Text("Equipe"), bgcolor=COLOR_HEADER, color="white"), lv], floating_action_button=fab, bgcolor=COLOR_BG)

    def view_form_equipe():
        nome = ft.TextField(label="Nome", bgcolor="white"); user = ft.TextField(label="Usuario", bgcolor="white")
        senha = ft.TextField(label="Senha", bgcolor="white"); tel = ft.TextField(label="Telefone", bgcolor="white")
        email = ft.TextField(label="Email", bgcolor="white")
        role = ft.Dropdown(label="Função", options=[ft.dropdown.Option("professor"), ft.dropdown.Option("auxiliar")], bgcolor="white")
        state.temp_img = None

        def salvar(e):
            conn=get_conn(); c=conn.cursor()
            c.execute("INSERT INTO usuarios (nome, usuario, senha, telefone, email, role, foto) VALUES (%s,%s,%s,%s,%s,%s,%s)", 
                     (nome.value, user.value, senha.value, tel.value, email.value, role.value, state.temp_img))
            conn.commit(); conn.close(); page.go("/equipe")

        return ft.View("/form_equipe", [
            ft.AppBar(title=ft.Text("Novo Membro"), bgcolor=COLOR_HEADER, color="white"),
            ft.Column([nome, user, senha, tel, email, role, 
                       ft.ElevatedButton("📷 Foto", on_click=lambda _: file_picker.pick_files()),
                       ft.ElevatedButton("SALVAR", on_click=salvar, bgcolor="green", color="white")], padding=20)
        ], bgcolor=COLOR_BG)

    # --- 6. AULA ---
    def view_nova_aula():
        tema = ft.TextField(label="Tema da Lição", bgcolor="white")
        conn = get_conn(); c = conn.cursor(); c.execute("SELECT nome FROM usuarios"); 
        profs = [ft.dropdown.Option(u[0]) for u in c.fetchall()]; conn.close()
        dd_prof = ft.Dropdown(label="Ministrante", options=profs, bgcolor="white")
        aux = ft.TextField(label="Auxiliares", bgcolor="white")
        
        def iniciar(e):
            if not tema.value: return
            equipe = f"{dd_prof.value}" + (f" | Aux: {aux.value}" if aux.value else "")
            conn=get_conn(); c=conn.cursor()
            c.execute("INSERT INTO aulas (data_aula, tema, professores) VALUES (NOW(), %s, %s) RETURNING id", (tema.value, equipe))
            state.aula_id = c.fetchone()[0]; conn.commit(); conn.close()
            page.go("/chamada")

        return ft.View("/nova_aula", [
            ft.AppBar(title=ft.Text("Iniciar Aula"), bgcolor=COLOR_HEADER, color="white"),
            ft.Container(padding=20, content=ft.Column([
                tema, dd_prof, aux,
                ft.ElevatedButton("ABRIR SALA", on_click=iniciar, bgcolor="green", color="white", width=300)
            ]))
        ], bgcolor=COLOR_BG)

    def view_chamada():
        conn=get_conn(); c=conn.cursor(); c.execute("SELECT nome FROM alunos ORDER BY nome"); 
        alunos_opts = [ft.dropdown.Option(x[0]) for x in c.fetchall()]; conn.close()
        
        dd_aluno = ft.Dropdown(label="Selecionar Criança", options=alunos_opts, expand=True, bgcolor="white")
        lv_presenca = ft.ListView(expand=True, spacing=5)

        def carregar_lista():
            lv_presenca.controls.clear()
            conn=get_conn(); c=conn.cursor()
            c.execute("SELECT f.id, a.nome, f.horario_saida FROM frequencia f JOIN alunos a ON f.id_aluno=a.id WHERE f.id_aula=%s ORDER BY f.horario_entrada DESC", (state.aula_id,))
            for fid, nome, saida in c.fetchall():
                
                def checkout_click(e, x=fid):
                    conn=get_conn(); c=conn.cursor(); c.execute("UPDATE frequencia SET horario_saida=NOW() WHERE id=%s", (x,)); conn.commit(); conn.close()
                    carregar_lista()

                btn_sai = ft.ElevatedButton("Saída", on_click=checkout_click, bgcolor="orange", color="white") if not saida else ft.Text("Saiu", color="grey")
                lv_presenca.controls.append(ft.Container(bgcolor="white", padding=10, border_radius=5, content=ft.Row([
                    ft.Text(nome, weight="bold", color="black"), ft.Container(expand=True), btn_sai
                ])))
            page.update()

        def add_aluno(e):
            conn=get_conn(); c=conn.cursor()
            c.execute("SELECT id FROM alunos WHERE nome=%s", (dd_aluno.value,))
            aid = c.fetchone()
            if aid:
                try: 
                    c.execute("INSERT INTO frequencia (id_aula, id_aluno, horario_entrada) VALUES (%s,%s,NOW())", (state.aula_id, aid[0]))
                    conn.commit()
                except: pass
            conn.close(); dd_aluno.value = ""; carregar_lista()

        def encerrar(e):
            state.aula_id = None; page.go("/home")

        carregar_lista()

        return ft.View("/chamada", [
            ft.AppBar(title=ft.Text("Aula Ao Vivo 🔴"), bgcolor="red", color="white", actions=[ft.IconButton(ft.icons.STOP, on_click=encerrar, icon_color="white")]),
            ft.Container(padding=10, content=ft.Row([dd_aluno, ft.IconButton(ft.icons.ADD_CIRCLE, icon_color="green", icon_size=40, on_click=add_aluno)])),
            ft.Container(padding=10, content=lv_presenca, expand=True)
        ], bgcolor=COLOR_BG)

    # --- 7. HISTÓRICO ---
    def view_historico():
        lv = ft.ListView(expand=True, spacing=5, padding=10)
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT id, data_aula, tema, professores FROM aulas ORDER BY data_aula DESC")
        for aid, dt, tema, profs in c.fetchall():
            card = ft.Container(bgcolor="white", padding=10, border_radius=10, content=ft.Column([
                ft.Row([ft.Text(dt.strftime("%d/%m/%Y"), color="blue", weight="bold"), ft.Text(f"Tema: {tema}", weight="bold")]),
                ft.Text(f"Equipe: {profs}", size=12, color="grey")
            ]))
            lv.controls.append(card)
        conn.close()
        return ft.View("/historico", [ft.AppBar(title=ft.Text("Histórico"), bgcolor=COLOR_HEADER, color="white"), lv], bgcolor=COLOR_BG)

    # --- ROTEADOR ---
    def route_change(route):
        page.views.clear()
        page.views.append(view_login())
        
        if page.route == "/home": page.views.append(view_home())
        if page.route == "/mural": page.views.append(view_mural())
        if page.route == "/novo_aviso": page.views.append(view_novo_aviso())
        if page.route == "/alunos": page.views.append(view_alunos())
        if page.route == "/nova_aula": page.views.append(view_nova_aula())
        if page.route == "/chamada": page.views.append(view_chamada())
        if page.route == "/equipe": page.views.append(view_equipe())
        if page.route == "/form_equipe": page.views.append(view_form_equipe())
        if page.route == "/historico": page.views.append(view_historico())
        
        if page.route.startswith("/form_aluno"): 
            import urllib.parse
            parsed = urllib.parse.urlparse(page.route)
            params = urllib.parse.parse_qs(parsed.query)
            aid = params.get('id', [None])[0]
            page.views.append(view_form_aluno(aid))
            
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/")

ft.app(target=main)