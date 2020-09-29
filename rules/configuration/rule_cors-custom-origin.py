import random
import string

from core.redis   import rds
from core.triage  import Triage
from core.parser  import ScanParser, ConfParser

class Rule:
  def __init__(self):
    self.rule = 'CFG_DZ19'
    self.rule_severity = 1
    self.rule_description = 'Checks if CORS Allows Arbitrary Origin Trust'
    self.rule_confirm = 'CORS Allows Arbitrary Origins'
    self.rule_details = ''
    self.rule_mitigation = '''Consider hardening your CORS Policy to define specific Origins \
https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS'''
    self.intensity = 1
  
  def randomize_origin(self):
    rand_str = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    return 'https://{}.com'.format(rand_str) 
  
  def check_rule(self, ip, port, values, conf):
    c = ConfParser(conf)
    t = Triage()
    p = ScanParser(port, values)
    
    domain  = p.get_domain()
    module  = p.get_module()
    product  = p.get_product()
    
    if 'http' not in module:
      return
    
    resp = None
    random_origin = self.randomize_origin()
    
    if domain:
      resp = t.http_request(domain, port, headers={'Origin':random_origin})
    else:
      resp = t.http_request(ip, port, headers={'Origin':random_origin})
    
    if resp is None:
      return
    
    if 'Access-Control-Allow-Origin' in resp.headers and resp.headers['Access-Control-Allow-Origin'] == random_origin:
      self.rule_details = 'Header used: "Origin: {}"'.format(random_origin)    
      js_data = {
                'ip':ip,
                'port':port,
                'domain':domain,
                'rule_id':self.rule,
                'rule_sev':self.rule_severity,
                'rule_desc':self.rule_description,
                'rule_confirm':self.rule_confirm,
                'rule_details':self.rule_details,
                'rule_mitigation':self.rule_mitigation
              }
      rds.store_vuln(js_data)

    return