"""Deterministic, data-only family policy editing laboratory. No API access."""
from __future__ import annotations
import copy
import hashlib
import json
import math
from pathlib import Path
import numpy as np

VERSION = 'conditional-passing-v3'
SHAPES = {'w1': (16, 8), 'b1': (16,), 'w2': (3, 16), 'b2': (3,)}
MAX_DELTA = 1.5
MAX_NORM = 5.0
MAX_EDITS = 200


def predict(cell, x, hidden=False):
    x = np.asarray(x, dtype=float)
    h = np.tanh(x @ np.asarray(cell['w1']).T + cell['b1'])
    y = np.tanh(h @ np.asarray(cell['w2']).T + cell['b2'])
    return (y, h) if hidden else y


def make_dataset(seed, n=256, shift=False):
    """Independent observation draws; shift changes density, not target mechanism."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(-1, 1, (n, 8))
    # Two mirrored contexts demand opposite lateral actions, not a gain change.
    if shift:
        x[:, :6] = np.sign(x[:, :6])*np.sqrt(np.abs(x[:, :6]))
    x[:, 7] = rng.choice([-1., 1.],n)
    goal=x[:,:2]
    avoidance=.65*x[:,2:4]+.35*x[:,4:6]
    u=np.maximum(x[:,6:7],0)
    lateral=np.column_stack((-goal[:,1],goal[:,0]))
    hazard=np.tanh(.8*np.sum(x[:,2:4]*x[:,4:6],axis=1)+.3*np.sum(x[:,2:4]**2,axis=1)-.2)
    old_move=np.tanh(1.15*goal-.25*avoidance)
    new_move=np.tanh(1.15*goal-.25*avoidance+1.2*u*x[:,7:8]*lateral)
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
    metrics = {'loss': target + 0.5*secondary + preserved,
            'movement_mse': target, 'active_movement_mse': float(np.mean(move[active])) if np.any(active) else 0.,
            'hazard_mse': secondary, 'preserved_movement_mse': preserved,
            'n': len(x)}
    for sign,label in [(-1,'right'),(1,'left')]:
        mask=active & (x[:,7]==sign)
        metrics[label+'_active_mse']=float(np.mean(move[mask])) if np.any(mask) else 0.
    return metrics


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


def generate_experiment(seed=101, sibling_count=4, train_steps=900):
    rng = np.random.default_rng(seed)
    source = {'version': VERSION, 'id': f'family-{seed}:source', 'unit_ids': list(range(16))}
    source.update({k: (rng.normal(0,.35,shape) if k.startswith('w') else np.zeros(shape)).tolist() for k,shape in SHAPES.items()})
    source = _train(source, make_dataset(seed+1000, 1536), train_steps, .015, 'base_y', False)
    siblings = []
    for i in range(sibling_count):
        c = copy.deepcopy(source)
        # Preserve frozen/plastic partition; permutation is exact before mild drift.
        order = np.r_[rng.permutation(4), 4+rng.permutation(12)]
        c['unit_ids'] = order.tolist()
        c['w1'] = (np.asarray(source['w1'])[order] + rng.normal(0,.008, (16,8))).tolist()
        c['b1'] = (np.asarray(source['b1'])[order] + rng.normal(0,.008, 16)).tolist()
        c['w2'] = (np.asarray(source['w2'])[:,order] + rng.normal(0,.008, (3,16))).tolist()
        c['id'] = f'family-{seed}:sibling-{i}'
        siblings.append(c)
    return {'version': VERSION, 'seed': seed, 'source': source, 'siblings': siblings,
            'train': make_dataset(seed+2000,384), 'validation': make_dataset(seed+3000,256),
            'validation_shift': make_dataset(seed+3500,256,True),
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
    packet = {'version': VERSION, 'task': 'Acquire opposite lateral passing maneuvers in left/right contexts when urgency is positive. Preserve movement when urgency <= 0 and preserve hazard estimate.',
            'inputs': ['goal_x','goal_y','obstacle_x','obstacle_y','neighbor_x','neighbor_y','urgency','passing_side_sign'],
            'target_equations': 'a=.65*x[2:4]+.35*x[4:6]; u=max(x[6],0); lateral=[-x[1],x[0]]; movement=tanh(1.15*x[0:2]-.25*a+1.2*u*x[7]*lateral); hazard=tanh(.8*dot(x[2:4],x[4:6])+.3*sum(x[2:4]**2)-.2). x[7] is -1 or +1. Base lacked the lateral term.',
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



def fingerprint(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()



def target(x):
    x=np.asarray(x,float)
    a=.65*x[:,2:4]+.35*x[:,4:6]
    lateral=np.column_stack((-x[:,1],x[:,0]))
    move=np.tanh(1.15*x[:,:2]-.25*a+1.2*np.maximum(x[:,6:7],0)*x[:,7:8]*lateral)
    hazard=np.tanh(.8*np.sum(x[:,2:4]*x[:,4:6],axis=1)+.3*np.sum(x[:,2:4]**2,axis=1)-.2)
    return np.column_stack((move,hazard))


def conditional_metrics(cell,dataset,reference=None):
    metrics=evaluate(cell,dataset)
    x=np.asarray(dataset['x'])
    active=x[:,6]>.35
    plus=x[active].copy(); minus=plus.copy()
    plus[:,7]=1; minus[:,7]=-1
    learned=predict(cell,plus)[:,:2]-predict(cell,minus)[:,:2]
    intended=target(plus)[:,:2]-target(minus)[:,:2]
    metrics['paired_context_contrast_mse']=float(np.mean((learned-intended)**2))
    if reference is not None:
        low=x[:,6]<=0
        metrics['unchanged_context_drift']=float(np.mean((predict(cell,x[low])[:,:2]-predict(reference,x[low])[:,:2])**2))
        metrics['frozen_equal']=bool(np.array_equal(np.asarray(cell['w1'])[:4],np.asarray(reference['w1'])[:4]) and np.array_equal(np.asarray(cell['b1'])[:4],np.asarray(reference['b1'])[:4]))
    return metrics


def analysis_packet(cell,train):
    x=np.asarray(train['x']); y=np.asarray(train['y'])
    pred,h=predict(cell,x,True)
    residual=np.arctanh(np.clip(y[:,:2],-.999,.999))-np.arctanh(np.clip(pred[:,:2],-.999,.999))
    hc=h-h.mean(0); rc=residual-residual.mean(0)
    corr=hc.T@rc / np.maximum(np.sqrt(np.sum(hc*hc,0)[:,None]*np.sum(rc*rc,0)[None,:]),1e-12)
    return {'training_only':True,'hidden_residual_correlations':corr.tolist(),
            'hidden_mean':h.mean(0).tolist(),'hidden_std':h.std(0).tolist(),
            'residual_logit_mean':residual.mean(0).tolist()}


def diff_patch(source, candidate, project=False):
    coords=editable_coordinates()
    v=np.array([np.asarray(candidate[k])[tuple(i)]-np.asarray(source[k])[tuple(i)] for k,i in coords])
    if project:
        v=np.clip(v,-MAX_DELTA,MAX_DELTA)
        v*=min(1.,MAX_NORM/max(np.linalg.norm(v),1e-20))
    patch={'edits':[{'tensor':k,'index':i,'delta':float(d)} for (k,i),d in zip(coords,v) if abs(d)>1e-15]}
    apply_patch(source,patch)
    return patch


def compile_candidate(source, train, specification):
    """Fixed data-only operator interpreter. Ridge is explicitly ordinary fitting."""
    if not isinstance(specification,dict) or set(specification)!={'label','operations'} or not isinstance(specification['label'],str):
        raise ValueError('candidate requires label and operations')
    operations=specification['operations']
    if not isinstance(operations,list) or len(operations)>12:
        raise ValueError('at most 12 operators')
    cell=copy.deepcopy(source); fitting=False
    for operation in operations:
        if not isinstance(operation,dict): raise ValueError('operator must be object')
        op=operation.get('op')
        if op=='delta':
            if set(operation)!={'op','edits'}: raise ValueError('delta needs edits')
            cell=apply_patch(cell,{'edits':operation['edits']})
        elif op=='set_hidden':
            if set(operation)!={'op','unit','weights','bias'}: raise ValueError('set_hidden fields')
            unit=operation['unit']
            if type(unit) is not int or not 4<=unit<16: raise ValueError('editable hidden units 4..15')
            weights=np.asarray(operation['weights'],float)
            bias=operation['bias']
            if weights.shape!=(8,) or not np.all(np.isfinite(weights)) or type(bias) not in (float,int) or not math.isfinite(bias):
                raise ValueError('finite hidden vector length8 and scalar bias required')
            cell['w1'][unit]=weights.tolist(); cell['b1'][unit]=bias
        elif op=='scale_output':
            if set(operation)!={'op','output','units','scale'}: raise ValueError('scale_output fields')
            output=operation['output']; units=operation['units']; scale=operation['scale']
            if type(output) is not int or output not in (0,1,2): raise ValueError('output0..2')
            if not isinstance(units,list) or len(set(units))!=len(units) or any(type(i) is not int or not 0<=i<16 for i in units): raise ValueError('unique units0..15')
            if type(scale) not in (float,int) or not math.isfinite(scale) or abs(scale)>4: raise ValueError('finite scale abs<=4')
            for unit in units: cell['w2'][output][unit]*=scale
        elif op=='ridge_readout':
            if set(operation)!={'op','units','alpha','blend'}: raise ValueError('ridge_readout fields')
            units=operation['units']; alpha=operation['alpha']; blend=operation['blend']
            if not isinstance(units,list) or not units or len(set(units))!=len(units) or any(type(i) is not int or not 0<=i<16 for i in units): raise ValueError('unique ridge units0..15')
            if type(alpha) not in (int,float) or not math.isfinite(alpha) or not .0001<=alpha<=100: raise ValueError('ridge alpha .0001..100')
            if type(blend) not in (int,float) or not math.isfinite(blend) or not 0<=blend<=1: raise ValueError('ridge blend0..1')
            x=np.asarray(train['x']); y=np.asarray(train['y'])
            _,h=predict(cell,x,True)
            design=np.column_stack((h[:,units],np.ones(len(x))))
            reference=predict(source,x)
            desired=y[:,:2].copy(); low=x[:,6]<=0
            desired[low]=reference[low,:2]
            desired=np.arctanh(np.clip(desired,-.999,.999))
            current=np.arctanh(np.clip(predict(cell,x)[:,:2],-.999,.999))
            weights=np.where(low,8.,1.)
            # Delta ridge preserves current coefficients as the regularization center.
            matrix=design.T@(weights[:,None]*design)/len(x)+alpha*np.eye(len(units)+1)
            rhs=design.T@(weights[:,None]*(desired-current))/len(x)
            delta=np.linalg.solve(matrix,rhs)*blend
            for out in range(2):
                for j,unit in enumerate(units): cell['w2'][out][unit]+=float(delta[j,out])
                cell['b2'][out]+=float(delta[-1,out])
            fitting=True
        else: raise ValueError('unknown operator')
        # All intermediate surgery must obey source-relative bounds too. Fitting
        # projects the complete proposal to the registered box and L2 radius.
        patch=diff_patch(source,cell,project=(op=='ridge_readout'))
        cell=apply_patch(source,patch)
    patch=diff_patch(source,cell)
    return {'patch':patch,'cell':cell,'mechanism':'ordinary_ridge_fitting' if fitting else 'manual_direct_surgery',
            'operations':copy.deepcopy(operations),'label':specification['label']}


def rollout(cells,seed=1701,steps=180,oracle=False):
    """Shared crossing arena with common passing sign and simultaneous actions."""
    rng=np.random.default_rng(seed); n=len(cells)
    angles=np.arange(n)*2*np.pi/n+rng.uniform(-.15,.15,n)
    pos=np.column_stack((np.cos(angles),np.sin(angles)))*.85
    goals=-pos.copy(); initial=pos.copy(); side=float(rng.choice([-1,1]))
    collision=hazards=0; effort=0.; hazard=np.array([.35,.25])
    start=float(np.mean(np.linalg.norm(goals-pos,axis=1)))
    for step in range(steps):
        actions=[]
        for i,cell in enumerate(cells):
            goal=goals[i]-pos[i]; gd=np.linalg.norm(goal)
            relatives=pos-pos[i]; distances=np.linalg.norm(relatives,axis=1); distances[i]=np.inf
            j=int(np.argmin(distances)); d=distances[j]
            neighbor=relatives[j]/max(d,.02)*np.exp(-d*3)
            hv=hazard-pos[i]; hd=np.linalg.norm(hv)
            obstacle=hv/max(hd,.02)*np.exp(-hd*4)
            urgency=float(np.clip(1-d/.5,-1,1))
            x=np.r_[goal/max(gd,1.),obstacle,neighbor,urgency,side]
            action=(target(x[None,:])[0] if oracle else predict(cell,x))[:2]
            actions.append(action if gd>.05 else np.zeros(2))
        actions=np.asarray(actions); pos+=.025*actions
        effort+=float(np.mean(np.sum(actions**2,axis=1)))
        hazards+=int(np.sum(np.linalg.norm(pos-hazard,axis=1)<.12))
        for i in range(n):
            for j in range(i): collision+=int(np.linalg.norm(pos[i]-pos[j])<.12)
    final=float(np.mean(np.linalg.norm(goals-pos,axis=1)))
    return {'exploratory':True,'seed':seed,'steps':steps,'side':side,'collision_pair_steps':collision,
            'hazard_cell_steps':hazards,'mean_goal_progress':start-final,'mean_final_goal_distance':final,
            'mean_action_energy':effort/steps,'initial_positions':initial.tolist(),'final_positions':pos.tolist(),
            'oracle_target_controller':oracle}
