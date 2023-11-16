from app import app, bot
from flask import render_template, request, Response
import os
from helpers import *
from conta_tokens import *

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods = ['POST'])
def chat():
    prompt = request.json['msg']
    nome_do_arquivo = 'contexto_ecomart'
    contexto = ''
    if os.path.exists(nome_do_arquivo):
        contexto = carrega(nome_do_arquivo)
    return Response(trata_resposta(prompt, contexto, nome_do_arquivo), mimetype = 'text/event-stream')

def trata_resposta(prompt, contexto, nome_do_arquivo):
    resposta_parcial = ''
    limite_maximo_tokens = 2048
    historico_parcial = limita_historico(historico, limite_maximo_tokens)
    for resposta in bot(prompt, historico_parcial):
        pedaco_da_resposta = resposta.choices[0].delta.get('content','')
        if len(pedaco_da_resposta):
            resposta_parcial += pedaco_da_resposta
            yield pedaco_da_resposta 
    conteudo = f"""
    Historico: {historico_parcial}
    Usuario: {prompt}
    IA: {resposta_parcial}
    """

    salva(nome_do_arquivo, conteudo)

@app.route("/limparhistorico", methods = ['POST'])
def limparhistorico():
    nome_do_arquivo = 'contexto_ecomart'
    if os.path.exists(nome_do_arquivo):
        os.remove(nome_do_arquivo)
    print("Historico limpo")
    return Response("Historico limpo", mimetype = 'text/event-stream')
