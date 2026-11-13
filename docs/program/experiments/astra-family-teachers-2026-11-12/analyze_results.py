#!/usr/bin/env python3
"""Summarize saved outcomes only. Does not evaluate policies or call APIs."""
import argparse
import json
import math
from pathlib import Path

RATES={'input':10.,'cached_input':1.,'cache_write_input':12.5,'output':50.}

def read(p): return json.loads(p.read_text())
def relative(before,after):
    return (before-after)/before*100 if before else (0. if after==0 else None)
def mean(xs): return sum(xs)/len(xs) if xs else None
def fmt(x): return 'undefined' if x is None else f'{x:.6g}'

def outcome(base,edited):
    hazard=edited['hazard_mse']-base['hazard_mse']
    preserved=(hazard<=max(.02*base['hazard_mse'],.0002)+1e-12 and
               edited['unchanged_context_behavior_drift_mse']<=.0005+1e-12 and edited['frozen_core_equal'])
    improvement=relative(base['active_movement_mse'],edited['active_movement_mse'])
    return {'baseline_active_mse':base['active_movement_mse'],'edited_active_mse':edited['active_movement_mse'],
            'active_improvement_percent':improvement,'baseline_movement_mse':base['movement_mse'],
            'edited_movement_mse':edited['movement_mse'],'baseline_hazard_mse':base['hazard_mse'],
            'edited_hazard_mse':edited['hazard_mse'],'hazard_mse_drift':hazard,
            'low_urgency_prediction_drift_mse':edited['unchanged_context_behavior_drift_mse'],
            'frozen_core_equal':edited['frozen_core_equal'],'retention_pass':bool(preserved),
            'five_percent_and_retention':bool(improvement is not None and improvement>=5 and preserved)}

