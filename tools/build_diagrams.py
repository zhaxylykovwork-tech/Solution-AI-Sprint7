"""Editable explicit C4/DFD layouts. Outputs SVG + PNG, no external renderer."""
from pathlib import Path
from html import escape
import math
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]/'Task3'/'diagrams'
FONT=next(p for p in [Path('C:/Windows/Fonts/arial.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')] if p.exists())

def render(name,title,subtitle,nodes,edges,boundaries,footer,W=1800,H=1100):
    ROOT.mkdir(parents=True,exist_ok=True)
    im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">','<rect width="100%" height="100%" fill="white"/>']
    def text(x,y,s,size=22,color='#172b4d'):
        d.text((x,y),s,font=ImageFont.truetype(str(FONT),size),fill=color)
        svg.append(f'<text x="{x}" y="{y+size}" font-family="Arial,DejaVu Sans,sans-serif" font-size="{size}" fill="{color}">{escape(s)}</text>')
    def line(pts,dash=False,color='#476582',width=3):
        if dash:
            for (x1,y1),(x2,y2) in zip(pts,pts[1:]):
                length=math.hypot(x2-x1,y2-y1)
                for a in range(0,int(length),20):
                    b=min(a+11,length)
                    d.line([(x1+(x2-x1)*a/length,y1+(y2-y1)*a/length),(x1+(x2-x1)*b/length,y1+(y2-y1)*b/length)],fill=color,width=width)
        else:d.line(pts,fill=color,width=width)
        svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="11 9"' if dash else '')+'/>')
    text(40,22,title,34);text(40,78,subtitle,23)
    for x,y,w,h,label in boundaries:
        line([(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)],True,'#71849c',2)
        tw=d.textlength(label,font=ImageFont.truetype(str(FONT),21))
        d.rectangle((x+10,y-30,x+tw+18,y-3),fill='white')
        svg.append(f'<rect x="{x+10}" y="{y-30}" width="{tw+8}" height="27" fill="white"/>')
        text(x+14,y-28,label,21)
    for pts,label,at in edges:
        line(pts)
        a,b=pts[-2:];angle=math.atan2(b[1]-a[1],b[0]-a[0]);tri=[b,(b[0]-15*math.cos(angle-.4),b[1]-15*math.sin(angle-.4)),(b[0]-15*math.cos(angle+.4),b[1]-15*math.sin(angle+.4))]
        d.polygon(tri,fill='#476582');svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in tri)+'" fill="#476582"/>')
        x,y=at;tw=d.textlength(label,font=ImageFont.truetype(str(FONT),21));d.rectangle((x-4,y-2,x+tw+4,y+28),fill='white');svg.append(f'<rect x="{x-4}" y="{y-2}" width="{tw+8}" height="30" fill="white"/>');text(x,y,label,21)
    for x,y,w,h,lines,kind in nodes:
        fill={'internal':'#e8f2ff','external':'#f1f3f6','model':'#e4f5ec','store':'#fff2d9'}[kind]
        d.rounded_rectangle((x,y,x+w,y+h),radius=8,fill=fill,outline='#476582',width=2)
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="#476582" stroke-width="2"/>')
        for i,s in enumerate(lines):
            assert d.textlength(s,font=ImageFont.truetype(str(FONT),22))<w-28,(name,s)
            text(x+14,y+16+i*31,s,22)
        assert len(lines)*31+25<=h,(name,lines)
    for i,s in enumerate(footer):text(40,H-90+i*30,s,21)
    im.save(ROOT/(name+'.png'));(ROOT/(name+'.svg')).write_text('\n'.join(svg+['</svg>']),encoding='utf-8')

def n(x,y,title,kind='internal',extra=(),w=350,h=160):return (x,y,w,h,[title,*extra],kind)
def e(pts,label,x,y):return(pts,label,(x,y))

