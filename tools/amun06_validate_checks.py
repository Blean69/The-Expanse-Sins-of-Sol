"""Bounded negative checks for concrete Amun06 graph/overlay validation gaps."""
from pathlib import Path
import copy,json,tempfile,shutil
from amun06_validate_package import check_boarding,effective_uniform,read
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/amun06-c/checks';SOURCE=Path('/run/media/haker/NVME 2/expanse-workers/weapon-behavior/build/amun06-a/final/core');GAME=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2')
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 OUT.mkdir(parents=True,exist_ok=True);records=[]
 with tempfile.TemporaryDirectory(prefix='amun-check-',dir=OUT)as temp:
  mod=Path(temp);(mod/'entities').mkdir();names=['expanse06_amun_boarding.'+x for x in ['ability','buff','action_data_source']];original={n:read(SOURCE/'entities'/n)for n in names}
  def reset():
   for n,d in original.items():write(mod/'entities'/n,d)
  def exercise(label,mutate,should_pass):
   reset();mutate();ok=True;reason=''
   try:check_boarding(mod,None)
   except (ValueError,AssertionError,KeyError)as e:ok=False;reason=str(e)
   assert ok==should_pass,(label,reason);records.append({'case':label,'expected':'PASS'if should_pass else'REJECT','observed':'PASS'if ok else'REJECT','diagnostic':reason})
  exercise('Reviewed three-second single-roll graph',lambda:None,True)
  def chance():
   p=mod/'entities/expanse06_amun_boarding.action_data_source';d=read(p);next(x for x in d['action_values']if x['action_value_id']=='capture_chance')['action_value']['values']=[1.0];write(p,d)
  exercise('Injected guaranteed capture instead of10%',chance,False)
  def repeated():
   p=mod/'entities/expanse06_amun_boarding.buff';d=read(p);d['time_actions']=[{}];write(p,d)
  exercise('Injected repeat attempt schedule',repeated,False)
  def recipient():
   p=mod/'entities/expanse06_amun_boarding.buff';d=read(p);d['trigger_event_actions'][0]['action_group']['actions'][0]['operators'][0]['new_owner_player']['owned_unit']['unit_type']='current_spawner';write(p,d)
  exercise('Injected capture recipient change',recipient,False)
  filename='attack_target_type_group.uniforms';base=read(GAME/'uniforms'/filename);array='attack_target_type_groups';idkey='unit_attack_target_type_group_id';flag='overwrite_attack_target_type_groups';new=copy.deepcopy(base[array][0]);new[idkey]='expanse06_validation_private_test';p=mod/'uniforms'/filename
  write(p,{array:[new],flag:False});merged=effective_uniform(mod,GAME,filename,array,idkey,flag);assert len(merged)==len(base[array])+1;records.append({'case':'Explicit additive private group retains installed groups','expected':'PASS','observed':'PASS'})
  write(p,{array:[new],flag:True});rejected=False
  try:effective_uniform(mod,GAME,filename,array,idkey,flag)
  except ValueError as e:rejected=True;why=str(e)
  assert rejected;records.append({'case':'Injected overwrite drops installed groups','expected':'REJECT','observed':'REJECT','diagnostic':why})
 write(ROOT/'audit/amun06-c/negative-checks.json',{'status':'PASS','checks':records,'only_owned_temporary_copies_mutated':True,'runtime':'NOT RUN'});print(json.dumps({'status':'PASS','cases':len(records)}))
if __name__=='__main__':main()
