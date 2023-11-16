from flask import Flask
import os
import openai
import dotenv
from time import sleep
from helpers import *

app = Flask(__name__)
app.secret_key = 'alura'
    
dotenv.load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

openai.api_base = "http://localhost:8080/v1"

from views import *

def limita_historico(historico, limite_maximo_tokens):
    total_tokens = 0
    historico_parcial = ''
    for linha in reversed(historico.split('\n')):
        tokens_linha = conta_tokens(linha)
        total_tokens = total_tokens + tokens_linha
        if total_tokens > limite_maximo_tokens:
            break
        historico_parcial = linha + '\n' + historico_parcial
    return historico_parcial

        

dados_ecommerce = carrega("dados_ecommerce.txt")

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

if __name__ == "__main__":
    app.run(debug = True)