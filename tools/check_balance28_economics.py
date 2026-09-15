"""Static scope/acquisition checks; does not launch the game or build a package."""
import json
from pathlib import Path
import tempfile
import jsonschema
import balance28_economics as recipe

BASE = Path('/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update27_5_menu')
SDK = Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools/json_schemas')


def run(base=BASE):
    base = Path(base)
    edits, origins, report = recipe.changes(base)
    def old(uid):
        return json.loads((base / f'entities/{uid}.unit').read_text())
    def new(uid):
        return edits.get(f'entities/{uid}.unit', old(uid))
    t, r, h, n = map(new, (recipe.TRUMAN, recipe.RAPTOR, recipe.HEPH, recipe.NATHAN))
    assert t['build']['supply_cost'] == 400 and 'supply' not in t['build']
    assert t['build']['price'] == {'credits': 7680.0, 'metal': 3016.0, 'crystal': 1520.0}
    assert t['build']['build_time'] == 240.0
    assert t['build']['exotic_price'] == old(recipe.TRUMAN)['build']['exotic_price']
    assert t['health'] == old(recipe.TRUMAN)['health']
    assert t['levels'] == old(recipe.TRUMAN)['levels']
    assert r['health']['levels'] == [old(recipe.RAPTOR)['health']['levels'][0]]
    assert r['antimatter'] == {'max_antimatter': 225.0, 'antimatter_restore_rate': .75}
    assert 'levels' not in r and 'items' not in r and r['item_builds'] == []
    assert h['health']['levels'][0] == old(recipe.HEPH)['health']['levels'][0]
    assert len(h['health']['levels']) == len(h['levels']['levels']) == 10
    assert all('weapon_modifiers' not in row for row in h['levels']['levels'])
    assert h['items']['levels'][0]['max_ship_component_count'] == 4
    for uid in (recipe.TRUMAN, recipe.RAPTOR, recipe.HEPH, recipe.NATHAN):
        before, after = old(uid), new(uid)
        for key in ('weapons', 'physics', 'move', 'hyperspace', 'spatial', 'skin_groups'):
            assert before.get(key) == after.get(key), (uid, key)
        if uid != recipe.TRUMAN:
            for key in ('price', 'build_time', 'supply_cost', 'exotic_price'):
                assert before['build'].get(key) == after['build'].get(key), (uid, key)
    assert n['health'] == old(recipe.NATHAN)['health']
    assert n['colonize_ability'] == recipe.COLONY
    assert b'weapon.torpedo.0' in (base / 'meshes/expanse27_nathan_hale_hull.mesh').read_bytes()
    for player in report['players']:
        rel = f'entities/{player}.player'
        before, after = json.loads((base / rel).read_text()), edits[rel]
        assert before['buildable_units'] == after['buildable_units']
        assert before['structures'] == after['structures']
        assert after['research']['research_subjects'] == before['research']['research_subjects'] + [recipe.UNLOCK]
        assert before['research']['research_domains'] == after['research']['research_domains']
        assert next(x['unit_limit'] for x in after['unit_limits']['global'] if x['tag'] == 'super_capital_ship') == 2
        assert 'trader_colony_frigate' in after['buildable_units'] and recipe.NATHAN in after['buildable_units']
    assert 'super_capital_ship' in old('trader_loyalist_titan_factory_structure')['unit_factory']['build_kinds']
    assert {'capital_ship', 'cruiser'} <= set(old('trader_capital_ship_factory_structure')['unit_factory']['build_kinds'])
    assert all(Path(source).is_file() for source in origins.values())
    schema_count = 0
    for rel, data in edits.items():
        schema = SDK / (rel.rsplit('.', 1)[-1].replace('_', '-') + '-schema.json')
        if schema.exists():
            jsonschema.Draft7Validator(json.loads(schema.read_text())).validate(data)
            schema_count += 1
    # Reapplication fixture: symlink readonly baseline definitions, then replace only
    # the overlay files in a temporary directory. No output package is produced.
    with tempfile.TemporaryDirectory(prefix='balance28-economics-') as tmp:
        fixture = Path(tmp)
        for directory in ('entities', 'localized_text'):
            (fixture / directory).mkdir()
            for source in (base / directory).iterdir():
                (fixture / directory / source.name).symlink_to(source)
        for rel, data in edits.items():
            target = fixture / rel
            target.unlink(missing_ok=True)
            target.write_text(json.dumps(data))
        reapplied, _, _ = recipe.changes(fixture)
        for rel, data in reapplied.items():
            assert data == json.loads((fixture / rel).read_text()), ('non-idempotent', rel)
    report['observed_checks'] = {'schema_definitions': schema_count, 'idempotent_reapplication': True,
                                 'scope_and_acquisition_invariants': True, 'runtime_tested': False}
    return report


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
