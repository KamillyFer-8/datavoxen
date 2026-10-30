"""Transcrição da matriz 15.1 do PDF fornecido, sem consulta de preços atuais."""
import json
from pathlib import Path

sources = [
 ('COD Mobile','Loja web oficial','https://store.callofdutymobile.com/pt-br/codm',[('460 CP',19.49),('960 CP',38.99)]),
 ('PUBG Mobile','App Store Brasil · iOS','https://apps.apple.com/br/app/pubg-mobile/id1330123889',[('300 UC',29.90),('600 UC',59.90)]),
 ('Free Fire','App Store Brasil · iOS','https://apps.apple.com/br/app/free-fire/id1300146617',[('100 diamantes',4.90),('520 diamantes',27.90)]),
 ('Fortnite','App Store Brasil · iOS','https://apps.apple.com/br/app/fortnite/id6483539426',[('800 V-Bucks',31.99),('2.400 V-Bucks',79.00)]),
 ('Brawl Stars','App Store Brasil · iOS','https://apps.apple.com/br/app/brawl-stars/id1229016807',[('30 gemas',12.50),('80 gemas',29.90)]),
 ('Clash Royale','App Store Brasil · iOS','https://apps.apple.com/br/app/clash-royale/id1053012308',[('Punhado de gemas',5.90),('Bolsa de gemas',29.90)]),
 ('VALORANT','Codashop Brasil · PC','https://app.codashop.com/pt-br/valorant',[('475 VP',18.90),('1.000 VP',38.90)]),
]
rows=[]
for game,channel,url,offers in sources:
    for product,price in offers:
        rows.append(dict(game=game,product=product,offer_type='Moeda virtual',price=price,currency='BRL',channel=channel,consulted_at='2026-10-29',source_url=url,verification_status='Histórico documentado no estudo; não reconfirmado',limitations='Recarga não equivale a cosmético; preço e disponibilidade variáveis.'+(' Referência PC adjacente.' if game=='VALORANT' else '')+(' Oferta promocional.' if game=='COD Mobile' else '')))
Path(__file__).resolve().parents[1].joinpath('backend/app/benchmarks.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
