import qrcode
from fpdf import FPDF
import json
import os

def gerar_folha_redacao(id_aluno, nome_aluno, turma):
    # 1. Preparar os dados para o QR Code (JSON)
    dados_qr = {
        "id": id_aluno,
        "nome": nome_aluno,
        "turma": turma
    }
    dados_json = json.dumps(dados_qr, ensure_ascii=False)
    
    # 2. Criar a imagem do QR Code temporariamente
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(dados_json)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    caminho_qr = f"qr_temp_{id_aluno}.png"
    img_qr.save(caminho_qr)
    
    # 3. Configurar e construir o PDF
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    # Definir margens ligeiramente menores para garantir espaço
    pdf.set_margins(left=10, top=10, right=10)
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    
    # --- Cabeçalho ---
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="Folha de Redação - Simulado ENEM", ln=True, align='C')
    pdf.ln(2) # Reduzi este espaço para caber na página
    
    # Inserir o QR Code no canto superior direito da página
    pdf.image(caminho_qr, x=170, y=10, w=28)
    
    # Quadro com os Dados do Aluno (à esquerda)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 8, txt=f"Nome: {nome_aluno}", border=1, ln=True)
    pdf.cell(70, 8, txt=f"Turma: {turma}", border=1)
    pdf.cell(70, 8, txt=f"Matrícula: {id_aluno}", border=1, ln=True)
    pdf.ln(6) # Reduzi o espaço antes das linhas
    
    # --- Linhas da Redação ---
    pdf.set_font("Arial", size=11)
    
    # 30 linhas com altura de 7.5mm (ajuste perfeito para 1 página A4)
    for i in range(1, 31):
        pdf.cell(10, 7.5, txt=str(i), border='B', align='R')
        pdf.cell(180, 7.5, txt="", border='B', ln=True)
        
    # 4. Guardar o ficheiro PDF
    nome_ficheiro = f"Redacao_{nome_aluno.replace(' ', '_')}.pdf"
    pdf.output(nome_ficheiro)
    
    # Limpar a imagem temporária do QR Code do disco
    if os.path.exists(caminho_qr):
        os.remove(caminho_qr)
        
    print(f"✅ Folha gerada com sucesso: {nome_ficheiro}")

# ==========================================
# Exemplo Prático: Gerar folhas para uma turma
# ==========================================
if __name__ == "__main__":
    turma_exemplo = [
        {"id": "2026001", "nome": "Ana Clara Guimarães", "turma": "3º Ano A"},
        {"id": "2026002", "nome": "João Pedro Silva", "turma": "3º Ano A"},
        {"id": "2026003", "nome": "Mariana Souza", "turma": "3º Ano A"}
    ]
    
    print("A gerar folhas de redação...")
    for aluno in turma_exemplo:
        gerar_folha_redacao(aluno["id"], aluno["nome"], aluno["turma"])
    
    print("Processo concluído!")