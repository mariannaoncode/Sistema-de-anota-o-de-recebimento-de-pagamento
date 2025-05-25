import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os

DATA_FILE = "funcionarios.json"

class DateEntry(tk.Entry):
    """
    Entry que formata DD/MM/AAAA enquanto o usuário digita,
    com as barras visíveis e posicionamento correto do cursor.
    """
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.var = tk.StringVar()
        self.configure(textvariable=self.var)
        self.var.trace_add('write', self.on_write)
        self.updating = False

    def on_write(self, *args):
        if self.updating:
            return

        self.updating = True
        value = self.var.get()

        # Extrai só os dígitos, máximo 8 (ddmmyyyy)
        digits = ''.join(filter(str.isdigit, value))[:8]

        # Monta a nova string com barras após 2 e 4 dígitos
        new_value = ''
        for i, ch in enumerate(digits):
            new_value += ch
            if i == 1 or i == 3:
                new_value += '/'

        self.var.set(new_value)

        # Garante que o cursor vá para o final após a atualização da string
        self.after_idle(lambda: self.icursor(tk.END))

        self.updating = False


class CadastroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de anotação de recebimento de pagamento")
        self.root.geometry("700x550")
        self.root.resizable(False, False)

        # Ícone peixe (coloque o peixe.ico na mesma pasta)
        icon_path = os.path.join(os.path.dirname(__file__), 'peixe.ico')
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        self.funcionarios = []
        self.load_data()

        self.selected_index = None

        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        frm_form = tk.Frame(self.root)
        frm_form.pack(padx=10, pady=10, fill=tk.X)
        

        lbl_nome = tk.Label(frm_form, text="Nome completo:")
        lbl_nome.grid(row=0, column=0, sticky=tk.W, pady=2, padx=5,)
        self.ent_nome = tk.Entry(frm_form)
        self.ent_nome.insert(0, " ")
        self.ent_nome.grid(row=0, column=1, sticky=tk.EW, pady=2, padx=5)

        lbl_nasc = tk.Label(frm_form, text="Data de nascimento (DD/MM/AAAA):")
        lbl_nasc.grid(row=1, column=0, sticky=tk.W, pady=2, padx=5)
        self.ent_nasc = DateEntry(frm_form)
        self.ent_nasc.grid(row=1, column=1, sticky=tk.EW, pady=2, padx=5)

        lbl_cad = tk.Label(frm_form, text="Data de pagamento (DD/MM/AAAA):")
        lbl_cad.grid(row=2, column=0, sticky=tk.W, pady=2, padx=5)
        self.ent_cad = DateEntry(frm_form)
        self.ent_cad.grid(row=2, column=1, sticky=tk.EW, pady=2, padx=5)

        self.var_pago = tk.IntVar()
        chk_pago = tk.Checkbutton(frm_form, text="Foi pago?", variable=self.var_pago)
        chk_pago.grid(row=3, column=1, sticky=tk.W, pady=2)

        frm_form.columnconfigure(1, weight=1)

        frm_buttons = tk.Frame(self.root)
        frm_buttons.pack(padx=10, pady=5, fill=tk.X)

        self.btn_add = tk.Button(frm_buttons, text="Adicionar", command=self.add_or_update_colaborador)
        self.btn_add.pack(side=tk.LEFT, padx=(0,5))
        btn_clear = tk.Button(frm_buttons, text="Limpar Campos", command=self.clear_fields)
        btn_clear.pack(side=tk.LEFT, padx=(0,5))
        self.btn_edit = tk.Button(frm_buttons, text="Editar selecionado", command=self.load_selected_colaborador, state=tk.DISABLED)
        self.btn_edit.pack(side=tk.LEFT, padx=(0,5))
        self.btn_delete = tk.Button(frm_buttons, text="Excluir selecionado", command=self.delete_selected_colaborador, state=tk.DISABLED)
        self.btn_delete.pack(side=tk.LEFT)

        frm_table = tk.Frame(self.root)
        frm_table.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        columns = ("nome", "nascimento", "pagamento", "pago", "aniversariante")
        self.tree = ttk.Treeview(frm_table, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("nome", text="Nome completo")
        self.tree.heading("nascimento", text="Data de nascimento")
        self.tree.heading("pagamento", text="Data de pagamento")
        self.tree.heading("pago", text="Foi Pago?")
        self.tree.heading("aniversariante", text="🎉 Aniversariante do Mês")
        self.tree.column("nome", width=200)
        self.tree.column("nascimento", width=100, anchor=tk.CENTER)
        self.tree.column("pagamento", width=120, anchor=tk.CENTER)
        self.tree.column("pago", width=80, anchor=tk.CENTER)
        self.tree.column("aniversariante", width=60, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.funcionarios = json.load(f)
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao carregar dados:\n{e}")
                self.funcionarios = []
        else:
            self.funcionarios = []

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.funcionarios, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar dados:\n{e}")

    def validate_date(self, date_text):
        try:
            datetime.strptime(date_text, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def add_or_update_colaborador(self):
        nome = self.ent_nome.get().strip()
        nasc = self.ent_nasc.get().strip()
        pag = self.ent_cad.get().strip()
        pago = bool(self.var_pago.get())

        if not nome:
            messagebox.showwarning("Validação", "O campo 'Nome completo' é obrigatório.")
            return
        if not self.validate_date(nasc):
            messagebox.showwarning("Validação", "Data de nascimento inválida. Use o formato DD/MM/AAAA.")
            return
        if not self.validate_date(pag):
            messagebox.showwarning("Validação", "Data de pagamento inválida. Use o formato DD/MM/AAAA.")
            return

        novo = {
            "nome": nome,
            "nascimento": nasc,
            "cadastro": pag,
            "pago": pago
        }

        if self.selected_index is None:
            self.funcionarios.append(novo)
            messagebox.showinfo("Sucesso", "Colaborador cadastrado com sucesso!")
        else:
            self.funcionarios[self.selected_index] = novo
            messagebox.showinfo("Sucesso", "Atualizado com sucesso!")
            self.selected_index = None
            self.btn_add.config(text="Cadastrar")
            self.btn_edit.config(state=tk.DISABLED)
            self.btn_delete.config(state=tk.DISABLED)

        self.save_data()
        self.refresh_table()
        self.clear_fields()

    def refresh_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        mes_atual = datetime.now().month
        for idx, colab in enumerate(self.funcionarios):
            pago_str = "Sim" if colab["pago"] else "Não"
            try:
                data_nasc = datetime.strptime(colab["nascimento"], "%d/%m/%Y")
                aniversariante = "🎉" if data_nasc.month == mes_atual else ""
            except:
                aniversariante = ""
            self.tree.insert("", tk.END, iid=idx, values=(colab["nome"], colab["nascimento"], colab["cadastro"], pago_str, aniversariante))

    def clear_fields(self):
        self.ent_nome.delete(0, tk.END)
        self.ent_nasc.delete(0, tk.END)
        self.ent_cad.delete(0, tk.END)
        self.var_pago.set(0)
        self.selected_index = None
        self.btn_add.config(text="Cadastrar")
        self.btn_edit.config(state=tk.DISABLED)
        self.btn_delete.config(state=tk.DISABLED)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_index = int(selected[0])
            self.btn_edit.config(state=tk.NORMAL)
            self.btn_delete.config(state=tk.NORMAL)
        else:
            self.selected_index = None
            self.btn_edit.config(state=tk.DISABLED)
            self.btn_delete.config(state=tk.DISABLED)

    def load_selected_colaborador(self):
        if self.selected_index is not None:
            colab = self.funcionarios[self.selected_index]
            self.ent_nome.delete(0, tk.END)
            self.ent_nome.insert(0, colab["nome"])
            self.ent_nasc.delete(0, tk.END)
            self.ent_nasc.insert(0, colab["nascimento"])
            self.ent_cad.delete(0, tk.END)
            self.ent_cad.insert(0, colab["pagamento"])
            self.var_pago.set(1 if colab["pago"] else 0)
            self.btn_add.config(text="Salvar Alterações")

    def delete_selected_colaborador(self):
        if self.selected_index is not None:
            confirm = messagebox.askyesno("Confirmação", "Deseja realmente excluir o comprovante selecionado?")
            if confirm:
                del self.funcionarios[self.selected_index]
                self.save_data()
                self.refresh_table()
                self.clear_fields()


if __name__ == "__main__":
    root = tk.Tk()
    app = CadastroApp(root)
    root.mainloop()
