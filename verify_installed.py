import pathlib,subprocess,sys,tempfile,json,hashlib,shutil
PYTHON=pathlib.Path(sys.argv[1]).absolute()
SOURCE=pathlib.Path(__file__).absolute().parent
COMMAND=PYTHON.parent/"vcd-state-ledger"
with tempfile.TemporaryDirectory() as td:
 work=pathlib.Path(td)
 def run(args,code=0):
  p=subprocess.run([str(COMMAND),*map(str,args)],cwd=work,text=True,capture_output=True,timeout=20)
  assert p.returncode==code,(args,p.returncode,p.stdout,p.stderr)
  if code==2:
   assert not p.stdout and p.stderr,(p.stdout,p.stderr)
   return None
  return json.loads(p.stdout)
 help_result=subprocess.run([str(COMMAND),"--help"],cwd=work,capture_output=True,text=True,timeout=10)
 assert help_result.returncode==0 and "usage:" in help_result.stdout
 installed=subprocess.run([str(PYTHON),"-I","-c","import vcd_state_ledger,pathlib,hashlib;print(hashlib.sha256(pathlib.Path(vcd_state_ledger.__file__).read_bytes()).hexdigest())"],cwd=work,capture_output=True,text=True,check=True).stdout.strip()
 assert installed==hashlib.sha256((SOURCE/"vcd_state_ledger.py").read_bytes()).hexdigest()
 for p in SOURCE.glob("example.*"):shutil.copyfile(p,work/p.name)
 r=run(['example.vcd','--end-tick','15'],1)
 assert r['unknown_bit_ticks']==10
 assert r['signals'][0]['bit_ticks']=={'0':10,'1':5,'x':0,'z':0}
 assert r['signals'][0]['names']==['top.alias','top.clk']
 assert all(sum(s['bit_ticks'].values())==s['width']*15 for s in r['signals'])
 text=(work/'example.vcd').read_text();header=text.split('$dumpvars')[0]
 (work/'known.vcd').write_text(header+'0! b00 " #10')
 assert run(['known.vcd'])['unknown_bit_ticks']==0
 (work/'bad.vcd').write_text(header+'0missing #10');run(['bad.vcd'],2)
 (work/'large.vcd').write_bytes(b' '*(2*1024*1024+1));run(['large.vcd'],2)
print(json.dumps({"installed_command":"vcd-state-ledger","outside_checkout":True,"source_identity_matched":True,"contract_checks":"passed"}))
