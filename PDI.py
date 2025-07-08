import streamlit as st
import pandas as pd
import sqlite3
import tempfile
import os
from datetime import datetime

st.set_page_config(page_title="Avaliação de Desempenho", layout="wide")
st.title("Sistema de Avaliação de Desempenho")

# Conexão com SQLite
conn = sqlite3.connect("avaliacoes.db")
c = conn.cursor()

# Criação de tabela se não existir
c.execute('''CREATE TABLE IF NOT EXISTS avaliacoes (
    nome TEXT,
    tipo TEXT,
    idx INTEGER,
    pergunta TEXT,
    nota INTEGER
)''')
conn.commit()

# Perguntas em escopo global
dgeral = [
    "1. Pensa em soluções criativas com o objetivo de sanar problemas.",
    "2. É capaz de administrar conflitos, opiniões divergentes e condições adversas no ambiente de trabalho.",
    "3. É capaz de reconhecer e aprender com os erros e experiências anteriores.",
    "4. Tem disponibilidade em atender solicitações e participar de atividades extras ou imprevistas.",
    "5. Se comunica com clareza, objetividade e sociabilidade com as demais pessoas.",
    "6. Procura realizar as atividades dentro de uma ordem adequada às necessidades do setor.",
    "7. Se relaciona adequadamente com os colegas, liderança e demais colaboradores.",
    "8. É capaz de se adaptar com agilidade às mudanças de métodos, processos, ferramentas, etc."
]

dtecnica = [
    "9. Apresenta preocupação de antecipar-se a erros.",
    "10. Tem proatividade para propor soluções inovadoras no setor e nos demais.",
    "11. Busca fazer com que a equipe cumpra normas, procedimentos e prazos.",
    "12. Apresenta capacidade de detectar e resolver problemas.",
    "13. Possui atitude preventiva em relação aos problemas.",
    "14. Realiza planejamento adequado de suas atividades e do setor.",
    "15. Faz administração adequada das prioridades do setor.",
    "16. Considera pontos estratégicos e impactos nas ações planejadas.",
    "17. Apresenta capacidade de negociação.",
    "18. Possui capacidade de argumentação.",
    "19. Busca atualização por cursos ou estudos.",
    "20. Dissemina o conhecimento entre os colegas.",
    "21. Possui conhecimento técnico adequado."
]

danalise = [
    "22. Apresenta soluções pertinentes visando a resolução de problemas.",
    "23. Apresenta capacidade de avaliação crítica."
]

dvisao = [
    "24. Elabora ações alinhadas com os objetivos e metas organizacionais."
]

dlideranca = [
    "25. Leva a equipe a alcançar resultados esperados.",
    "26. Fornece feedback para a equipe.",
    "27. Soluciona conflitos internos e externos.",
    "28. Mantém a equipe motivada.",
    "29. Compartilha informações com a equipe.",
    "30. Cria clima de união para execução de atividades.",
    "31. É acessível e coopera com a equipe.",
    "32. Promove o desenvolvimento profissional da equipe."
]

perguntas_completas = dgeral + dtecnica + danalise + dvisao + dlideranca

# Função global
def avaliar_bloco(titulo, perguntas, tipo, nome):
    st.markdown(f"### {titulo}")
    bloco = []
    for i, p in enumerate(perguntas):
        nota = st.slider(p, 0, 5, 0, key=p+titulo+tipo+nome)
        bloco.append(nota)
    return bloco

def salvar_avaliacao(nome, tipo, respostas):
    c.execute("DELETE FROM avaliacoes WHERE nome=? AND tipo=?", (nome, tipo))
    for i, (p, nota) in enumerate(zip(perguntas_completas, respostas)):
        c.execute("INSERT INTO avaliacoes (nome, tipo, idx, pergunta, nota) VALUES (?, ?, ?, ?, ?)",
                  (nome, tipo, i, p, nota))
    conn.commit()

def carregar_avaliacao(nome, tipo):
    c.execute("SELECT idx, nota FROM avaliacoes WHERE nome=? AND tipo=?", (nome, tipo))
    dados = {idx: nota for idx, nota in c.fetchall()}
    return [dados.get(i, 0) for i in range(len(perguntas_completas))]