def flagship():
    nodes=[n(30,250,'АБС + rules','external',['[Соседние системы]','Операции / сигналы'],w=260),
        n(400,240,'C1 Ingestion / Features',extra=['[Container / Python]','As-of / snapshot manifest']),n(850,240,'C2 Batch Ranker','model',['[Container / Python]','IsolationForest / reasons']),n(1300,240,'C3 Validator / Queue',extra=['[Container / Python+MQ]','Mandatory / control / model']),
        n(400,650,'C6 Model Registry','store',['[Container / artifact store]','Signed model / test manifest']),n(850,650,'C5 Audit / Outcomes','store',['[Container / PostgreSQL]','Expert / outcome / formal']),n(1300,650,'C4 Case API / UI',extra=['[Container / Web API]','Human decision + audit']),
        n(1300,870,'Финмонитор + IdP','external',['[Person / external IdP]'],h=100)]
    edges=[e([(290,330),(400,330)],'F1',325,295),e([(750,320),(850,320)],'F2',780,285),e([(1200,320),(1300,320)],'F4',1230,285),e([(1475,400),(1475,650)],'F5',1490,510),e([(1300,730),(1200,730)],'F7',1230,695),e([(575,650),(575,520),(1025,520),(1025,400)],'F3',710,485),e([(850,770),(795,770),(795,190),(575,190),(575,240)],'F8 offline',805,565),e([(1475,870),(1475,810)],'F6 HTTPS',1500,825)]
    render('flagship-container','C4 L2 | №1: приоритизация ручных проверок','TB1 источник → обработка; TB2 банковский сервис; TB3 артефакты; TB4 сотрудник / IdP.',nodes,edges,[(340,140,1400,700,'TB2 | Система приоритизации'),(10,225,300,205,'TB1'),(380,625,390,205,'TB3'),(1280,850,440,130,'TB4'),(1280,625,440,205,'TB5')],['Синие: код/сервисы. Зелёный: ML runtime. Жёлтые: хранилища. Серые: внешние системы/человек.','F1 пересекает TB1/TB2. F5 проверяется до case. Платёжный шлюз не связан с ML.'])

def component():
    nodes=[n(30,270,'C1 Features','external',['[Neighbour container]','Manifest + cutoff'],w=260),
        n(400,250,'Manifest Loader',extra=['[Component / code]','Hash / batchId / schema']),n(850,250,'Feature Guard',extra=['[Component / code]','Freshness / history']),n(1300,250,'Model Scorer','model',['[Component / ML]','Pinned preprocessing + IF']),
        n(850,650,'Result / Outbox',extra=['[Component / code]','Atomic result + delivery']),n(1300,650,'Result Assembler',extra=['[Component / code]','Score / reasons / ABSTAIN']),n(30,650,'C3 Validator / Queue','external',['[Neighbour container]','Validate before case'],w=270)]
    edges=[e([(290,330),(400,330)],'load',310,295),e([(750,330),(850,330)],'check',770,295),e([(1200,330),(1300,330)],'score',1220,295),e([(1475,410),(1475,650)],'assemble',1490,510),e([(1300,730),(1200,730)],'persist',1215,695),e([(850,730),(300,730)],'F4',550,695)]
    render('flagship-component','C4 L3 | Компоненты контейнера C2 Batch Ranker','Внутри пунктирной рамки один deployment. Loader/Guard/Assembler/Outbox — код, Scorer — ML.',nodes,edges,[(340,150,1400,710,'C2 Batch Ranker | deployment boundary'),(1280,225,440,205,'TB3')],['TB3: подписанный digest модели проверяется перед Scorer; нет сетевой загрузки latest.','Ошибка признаков → ABSTAIN/FALLBACK. Outbox retry не выполняет платёж и не создаёт дубли cases.'])

