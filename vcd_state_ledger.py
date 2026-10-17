"""Account for captured VCD bit-state time and delta value changes without a viewer."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

MAX_BYTES=2*1024*1024
UNITS={'s':10**15,'ms':10**12,'us':10**9,'ns':10**6,'ps':1000,'fs':1}

def analyze(text: str, end_tick: int | None=None) -> dict:
    if len(text.encode('ascii'))>MAX_BYTES:
        raise ValueError('VCD exceeds 2 MiB')
    tokens=re.findall(r'\S+',text)
    if len(tokens)>250000:
        raise ValueError('token budget exceeded')
    pos=0;scope=[];signals={};names=set();timescale=None;header=True;dump=False
    now=0;events=0
    def command():
        nonlocal pos
        values=[]
        while pos<len(tokens) and tokens[pos]!='$end':
            values.append(tokens[pos]);pos+=1
        if pos==len(tokens):raise ValueError('unterminated VCD directive')
        pos+=1
        return values
    def charge(s,t):
        delta=t-s['last_tick']
        for bit in '01xz':s['bit_ticks'][bit]+=delta*s['value'].count(bit)
        s['last_tick']=t
    while pos<len(tokens):
        token=tokens[pos];pos+=1
        if header:
            if token in ('$date','$version','$comment'):command()
            elif token=='$timescale':
                value=''.join(command());m=re.fullmatch(r'(1|10|100)(s|ms|us|ns|ps|fs)',value)
                if not m or timescale is not None:raise ValueError('exactly one valid timescale required')
                timescale={'magnitude':int(m[1]),'unit':m[2],'femtoseconds_per_tick':int(m[1])*UNITS[m[2]]}
            elif token=='$scope':
                v=command()
                if len(v)!=2 or v[0]!='module' or len(scope)>=32:raise ValueError('only bounded module scopes supported')
                scope.append(v[1])
            elif token=='$upscope':
                if command() or not scope:raise ValueError('unbalanced scope')
                scope.pop()
            elif token=='$var':
                v=command()
                if len(v) not in (4,5) or v[0] not in ('wire','reg','logic') or not v[1].isdigit():raise ValueError('unsupported variable declaration')
                width=int(v[1]);code=v[2];name='.'.join(scope+[v[3]+(' '+v[4] if len(v)==5 else '')])
                if not 1<=width<=256 or len(code)>64 or name in names or len(names)>=2000:raise ValueError('variable width/name budget or duplicate name')
                if any(not c.isprintable() for c in code+name):raise ValueError('nonprinting variable identity')
                names.add(name)
                if code in signals:
                    if signals[code]['width']!=width:raise ValueError('alias widths differ')
                    signals[code]['names'].append(name)
                else:
                    if len(signals)>=512:raise ValueError('signal budget exceeded')
                    signals[code]={'code':code,'names':[name],'width':width,'value':'x'*width,'last_tick':0,'bit_ticks':dict.fromkeys('01xz',0),'value_changes':0,'rising_edges':0,'falling_edges':0}
            elif token=='$enddefinitions':
                if command() or scope or timescale is None or not signals:raise ValueError('incomplete definitions')
                header=False
            else:raise ValueError('unsupported header directive '+token)
            continue
        if token=='$comment':command();continue
        if token=='$dumpvars':
            if dump or now!=0:raise ValueError('dumpvars only permitted at tick zero')
            dump=True;continue
        if token=='$end':
            if not dump:raise ValueError('unexpected $end')
            dump=False;continue
        if token.startswith('#'):
            if dump or not re.fullmatch(r'#[0-9]{1,15}',token):raise ValueError('invalid timestamp')
            t=int(token[1:])
            if t<now:raise ValueError('timestamps must not decrease')
            now=t;continue
        if token.startswith(('b','B')):
            value=token[1:].lower()
            if pos>=len(tokens):raise ValueError('missing vector identifier')
            code=tokens[pos];pos+=1
        elif token and token[0].lower() in '01xz':value=token[0].lower();code=token[1:]
        else:raise ValueError('unsupported data token '+token)
        if code not in signals or not re.fullmatch('[01xz]+',value):raise ValueError('unknown signal or invalid value')
        s=signals[code];width=s['width']
        if len(value)>width or (not token.startswith(('b','B')) and width!=1):raise ValueError('value width mismatch')
        value=value.rjust(width,value[0] if value[0] in 'xz' else '0')
        charge(s,now);events+=1
        if events>100000:raise ValueError('value event budget exceeded')
        if value!=s['value']:
            s['value_changes']+=1
            if width==1:
                s['rising_edges']+=int(s['value']=='0' and value=='1')
                s['falling_edges']+=int(s['value']=='1' and value=='0')
        s['value']=value
    if header or dump:raise ValueError('incomplete VCD')
    end=now if end_tick is None else end_tick
    if type(end) is not int or not now<=end<=10**15-1 or end<=0:raise ValueError('end tick must be positive, bounded and not precede captured time')
    report=[]
    for code,s in sorted(signals.items()):
        charge(s,end)
        assert sum(s['bit_ticks'].values())==s['width']*end
        report.append({k:v for k,v in s.items() if k!='last_tick'} | {'names':sorted(s['names'])})
    return {'timescale':timescale,'start_tick':0,'last_captured_tick':now,'end_tick':end,'value_events':events,'signals':report,
            'unknown_bit_ticks':sum(s['bit_ticks']['x']+s['bit_ticks']['z'] for s in signals.values()),
            'scope':'Captured digital states only. Same-tick changes count but accrue no elapsed time. No analog/power or physical-clock claim; end override explicitly holds last states.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('--end-tick',type=int);a=p.parse_args()
    try:
        with Path(a.input).open('rb') as f:raw=f.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:raise ValueError('VCD exceeds 2 MiB')
        report=analyze(raw.decode('ascii'),a.end_tick);print(json.dumps(report,sort_keys=True,indent=2));return int(report['unknown_bit_ticks']>0)
    except (ValueError,OSError,UnicodeError,OverflowError,RecursionError) as e:
        print(json.dumps({'error':str(e)}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