def gerar_html(nome, gestor, auto):
    html = f"""
    <html><head><style>
    body {{ font-family: Arial; margin: 40px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #999; padding: 8px; text-align: left; }}
th {{ background-color: #eee; }}
</style></head><body>
    <h1>Avaliação de Desempenho</h1>
    <h2>{nome}</h2>
    <table>
        <tr><th>Competência</th><th>Pergunta</th><th>Nota Esperada</th><th>Liderado</th><th>Gestor</th><th>Nota Final</th><th>GAP</th></tr>
    """
    for i, pergunta in enumerate(perguntas_completas):
        esperado = 5
        liderado = auto[i]
        gestor_nota = gestor[i]
        media = round((liderado + gestor_nota)/2, 2)
        gap = esperado - media
        html += f"<tr><td>{i+1}</td><td>{pergunta}</td><td>{esperado}</td><td>{liderado}</td><td>{gestor_nota}</td><td>{media}</td><td>{gap}</td></tr>"
    html += "</table>"

    # Cálculo da nota final
    nota_final_liderado = sum(auto)
    nota_final_gestor = sum(gestor)
    nota_final = round((nota_final_liderado + nota_final_gestor) / 2, 2)

    html += f"""
    <br><h3>Resultado Consolidado</h3>
    <p><strong>Nota Final do Avaliado:</strong> {nota_final}</p>
    <p><strong>Soma das Notas do Gestor:</strong> {nota_final_gestor}</p>
    <p><strong>Soma das Notas do Liderado:</strong> {nota_final_liderado}</p>
    """

    html += "</table>"

# Cálculo da nota final
nota_final_liderado = sum(auto)
nota_final_gestor = sum(gestor)
nota_final = round((nota_final_liderado + nota_final_gestor) / 2, 2)

html += f"""
<br><h3>Resultado Consolidado</h3>
<p><strong>Nota Final do Avaliado:</strong> {nota_final}</p>
<p><strong>Soma das Notas do Gestor:</strong> {nota_final_gestor}</p>
<p><strong>Soma das Notas do Liderado:</strong> {nota_final_liderado}</p>
"""

html += "</body></html>"
return html

aba = st.sidebar.radio("Selecione uma aba:", (
    "Avaliação do Gestor", "Autoavaliação", "Resultado Consolidado"
))

if aba == "Avaliação do Gestor":
    st.header("Formulário de Avaliação do Gestor")
    nome = st.text_input("Nome do Avaliado")
    respostas = avaliar_bloco("Dimensão Geral", dgeral, "gestor", nome)
    respostas += avaliar_bloco("Dimensão Técnica", dtecnica, "gestor", nome)
    respostas += avaliar_bloco("Capacidade de Análise", danalise, "gestor", nome)
    respostas += avaliar_bloco("Visão Estratégica", dvisao, "gestor", nome)
    respostas += avaliar_bloco("Liderança", dlideranca, "gestor", nome)

    if st.button("Salvar Avaliação do Gestor"):
        salvar_avaliacao(nome, "gestor", respostas)
        salvar_avaliacao(nome, "auto", [0]*len(perguntas_completas))
        st.success("Avaliação do gestor salva com sucesso!")

elif aba == "Autoavaliação":
    st.header("Formulário de Autoavaliação")
    c.execute("SELECT DISTINCT nome FROM avaliacoes WHERE tipo='gestor'")
    nomes_avaliados = [row[0] for row in c.fetchall()]
    nome = st.selectbox("Selecione o nome do Avaliado", nomes_avaliados)

    respostas_auto = avaliar_bloco("Dimensão Geral", dgeral, "auto", nome)
    respostas_auto += avaliar_bloco("Dimensão Técnica", dtecnica, "auto", nome)
    respostas_auto += avaliar_bloco("Capacidade de Análise", danalise, "auto", nome)
    respostas_auto += avaliar_bloco("Visão Estratégica", dvisao, "auto", nome)
    respostas_auto += avaliar_bloco("Liderança", dlideranca, "auto", nome)

    if st.button("Salvar Autoavaliação"):
        salvar_avaliacao(nome, "auto", respostas_auto)
        st.success("Autoavaliação salva com sucesso!")

elif aba == "Resultado Consolidado":
    st.header("Resultado Consolidado")
    c.execute("SELECT DISTINCT nome FROM avaliacoes")
    nomes = [row[0] for row in c.fetchall()]
    dados = []
    for nome in nomes:
        gestor = carregar_avaliacao(nome, "gestor")
        auto = carregar_avaliacao(nome, "auto")
        if gestor and auto:
            media = round((sum(gestor) + sum(auto))/2, 2)
            dados.append({"Avaliado": nome, "Nota Gestor": sum(gestor), "Nota Auto": sum(auto), "Média Final": media})
    df = pd.DataFrame(dados)
    st.dataframe(df)

    st.markdown("### Gerar Relatório HTML")
    nome_escolhido = st.selectbox("Selecione o nome para gerar o relatório", nomes)
    if st.button("Gerar Relatório"):
        gestor = carregar_avaliacao(nome_escolhido, "gestor")
        auto = carregar_avaliacao(nome_escolhido, "auto")
        html = gerar_html(nome_escolhido, gestor, auto)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
            f.write(html.encode("utf-8"))
            path = f.name
        st.success("Relatório HTML gerado com sucesso!")
        with open(path, "r", encoding="utf-8") as file:
            st.download_button("Baixar Relatório HTML", file.read(), file_name=f"relatorio_{nome_escolhido}.html")

conn.close()
