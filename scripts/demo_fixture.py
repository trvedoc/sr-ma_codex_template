"""Create explicitly artificial data in an isolated project for tests/demo."""
from pathlib import Path
import csv
import json
import shutil


def create_demo(source, destination):
    source, destination = Path(source), Path(destination)
    if destination.exists():
        raise FileExistsError(f'Refusing to replace existing demo folder: {destination}')
    destination.mkdir(parents=True)
    schema = json.loads((source / 'data/schema.json').read_text())
    for path, headers in schema.items():
        target = destination / path
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('w', newline='', encoding='utf-8') as handle:
            csv.writer(handle).writerow(headers)
    for path in ('scripts', 'analysis/R', 'analysis/tests'):
        shutil.copytree(source / path, destination / path,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for path in ('data/schema.json', 'analysis/run.R', 'renv.lock'):
        if (source / path).is_file():
            (destination / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / path, destination / path)
    (destination / 'protocol/analysis-plan.md').write_text('Artificial demo: independent MD, FE model, z inference.\n')
    config = {
        'template_version':'1.0.0',
        'review':{'id':'demo','title':'DEMO ONLY: artificial data',
                  'question':'Test the template on artificial effect estimates.',
                  'type':'artificial_demo','registration_url':'','protocol_version':'demo-1'},
        'team':[{'id':'demo-reviewer','name':'Artificial test identity','role':'demo verifier'}],
        'analysis':{'enabled':True,'module':'pairwise_independent',
                    'plan_approved_by':'demo-reviewer','plan_approved_date':'2026-10-08'}
    }
    (destination / 'review.json').write_text(json.dumps(config, indent=2) + '\n')

    def write_rows(path, records):
        with (destination / path).open('w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=schema[path])
            writer.writeheader()
            for record in records:
                writer.writerow(record)

    (destination / 'search/strategies').mkdir(parents=True, exist_ok=True)
    (destination / 'search/exports').mkdir(parents=True, exist_ok=True)
    (destination / 'search/strategies/demo.txt').write_text('ARTIFICIAL TEST QUERY; no database was searched.\n')
    (destination / 'search/exports/demo.txt').write_text('ARTIFICIAL TEST EXPORT: two artificial records.\n')
    date, verifier = '2026-10-08', 'demo-reviewer'
    write_rows('search/search-log.csv', [{'search_id':'SEARCH1','database':'Artificial',
        'platform':'Artificial','search_date':date,'query_file':'search/strategies/demo.txt',
        'export_file':'search/exports/demo.txt','records_exported':'2','searcher':verifier}])
    write_rows('search/records.csv', [{'record_id':f'REC{i}','search_id':'SEARCH1',
        'title':f'Artificial report {i}'} for i in (1, 2)])
    write_rows('search/deduplication-map.csv', [{'record_id':f'REC{i}',
        'retained_record_id':f'REC{i}','decision':'retained','reason':'Artificial unique record',
        'reviewed_by':verifier,'reviewed_date':date} for i in (1, 2)])
    write_rows('screening/final-title-abstract.csv', [{'record_id':f'REC{i}',
        'decision':'include','resolved_by':verifier,'resolved_date':date} for i in (1, 2)])
    write_rows('studies/studies.csv', [{'study_id':f'STUDY{i}',
        'study_label':f'Artificial study {i}','design':'artificial'} for i in (1, 2)])
    write_rows('studies/reports.csv', [{'report_id':f'REPORT{i}','study_id':f'STUDY{i}',
        'record_id':f'REC{i}','reference':f'Artificial report {i}; not a real publication.',
        'availability_status':'available'} for i in (1, 2)])
    write_rows('screening/final-full-text.csv', [{'report_id':f'REPORT{i}',
        'decision':'include','resolved_by':verifier,'resolved_date':date} for i in (1, 2)])
    write_rows('analysis/syntheses.csv', [{'synthesis_id':'SYN1','outcome':'Artificial outcome',
        'comparison':'Artificial A vs B','timepoint':'Artificial endpoint','effect_measure':'MD',
        'analysis_scale':'identity','direction':'Positive means higher artificial outcome',
        'method':'FE','inference':'z','confidence_level':'95',
        'plan_location':'protocol/analysis-plan.md','approved_by':verifier,'approved_date':date}])
    extracted, effects = [], []
    for i, effect, variance in ((1, '0.2', '0.04'), (2, '0.6', '0.09')):
        for field, value in (('effect_value', effect), ('sampling_variance', variance)):
            extracted.append({'entry_id':f'ENTRY{i}_{field}','study_id':f'STUDY{i}',
                'report_id':f'REPORT{i}','outcome':'Artificial outcome','timepoint':'Artificial endpoint',
                'field':field,'value':value,'value_status':'reported','unit':'Artificial units',
                'source_location':'Artificial fixture','verification_status':'verified',
                'verified_by':verifier,'verified_date':date})
        effects.append({'effect_id':f'EFFECT{i}','study_id':f'STUDY{i}','report_id':f'REPORT{i}',
            'synthesis_id':'SYN1','effect_measure':'MD','analysis_scale':'identity',
            'effect_value':effect,'sampling_variance':variance,
            'input_entry_ids':f'ENTRY{i}_effect_value;ENTRY{i}_sampling_variance',
            'derivation':'Artificial inputs copied from the demo fixture; no real study.',
            'include':'true','verification_status':'verified','verified_by':verifier,'verified_date':date})
    write_rows('extraction/adjudicated.csv', extracted)
    write_rows('analysis/effects.csv', effects)
    (destination / 'DEMO_ONLY.md').write_text('All records, identities, decisions, and effect estimates here are artificial.\n')
    return destination
