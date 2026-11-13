"""Deterministic, data-only family policy editing laboratory. No API access."""
from __future__ import annotations
import copy
import hashlib
import json
import math
from pathlib import Path
import numpy as np

VERSION = 'family-policy-v1'
SHAPES = {'w1': (10, 8), 'b1': (10,), 'w2': (3, 10), 'b2': (3,)}
MAX_DELTA = 0.75
MAX_NORM = 2.0
MAX_EDITS = 100


def predict(cell, x, hidden=False):
    x = np.asarray(x, dtype=float)
    h = np.tanh(x @ np.asarray(cell['w1']).T + cell['b1'])
    y = np.tanh(h @ np.asarray(cell['w2']).T + cell['b2'])
    return (y, h) if hidden else y


def make_dataset(seed, n=256, shift=False):
    """Independent observation draws; shift changes density, not target mechanism."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(-1, 1, (n, 8))
    # goal bearing, obstacle vector, neighbor vector, urgency, sensor intensity.
    if shift:
        x[:, 2:6] = np.sign(x[:, 2:6]) * np.sqrt(np.abs(x[:, 2:6]))
    goal = x[:, :2]
    avoidance = 0.65*x[:, 2:4] + 0.35*x[:, 4:6]
    urgency = np.maximum(x[:, 6:7], 0)
    intensity = (x[:, 7:8]+1)/2
    hazard = np.tanh(0.8*np.sum(x[:, 2:4]*x[:, 4:6], axis=1) + 0.6*x[:, 7])
    old_move = np.tanh(1.15*goal - 0.25*avoidance)
    new_move = np.tanh(1.15*goal - (0.25 + 1.25*urgency*intensity)*avoidance)
    return {'id': f'{seed}:{n}:{int(shift)}', 'x': x.tolist(),
            'base_y': np.column_stack((old_move, hazard)).tolist(),
            'y': np.column_stack((new_move, hazard)).tolist()}


def evaluate(cell, dataset):
    x, y = np.asarray(dataset['x']), np.asarray(dataset['y'])
    pred = predict(cell, x)
    move = np.mean((pred[:, :2]-y[:, :2])**2, axis=1)
    secondary = float(np.mean((pred[:, 2]-y[:, 2])**2))
    preserve = x[:, 6] <= 0
    active = x[:, 6] > 0.35
    target = float(np.mean(move))
    preserved = float(np.mean(move[preserve])) if np.any(preserve) else 0.0
    return {'loss': target + 0.5*secondary + preserved,
            'movement_mse': target, 'active_movement_mse': float(np.mean(move[active])) if np.any(active) else 0.,
            'hazard_mse': secondary, 'preserved_movement_mse': preserved,
            'n': len(x)}


def _train(cell, dataset, steps, lr, target='y', frozen=True):
    """Gradient baseline only; never called by apply_patch or teacher_packet."""
    c = copy.deepcopy(cell)
    a = {k: np.array(c[k], dtype=float) for k in SHAPES}
    x, y = np.asarray(dataset['x']), np.asarray(dataset[target])
    sample = np.ones_like(y)
    sample[:, 2] = 0.5
    sample[x[:, 6] <= 0, :2] += 1.0
    first, second = {k: np.zeros_like(v) for k,v in a.items()}, {k: np.zeros_like(v) for k,v in a.items()}
    for t in range(1, steps+1):
        h = np.tanh(x @ a['w1'].T+a['b1'])
        out = np.tanh(h @ a['w2'].T+a['b2'])
        d = (out-y)*sample*(1-out*out)/len(x)
        dh = (d @ a['w2'])*(1-h*h)
        g = {'w2': d.T @ h, 'b2': d.sum(0), 'w1': dh.T @ x, 'b1': dh.sum(0)}
        if frozen:
            g['w1'][:4] = 0
            g['b1'][:4] = 0
        for k in a:
            first[k] = .9*first[k]+.1*g[k]
            second[k] = .999*second[k]+.001*g[k]**2
            a[k] -= lr*(first[k]/(1-.9**t))/(np.sqrt(second[k]/(1-.999**t))+1e-8)
    c.update({k:v.tolist() for k,v in a.items()})
    return c


def generate_experiment(seed=17, sibling_count=4, train_steps=900):
    rng = np.random.default_rng(seed)
    source = {'version': VERSION, 'id': f'family-{seed}:source', 'unit_ids': list(range(10))}
    source.update({k: (rng.normal(0,.35,shape) if k.startswith('w') else np.zeros(shape)).tolist() for k,shape in SHAPES.items()})
    source = _train(source, make_dataset(seed+1000, 1536), train_steps, .015, 'base_y', False)
    siblings = []
    for i in range(sibling_count):
        c = copy.deepcopy(source)
        # Preserve frozen/plastic partition; permutation is exact before mild drift.
        order = np.r_[rng.permutation(4), 4+rng.permutation(6)]
        c['unit_ids'] = order.tolist()
        c['w1'] = (np.asarray(source['w1'])[order] + rng.normal(0,.008, (10,8))).tolist()
        c['b1'] = (np.asarray(source['b1'])[order] + rng.normal(0,.008, 10)).tolist()
        c['w2'] = (np.asarray(source['w2'])[:,order] + rng.normal(0,.008, (3,10))).tolist()
        c['id'] = f'family-{seed}:sibling-{i}'
        siblings.append(c)
    return {'version': VERSION, 'seed': seed, 'source': source, 'siblings': siblings,
            'train': make_dataset(seed+2000,96), 'validation': make_dataset(seed+3000,256),
            'test': make_dataset(seed+4000,1024), 'test_shift': make_dataset(seed+5000,1024,True)}


def editable_coordinates():
    return [(k, list(idx)) for k,shape in SHAPES.items() for idx in np.ndindex(shape)
            if not (k in ('w1','b1') and idx[0]<4)]


def apply_patch(cell, patch):
    """Atomic strict sparse delta application. No arbitrary code or weight aliases."""
    if not isinstance(patch, dict) or set(patch) != {'edits'} or not isinstance(patch['edits'],list):
        raise ValueError('patch must contain only edits list')
    if len(patch['edits']) > MAX_EDITS:
        raise ValueError('too many edits')
    allowed = {(k,tuple(i)) for k,i in editable_coordinates()}
    seen, squared = set(), 0.
    c = copy.deepcopy(cell)
    arrays = {k:np.array(c[k], dtype=float) for k in SHAPES}
    for e in patch['edits']:
        if not isinstance(e,dict) or set(e) != {'tensor','index','delta'}:
            raise ValueError('each edit needs tensor, index, delta')
        if not isinstance(e['index'],list) or not all(type(i) is int for i in e['index']):
            raise ValueError('index must be integer list')
        key = (e['tensor'],tuple(e['index']))
        if key not in allowed or key in seen:
            raise ValueError('frozen, invalid, or duplicate coordinate')
        if type(e['delta']) not in (int,float) or not math.isfinite(e['delta']) or abs(e['delta'])>MAX_DELTA:
            raise ValueError('nonfinite or out-of-bound delta')
        seen.add(key)
        squared += e['delta']**2
        arrays[key[0]][key[1]] += e['delta']
    if squared > MAX_NORM**2+1e-12:
        raise ValueError('patch exceeds L2 bound')
    c.update({k:v.tolist() for k,v in arrays.items()})
    return c


def transfer_patch(patch, source, sibling, aligned=True):
    result = copy.deepcopy(patch)
    if aligned:
        mapping = {i:sibling['unit_ids'].index(uid) for i,uid in enumerate(source['unit_ids'])}
        for edit in result['edits']:
            if edit['tensor'] in ('w1','b1'):
                edit['index'][0] = mapping[edit['index'][0]]
            elif edit['tensor']=='w2':
                edit['index'][1] = mapping[edit['index'][1]]
    apply_patch(sibling,result)
    return result


def teacher_packet(cell, train, validation=None, examples=32, visibility="weights"):
    # Explicit arguments make it impossible to accidentally serialize an experiment's test.
    x = np.asarray(train['x'])[:examples]
    pred,h = predict(cell,x,True)
    if visibility not in ('weights','behavior'):
        raise ValueError('visibility must be weights or behavior')
    packet = {'version': VERSION, 'task': 'Increase avoidance of obstacle and neighbor vectors when urgency and sensor intensity are high. Preserve goal following when urgency <= 0 and preserve hazard estimate.',
            'inputs': ['goal_x','goal_y','obstacle_x','obstacle_y','neighbor_x','neighbor_y','urgency','sensor_intensity'],
            'target_equations': 'a=.65*x[2:4]+.35*x[4:6]; u=max(x[6],0); s=(x[7]+1)/2; movement=tanh(1.15*x[0:2]-(.25+1.25*u*s)*a); hazard=tanh(.8*dot(x[2:4],x[4:6])+.6*x[7]). Base learned movement used .25*a. No supplied gradient.',
            'outputs': ['move_x','move_y','hazard'], 'architecture': 'h=tanh(x @ w1.T+b1); y=tanh(h @ w2.T+b2)',
            'cell':copy.deepcopy(cell), 'limits': {'max_edits':MAX_EDITS,'max_abs_delta':MAX_DELTA,'max_l2_delta':MAX_NORM,'frozen':'w1 rows 0..3 and b1 indices 0..3'},
            'patch_schema': {'edits':[{'tensor':'w2','index':[0,4],'delta':0.01}]},
            'examples': [{'x':a.tolist(),'target':b,'prediction':p.tolist(),'hidden':z.tolist()} for a,b,p,z in zip(x,train['y'],pred,h)],
            'train_metrics':evaluate(cell,train), 'validation_metrics':evaluate(cell,validation) if validation else None}
    packet['tensor_shapes'] = {k:list(v) for k,v in SHAPES.items()}
    packet['visibility'] = visibility
    if visibility == 'behavior':
        del packet['cell']
        for example in packet['examples']:
            del example['hidden']
    return packet


def random_patch(seed, norm, support=None):
    rng = np.random.default_rng(seed)
    coords = editable_coordinates() if support is None else [(e['tensor'],e['index']) for e in support['edits']]
    if not coords or norm==0:
        return {'edits':[]}
    if norm<0 or norm>MAX_NORM:
        raise ValueError('invalid norm')
    # Same support matching removes sparsity/coordinate-selection confound.
    if norm > MAX_DELTA*math.sqrt(len(coords))+1e-12:
        raise ValueError('norm infeasible on support')
    v = rng.normal(size=len(coords))
    low, high = 0., 1.
    while np.linalg.norm(np.clip(v*high,-MAX_DELTA,MAX_DELTA)) < norm-1e-14:
        high *= 2
    for _ in range(100):
        mid=(low+high)/2
        if np.linalg.norm(np.clip(v*mid,-MAX_DELTA,MAX_DELTA)) < norm:
            low=mid
        else:
            high=mid
    v=np.clip(v*high,-MAX_DELTA,MAX_DELTA)
    return {'edits':[{'tensor':k,'index':i,'delta':float(d)} for (k,i),d in zip(coords,v)]}


def patch_norm(patch):
    return math.sqrt(sum(e['delta']**2 for e in patch['edits']))


def local_evolution(cell, validation, proposals=8, seed=0, norm=.4):
    """Same number of scored candidate proposals; independent source-relative edits."""
    best, score = {'edits':[]}, evaluate(cell,validation)['loss']
    trace = []
    for i in range(proposals):
        patch = random_patch(seed+i,norm)
        loss = evaluate(apply_patch(cell,patch),validation)['loss']
        trace.append({'proposal':i,'validation_loss':loss,'patch':patch})
        if loss<score:
            best,score = patch,loss
    return {'patch':best,'validation_loss':score,'trace':trace,'candidate_evaluations':proposals}


def gradient_diagnostic(cell, train, steps=100):
    """Unlimited-delta gradient comparator; not budget matched and not a teacher arm."""
    return _train(cell,train,steps,.005)



def rollout(cells, seed=701, steps=160):
    """Exploratory closed-loop shared torus. No teacher present during inference.

    Attraction to a shared moving resource competes with a hazard and peers.
    These observations are outside the iid training process; no claim that the
    prescribed static target is optimal for this dynamical environment.
    """
    if len(cells)<2:
        raise ValueError('rollout requires at least two cells')
    rng=np.random.default_rng(seed)
    pos=rng.uniform(-1,1,(len(cells),2))
    initial=pos.copy()
    collisions=hazard_events=0
    progress=effort=0.
    hazard=np.array([.15,-.1])
    def wrap(a):
        return (a+1)%2-1
    for t in range(steps):
        goal=np.array([.65*np.cos(t*.018),.65*np.sin(t*.018)])
        commands=[]
        old_distance=np.linalg.norm(wrap(goal-pos),axis=1)
        for i,c in enumerate(cells):
            toward=wrap(goal-pos[i])
            toward_hazard=wrap(hazard-pos[i])
            relatives=wrap(pos-pos[i])
            distances=np.linalg.norm(relatives,axis=1)
            distances[i]=np.inf
            nearest=int(np.argmin(distances))
            hd=np.linalg.norm(toward_hazard)
            obstacle=toward_hazard/max(hd,.05)*np.exp(-hd*3)
            neighbor=relatives[nearest]/max(distances[nearest],.05)*np.exp(-distances[nearest]*3)
            intensity=2*np.exp(-min(hd,distances[nearest])*3)-1
            x=np.r_[toward,obstacle,neighbor,.8,intensity]
            commands.append(predict(c,x)[:2])
        commands=np.asarray(commands)
        pos=wrap(pos+.035*commands)
        effort+=float(np.mean(np.sum(commands**2,axis=1)))
        progress+=float(np.mean(old_distance-np.linalg.norm(wrap(goal-pos),axis=1)))
        hazard_events+=int(np.sum(np.linalg.norm(wrap(pos-hazard),axis=1)<.13))
        for i in range(len(cells)):
            for j in range(i):
                collisions+=int(np.linalg.norm(wrap(pos[i]-pos[j]))<.12)
    return {'exploratory':True,'steps':steps,'cells':len(cells),'seed':seed,
            'collision_pair_steps':collisions,'hazard_cell_steps':hazard_events,
            'mean_progress_per_step':progress/steps,'mean_action_energy':effort/steps,
            'initial_positions':initial.tolist(),'final_positions':pos.tolist()}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--seed',type=int,default=17)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    exp=generate_experiment(args.seed)
    report={'source':evaluate(exp['source'],exp['test']), 'gradient_diagnostic':evaluate(gradient_diagnostic(exp['source'],exp['train']),exp['test']), 'local_evolution':local_evolution(exp['source'],exp['validation'],seed=args.seed)}
    if args.output:
        args.output.mkdir(parents=True,exist_ok=True)
        (args.output/'experiment.json').write_text(json.dumps(exp,indent=2)+'\n')
        (args.output/'baselines.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='local_evolution'},indent=2))
