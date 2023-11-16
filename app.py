from flask import Flask,render_template, request, Response
import os
import openai
import dotenv
from time import sleep
import tiktoken

app = Flask(__name__)
app.secret_key = 'alura'
    
dotenv.load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

openai.api_base = "http://localhost:8080/v1"

def carrega(nome_do_arquivo):
    try:
        with open(nome_do_arquivo, "r") as arquivo:
            dados = arquivo.read()
            return dados
    except IOError as e:
        print(f"Erro no carregamento de arquivo: {e}")

def salva(nome_do_arquivo, conteudo):
    try:
        with open(nome_do_arquivo, "a", encoding="utf-8") as arquivo:
            arquivo.write(conteudo)
    except IOError as e:
        print(f"Erro ao salvar arquivo: {e}")

def conta_tokens(prompt):
    codificador = tiktoken.encoding_for_model("gpt-3.5-turbo")
    lista_de_tokens = codificador.encode(prompt)
    contagem = len(lista_de_tokens)
    return contagem

dados_ecommerce = carrega("dados_ecommerce.txt")
print(conta_tokens(dados_ecommerce))

def bot(prompt, contexto):
    maxima_repeticao = 1
    repeticao = 0
    while True:
        try:
            model='gpt-3.5-turbo.bin'
            prompt_do_sistema = f"""
            Você é um chatbot de atendimento a clientes de um e-commerce.
            Você não deve responder perguntas que não sejam dados do ecommerce informado!
            ## Dados do ecommerce:
            {dados_ecommerce}
            ## Contexto:
            {contexto}
            """

            tamanho_esperado_saida = 2000
            total_tokens_modelo = 4000
            if conta_tokens(prompt_do_sistema) >= total_tokens_modelo - tamanho_esperado_saida:
                model = 'gpt-3.5-turbo-16k.bin'

            response = openai.ChatCompletion.create(
                messages=[
                    {
                        "role": "system",
                        "content": prompt_do_sistema
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                stream = True,
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                model = model)
            return response
        except Exception as erro:
            repeticao += 1
            if repeticao >= maxima_repeticao:
                return "Erro no GPT3: %s" % erro
            print('Erro de comunicação com OpenAI:', erro)
            sleep(1)

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
    for resposta in bot(prompt, contexto):
        pedaco_da_resposta = resposta.choices[0].delta.get('content','')
        if len(pedaco_da_resposta):
            resposta_parcial += pedaco_da_resposta
            yield pedaco_da_resposta 
    conteudo = f"""
    Usuario: {prompt}
    IA: {resposta_parcial}
    """

    salva(nome_do_arquivo, conteudo)

if __name__ == "__main__":
    app.run(debug = True)