def document(name,title,source,worker,output):
    nodes=[n(30,250,source,'external',['[Neighbour system]','Version / hash / ACL'],w=270),n(400,240,'C1 Quarantine / Input',extra=['[Container / sandbox]','Type / limits / version']),n(850,240,'C2 Job Orchestrator',extra=['[Container / API + MQ]','202 jobId / async / retry']),n(1300,240,worker,'model',['[Container / ML + code]','Pinned model / no egress']),n(1300,650,'C4 Validator / Review',extra=['[Container / API + UI]','Source / schema / human']),n(850,650,'C5 Approved Store','store',['[Container / DB+objects]','Version + signed approval']),n(30,650,output,'external',['[Neighbour system]','Read approved version'],w=270),n(1300,870,'Оператор + IdP / Audit','external',['[Person / external services]'],h=100)]
    edges=[e([(300,330),(400,330)],'D1',330,295),e([(750,320),(850,320)],'D2',780,285),e([(1200,320),(1300,320)],'job',1230,285),e([(1475,400),(1475,650)],'D3/D4',1490,510),e([(1300,730),(1200,730)],'D5',1230,695),e([(850,730),(300,730)],'approved',530,695),e([(1475,870),(1475,810)],'HTTPS',1500,825)]
    render(name,'C4 L2 | '+title,'D1 пересекает TB1. Пунктирные TB — границы доверия; угрозы и протоколы в architecture.md.',nodes,edges,[(340,140,1400,700,'TB2 | Банковский сервис документов'),(10,225,300,205,'TB1'),(1280,215,440,205,'TB3'),(1280,850,440,130,'TB4'),(10,625,300,205,'TB5')],['D2/D3: асинхронные задания и structured result. D4: независимая проверка до UI и подтверждения.','TB5: downstream читает только approved version; сбой/конфликт → REVIEW или ручной ввод.'])

def dfd():
    nodes=[n(40,250,'D1 Raw snapshot','store',['Операции / rules','Cutoff / manifest']),n(500,250,'P1 Point-in-time',extra=['Сверка / features','Никаких future outcomes']),n(960,250,'P2 Rank','model',['Аномальность / reasons','Untrusted output']),n(1420,250,'P3 Validate',extra=['Schema / source / quota','READY либо ABSTAIN'],w=330),n(1420,650,'D2 Verified cases','store',['Mandatory / control / model','Idempotent delivery'],w=330),n(960,650,'P4 Human review',extra=['Expert / independent audit','No automatic payment']),n(500,650,'D3 Outcomes / Audit','store',['Event time / known_at','3 different outcome traces']),n(40,650,'Offline evaluation',extra=['Permitted export','Mature cohorts only'])]
    edges=[e([(390,330),(500,330)],'TB1',415,295),e([(850,330),(960,330)],'features',860,295),e([(1310,330),(1420,330)],'candidate',1320,295),e([(1585,410),(1585,650)],'verified',1600,510),e([(1420,730),(1310,730)],'case',1345,695),e([(960,730),(850,730)],'event',870,695),e([(500,730),(390,730)],'offline',405,695)]
    render('flagship-dfd','DFD | №1: происхождение данных и допуск результата','D — хранилище, P — процесс. Это поток данных, а не дополнительная C4-диаграмма.',nodes,edges,[(460,150,1310,710,'TB2 | Обработка в банковском контуре'),(20,225,390,205,'TB1'),(940,225,390,205,'TB3'),(940,625,390,205,'TB4'),(1400,625,370,205,'TB5')],['TB3: model artifacts → P2 (signed digest). TB4: человек → P4 (OIDC/RBAC/audit).','TB5: P3 → D2, граница доверия к проверенному case. Ни один score не означает HOLD/RELEASE.'])

if __name__=='__main__':
    flagship();component();document('ocr-container','№2 OCR','Документооборот','C3 OCR Worker','№18 / Андеррайтинг');document('extraction-container','№18 Извлечение','Verified OCR / digital','C3 Extractor Worker','Кредитная система');dfd()
