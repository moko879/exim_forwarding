import subprocess
import re

class ParseResult():
  def __init__(self, forwarded=set(), accepted=set(), bounced=set(), expired=set()):
    assert isinstance(forwarded, set)
    assert isinstance(accepted, set)
    assert isinstance(bounced, set)
    assert isinstance(expired, set)
    self._forwarded = forwarded
    self._accepted = accepted
    self._bounced = bounced
    self._expired = expired

  @property
  def forwarded(self):
    return self._forwarded

  @property
  def accepted(self):
    return self._accepted

  @property
  def bounced(self):
    return self._bounced

  @property
  def expired(self):
    return self._expired

  @property
  def undelivered(self):
    return self._bounced | self._expired
  
  @property
  def delivered(self):
    return self._forwarded | self._accepted
  
  def __repr__(self):
    return  "Result(" + \
      "forwarded = " + str(self.forwarded) + ", " \
      "accepted = " + str(self.accepted) + ", " \
      "bounced = " + str(self.bounced) + ", " \
      "expired = " + str(self.expired) + ")"

def _parse_addresses(stdout):
  rows = str(stdout).split('\n')
  mailboxes = set()
  forwarded = set()
  bounced = set()
  expired = set()
  unknown = set()
  print(stdout)
  for r in range(0,len(rows)):
    match = re.search("^([\\w.+-]+@[\\w.-]+)($|\W)", rows[r])
    if match is None:
      continue;
    email = match.group(1)
    print(email,":",rows[r])

    if rows[r].endswith("[duplicate, would not be delivered]"):
      continue;

    if re.search("^\\s*router = virtual_user", rows[r+1]) != None:
      mailboxes.add(email)

    elif re.search("^\\s*<-- ([\\w.+-]+@[\\w.-]+)$", rows[r+1]):
      offset = 2
      while re.search("^\\s*<-- ([\\w.+-]+@[\\w.-]+)$", rows[r+offset]):
        offset += 1
      assert \
         (re.search("^\\s*router = virtual_user", rows[r+offset]) != None or
         #TODO: remove this once we have no remote domains.
         re.search("^\\s*router = lookuphost", rows[r+offset]) != None)
      forwarded.add(email)
    
    elif rows[r].startswith(email + " is undeliverable: Temporary email address has expired"):
      expired.add(email)

    elif rows[r].startswith(email + " is undeliverable:"):
      bounced.add(email)

    else:
      unknown.add(email)

  assert unknown == set()

  return ParseResult(
    forwarded = forwarded,
    accepted = mailboxes,
    bounced = bounced,
    expired = expired)

def _get_conf(conf_suffix=None, conf_file=None):
  if conf_file:
    return conf_file
  if conf_suffix:
    return "/etc/exim.conf." + conf_suffix
  return "/etc/exim.conf"

def get_addresses(emails_in, conf_suffix=None, conf_file=None):
  conf = _get_conf(conf_suffix, conf_file)
  output = subprocess.run(["exim -C "+conf+" -bt " + ",".join(emails_in)],
    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf8")
  return _parse_addresses(output.stdout)

def verify_addresses(emails_in, conf_suffix=None, conf_file=None):
  conf = _get_conf(conf_suffix, conf_file)
  output = subprocess.run(["exim -C "+conf+" -bv " + ",".join(emails_in)],
    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf8")
  verified = set()
  for email in emails_in:
    if (email+" verified") in output.stdout:
      verified.add(email)
  return verified
