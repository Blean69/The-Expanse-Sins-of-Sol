"""Small shared offline package gate for separately frozen doctrine stages."""
from pathlib import Path
import json,shutil,zipfile
from validate_experiments import read,require,file_hashes,sha256,tree_hash,verify_zip,verify_pins
from build_polish import write
from update20_fleet import ROOT,GAME
from update11_validate import schema_check
SDK=GAME.parent/'Sins of a Solar Empire II - Mod Tools'

def registries(out):
    for kind in ['unit','unit_skin','weapon','ability','buff','action_data_source','unit_item','research_subject','player','npc_reward','exotic']:
        # Native overrides must not be re-registered in additive entity manifests.
        ids=sorted(p.stem for p in (out/'entities').glob('*.'+kind) if not (GAME/'entities'/p.name).exists())
        write(out/'entities'/f'{kind}.entity_manifest',{'ids':ids})

def package(base,out,edits,origins,readme,audit,art=None,package_existing=False,art_replacements=None, magazine_position_replacements=None):
    import jsonschema
    from amun06_validate_package import AmunResolver,check_action_values
    from build_combat03 import check_actions
    art=art or {};art_replacements=art_replacements or {};magazine_position_replacements=magazine_position_replacements or {};pins=verify_pins(ROOT,GAME,SDK)
    class DoctrineResolver(AmunResolver):
        def weapon(self,name,skins,source):
            data=read(self.resolve('entities/'+name+'.weapon',source))
            if data.get('weapon_type')!='planet_bombing':return super().weapon(name,skins,source)
            require(data['uniforms_target_filter_id'] in self.filters,'Unknown bombing target filter')
            require(data['acquire_target_logic']=='order_target_only','Automatic planetary attack')
            for skin in skins:
                for stage in skin['skin_stages']:
                    aliases={x['alias_name'] for x in stage.get('effects',{}).get('effect_alias_bindings',[])}
                    for k,v in data.get('effects',{}).items():
                        if k.endswith('_effect') and isinstance(v,str):require(v in aliases,'Unbound bombing effect '+v)
            return data
    require(base.is_dir() and base.with_suffix('.zip').is_file(),'Missing frozen predecessor')
    baseline={'zip_sha256':sha256(base.with_suffix('.zip')),'tree_sha256':tree_hash(file_hashes(base))}
    if not package_existing:
        require(not out.exists() and not out.with_suffix('.zip').exists(),'Existing candidate '+str(out))
        shutil.copytree(base,out,symlinks=True)
        for rel,src in art.items():
            if (out/rel).exists():
                require(rel in art_replacements and sha256(base/rel)==art_replacements[rel],'Unapproved art replacement '+rel)
            else:require(rel not in art_replacements,'Replacement missing predecessor '+rel)
            (out/rel).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out/rel)
        for rel,d in edits.items():write(out/rel,d)
        registries(out);shutil.copy2(readme,out/'PLAYTEST-README.md')
    before,after=file_hashes(base),file_hashes(out)
    require(set(before)<=set(after),'Deleted predecessor file')
    allowed=set(edits)|set(art)|{'PLAYTEST-README.md'}|{r for r in after if r.endswith('.entity_manifest')}
    require(all(r in allowed for r,h in after.items() if h!=before.get(r)),'Unexpected package drift')
    checks=[]
    for rel,d in edits.items():
        require(read(out/rel)==d,'Definition mismatch '+rel)
        source=Path(origins[rel]) if rel in origins else base/rel
        result=schema_check(out/rel,source if source.is_file() else None)
        if result:checks.append(result)
        if rel.startswith('uniforms/'):
            sn=Path(rel).stem.replace('_','-')+'-uniforms-schema.json';sp=SDK/'json_schemas'/sn
            if sp.exists():
                schema=read(sp)
                for k,v in d.items():
                    if k in schema['properties']:
                        # Keep the document resolver: nested uniform arrays use
                        # local $defs, lost when validating an isolated property.
                        validator=jsonschema.Draft202012Validator(schema)
                        errors=list(validator.descend(v,schema['properties'][k]))
                        if errors:raise errors[0]
                    else:
                        require(source.is_file() and read(source).get(k)==v,'Changed unknown uniform field '+rel+':'+k)
                        checks.append({'file':rel,'unchanged_installed_extension':k,'source':str(source),'source_sha256':sha256(source)})
    for rel,src in art.items():require(after[rel]==sha256(src),'Art drift')
    audio=[r for r in before if r.endswith(('.ogg','.sound'))]
    for rel in audio:require(after[rel]==before[rel],'Audio changed')
    for rel in before:
        if (rel.endswith('.weapon') and 'rail' in rel) or ('magazine' in rel) or ('torpedo' in rel and rel.endswith('.unit')):
            if rel in magazine_position_replacements:
                require(rel.endswith('.ability') and 'magazine' in rel,'Invalid geometry exception '+rel)
                require(before[rel]==magazine_position_replacements[rel],'Magazine predecessor drift '+rel)
                a,b=read(base/rel),read(out/rel)
                require('ability_positions' in a and 'ability_positions' in b,'Missing launch origins '+rel)
                a.pop('ability_positions');b.pop('ability_positions')
                require(a==b,'Magazine mechanics changed under geometry exception '+rel)
            else:require(after[rel]==before[rel],'Existing rail/magazine/projectile altered '+rel)
    # No incidental conventional shields, invalid disabled bursts or tag overflow.
    for p in (out/'entities').glob('expanse*.unit'):
        for level in read(p).get('health',{}).get('levels',[]):
            require(level.get('max_shield_points',0)==0,'Unplanned shield pool '+p.name)
            require('shield_burst_restore' not in level,'Disabled optional burst restored '+p.name)
    tags=read(GAME/'uniforms/weapon.uniforms')['weapon_tags']+read(out/'uniforms/weapon.uniforms')['weapon_tags']
    names=[x['name'] for x in tags];require(len(names)<=32 and len(names)==len(set(names)),'Weapon registry overflow/duplicates')
    tags=read(out/'uniforms/unit_tag.uniforms')['unit_tags'];require(len(tags)==len(set(x['name'] for x in tags)),'Duplicate unit tag')
    for p in (out/'entities').glob('*.entity_manifest'):
        ids=read(p)['ids'];require(len(ids)==len(set(ids)),'Duplicate entity registry')
        for ident in ids:require((out/'entities'/f'{ident}.{p.stem}').is_file(),'Missing registered entity')
    resolver=DoctrineResolver(out,GAME);actions=[]
    for rel in edits:
        if not rel.endswith('.unit'):continue
        ident=Path(rel).stem;u=resolver.unit(ident,'Doctrine integration')
        actions.append({'unit':ident,'actions':check_actions(out,resolver,ident),'values':check_action_values(out,GAME,resolver,u)})
    # Equipment-granted abilities are absent from a hull's ordinary ability bar.
    # Walk each changed ability too, so station/item actions cannot evade this
    # typed scalar/filter/reference check merely by being equipment-dependent.
    equipment_actions=[]
    for rel in edits:
        if rel.endswith('.ability'):
            equipment_actions.extend(check_action_values(out,GAME,resolver,{'abilities':[{'abilities':[Path(rel).stem]}]}))
    require(after['PLAYTEST-README.md']==sha256(readme),'README drift')
    report={'status':'PASS OFFLINE ONLY','schemas':checks,'actions':actions,'all_changed_ability_graphs':equipment_actions,'audio_files_preserved':len(audio),'pins':pins,'baseline':baseline,
        'magazine_position_only_replacements':magazine_position_replacements,
        'changed_files':sorted(r for r,h in after.items() if h!=before.get(r)),
        'runtime':{k:'NOT RUN' for k in ['load','opening_viability','menus','existing_and_new_research','colonization','bombardment','stacking','ownership','save_reload','multiplayer']}}
    write(audit/'validation.json',report)
    zp=out.with_suffix('.zip');require(not zp.exists(),'Existing package ZIP')
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file():
                require(not p.is_symlink(),'Symlink in package');zi=zipfile.ZipInfo(p.relative_to(out).as_posix(),(2026,9,14,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16;z.writestr(zi,p.read_bytes())
    summary={**verify_zip(zp,out),'installed':False,'runtime':'NOT RUN'}
    write(audit/'package-summary.json',summary);out.with_suffix('.sha256').write_text(summary['zip_sha256']+'  '+zp.name+'\n')
    return summary