def summarize(data,out):
    rows=[]; transfers=[]; randoms=[]; rollouts=[]; controls=[]
    for result in data['results']:
        base=next(c for c in result['controls'] if c['name']=='no_edit')
        identity={'seed':result['seed'],'arm':result['arm']}
        for split in ('test','test_shift'):
            rows.append({**identity,'split':split,'selected_round':result['selected_round'],
                         **outcome(base['metrics'][split],result['source']['metrics'][split])})
            sibling_rows=[]
            for sibling in result['siblings']:
                for alignment in ('aligned','raw'):
                    variants=sibling['variants']
                    row={**identity,'sibling':sibling['id'],'alignment':alignment,'split':split,
                         **outcome(variants['no_edit']['metrics'][split],variants[alignment]['metrics'][split])}
                    transfers.append(row); sibling_rows.append(row)
            for control in result['controls']:
                controls.append({**identity,'split':split,'control':control['name'],
                                 **outcome(base['metrics'][split],control['metrics'][split])})
            draws=result['random_distribution']['draws']
            teacher=result['source']['metrics'][split]['active_movement_mse']
            scores=[d['metrics'][split]['active_movement_mse'] for d in draws]
            less=sum(v<teacher and not math.isclose(v,teacher,rel_tol=1e-12,abs_tol=1e-15) for v in scores); ties=sum(math.isclose(v,teacher,rel_tol=1e-12,abs_tol=1e-15) for v in scores)
            randoms.append({**identity,'split':split,'draws':len(scores),'random_mean_active_mse':mean(scores),
                            'teacher_active_mse':teacher,'random_strictly_lower_count':less,'ties':ties,
                            'teacher_error_midrank_percentile':100*(less+.5*ties)/len(scores) if scores else None,
                            'interpretation':'Lower percentile means lower error; unselected reference, not a formal p value.'})
        for variant in ('no_edit','edited_aligned','edited_raw'):
            available=[x[variant] for x in result['exploratory_rollout'] if variant in x]
            rollouts.append({**identity,'variant':variant,'rollout_seeds':len(available),
                             **{key:mean([v[key] for v in available]) for key in ('collision_pair_steps','hazard_cell_steps','mean_progress_per_step','mean_action_energy')}})
    counts={'valid':0,'invalid':0,'accepted':0,'valid_rejected':0,'selected_no_edit':sum(r['selected_round'] is None for r in data['results'])}
    failures=[]
    for path in sorted((out/'candidates').glob('*.json')):
        c=read(path)
        counts['valid' if c['valid'] else 'invalid']+=1
        if c['accepted']: counts['accepted']+=1
        elif c['valid']: counts['valid_rejected']+=1
        if not c['valid']: failures.append({'file':str(path.relative_to(out)),'error':c.get('error')})
    usage={'input_tokens':0,'cached_input_tokens':0,'cache_write_input_tokens':0,'output_tokens':0,'response_files':0,'estimated_usd':0.,'rates_per_million':RATES,'invoice':False}
    # Includes calibration and transport-failure records wherever saved under artifact root.
    for path in sorted(out.rglob('*.response.json')):
        record=read(path); response=record.get('response',{}); u=response.get('usage') or {}
        if record.get('error') or not response: failures.append({'file':str(path.relative_to(out)),'error':record.get('error', 'missing response')})
        usage['response_files']+=1
        input_tokens=u.get('input_tokens',0); details=u.get('input_tokens_details') or {}
        cached=details.get('cached_tokens',0); writes=details.get('cache_write_tokens',details.get('cache_creation_tokens',0))
        output=u.get('output_tokens',0)
        usage['input_tokens']+=input_tokens; usage['cached_input_tokens']+=cached
        usage['cache_write_input_tokens']+=writes; usage['output_tokens']+=output
        usage['estimated_usd']+=(max(0,input_tokens-cached-writes)*10+cached*1+writes*12.5+output*50)/1e6
    families=[]
    for seed in sorted({r['seed'] for r in transfers}):
        for arm in sorted({r['arm'] for r in transfers}):
            for split in ('test','test_shift'):
                for alignment in ('aligned','raw'):
                    group=[r for r in transfers if (r['seed'],r['arm'],r['split'],r['alignment'])==(seed,arm,split,alignment)]
                    if group: families.append({'seed':seed,'arm':arm,'split':split,'alignment':alignment,'siblings':len(group),
                                               'mean_baseline_active_mse':mean([r['baseline_active_mse'] for r in group]),
                                               'mean_edited_active_mse':mean([r['edited_active_mse'] for r in group]),
                                               'mean_active_improvement_percent':mean([r['active_improvement_percent'] for r in group if r['active_improvement_percent'] is not None]),
                                               'retention_pass_count':sum(r['retention_pass'] for r in group)})
    return {'source':rows,'family_transfer':families,'siblings':transfers,'controls':controls,'random_reference':randoms,
            'rollout_family_means':rollouts,'paired_round1':data.get('paired_round1',[]),'counts':counts,'usage':usage,'failures':failures}


