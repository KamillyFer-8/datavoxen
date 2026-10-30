"""Reúne capturas reais de todas as rotas sem modificar os arquivos originais."""
from pathlib import Path
import html
import zipfile
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
folder = root / 'output/prints'
titles = ['Visão geral', 'Estratégias', 'Simulador financeiro', 'Produtos e preços', 'Jogadores e coortes', 'Finanças', 'Benchmarking', 'Relatórios', 'Metodologia e fontes', 'Arquivos do estudo']
desktop = sorted((folder/'desktop').glob('*.png'))
assert len(desktop)==10, len(desktop)

style = '''body{margin:0;background:#e5e5e5;color:#151515;font:16px 'Segoe UI',Arial,sans-serif}main{max-width:1300px;margin:auto;padding:36px}h1{font-size:32px;letter-spacing:-1px}p{line-height:1.7;color:#555}nav{display:flex;gap:18px;margin:25px 0}a{color:inherit}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:20px;margin-bottom:40px}article{background:#fff;border-radius:24px;padding:18px}article img{width:100%;height:380px;object-fit:contain;object-position:top;background:#fafafa}h3{font-size:16px}small{color:#777}'''
parts = [f'<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Datavoxen — telas no computador</title><style>{style}</style><main><h1>Datavoxen · Telas no computador</h1><p>Capturas reais de 30/10/2026. São 10 telas da versão desktop. Clique em uma imagem para abrir o print completo.</p><p>Edição pública SQLite: consulta e exportação sem conta. O acervo inclui o PDF original e a base oficial.</p>']
for name,files in [('desktop',desktop)]:
    parts.append(f'<h2 id="{name}">{name.capitalize()}</h2><section>')
    for i,path in enumerate(files):
        rel=html.escape(path.relative_to(folder).as_posix(),quote=True)
        title=html.escape(titles[i])
        parts.append(f'<article><h3>{i+1:02} · {title}</h3><a href="{rel}"><img src="{rel}" alt="{title} — {name}" loading="lazy"></a><p><a href="{rel}">Abrir imagem completa</a></p></article>')
    parts.append('</section>')
parts.append('</main></html>')
(folder/'galeria.html').write_text(''.join(parts),encoding='utf-8')
(folder/'LEIA-ME.txt').write_text('DATAVOXEN — Capturas reais de 30/10/2026\n\nAbra galeria.html para navegar pelas imagens.\nSomente computador: 10 telas completas da versão desktop.\nSimulador com todos os painéis de parâmetros abertos.\nTabelas mostram a página inicial, conforme exibida na aplicação.\nEdição pública SQLite: acervo com PDF, banco e dados oficiais. Sem contas ou banco na nuvem.\n',encoding='utf-8')

# Folha de contato apenas para orientação e conferência; os PNGs completos estão no ZIP.
sheet=Image.new('RGB',(1500,1340),'#e5e5e5')
draw=ImageDraw.Draw(sheet)
try: font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',21)
except OSError: font=ImageFont.load_default()
for i,path in enumerate(desktop):
    x=20+(i%5)*298; y=20+(i//5)*660
    draw.rounded_rectangle((x,y,x+280,y+640),radius=16,fill='white')
    draw.text((x+14,y+13),f'{i+1:02} {titles[i]}',fill='#222',font=font)
    with Image.open(path) as im:
        im=im.convert('RGB'); im.thumbnail((256,575))
        sheet.paste(im,(x+(280-im.width)//2,y+55))
sheet.save(folder/'visao-de-todas-as-telas.jpg',quality=90)
archive=root/'output/Datavoxen_Todas_as_Telas.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for path in sorted(folder.rglob('*')):
        if path.is_file() and 'mobile' not in path.relative_to(folder).parts: z.write(path,path.relative_to(folder))
print(f'{len(desktop)} capturas desktop. ZIP: {archive} ({archive.stat().st_size} bytes)')
