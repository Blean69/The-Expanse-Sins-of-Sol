#!/usr/bin/env python3
"""Offline negative controls; these are not a game-state or multiplayer test."""
from pathlib import Path
import copy, json, subprocess, sys, tempfile
import update18_scenario as b

def main():
    source=b.read(Path(__file__).with_name('update18_scenario_source.json'))
    cases=[]
    d=copy.deepcopy(source);d['nodes'][2]['id']=1;cases.append(('duplicate node',d,'Duplicate node ID/key'))
    d=copy.deepcopy(source);d['lanes'].append(d['lanes'][0]);cases.append(('duplicate lane',d,'Duplicate lane'))
    d=copy.deepcopy(source);d['nodes'][1]['parent']='mars';d['nodes'][2]['parent']='earth';cases.append(('parent cycle',d,'Cyclic parent hierarchy'))
    d=copy.deepcopy(source);d['lanes']=[x for x in d['lanes'] if 'jupiter' not in x];cases.append(('disconnected objective',d,'Disconnected or orphan node'))
    d=copy.deepcopy(source);d['nodes'][1]['filling']='made_up_filling';cases.append(('unknown filling',d,'Unknown filling'))
    results=[]
    with tempfile.TemporaryDirectory(prefix='expanse18-scenario-test-') as temp:
        temp=Path(temp)
        for i,(name,data,message) in enumerate(cases):
            p=temp/f'{i}.json';b.write(p,data)
            result=subprocess.run([sys.executable,str(Path(__file__).with_name('update18_scenario.py')),'--source',str(p),'--output',str(temp/f'out{i}'),'--audit',str(temp/f'audit{i}')],text=True,capture_output=True)
            assert result.returncode!=0 and message in result.stderr,(name,result.stderr)
            results.append({'case':name,'status':'PASS rejected malformed input','expected_error':message})
    b.write(b.ROOT/'audit/update18-scenario/negative-controls.json',{'status':'PASS OFFLINE','cases':results,'runtime':'NOT RUN'})
    print(json.dumps(results,indent=2))
if __name__=='__main__': main()
