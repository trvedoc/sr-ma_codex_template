"""Structural checks for an SR/MA project; does not verify scientific judgments."""
from pathlib import Path
import argparse
import csv
import datetime as dt
import json
import math
import sys


def validate_project(root, analysis_ready=False):
    root = Path(root).resolve()
    errors = []
    tables = {}
    try:
        schema = json.loads((root / 'data/schema.json').read_text(encoding='utf-8'))
        config = json.loads((root / 'review.json').read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        return [f'Cannot read project configuration/schema: {exc}']
    if not isinstance(schema, dict) or not isinstance(config, dict):
        return ['Project configuration and schema must be JSON objects.']
    if any(not isinstance(path, str) or not isinstance(fields, list) or
           not all(isinstance(field, str) for field in fields)
           for path, fields in schema.items()):
        return ['Schema must map relative filenames to lists of column names.']
    configured_analysis = config.get('analysis', {})
    if isinstance(configured_analysis, dict) and configured_analysis.get('enabled') is True:
        analysis_ready = True

    def issue(path, line, message):
        errors.append(f'{path}:{line}: {message}')

    for path, required in schema.items():
        try:
            with (root / path).open(newline='', encoding='utf-8-sig') as handle:
                reader = csv.DictReader(handle)
                headers = reader.fieldnames or []
                if len(headers) != len(set(headers)):
                    issue(path, 1, 'Duplicate column names.')
                missing = set(required) - set(headers)
                if missing:
                    issue(path, 1, f'Missing columns: {sorted(missing)}')
                rows = []
                for line, row in enumerate(reader, 2):
                    if None in row or any(value is None for value in row.values()):
                        issue(path, line, 'Row length does not match the header.')
                        continue
                    row = {key: value.strip() for key, value in row.items()}
                    if not any(row.values()):
                        continue
                    row['_line'] = line
                    rows.append(row)
                    for key, value in row.items():
                        if value and (key == 'date' or key.endswith('_date') or key in ('coverage_start', 'coverage_end')):
                            try:
                                if dt.date.fromisoformat(value).isoformat() != value:
                                    raise ValueError()
                            except ValueError:
                                issue(path, line, f'{key} must use YYYY-MM-DD.')
                tables[path] = rows
        except OSError as exc:
            issue(path, 1, str(exc))
            tables[path] = []
    if errors:
        return errors

    def rows(path):
        return tables.get(path, [])

    def require(path, row, fields):
        for field in fields:
            if not row.get(field, ''):
                issue(path, row['_line'], f'{field} is required.')

    def unique(path, fields):
        seen = set()
        for row in rows(path):
            require(path, row, fields)
            key = tuple(row.get(field, '') for field in fields)
            if key in seen:
                issue(path, row['_line'], f'Duplicate key {key}.')
            seen.add(key)

    keys = {
        'protocol/amendments.csv': ('amendment_id',),
        'search/search-log.csv': ('search_id',),
        'search/records.csv': ('record_id',),
        'search/deduplication-map.csv': ('record_id',),
        'screening/title-abstract.csv': ('record_id', 'reviewer_id'),
        'screening/final-title-abstract.csv': ('record_id',),
        'screening/full-text.csv': ('report_id', 'reviewer_id'),
        'screening/final-full-text.csv': ('report_id',),
        'studies/studies.csv': ('study_id',),
        'studies/reports.csv': ('report_id',),
        'extraction/reviewer-1.csv': ('entry_id',),
        'extraction/reviewer-2.csv': ('entry_id',),
        'extraction/adjudicated.csv': ('entry_id',),
        'risk-of-bias/assessments.csv': ('assessment_id',),
        'risk-of-bias/adjudicated.csv': ('assessment_id',),
        'certainty/assessments.csv': ('synthesis_id', 'domain', 'reviewer_id'),
        'analysis/syntheses.csv': ('synthesis_id',),
        'analysis/effects.csv': ('effect_id',),
        'reporting/prisma-counts.csv': ('item_id',),
    }
    for path, fields in keys.items():
        unique(path, fields)

    catalogs = {
        'search_id': {r['search_id'] for r in rows('search/search-log.csv')},
        'record_id': {r['record_id'] for r in rows('search/records.csv')},
        'study_id': {r['study_id'] for r in rows('studies/studies.csv')},
        'report_id': {r['report_id'] for r in rows('studies/reports.csv')},
        'synthesis_id': {r['synthesis_id'] for r in rows('analysis/syntheses.csv')},
    }
    owner = {'search_id': 'search/search-log.csv', 'record_id': 'search/records.csv',
             'study_id': 'studies/studies.csv', 'report_id': 'studies/reports.csv',
             'synthesis_id': 'analysis/syntheses.csv'}
    team = config.get('team', [])
    team_ids = set()
    if not isinstance(team, list):
        errors.append('review.json: team must be a list of human team-member objects.')
        team = []
    for member in team:
        if not isinstance(member, dict) or not all(member.get(k) for k in ('id', 'name', 'role')):
            errors.append('review.json: each team member needs id, name, and role.')
            continue
        if member['id'] in team_ids:
            errors.append(f'review.json: duplicate team ID {member["id"]}.')
        team_ids.add(member['id'])

    reports = {r['report_id']: r for r in rows('studies/reports.csv')}
    for path, content in tables.items():
        for row in content:
            for field, known in catalogs.items():
                if field in row and path != owner[field] and row[field] and row[field] not in known:
                    issue(path, row['_line'], f'Unknown {field}: {row[field]}')
            for field in ('reviewer_id', 'resolved_by', 'verified_by', 'approved_by', 'reviewed_by'):
                if row.get(field) and row[field] not in team_ids:
                    issue(path, row['_line'], f'{field} must identify a declared human team member.')
            if row.get('report_id') and row.get('study_id') and row['report_id'] in reports:
                if reports[row['report_id']]['study_id'] != row['study_id']:
                    issue(path, row['_line'], 'Report belongs to a different study.')

    def relative_file(path, row, field):
        value = row.get(field, '')
        if not value:
            return
        candidate = (root / value).resolve()
        if not candidate.is_relative_to(root) or not candidate.is_file():
            issue(path, row['_line'], f'{field} must reference an existing file inside the project.')

    for row in rows('search/search-log.csv'):
        path = 'search/search-log.csv'
        require(path, row, ('database', 'platform', 'search_date', 'query_file', 'export_file', 'records_exported', 'searcher'))
        for field in ('query_file', 'export_file'):
            relative_file(path, row, field)
        try:
            count = int(row['records_exported'])
            if count < 0 or str(count) != row['records_exported']:
                raise ValueError()
            observed = sum(r['search_id'] == row['search_id'] for r in rows('search/records.csv'))
            if observed != count:
                issue(path, row['_line'], f'Export count {count} differs from {observed} registered search records.')
        except ValueError:
            issue(path, row['_line'], 'records_exported must be a nonnegative integer.')
    for row in rows('search/records.csv'):
        require('search/records.csv', row, ('search_id', 'title'))
    for row in rows('studies/reports.csv'):
        require('studies/reports.csv', row, ('study_id', 'record_id', 'reference', 'availability_status'))
        if row['availability_status'] not in ('available', 'unavailable', 'pending'):
            issue('studies/reports.csv', row['_line'], 'Unknown availability_status.')

    mapping = {r['record_id']: r for r in rows('search/deduplication-map.csv')}
    for row in mapping.values():
        path = 'search/deduplication-map.csv'
        require(path, row, ('retained_record_id', 'decision', 'reason', 'reviewed_by', 'reviewed_date'))
        retained = row['retained_record_id']
        if retained not in catalogs['record_id']:
            issue(path, row['_line'], 'Unknown retained_record_id.')
        if row['decision'] == 'retained':
            if retained != row['record_id']:
                issue(path, row['_line'], 'A retained record must map to itself.')
        elif row['decision'] == 'duplicate':
            if retained == row['record_id'] or retained not in mapping or mapping[retained]['decision'] != 'retained':
                issue(path, row['_line'], 'Duplicate must map directly to a canonical retained record.')
        else:
            issue(path, row['_line'], 'decision must be retained or duplicate.')

    for path in ('screening/title-abstract.csv', 'screening/full-text.csv',
                 'screening/final-title-abstract.csv', 'screening/final-full-text.csv'):
        final = '/final-' in path
        for row in rows(path):
            require(path, row, ('decision', 'resolved_by', 'resolved_date') if final else ('reviewer_id', 'decision', 'decision_date'))
            allowed = ('include', 'exclude') if final else ('include', 'exclude', 'unclear')
            if row['decision'] not in allowed:
                issue(path, row['_line'], f'decision must be one of {allowed}.')
            if path == 'screening/final-full-text.csv' and row['decision'] == 'exclude':
                require(path, row, ('exclusion_reason',))
            if path == 'screening/final-title-abstract.csv':
                if row['record_id'] not in mapping or mapping[row['record_id']]['decision'] != 'retained':
                    issue(path, row['_line'], 'Final title/abstract decision must use a canonical retained record.')
    for row in rows('protocol/amendments.csv'):
        require('protocol/amendments.csv', row, ('date', 'section', 'previous_rule', 'new_rule', 'reason', 'approved_by'))

    for path in ('extraction/reviewer-1.csv', 'extraction/reviewer-2.csv', 'extraction/adjudicated.csv'):
        for row in rows(path):
            require(path, row, ('study_id', 'report_id', 'field', 'value_status'))
            if row['value_status'] not in ('reported', 'not_reported', 'unclear', 'not_applicable'):
                issue(path, row['_line'], 'Unknown value_status.')
            if row['value_status'] == 'reported':
                require(path, row, ('value', 'source_location'))
            if path != 'extraction/adjudicated.csv':
                require(path, row, ('reviewer_id', 'extracted_date'))
    for path in ('extraction/adjudicated.csv', 'risk-of-bias/adjudicated.csv'):
        for row in rows(path):
            if row['verification_status'] not in ('pending', 'verified'):
                issue(path, row['_line'], 'verification_status must be pending or verified.')
            if row['verification_status'] == 'verified':
                require(path, row, ('study_id', 'report_id', 'source_location', 'verified_by', 'verified_date'))
    for path in ('risk-of-bias/assessments.csv', 'risk-of-bias/adjudicated.csv'):
        for row in rows(path):
            require(path, row, ('study_id', 'report_id', 'tool', 'tool_version', 'domain', 'judgment', 'supporting_evidence'))
            if path.endswith('/assessments.csv'):
                require(path, row, ('reviewer_id', 'assessment_date'))
    for row in rows('certainty/assessments.csv'):
        require('certainty/assessments.csv', row, ('framework', 'domain', 'judgment', 'reason', 'reviewer_id', 'assessment_date'))

    scales = {'MD':'identity', 'SMD':'identity', 'RD':'identity', 'RR':'log', 'OR':'log', 'HR':'log', 'ZCOR':'fisher_z'}
    syntheses = {r['synthesis_id']: r for r in rows('analysis/syntheses.csv')}
    for row in syntheses.values():
        path = 'analysis/syntheses.csv'
        require(path, row, ('outcome', 'comparison', 'timepoint', 'effect_measure', 'analysis_scale', 'direction', 'method', 'inference', 'confidence_level', 'plan_location', 'approved_by', 'approved_date'))
        measure, scale = row['effect_measure'], row['analysis_scale']
        if measure not in set(scales) | {'GEN'} or scale not in ('identity', 'log', 'fisher_z'):
            issue(path, row['_line'], 'Unsupported measure or analysis scale; configure an appropriate module.')
        elif measure in scales and scale != scales[measure]:
            issue(path, row['_line'], 'Effect measure and analysis scale disagree.')
        if row['method'] not in ('EE', 'FE', 'REML', 'DL', 'PM'):
            issue(path, row['_line'], 'Unsupported model method.')
        if row['inference'] not in ('z', 't', 'knha'):
            issue(path, row['_line'], 'Unsupported inference method.')
        if row['inference'] == 'knha' and row['method'] in ('EE', 'FE'):
            issue(path, row['_line'], 'knha inference is reserved for random-effects models in this module.')
        try:
            level = float(row['confidence_level'])
            if not math.isfinite(level) or not 0 < level < 100:
                raise ValueError()
        except ValueError:
            issue(path, row['_line'], 'confidence_level must be between zero and 100.')

    entries = {r['entry_id']: r for r in rows('extraction/adjudicated.csv')}
    included_reports = {r['report_id'] for r in rows('screening/final-full-text.csv') if r['decision'] == 'include'}
    selected = []
    for row in rows('analysis/effects.csv'):
        path = 'analysis/effects.csv'
        require(path, row, ('study_id', 'report_id', 'synthesis_id', 'include', 'verification_status'))
        if row['include'] not in ('true', 'false'):
            issue(path, row['_line'], 'include must be true or false.')
        if row['verification_status'] not in ('pending', 'verified'):
            issue(path, row['_line'], 'verification_status must be pending or verified.')
        if row['include'] == 'false':
            require(path, row, ('exclusion_reason',))
            continue
        if row['include'] != 'true':
            continue
        selected.append(row)
        require(path, row, ('effect_measure', 'analysis_scale', 'effect_value', 'sampling_variance', 'input_entry_ids', 'derivation', 'verified_by', 'verified_date'))
        if row['verification_status'] != 'verified':
            issue(path, row['_line'], 'Included effect has not been verified.')
        if row['report_id'] not in included_reports:
            issue(path, row['_line'], 'Included effect needs a resolved included source report.')
        if row['report_id'] in reports and reports[row['report_id']]['availability_status'] != 'available':
            issue(path, row['_line'], 'Included effect source report must be available.')
        spec = syntheses.get(row['synthesis_id'])
        if spec and (row['effect_measure'], row['analysis_scale']) != (spec['effect_measure'], spec['analysis_scale']):
            issue(path, row['_line'], 'Effect measure/scale differs from its synthesis.')
        try:
            effect = float(row['effect_value'])
            variance = float(row['sampling_variance'])
            if not math.isfinite(effect) or not math.isfinite(variance) or variance <= 0:
                raise ValueError()
        except ValueError:
            issue(path, row['_line'], 'Effect and variance must be finite; variance must be positive.')
        entry_ids = row['input_entry_ids'].split(';') if row['input_entry_ids'] else []
        for entry_id in entry_ids:
            entry = entries.get(entry_id.strip())
            if not entry or entry['verification_status'] != 'verified' or entry['value_status'] != 'reported' or entry['study_id'] != row['study_id']:
                issue(path, row['_line'], f'Input entry {entry_id!r} must be a verified reported value from this study.')
        if len(entry_ids) != len(set(x.strip() for x in entry_ids)):
            issue(path, row['_line'], 'Repeated input entry IDs.')
    for row in rows('reporting/prisma-counts.csv'):
        require('reporting/prisma-counts.csv', row, ('label', 'count', 'unit', 'source', 'verified_by', 'verified_date'))
        try:
            if int(row['count']) < 0 or str(int(row['count'])) != row['count']:
                raise ValueError()
        except ValueError:
            issue('reporting/prisma-counts.csv', row['_line'], 'count must be a nonnegative integer.')

    analysis = config.get('analysis', {})
    if not isinstance(analysis, dict) or not isinstance(analysis.get('enabled'), bool):
        errors.append('review.json: analysis.enabled must be true or false.')
        analysis = {}
    if analysis_ready:
        review = config.get('review', {})
        if not isinstance(review, dict) or not all(review.get(k) for k in ('id', 'title', 'question', 'type', 'protocol_version')):
            errors.append('review.json: fill review id, title, question, type, and protocol_version.')
        if analysis.get('enabled') is not True or analysis.get('module') != 'pairwise_independent':
            errors.append('review.json: enable and configure pairwise_independent, or implement a different module.')
        if analysis.get('plan_approved_by') not in team_ids:
            errors.append('review.json: analysis plan needs a declared human approver.')
        try:
            value = analysis.get('plan_approved_date', '')
            if dt.date.fromisoformat(value).isoformat() != value:
                raise ValueError()
        except (TypeError, ValueError):
            errors.append('review.json: analysis plan needs an approval date in YYYY-MM-DD format.')
        if not syntheses or not selected:
            errors.append('Analysis needs synthesis definitions and verified included effects.')
        for synthesis_id in syntheses:
            group = [r for r in selected if r['synthesis_id'] == synthesis_id]
            study_ids = [r['study_id'] for r in group]
            if len(group) < 2:
                errors.append(f'{synthesis_id}: included module requires at least two studies.')
            if len(study_ids) != len(set(study_ids)):
                errors.append(f'{synthesis_id}: repeated study IDs imply dependent effects; use another module or an approved selection rule.')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--analysis-ready', action='store_true')
    args = parser.parse_args()
    errors = validate_project(args.root, args.analysis_ready)
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    mode = 'Configured analysis inputs' if args.analysis_ready else 'Project structure and populated rows'
    print(f'{mode} passed validation. This does not establish review completion or scientific validity.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
