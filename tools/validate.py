"""Validate deliverable consistency; not a production bank service test suite."""
from pathlib import Path
import copy
import importlib.util
import json
import re
import xml.etree.ElementTree as ET
from decimal import Decimal

ROOT=Path(__file__).resolve().parents[1]
def main():
    checked=0
    for f in ROOT.rglob('*.md'):
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',f.read_text(encoding='utf8')):
            if '://' in target or target.startswith('#'):continue
            dest=(f.parent/target.split('#')[0]).resolve()
            assert dest.is_relative_to(ROOT) and dest.exists(),(f,target)
            checked+=1
    triage=(ROOT/'Task1/triage.md').read_text(encoding='utf8')
    assert re.findall(r'^\| (\d+) \|',triage.split('## Канвас')[0],re.M)==[str(i) for i in range(1,19)]
    for f in ROOT.rglob('*.json'):json.loads(f.read_text(encoding='utf8'))
    for f in (ROOT/'Task3/diagrams').glob('*.svg'):ET.parse(f)
    assert len(list((ROOT/'Task3/diagrams').glob('*.png')))==5
    spec=importlib.util.spec_from_file_location('cost',ROOT/'Task4/calculate.py')
    cost=importlib.util.module_from_spec(spec);spec.loader.exec_module(cost)
    calc=cost.calculate();saved=json.loads((ROOT/'Task4/calculation.json').read_text(encoding='utf8'))
    for key,value in calc.items():
        scale=Decimal('.000001') if 'per_all_operation' in key else Decimal('.01')
        assert Decimal(str(saved[key]))==value.quantize(scale),key
    assert calc['tco_24_direct']>calc['tco_12_direct']>0
    assert calc['combined_24']==calc['current_process_24']+calc['tco_24_direct']
    # jsonschema is required for the release consistency check.
    import jsonschema
    from jsonschema import Draft202012Validator, FormatChecker
    schemas={name:json.loads((ROOT/f'Task3/contracts/{name}.schema.json').read_text(encoding='utf8')) for name in ['rank','document']}
    validators={}
    for name,schema in schemas.items():
        Draft202012Validator.check_schema(schema)
        validators[name]=Draft202012Validator(schema,format_checker=FormatChecker())
    examples=json.loads((ROOT/'Task3/contracts/examples.json').read_text(encoding='utf8'))
    validators['rank'].validate(examples['rank']);validators['rank'].validate(examples['abstain']);validators['document'].validate(examples['document'])
    bad=[]
    def mutate(base,path,value):
        item=copy.deepcopy(examples[base]);obj=item
        for part in path[:-1]:obj=obj[part]
        obj[path[-1]]=value
        return item
    bad.extend([('rank',mutate('rank',['score'],None)),('rank',mutate('rank',['sourceRefs'],[])),('rank',mutate('abstain',['score'],.9)),('rank',mutate('rank',['cutoff'],'not-a-time'))])
    payment=copy.deepcopy(examples['rank']);payment['action']='HOLD';bad.append(('rank',payment))
    bad.extend([('document',mutate('document',['fields',0,'source'],None)),('document',mutate('document',['fields',0,'unit'],None)),('document',mutate('document',['fields',0,'value'],'a number')),('document',mutate('document',['fields',1,'issue'],'NONE')),('document',mutate('document',['hash'],'fake'))])
    for name,item in bad:assert list(validators[name].iter_errors(item)),(name,item)
    print(f'PASS: {checked} local links; 18 triage rows; JSON/SVG; 5 diagram pairs; TCO; 3 valid and {len(bad)} invalid contract examples')
    print('LIMIT: no model quality, bank integration, legal approval or production SLO is verified by this script')

if __name__=='__main__':main()
