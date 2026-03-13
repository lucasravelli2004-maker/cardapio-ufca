import requests
from bs4 import BeautifulSoup
import pdfplumber
import pandas as pd
import io

def atualizar_cardapio():
    url = "https://www.ufca.edu.br/assuntos-estudantis/refeitorio-universitario/cardapios/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    print(f"Acessando o site: {url}")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    pdf_url = None
    print("Buscando o link do documento...")
    
    # Procura por links (tag 'a') que tenham o atributo 'href'
    for link in soup.find_all('a', href=True):
        href = link['href'].lower()
        texto = link.text.lower()
        
        # Só aceita se o link terminar EXPLICITAMENTE em .pdf
        if href.endswith('.pdf'):
            pdf_url = link['href']
            # Garante que o link está completo se for um caminho relativo
            if pdf_url.startswith('/'):
                pdf_url = "https://www.ufca.edu.br" + pdf_url
            break # Encontrou o primeiro PDF, para de procurar
            
    if not pdf_url:
        print("❌ ERRO: Nenhum link terminando em .pdf foi encontrado na página.")
        return

    print(f"✅ PDF verdadeiro encontrado: {pdf_url}")
    print("Baixando e lendo o arquivo...")
    
    try:
        pdf_response = requests.get(pdf_url, headers=headers)
        
        with pdfplumber.open(io.BytesIO(pdf_response.content)) as pdf:
            pagina = pdf.pages[0] # Lê a primeira página
            tabela_extraida = pagina.extract_table()
            
        if tabela_extraida:
            print("✅ Tabela extraída com sucesso!")
            
            # Limpa linhas vazias e tenta arranjar a tabela
            tabela_limpa = [linha for linha in tabela_extraida if any(celula for celula in linha)]
            
            # Se a tabela tiver cabeçalho na primeira linha
            df = pd.DataFrame(tabela_limpa[1:], columns=tabela_limpa[0])
            tabela_html = df.to_html(index=False, classes='table table-striped table-hover table-bordered text-center', na_rep='-')
            
            html_completo = f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Cardápio da Semana - RU UFCA</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {{ background-color: #f8f9fa; padding: 20px; }}
                    .container {{ background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                    thead {{ background-color: #005b96; color: white; }}
                </style>
            </head>
            <body>
                <div class="container mt-4">
                    <h2 class="mb-4 text-center">Cardápio da Semana - RU UFCA</h2>
                    <div class="table-responsive">
                        {tabela_html}
                    </div>
                    <p class="text-muted text-center mt-3"><small>Atualizado automaticamente.</small></p>
                </div>
            </body>
            </html>
            """
            
            with open('index.html', 'w', encoding='utf-8') as f:
                f.write(html_completo)
            print("✅ Site (index.html) gerado com sucesso!")
        else:
            print("❌ ERRO: O PDF foi baixado, mas o robô não encontrou nenhuma tabela legível na primeira página.")
            
    except Exception as e:
        print(f"❌ ERRO ao tentar baixar ou ler o arquivo: {e}")

if __name__ == '__main__':
    atualizar_cardapio()
