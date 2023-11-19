from app import app, bot
from flask import render_template, request, Response, session, flash, redirect, url_for
import os
from helpers import *
from conta_tokens import *
from resumidor import criando_resumo
from models import *

@app.route("/")
def home():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
            return redirect(url_for('login'))
    return render_template("index.html")


@app.route("/chat", methods = ['POST'])
def chat():
    prompt = request.json['msg']
    nome_do_arquivo = 'contexto_ecomart - ' + session['usuario_logado']
    contexto = ''
    if os.path.exists(nome_do_arquivo):
        contexto = carrega(nome_do_arquivo)
    return Response(trata_resposta(prompt, contexto, nome_do_arquivo), mimetype = 'text/event-stream')

def trata_resposta(prompt, contexto, nome_do_arquivo):
    resposta_parcial = ''
    historico_resumido = criando_resumo(contexto)
    for resposta in bot(prompt, historico_resumido):
        pedaco_da_resposta = resposta.choices[0].delta.get('content','')
        if len(pedaco_da_resposta):
            resposta_parcial += pedaco_da_resposta
            yield pedaco_da_resposta 
    conteudo = f"""
    Historico: {historico_resumido}
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

@app.route('/login')
def login():
    return render_template('login.html', proxima='/')

@app.route('/autenticar', methods=['POST',])
def autenticar():
    if request.form['usuario'] in usuarios:
        usuario = usuarios[request.form['usuario']]
        if request.form['senha'] == usuario.senha:
            session['usuario_logado'] = usuario.nickname
            flash(usuario.nickname + ' logado com sucesso!')
            return redirect(request.form['proxima'])
    else:
        flash('Usuário não logado.')
        return redirect(url_for('login'))
    
@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Logout efetuado com sucesso!')
    return redirect(url_for('login'))

