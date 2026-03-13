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
    print("Procurando o botão verde 'Baixar documento'...")
    
    for link in soup.find_all('a', href=True):
        texto = link.get_text(strip=True).lower()
        href = link['href']
        
        if 'baixar documento' in texto:
            if href.startswith('http') or href.startswith('/'):
                pdf_url = href
                if pdf_url.startswith('/'):
                    pdf_url = "https://www.ufca.edu.br" + pdf_url
                break
            
    if not pdf_url:
        print("❌ ERRO: O botão 'Baixar documento' não foi encontrado na página.")
        return

    print(f"✅ Botão encontrado! O link verdadeiro do PDF é: {pdf_url}")
    print("Baixando e lendo o arquivo...")
    
    try:
        pdf_response = requests.get(pdf_url, headers=headers)
        
        with pdfplumber.open(io.BytesIO(pdf_response.content)) as pdf:
            pagina = pdf.pages[0] 
            tabela_extraida = pagina.extract_table()
            
        if tabela_extraida:
            print("✅ Tabela extraída com sucesso! Iniciando a limpeza dos dados...")
            
            # Limpa linhas totalmente vazias
            tabela_limpa = [linha for linha in tabela_extraida if any(celula for celula in linha)]
            
            # Cria a tabela usando a biblioteca Pandas
            df = pd.DataFrame(tabela_limpa[1:], columns=tabela_limpa[0])
            
            # --- INÍCIO DA FAXINA NOS DADOS ---
            # Converte tudo para texto
            df = df.astype(str)
            
            # Remove a palavra 'None' e substitui por vazio ou traço
            df = df.replace('None', '', regex=False)
            
            # Troca o '\n' do PDF pela quebra de linha oficial do HTML (<br>)
            df = df.replace(r'\n', '<br>', regex=True)
            
            # Faz a mesma limpeza nos títulos das colunas (cabeçalho)
            df.columns = [str(col).replace('None', '').replace('\n', '<br>') for col in df.columns]
            # -----------------------------------
            
            # Transforma em tabela HTML (escape=False permite que o <br> funcione)
            tabela_html = df.to_html(index=False, escape=False, classes='table table-striped table-hover table-bordered text-center align-middle')
            
            html_completo = f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Cardápio da Semana - RU UFCA</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {{ background-color: #f8f9fa; padding: 20px; font-size: 14px; }}
                    .container {{ background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 95%; }}
                    thead {{ background-color: #005b96; color: white; vertical-align: middle; }}
                    th, td {{ padding: 12px !important; vertical-align: middle; }}
                </style>
            </head>
            <body>
                <div class="container mt-4">
                    <h2 class="mb-4 text-center" style="color: #005b96;">Cardápio da Semana - RU UFCA</h2>
                    <div class="table-responsive">
                        {tabela_html}
                    </div>
                    <p class="text-muted text-center mt-4"><small>Atualizado automaticamente. Sistema não oficial.</small></p>
                </div>
            </body>
            </html>
            """
            
            with open('index.html', 'w', encoding='utf-8') as f:
                f.write(html_completo)
            print("✅ Site gerado, limpo e formatado com sucesso!")
        else:
            print("❌ ERRO: Nenhuma tabela legível encontrada.")
            
    except Exception as e:
        print(f"❌ ERRO ao tentar baixar ou ler o arquivo: {e}")

if __name__ == '__main__':
    atualizar_cardapio()
            
    except Exception as e:
        print(f"❌ ERRO ao tentar baixar ou ler o arquivo: {e}")

if __name__ == '__main__':
    atualizar_cardapio()
