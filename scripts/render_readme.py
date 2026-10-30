"""Converte o README atual em um PDF de revisão com capturas desktop."""
import re
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, PageBreak, Image, XPreformatted, KeepTogether,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT/'output/pdf/Datavoxen_README_para_Revisao.pdf'
WIDTH, HEIGHT = A4
MARGIN = 45
CONTENT_WIDTH = WIDTH - 2*MARGIN - 12


def setup_fonts():
    font_root = Path('C:/Windows/Fonts')
    if (font_root/'segoeui.ttf').is_file():
        for name, file in [('Body','segoeui.ttf'),('BodyBold','segoeuib.ttf'),('Code','consola.ttf')]:
            pdfmetrics.registerFont(TTFont(name,str(font_root/file)))
        pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='Body',boldItalic='BodyBold')
        return 'Body','BodyBold','Code'
    return 'Helvetica','Helvetica-Bold','Courier'


BODY, BOLD, CODE = setup_fonts()
styles = {
    'title': ParagraphStyle('Title',fontName=BOLD,fontSize=30,leading=36,spaceAfter=15,textColor=colors.HexColor('#151515'),keepWithNext=True),
    'h2': ParagraphStyle('Section',fontName=BOLD,fontSize=14,leading=19,spaceBefore=17,spaceAfter=9,keepWithNext=True),
    'body': ParagraphStyle('Body',fontName=BODY,fontSize=9.6,leading=14.2,spaceAfter=9,textColor=colors.HexColor('#303030'),splitLongWords=True),
    'list': ParagraphStyle('List',fontName=BODY,fontSize=9.4,leading=14,spaceAfter=5,splitLongWords=True),
    'cell': ParagraphStyle('Cell',fontName=BODY,fontSize=8.5,leading=12,splitLongWords=True),
    'head': ParagraphStyle('TableHead',fontName=BOLD,fontSize=8.5,leading=12,textColor=colors.white),
    'code': ParagraphStyle('Code',fontName=CODE,fontSize=7.7,leading=11,spaceBefore=3,spaceAfter=12,backColor=colors.HexColor('#f3f3f3'),borderPadding=9),
    'caption': ParagraphStyle('Caption',fontName=BODY,fontSize=9,leading=13,spaceAfter=12,textColor=colors.HexColor('#666666')),
}


def inline(text):
    text=text.replace('—','-').replace('−','-').replace('–','-')
    tokens=re.split(r'(\*\*.+?\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))',text)
    result=[]
    for token in tokens:
        if token.startswith('**') and token.endswith('**'):
            result.append('<b>'+escape(token[2:-2])+'</b>')
        elif token.startswith('`') and token.endswith('`'):
            result.append(f'<font name="{CODE}" size="8.5">'+escape(token[1:-1])+'</font>')
        elif re.fullmatch(r'\[[^\]]+\]\([^)]+\)',token):
            match=re.fullmatch(r'\[([^\]]+)\]\(([^)]+)\)',token)
            label,url=match.groups()
            if url.startswith(('http://','https://')):
                result.append(f'<a href="{escape(url)}" color="#303030"><u>{escape(label)}</u></a>')
            else:
                result.append(escape(label)+f' <font name="{CODE}" size="7.8">('+escape(url)+')</font>')
        else:
            result.append(escape(token))
    return ''.join(result)


def footer(canvas,doc):
    canvas.saveState()
    canvas.setFont('Helvetica',8)
    canvas.setFillColor(colors.HexColor('#707070'))
    canvas.setStrokeColor(colors.HexColor('#dddddd'))
    canvas.setLineWidth(.5)
    canvas.line(MARGIN,32,WIDTH-MARGIN,32)
    canvas.drawRightString(WIDTH-MARGIN,20,str(doc.page))
    canvas.restoreState()


class ReviewCanvas(Canvas):
    def showPage(self):
        from types import SimpleNamespace
        self.saveState()
        self.resetTransforms()
        footer(self,SimpleNamespace(page=self.getPageNumber()))
        self.restoreState()
        super().showPage()


