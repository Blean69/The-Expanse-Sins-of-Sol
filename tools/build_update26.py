"""Cumulative UI/roster/command/native-contact and existing-art polish candidate."""
import argparse,copy,json
from pathlib import Path
from update20_fleet import ROOT,GAME
from update26_research import changes as research_changes
from update26_contacts import changes as contact_changes
from update26_command_gameplay import changes as command_changes
from doctrine_package import package
from validate_experiments import read,require,sha256
from build_polish import write

def definitions(base,sandbox=False):
 edits,loc,research=research_changes(base,sandbox);origins={};art={};replacements={}
 command,cloc,co,cr=command_changes(base)
 require(not(set(edits)&set(command)),'Command shared edit collision')
 edits.update(command);loc.update(cloc);origins.update(co)
 for rel,src in cr['art_files'].items():
  p=Path(src);require(p.is_file() and not p.is_symlink(),'Missing command art '+rel);art[rel]=p
  contract=read(ROOT/'audit/update26-command/art-contract.json');require(sha256(p)==contract['files'][rel],'Command art drift '+rel)
 contacts,nloc,no,na,nr=contact_changes(base)
 require(not(set(edits)&set(contacts)),'NPC shared edit collision')
 edits.update(contacts);loc.update(nloc);origins.update(no);art.update(na)
 # Each replacement is authorized against the exact frozen predecessor hash.
 storm=read(ROOT/'audit/update26-storm/replacement-manifest.json')
 for row in storm['files']:
  rel=row['path'];p=Path(storm['game_directory'])/rel
  require(p.is_file() and not p.is_symlink() and sha256(p)==row['sha256'],'Storm art drift '+rel)
  require(rel not in art,'Art overlap '+rel);art[rel]=p
  if row['action']=='replace':require(sha256(base/rel)==row['previous_sha256'],'Storm predecessor drift');replacements[rel]=row['previous_sha256']
 # Platform/Murphy manifest is added by the integrator once its geometry review is complete.
 platform_path=ROOT/'audit/update26-platform/integration-spec.json'
 require(platform_path.exists(),'Reviewed platform integration spec missing')
 platform=read(platform_path)
 combined=read(ROOT/'audit/update26-platform/combined-art-manifest.json')
 for rel,row in combined['files'].items():
  h=row['sha256'];p=Path(combined['game'])/rel
  require(p.is_file() and not p.is_symlink() and sha256(p)==h,'Platform/Murphy art drift '+rel)
  if (base/rel).exists() and sha256(base/rel)==h:continue
  require(rel not in art,'Art overlap '+rel);art[rel]=p
  if (base/rel).exists():replacements[rel]=sha256(base/rel)
 rel='entities/expanse22_foehammer_battery.unit';d=read(base/rel)
 guidance=platform['spatial_patch_guidance'];require(d['spatial']==guidance['old'],'Platform spatial predecessor drift')
 d['spatial']['box']=copy.deepcopy(guidance['new_art_bounds']['box']);d['spatial']['radius']=max(d['spatial']['radius'],guidance['new_art_bounds']['radius']);edits[rel]=d
 text=read(base/'localized_text/en.localized_text');text.update(loc);edits['localized_text/en.localized_text']=text
 meta=read(base/'.mod_meta_data');meta.update(display_name='The Expanse —0.26 Fleet Polish'+(' Sandbox' if sandbox else ''),display_version='0.26.0',short_description='Compact military tree, direct OPA colonization, polished hulls and paid NPC services.',long_description='Cumulative candidate over frozen0.25. Removes obsolete TEC ship production and unused military branches; preserves civilian research, existing weapon balance and shieldless baseline. Enlarged OPA command has direct colonization and doubled hull/armor. Polished Storm, Murphy and Foehammer. Tycho/Ceres native paid contacts are guaranteed on the Contacts variant of Three Homes. ProtoTech production/plating and exclusive salvage remain separate unverified work. Offline checks only; runtime/MP NOT RUN.')
 edits['.mod_meta_data']=meta
 return edits,origins,art,replacements,{'research':research,'command':cr,'contacts':nr,'storm':storm,'platform':platform}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--sandbox',action='store_true');p.add_argument('--package-existing',action='store_true');a=p.parse_args()
 suffix='_sandbox' if a.sandbox else '';base=ROOT/'build/experiments'/('expanse_update25'+suffix);out=ROOT/'build/experiments'/('expanse_update26'+suffix);audit=ROOT/'audit'/('update26'+suffix)
 edits,origins,art,replacements,r=definitions(base,a.sandbox);write(audit/'integration.json',r)
 print(json.dumps(package(base,out,edits,origins,ROOT/'docs/update26.md',audit,art,a.package_existing,art_replacements=replacements),indent=2))
