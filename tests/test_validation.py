from pathlib import Path
import csv
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from demo_fixture import create_demo
from validate_project import validate_project


class ProjectValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = create_demo(ROOT, Path(self.temporary.name) / 'project')

    def tearDown(self):
        self.temporary.cleanup()

    def mutate(self, path, operation):
        target = self.root / path
        with target.open(newline='') as handle:
            reader = csv.DictReader(handle)
            fields, records = reader.fieldnames, list(reader)
        operation(records)
        with target.open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(records)

    def test_valid_artificial_project(self):
        self.assertEqual(validate_project(self.root, analysis_ready=True), [])

    def test_empty_starter_is_valid_but_not_analysis_ready(self):
        schema = json.loads((self.root / 'data/schema.json').read_text())
        for path, fields in schema.items():
            with (self.root / path).open('w', newline='') as handle:
                csv.writer(handle).writerow(fields)
        config = json.loads((self.root / 'review.json').read_text())
        config['analysis']['enabled'] = False
        config['analysis']['module'] = 'unconfigured'
        (self.root / 'review.json').write_text(json.dumps(config))
        self.assertEqual(validate_project(self.root), [])
        self.assertTrue(validate_project(self.root, analysis_ready=True))

    def test_dependent_effects_rejected(self):
        def duplicate(records):
            row = dict(records[0])
            row['effect_id'] = 'EXTRA_EFFECT'
            records.append(row)
        self.mutate('analysis/effects.csv', duplicate)
        self.assertTrue(any('dependent effects' in error for error in validate_project(self.root, True)))

    def test_unverified_effect_rejected(self):
        self.mutate('analysis/effects.csv', lambda r: r[0].update(verification_status='pending'))
        self.assertTrue(any('not been verified' in error for error in validate_project(self.root, True)))

    def test_unverified_source_entry_rejected(self):
        self.mutate('extraction/adjudicated.csv', lambda r: r[0].update(verification_status='pending'))
        self.assertTrue(any('verified reported value' in error for error in validate_project(self.root, True)))

    def test_measure_scale_mismatch_rejected(self):
        self.mutate('analysis/effects.csv', lambda r: r[0].update(analysis_scale='log'))
        self.assertTrue(any('differs from its synthesis' in error for error in validate_project(self.root, True)))

    def test_invalid_variance_rejected(self):
        for value in ('0', '-1', 'NaN', 'inf', ''):
            with self.subTest(value=value):
                self.mutate('analysis/effects.csv', lambda r: r[0].update(sampling_variance=value))
                self.assertTrue(any('variance' in error for error in validate_project(self.root, True)))

    def test_unknown_study_rejected(self):
        self.mutate('analysis/effects.csv', lambda r: r[0].update(study_id='UNKNOWN'))
        self.assertTrue(any('Unknown study_id' in error for error in validate_project(self.root, True)))

    def test_excluded_report_rejected(self):
        self.mutate('screening/final-full-text.csv', lambda r: r[0].update(decision='exclude', exclusion_reason='Artificial exclusion'))
        self.assertTrue(any('included source report' in error for error in validate_project(self.root, True)))

    def test_undeclared_verifier_rejected(self):
        self.mutate('analysis/effects.csv', lambda r: r[0].update(verified_by='UNKNOWN'))
        self.assertTrue(any('declared human' in error for error in validate_project(self.root, True)))

    def test_duplicate_record_chain_rejected(self):
        self.mutate('search/deduplication-map.csv', lambda r: r[0].update(decision='duplicate'))
        self.assertTrue(any('canonical retained record' in error for error in validate_project(self.root)))

    def test_export_count_mismatch_rejected(self):
        self.mutate('search/search-log.csv', lambda r: r[0].update(records_exported='3'))
        self.assertTrue(any('differs from' in error for error in validate_project(self.root)))

    def test_blank_reported_value_rejected(self):
        self.mutate('extraction/adjudicated.csv', lambda r: r[0].update(value=''))
        self.assertTrue(any('value is required' in error for error in validate_project(self.root)))

    def test_csv_header_and_row_length_rejected(self):
        (self.root / 'analysis/effects.csv').write_text('effect_id,effect_id\nX,X,EXTRA\n')
        self.assertTrue(validate_project(self.root))

    def test_enabled_analysis_checked_by_default(self):
        self.mutate('analysis/effects.csv', lambda r: r[0].update(include='false', exclusion_reason='Artificial exclusion'))
        self.assertTrue(any('at least two' in error for error in validate_project(self.root)))

    def test_nonobject_configuration_rejected(self):
        (self.root / 'review.json').write_text('[]')
        self.assertTrue(any('JSON objects' in error for error in validate_project(self.root)))


if __name__ == '__main__':
    unittest.main()
