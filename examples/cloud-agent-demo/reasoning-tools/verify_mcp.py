#!/usr/bin/env python3
"""Synthetic, deterministic MCP integration checks. Never supply private reasoning."""
import json,os,pathlib,selectors,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parent
class MCP:
 def __init__(self,name,command):
  self.name=name; self.counter=0; self.events=[]
  self.out=open(ROOT/'evidence'/f'{name}.stdout.jsonl','w')
  self.err=open(ROOT/'evidence'/f'{name}.stderr.txt','w')
  home=ROOT/'runtime'/name;home.mkdir(parents=True,exist_ok=True)
  self.p=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.err,text=True,bufsize=1,cwd=ROOT,env={'PATH':os.environ['PATH'],'HOME':str(home),'DISABLE_THOUGHT_LOGGING':'true','NO_COLOR':'1'})
  self.selector=selectors.DefaultSelector();self.selector.register(self.p.stdout,selectors.EVENT_READ)
 def call(self,method,params=None,notification=False):
  self.counter+=1;request={'jsonrpc':'2.0','method':method}
  if not notification:request['id']=self.counter
  if params is not None:request['params']=params
  self.events.append({'request':request});self.p.stdin.write(json.dumps(request)+'\n');self.p.stdin.flush()
  if notification:return None
  until=time.monotonic()+20
  while time.monotonic()<until:
   if not self.selector.select(max(0,until-time.monotonic())):break
   line=self.p.stdout.readline()
   if not line:raise RuntimeError(f'{self.name} exited: {self.p.poll()}')
   self.out.write(line);self.out.flush();response=json.loads(line);self.events.append({'response':response})
   if response.get('id')==self.counter:return response
  raise TimeoutError(f'{self.name} timeout on {method}')
 def close(self):
  self.p.stdin.close()
  try:self.p.wait(timeout=5)
  except subprocess.TimeoutExpired:self.p.terminate();self.p.wait(timeout=5)
  self.out.close();self.err.close();self.selector.close()
  (ROOT/'evidence'/f'{self.name}.transcript.json').write_text(json.dumps(self.events,indent=2)+'\n')

def verify_sequential():
 m=MCP('sequential',['node',str(ROOT/'node_modules/@modelcontextprotocol/server-sequential-thinking/dist/index.js')])
 checks=[]
 try:
  init=m.call('initialize',{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'synthetic-acceptance-tests','version':'1.0.0'}})
  assert init['result']['serverInfo']['version']=='2026.8.31';checks.append('initialize/version')
  m.call('notifications/initialized',notification=True)
  listing=m.call('tools/list',{});ts=listing['result']['tools'];assert len(ts)==1
  t=ts[0];assert t['name']=='sequentialthinking'
  schema=t['inputSchema'];props=schema['properties']
  assert schema['type']=='object'
  assert set(schema['required'])=={'thought','nextThoughtNeeded','thoughtNumber','totalThoughts'}
  assert props['thought']['type']=='string'
  assert set(props['nextThoughtNeeded']['type'])=={'boolean','string'}
  for field in ['thoughtNumber','totalThoughts','revisesThought','branchFromThought']:
   assert props[field]['type']=='integer' and props[field]['minimum']==1
  assert props['branchId']['type']=='string'
  out=t['outputSchema'];op=out['properties']
  assert set(out['required'])=={'thoughtNumber','totalThoughts','nextThoughtNeeded','branches','thoughtHistoryLength'}
  assert op['nextThoughtNeeded']['type']=='boolean'
  assert op['branches']['type']=='array' and op['branches']['items']['type']=='string'
  for field in ['thoughtNumber','totalThoughts','thoughtHistoryLength']:assert op[field]['type']=='number'
  checks.append('tools/list input and output schema required fields/types/minimum')
  (ROOT/'evidence'/'sequential.tools.json').write_text(json.dumps(ts,indent=2)+'\n')
  valid={'thought':'Synthetic protocol verification','nextThoughtNeeded':False,'thoughtNumber':1,'totalThoughts':1}
  good=m.call('tools/call',{'name':t['name'],'arguments':valid});r=good['result'];assert not r.get('isError')
  assert r['structuredContent']=={'thoughtNumber':1,'totalThoughts':1,'nextThoughtNeeded':False,'branches':[],'thoughtHistoryLength':1};checks.append('synthetic tools/call exact result')
  bad=m.call('tools/call',{'name':t['name'],'arguments':{**valid,'thoughtNumber':0}})
  assert bad.get('error') or bad.get('result',{}).get('isError'),bad;checks.append('invalid thoughtNumber=0 rejected')
  again=m.call('tools/call',{'name':t['name'],'arguments':{**valid,'thoughtNumber':2,'totalThoughts':2}})
  assert again['result']['structuredContent']['thoughtHistoryLength']==2;checks.append('invalid request did not mutate history')
  result={'status':'PASS','serverInfo':init['result']['serverInfo'],'tool':t['name'],'checks':checks}
  print(json.dumps(result,indent=2));return result
 finally:m.close()

if __name__=='__main__':
 result={'sequential':verify_sequential()}
 (ROOT/'evidence'/'acceptance-results.json').write_text(json.dumps(result,indent=2)+'\n')
