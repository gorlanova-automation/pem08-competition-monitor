"""Интеграционные запросы к локальному серверу, только публичные учебные источники."""
import json
import time
from pathlib import Path
import requests
ROOT = Path(__file__).resolve().parent
OUT = ROOT/'evidence'
OUT.mkdir(exist_ok=True)
records = []
base = 'http://127.0.0.1:18104'
for source in ['n8n','make','zapier']:
    for kind in ['text','image']:
        start = time.perf_counter()
        if kind == 'text':
            r = requests.post(base+'/analyzetext', json={'text': (ROOT/'data'/(source+'.txt')).read_text(encoding='utf-8')}, timeout=120)
        else:
            with (ROOT/'data'/(source+'.jpg')).open('rb') as f:
                r = requests.post(base+'/analyzeimage', files={'file':(source+'.jpg',f,'image/jpeg')}, timeout=120)
        obj = r.json()
        result = {'source':source,'type':kind,'http':r.status_code,'seconds':round(time.perf_counter()-start,2),'response':obj}
        (OUT/(source+'_'+kind+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        records.append(result)
        print(source,kind,r.status_code,'success=',obj.get('success'),flush=True)
        if not obj.get('success'):
            print('Safe error:',obj.get('error'),flush=True)
start = time.perf_counter()
r = requests.post(base+'/parsedemo',json={'url':'https://n8n.io/'},timeout=120)
record = {'source':'n8n','type':'parse_capture','http':r.status_code,'seconds':round(time.perf_counter()-start,2),'response':r.json()}
records.append(record)
(OUT/'parsedemo_capture.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'live_tests.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
history=requests.get(base+'/history',timeout=10).json()
(OUT/'history_public_tests.json').write_text(json.dumps(history,ensure_ascii=False,indent=2),encoding='utf-8')
print('parse',record['response'].get('success'),'history',history.get('total'),flush=True)