def markdown(s):
    lines=['# Astra family teachers results','',
           'Three source seeds are the replicate units. Siblings are correlated family members. These results do not support a population significance claim.', '',
           'The weight-visible condition supplies both numerical matrices and hidden activations. This comparison cannot isolate the contribution of matrices from activations. Scrambled values form a contradictory-evidence control, not a decisive mechanism test.', '',
           '## Source outcomes','',
           '| Seed | Arm | Split | Active baseline | Active edited | Improvement % | Movement edited | Hazard drift | Low-urgency drift | Retention | ≥5% + retention |',
           '|---|---|---|---:|---:|---:|---:|---:|---:|---|---|']
    for r in s['source']:
        lines.append('| '+' | '.join(map(str,[r['seed'],r['arm'],r['split'],fmt(r['baseline_active_mse']),fmt(r['edited_active_mse']),fmt(r['active_improvement_percent']),fmt(r['edited_movement_mse']),fmt(r['hazard_mse_drift']),fmt(r['low_urgency_prediction_drift_mse']),r['retention_pass'],r['five_percent_and_retention']]))+' |')
    for arm in sorted({r['arm'] for r in s['source']}):
        for split in ('test','test_shift'):
            rows=[r for r in s['source'] if r['arm']==arm and r['split']==split]
            lines.extend(['',f"{arm}, {split}: {sum(r['five_percent_and_retention'] for r in rows)}/{len(rows)} source seeds meet the 5% improvement and retention rule."])
    lines+=['','## Family transfer','','| Seed | Arm | Split | Alignment | Mean baseline active | Mean edited active | Mean improvement % | Retention count |','|---|---|---|---|---:|---:|---:|---:|']
    for r in s['family_transfer']:
        lines.append(f"| {r['seed']} | {r['arm']} | {r['split']} | {r['alignment']} | {fmt(r['mean_baseline_active_mse'])} | {fmt(r['mean_edited_active_mse'])} | {fmt(r['mean_active_improvement_percent'])} | {r['retention_pass_count']}/{r['siblings']} |")
    lines+=['','## Per-sibling outcomes','','| Seed | Arm | Sibling | Split | Alignment | Active baseline | Active edited | Improvement % | Retention |','|---|---|---|---|---|---:|---:|---:|---|']
    for r in s['siblings']:
        lines.append(f"| {r['seed']} | {r['arm']} | {r['sibling']} | {r['split']} | {r['alignment']} | {fmt(r['baseline_active_mse'])} | {fmt(r['edited_active_mse'])} | {fmt(r['active_improvement_percent'])} | {r['retention_pass']} |")
    lines+=['','## Controls and interpretation','','Local search has three candidate evaluations and the same selection gate. Tokens, time, information and computation are not matched. The gradient comparator is a separate optimization diagnostic. Random directions match selected support and norm. All 32 remain unselected. Their midrank percentiles count ties and are descriptive, not formal p values.\n\nFull control values and the true-versus-scrambled round-one pair are in summary.json.','',
            '## Shared-arena rollout means','','Three fixed rollout seeds are averaged within each source family. These exploratory dynamics do not establish that static imitation targets are optimal.','',
            '| Seed | Arm | Variant | Collisions | Hazard steps | Progress | Energy |','|---|---|---|---:|---:|---:|---:|']
    for r in s['rollout_family_means']:
        lines.append(f"| {r['seed']} | {r['arm']} | {r['variant']} | {fmt(r['collision_pair_steps'])} | {fmt(r['hazard_cell_steps'])} | {fmt(r['mean_progress_per_step'])} | {fmt(r['mean_action_energy'])} |")
    lines+=['','## Control outcomes','','| Seed | Arm | Split | Control | Active edited | Improvement % | Retention |','|---|---|---|---|---:|---:|---|']
    for r in s['controls']:
        lines.append(f"| {r['seed']} | {r['arm']} | {r['split']} | {r['control']} | {fmt(r['edited_active_mse'])} | {fmt(r['active_improvement_percent'])} | {r['retention_pass']} |")
    lines+=['','| Seed | Arm | Split | Random mean active | Teacher error midrank % | Ties |','|---|---|---|---:|---:|---:|']
    for r in s['random_reference']:
        lines.append(f"| {r['seed']} | {r['arm']} | {r['split']} | {fmt(r['random_mean_active_mse'])} | {fmt(r['teacher_error_midrank_percentile'])} | {r['ties']} |")
    lines+=['','## First-round true and scrambled pairs','','These rows compare round one directly. Best-of-three choices do not enter this comparison.','', '| Seed | Condition | Valid | Accepted | Split | Active MSE | Hazard MSE |','|---|---|---|---|---|---:|---:|']
    for pair in s['paired_round1']:
        for arm, value in pair['arms'].items():
            for split in ('test','test_shift'):
                m=value['metrics'][split];c=value['candidate']
                lines.append(f"| {pair['seed']} | {arm} | {c.get('valid')} | {c.get('accepted')} | {split} | {fmt(m['active_movement_mse'])} | {fmt(m['hazard_mse'])} |")
    lines+=['','## Capture and usage','',f"Candidate counts: {json.dumps(s['counts'],sort_keys=True)}.",'',
            f"Estimated API cost: ${s['usage']['estimated_usd']:.6f}. This uses saved token usage at $10/M ordinary input, $1/M cached input, $12.50/M cache-write input and $50/M output. It includes calibration responses saved beneath the artifact directory. This is an estimate, not an invoice. Coding-agent token usage is unavailable.",'',
            f"Candidate/response-pattern failures: {len(s['failures'])}. The earlier TLS failure is archived separately under data/transport_failures and does not match the response-file suffix counted here. Details and raw token counts are in summary.json.",'']
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    summary=summarize(read(a.out/'results.json'),a.out)
    (a.out/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    (a.out.parent/'RESULTS.md').write_text(markdown(summary))
    print(a.out/'summary.json')

if __name__=='__main__': main()
