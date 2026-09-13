"""Main-owned escorts and local infrastructure; exact native build economics retained."""
import copy
from build_polish import write
from validate_experiments import read

PLAYERS=['trader_loyalist','trader_rebel','dlc_trader_loyalist']
INSTALLATION='expanse15_missile_defense'

def apply(out, game):
    for pid in PLAYERS:
        p=out/'entities'/(pid+'.player'); d=read(p)
        for escort in d.get('trade',{}).get('trade_ship_escorts',[]):
            escort['unit']={'trader_antifighter_frigate':'trader_light_frigate','trader_heavy_cruiser':'expanse_mcrn_corvette'}.get(escort['unit'],escort['unit'])
        d['buildable_units'].append('expanse15_truman')
        d['structures'].append(INSTALLATION)
        write(p,d)
    loc=read(out/'localized_text/en.localized_text')
    for index,unit,title in [(0,'trader_light_frigate','Morrigan Trade Escorts'),(1,'expanse_mcrn_corvette','Tachi Heavy Trade Escorts')]:
        rid=f'trader_unlock_trade_escorts_{index}'
        d=read(game/'entities'/(rid+'.research_subject'))
        def replace(x):
            if isinstance(x,dict):
                for k,v in x.items():
                    if k=='units_listing':x[k]=[unit]
                    else:replace(v)
            elif isinstance(x,list):
                for v in x:replace(v)
        replace(d)
        for k in ['name','name_uppercase','description']:
            if k in d:
                loc[d[k]]= title.upper() if k=='name_uppercase' else (title if k=='name' else 'Trade ships receive '+('a Morrigan light escort.' if index==0 else 'a Tachi heavy escort. The earlier Morrigan escort remains available.'))
        write(out/'entities'/(rid+'.research_subject'),d)
    u=read(out/'entities/trader_gauss_defense_structure.unit')
    u['skin_groups']=[{'skins':[INSTALLATION]}]
    # Existing orbital-defense build kind, costs, supply and construction behavior.
    u['build']['prerequisites']=[['trader_unlock_long_range_cruiser']]
    w=read(game/'entities/trader_long_range_cruiser_medium_missile.weapon')
    w.update(name=INSTALLATION+'.weapon.name',range=10000.,damage=150.,cooldown_duration=8.)
    mount=u['weapons']['weapons'][0];mount['weapon']=INSTALLATION
    # Launches forward through the existing three muzzle points; platform turns.
    u['ai']['attack_target_type_groups']=copy.deepcopy(w['attack_target_type_groups'])
    u['ai']['attack_target_type_groups_matching_weapon']=INSTALLATION
    u['abilities']=[{'abilities':['expanse11_no_shields']}]
    s=read(game/'entities/trader_gauss_defense_structure.unit_skin')
    stage=s['skin_stages'][0]
    stage['gui'].update(name=INSTALLATION+'.name',description=INSTALLATION+'.description')
    aliases=read(game/'entities/trader_long_range_cruiser.unit_skin')['skin_stages'][0]['effects']['effect_alias_bindings']
    old={a['alias_name']:a for a in stage['effects'].get('effect_alias_bindings',[])}
    old.update({a['alias_name']:a for a in aliases if 'medium_missile' in a['alias_name']})
    stage['effects']['effect_alias_bindings']=list(old.values())
    for ext,d in [('unit',u),('weapon',w),('unit_skin',s)]:write(out/'entities'/(INSTALLATION+'.'+ext),d)
    loc.update({INSTALLATION+'.name':'Orbital Missile Defense',INSTALLATION+'.weapon.name':'Defense missile battery',INSTALLATION+'.description':'Local defense installation. Two interceptable missiles per 8-second cycle, 150 damage each, 10,000 range. Requires the existing Javelis unlock. Uses TEC platform art. No empire-wide bonuses; cannot move between planets.'})
    write(out/'localized_text/en.localized_text',loc)