def build():
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    lines=(ROOT/'README.md').read_text(encoding='utf-8').splitlines()
    story=[];index=0
    while index<len(lines):
        line=lines[index].strip()
        if not line: index+=1;continue
        if line.startswith('```'):
            language=line[3:];index+=1;code=[]
            while index<len(lines) and not lines[index].startswith('```'):
                value=lines[index].replace('—','-').replace('−','-').replace('–','-')
                wrapped=textwrap.wrap(value,width=98,expand_tabs=False,replace_whitespace=False,drop_whitespace=False,subsequent_indent='    ') if value else ['']
                code.extend(wrapped);index+=1
            story.append(XPreformatted(escape('\n'.join(code)),styles['code']))
            index+=1;continue
        image=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',line)
        if image:
            label,relative=image.groups()
            if 'mobile' in relative: raise ValueError('A revisão só deve incluir capturas desktop')
            path=ROOT/relative
            from PIL import Image as PILImage
            with PILImage.open(path) as bitmap: width,height=bitmap.size
            scale=min(CONTENT_WIDTH/width,480/height)
            story.extend([KeepTogether([Paragraph(label+' - versão desktop',styles['h2']),Paragraph('Captura real da aplicação. Amplie o PDF para conferir os detalhes da interface.',styles['caption']),Image(str(path),width=width*scale,height=height*scale)]),PageBreak()])
            index+=1;continue
        if line.startswith('# '):
            story.append(Paragraph(inline(line[2:]),styles['title']));index+=1;continue
        if line.startswith('## '):
            story.append(Paragraph(inline(line[3:]),styles['h2']));index+=1;continue
        if line.startswith('|'):
            rows=[]
            while index<len(lines) and lines[index].strip().startswith('|'):
                raw=lines[index].strip()
                if not re.fullmatch(r'[| :\-]+',raw): rows.append([cell.strip() for cell in raw.strip('|').split('|')])
                index+=1
            cells=[[Paragraph(inline(cell),styles['head' if row_index==0 else 'cell']) for cell in row] for row_index,row in enumerate(rows)]
            widths=[CONTENT_WIDTH*.40,CONTENT_WIDTH*.60] if len(rows[0])==2 else [CONTENT_WIDTH/len(rows[0])]*len(rows[0])
            table=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#242424')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f4f4f4'),colors.white]),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('LINEBELOW',(0,0),(-1,0),.5,colors.black)]))
            story.extend([table,Spacer(1,10)]);continue
        if line.startswith('- ') or re.match(r'^\d+\. ',line):
            numbered=not line.startswith('- ');items=[]
            while index<len(lines):
                value=lines[index].strip()
                match=re.match(r'^\d+\. (.+)',value) if numbered else re.match(r'^- (.+)',value)
                if not match: break
                items.append(ListItem(Paragraph(inline(match.group(1)),styles['list'])));index+=1
            story.append(ListFlowable(items,bulletType='1' if numbered else 'bullet',leftIndent=15,bulletFontName=BODY,bulletFontSize=8,spaceAfter=9));continue
        paragraph=[line];index+=1
        while index<len(lines) and lines[index].strip() and not lines[index].startswith(('#','```','|','- ','![')) and not re.match(r'^\d+\. ',lines[index]):
            paragraph.append(lines[index].strip());index+=1
        story.append(Paragraph(inline(' '.join(paragraph)),styles['body']))
    while story and isinstance(story[-1],PageBreak): story.pop()
    doc=SimpleDocTemplate(str(OUTPUT),pagesize=A4,leftMargin=MARGIN,rightMargin=MARGIN,topMargin=45,bottomMargin=45,title='Datavoxen - README para revisão',author='Datavoxen',subject='Documentação do projeto público com SQLite e capturas desktop')
    doc.build(story,canvasmaker=ReviewCanvas)
    from pypdf import PdfReader
    reader=PdfReader(OUTPUT)
    text='\n'.join(page.extract_text() for page in reader.pages)
    for required in ['OpenAI Codex','Publicação na Vercel','Limitações e validação futura','Contexto do mercado brasileiro','Cenários e resultados']:
        assert required in text,required
    print(f'{OUTPUT}\n{len(reader.pages)} páginas | {OUTPUT.stat().st_size} bytes')


if __name__=='__main__': build()
