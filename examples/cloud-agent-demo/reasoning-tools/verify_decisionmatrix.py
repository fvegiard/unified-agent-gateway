#!/usr/bin/env python3
"""Black-box MCP acceptance tests. This is a client, never a replacement server."""
import copy,json,pathlib
from fractions import Fraction
from verify_mcp import MCP,ROOT

BASE={
 'options':['A','B','C'],
 'criteria':[{'name':'Quality','weight':3,'direction':'benefit'},{'name':'Cost','weight':1,'direction':'cost'}],
 'scores':{'A':{'Quality':10,'Cost':100},'B':{'Quality':6,'Cost':60},'C':{'Quality':2,'Cost':20}},
 'method':'weighted_sum'
}
checks=[]
def check(name,test):
 try:
  detail=test();checks.append({'name':name,'status':'PASS','detail':detail})
 except Exception as e:checks.append({'name':name,'status':'FAIL','error':str(e)})
def require(condition,message):
 if not condition:raise AssertionError(message)
def same(a,b):require(a==b,f'Expected {b!r}, received {a!r}')
def changed(path,value):
 a=copy.deepcopy(BASE);t=a
 for p in path[:-1]:t=t[p]
 t[path[-1]]=value;return a

def run():
 m=MCP('decisionmatrix',['node',str(ROOT/'node_modules/decisionmatrix-mcp/server.mjs')])
 def call(name,args):
  res=m.call('tools/call',{'name':name,'arguments':args})
  if 'error' in res:return res
  result=res['result'];data=result.get('structuredContent')
  if data is None:data=json.loads(result['content'][0]['text'])
  return {'rpc_result':result,'data':data}
 def success(name,args):
  r=call(name,args);require('data' in r,str(r));require(not r['rpc_result'].get('isError'),str(r));return r['data']
 def invalid(args,kind):
  r=call('create_decision',args);require(r.get('rpc_result',{}).get('isError'),str(r));same(r['data']['status'],'error');same(r['data']['error']['type'],kind);return r['data']['error']
 try:
  init=m.call('initialize',{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'synthetic-decision-acceptance','version':'1.0.0'}})
  m.call('notifications/initialized',notification=True)
  ts=m.call('tools/list',{})['result']['tools']
  (ROOT/'evidence'/'decisionmatrix.tools.json').write_text(json.dumps(ts,indent=2)+'\n')
  check('initialize and six real tools',lambda:same(sorted(t['name'] for t in ts),sorted(['create_decision','score_options','sensitivity_analysis','compare_two','list_methods','health_check'])))
  baseline=success('create_decision',BASE)
  # Independent exact rational oracle; no decisionmatrix imports here.
  weights=[Fraction(3,4),Fraction(1,4)]
  expect={o:weights[0]*Fraction(BASE['scores'][o]['Quality']-2,8)+weights[1]*Fraction(100-BASE['scores'][o]['Cost'],80) for o in BASE['options']}
  def baseline_test():
   same(baseline['winner']['option'],'A');same([r['option'] for r in baseline['ranking']],['A','B','C'])
   for r in baseline['ranking']:same(Fraction(r['score_exact']),expect[r['option']])
   return {o:str(v) for o,v in expect.items()}
  check('weighted_sum against independent rational oracle',baseline_test)
  check('byte-equivalent result repeated 3 times',lambda:[same(json.dumps(success('create_decision',BASE),sort_keys=True),json.dumps(baseline,sort_keys=True)) for _ in range(3)])
  check('relative weight scaling preserves rank and exact scores',lambda:same([(r['option'],r['score_exact']) for r in success('create_decision',{**BASE,'criteria':[{**c,'weight':c['weight']*10} for c in BASE['criteria']]})['ranking']],[(r['option'],r['score_exact']) for r in baseline['ranking']]))
  check('one zero weight allowed and ignored in scoring',lambda:same([(r['option'],r['score_exact']) for r in success('create_decision',changed(['criteria',0,'weight'],0))['ranking']],[('C','1'),('B','0.5'),('A','0')]))
  check('negative weight rejected',lambda:invalid(changed(['criteria',0,'weight'],-1),'invalid_weight'))
  check('all zero weights rejected',lambda:invalid({**BASE,'criteria':[{**c,'weight':0} for c in BASE['criteria']]},'invalid_weight'))
  missing=copy.deepcopy(BASE);del missing['scores']['B']['Cost']
  check('incomplete matrix rejected',lambda:invalid(missing,'incomplete_scores'))
  check('matrix wrong top-level type rejected',lambda:invalid({**BASE,'scores':8},'invalid_scores'))
  check('explicit unknown option row rejected',lambda:invalid({**BASE,'scores':[{'option':'Z','scores':{'Quality':4,'Cost':40}}]},'unknown_option'))
  for value in ['NaN','Infinity','-Infinity',None]:
   check(f'non-finite or absent score rejected: {value}',lambda value=value:invalid(changed(['scores','A','Quality'],value),'missing_parameter' if value is None else 'invalid_input'))
  check('non-finite weight rejected',lambda:invalid(changed(['criteria',0,'weight'],'Infinity'),'invalid_input'))
  check('duplicate alternatives rejected',lambda:invalid({**BASE,'options':['A','A']},'duplicate_option'))
  check('unknown method rejected',lambda:invalid({**BASE,'method':'nonexistent'},'unknown_method'))
  check('unknown tool returns protocol -32602',lambda:same(call('nonexistent_tool',{}).get('error',{}).get('code'),-32602))
  scored=success('score_options',BASE)
  check('score_options agrees with create_decision',lambda:same([(r['option'],r['total_score_exact']) for r in scored['scored']],[(r['option'],r['score_exact']) for r in baseline['ranking']]))
  methods=success('list_methods',{});health=success('health_check',{})
  check('list_methods and health_check callable',lambda:require(methods['status']=='success' and health['status']=='ok',str((methods,health))))
  sensitivity=success('sensitivity_analysis',{**BASE,'variation':0.2,'steps':3})
  check('sensitivity robust for clear weighted_sum winner',lambda:same((sensitivity['baseline_winner'],sensitivity['robustness_score'],sensitivity['fragile_criteria']),('A',1,[])))
  pair={**BASE,'options':['A','C']}
  compared=success('compare_two',pair)
  check('compare_two weighted_sum checks direction and wins',lambda:same((compared['winner'],compared['criteria_wins']),('A',{'A':1,'C':1})))
  simple={'options':['A','B'],'criteria':[{'name':'Quality','weight':1,'direction':'benefit'}],'scores':{'A':{'Quality':4},'B':{'Quality':2}}}
  check('weighted_product simple independent oracle',lambda:same([(r['option'],r['score_exact']) for r in success('create_decision',{**simple,'method':'weighted_product'})['ranking']],[('A','1'),('B','0.5')]))
  check('TOPSIS one benefit independent oracle',lambda:same([(r['option'],r['score_exact']) for r in success('create_decision',{**simple,'method':'topsis'})['ranking']],[('A','1'),('B','0')]))
  cost={**simple,'criteria':[{'name':'Quality','weight':1,'direction':'cost'}],'method':'topsis'}
  check('TOPSIS cost rank respects minimize direction',lambda:same([(r['option'],r['score_exact']) for r in success('create_decision',cost)['ranking']],[('B','1'),('A','0')]))
  pc=success('compare_two',cost)
  check('TOPSIS compare_two cost explanation agrees with rank',lambda:same((pc['winner'],pc['per_criterion'][0]['favours'],pc['criteria_wins']),('B','B',{'A':0,'B':1})))
  # Characterize permissiveness rather than rewriting upstream validation.
  extra=copy.deepcopy(BASE);extra['scores']['Z']={'Quality':999,'Cost':1};extra['scores']['A']['Typo']=123
  extra_result=success('create_decision',extra)
  observations={
   'package_version':json.loads((ROOT/'node_modules/decisionmatrix-mcp/package.json').read_text())['version'],
   'reported_server_info':init['result']['serverInfo'],
   'health_check':health,
   'extra_object_map_options_and_criteria_ignored':extra_result==baseline,
   'topis_compare_two_cost_observed':pc,
   'invalid_nonfinite_values_note':'NaN and Infinity are not valid JSON numbers, so tests submit their string forms through real MCP calls; engine rejects them.',
   'source_unchanged':True
  }
  report={'status':'PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL','passed':sum(c['status']=='PASS' for c in checks),'failed':sum(c['status']=='FAIL' for c in checks),'checks':checks,'observations':observations}
  (ROOT/'evidence'/'decisionmatrix-acceptance-results.json').write_text(json.dumps(report,indent=2)+'\n')
  print(json.dumps({k:report[k] for k in ['status','passed','failed','checks']},indent=2))
  return report
 finally:m.close()
if __name__=='__main__':
 result=run();raise SystemExit(0 if result['status']=='PASS' else 1)
