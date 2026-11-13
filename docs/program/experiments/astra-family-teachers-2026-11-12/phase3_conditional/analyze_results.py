#!/usr/bin/env python3
"""Summarize captured phase3 evidence without selecting or modifying candidates."""
import argparse
import json
from pathlib import Path


def summarize(data):
    config=data['config']
    lines=['# Conditional passing results','',
           'This tool-assisted study followed phase 1. Three source seeds are the replicate units. Manual and fitted selections are action-type strata within an adaptive teacher, not randomized arms.','',
           'Ridge operations perform ordinary numerical optimization. Their success would not establish direct weight reading.','',
           '| Seed | Selection | Split | Left improvement % | Right improvement % | Contrast improvement % | Hazard error rise | Unchanged drift | Retention | Primary pass |',
           '|---|---|---|---:|---:|---:|---:|---:|---|---|']
    all_pass={}
    for row in data['results']:
        baseline=next(c for c in row['controls'] if c['name']=='no_edit')['metrics']
        variants={k:v for k,v in row['variants'].items()}
        variants.update({c['name']:c for c in row['controls'] if c['name']!='no_edit'})
        for name,v in variants.items():
            pass_both=True
            for split in ('test','test_shift'):
                b=baseline[split]; a=v['metrics'][split]
                gains=[1-a[k]/b[k] for k in ('left_active_mse','right_active_mse','paired_context_contrast_mse')]
                hazard=a['hazard_mse']-b['hazard_mse']
                retention=hazard<=max(config['hazard_absolute_budget'],config['hazard_relative_budget']*b['hazard_mse']) and a['unchanged_context_drift']<=config['low_drift_budget'] and a['frozen_equal']
                passed=retention and min(gains)>=config['primary_required_improvement']
                pass_both=pass_both and passed
                vals=' | '.join(f'{100*g:.3f}' for g in gains)
                lines.append(f'| {row["seed"]} | {name} | {split} | {vals} | {hazard:.7g} | {a["unchanged_context_drift"]:.7g} | {retention} | {passed} |')
            all_pass[name]=all_pass.get(name,0)+int(pass_both)
    lines.extend(['','Primary passes on both final distributions:',''])
    for name,count in all_pass.items():lines.append(f'- {name}: {count}/{len(data["results"])} source seeds.')
    lines.extend(['','## Shared crossing arena','','These secondary runs do not select candidates. An exact target controller is included to expose limits of the prescribed behavior.','',
                  '| Seed | Rollout | Controller | Collision pair-steps | Hazard cell-steps | Goal progress | Effort |','|---|---|---|---:|---:|---:|---:|'])
    for row in data['results']:
        for rollout in row['exploratory_colony']:
            for name in ('baseline','edited','oracle_target'):
                m=rollout[name]
                lines.append(f'| {row["seed"]} | {rollout["seed"]} | {name} | {m["collision_pair_steps"]} | {m["hazard_cell_steps"]} | {m["mean_goal_progress"]:.6g} | {m["mean_action_energy"]:.6g} |')
    return '\n'.join(lines)+'\n'


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path,default=Path(__file__).parent/'data'/'results.json');parser.add_argument('--output',type=Path,default=Path(__file__).parent/'RESULTS.md');args=parser.parse_args()
    args.output.write_text(summarize(json.loads(args.data.read_text())))
    print(args.output)
