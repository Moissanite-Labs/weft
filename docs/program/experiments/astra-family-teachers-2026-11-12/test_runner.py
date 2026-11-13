"""Offline request-boundary and append-only processing checks."""
import json
import tempfile
import unittest
from pathlib import Path
import run_experiment as runner


class RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exp = runner.lab.generate_experiment(17, train_steps=10)

    def test_packets_hide_holdout_and_blind_representation(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            for arm in runner.ARMS:
                path = runner.request(out, self.exp, arm, 1, [])
                packet = json.loads(runner.read(path)['input'])
                for key in ('test', 'test_shift', 'siblings', 'validation', 'train'):
                    self.assertNotIn(key, packet)
                if arm == 'behavior_only':
                    self.assertTrue(all('hidden' not in row for row in packet['examples']))
                    for name in runner.lab.SHAPES:
                        self.assertEqual(packet['cell'][name]['values'], 'withheld')

    def test_invalid_response_archived_and_next_round_issued(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            runner.write(out/'experiments/seed-17.json', self.exp)
            requests = runner.process(out)
            path = Path(requests[0])
            runner.write(path.with_suffix('.response.json'), {'response': {'output': []}})
            runner.process(out)
            result = runner.read(out/'candidates'/path.name)
            self.assertFalse(result['valid'])
            self.assertFalse(result['accepted'])
            self.assertTrue((out/'requests'/path.name.replace('round-1', 'round-2')).exists())
            with self.assertRaises(ValueError):
                runner.finish(out)

    def test_scramble_is_packet_only_and_preserves_tensor_marginals(self):
        import copy
        import numpy as np
        original = copy.deepcopy(self.exp)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            packet = json.loads(runner.read(runner.request(out,self.exp,'scrambled_weights',1,[]))['input'])
            self.assertEqual(packet['arm'],'weights_behavior')
            for name in runner.lab.SHAPES:
                self.assertEqual(sorted(np.asarray(packet['cell'][name]).ravel()),sorted(np.asarray(self.exp['source'][name]).ravel()))
            self.assertEqual(self.exp,original)
            self.assertEqual(sum(runner.CONFIG['rounds_by_arm'].values())*3,21)
            self.assertEqual(runner.CONFIG['rounds_by_arm']['scrambled_weights'],1)
            for key in ('test','test_shift','siblings','validation'):
                self.assertNotIn(key,packet)
            self.assertTrue((out/'scramble_private/seed-17.json').exists())

    def test_candidate_inputs_are_bound(self):
        for target in ('source', 'request', 'config'):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp)
                runner.write(out/'config.json', runner.CONFIG)
                runner.write(out/'experiments/seed-17.json', self.exp)
                req = Path(runner.process(out)[0])
                runner.write(req.with_suffix('.response.json'), {'response': {'output': []}})
                runner.process(out)
                if target == 'source':
                    value = runner.read(out/'experiments/seed-17.json')
                    value['source']['b2'][0] += .01
                    runner.write(out/'experiments/seed-17.json', value)
                elif target == 'request':
                    value = runner.read(req)
                    value['instructions'] += 'tampered'
                    runner.write(req,value)
                else:
                    value = dict(runner.CONFIG)
                    value['rounds'] = 99
                    runner.write(out/'config.json',value)
                with self.assertRaises(ValueError): runner.process(out)

    def test_replay_requires_existing_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'existing results'):
                runner.validate_replay(Path(tmp))

    def test_no_edit_fails_improvement_gate(self):
        result = runner.gate(self.exp['source'], self.exp['source'], self.exp['validation'])
        self.assertFalse(result['accepted'])
        self.assertEqual(result['low_urgency_drift_mse'], 0)

    def test_output_must_be_strict_json_data(self):
        for text in ('```json\n{}\n```', '{"hypothesis":"x","edits":[],"code":"print(1)"}'):
            envelope = {'response': {'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': text}]}]}}
            with self.assertRaises(ValueError): runner.extract_response(envelope)


if __name__ == '__main__': unittest.main()
