import pytest
import exim

@pytest.mark.parametrize("name,received,expected", [
    ("Virtual user", ["test@kruskal.net"], {"test@kruskal.net"}),
    ("valias override (same)", ["test.com@kruskal.net"], {"test@kruskal.net"}),
    ("valias override (different)", ["test2.com@kruskal.net"], {"test2@kruskal.net"}),
    ("ralias", ["blah.com@kruskal.net"], {"test@kruskal.net"}),
    ("Multiple valias", ["multiple@kruskal.net"], {"test@kruskal.net", "test2@kruskal.net"}),
    ("Multiple ralias", ["blah.mul@kruskal.net"], {"test@kruskal.net", "test2@kruskal.net"}),
    ("Not expired ealias", ["live@kruskal.net"], {"test@kruskal.net"}),
    ("Not expired ealias ralias override", ["live.com@kruskal.net"], {"test2@kruskal.net"}),
    ("Eternal ealias", ["eternal@kruskal.net"], {"test@kruskal.net"}),
    ("Eternal ealias ralias override", ["eternal.com@kruskal.net"], {"test2@kruskal.net"}),
    ("Multiple not expired ealias", ["multiple-live@kruskal.net"], {"test@kruskal.net", "test2@kruskal.net"}),
])
def test_delivered(name, received, expected, parse_matcher):
  assert exim.get_addresses(received, conf_suffix="mock") == parse_matcher(
    delivered = expected, bounced = set())

@pytest.mark.parametrize("name,received,expected", [
    ("Bounce", ["invalid@kruskal.net"], {"invalid@kruskal.net"}),
    ("Multiple Bounce", ["invalid@kruskal.net", "invalid2@kruskal.net"], {"invalid@kruskal.net", "invalid2@kruskal.net"}),
])
def test_bounced(name, received, expected, parse_matcher):
  assert exim.get_addresses(received, conf_suffix="mock")== parse_matcher(
    delivered = set(), bounced = expected)

@pytest.mark.parametrize("name,received", [
    ("Expired", ["expired@kruskal.net"]),
    ("Expired ralias override", ["expired.com@kruskal.net"]),
    ("Multiple Expired", ["multiple-expired@kruskal.net"]),
])
def test_expired(name, received, parse_matcher):
  assert exim.get_addresses(received, conf_suffix="mock")== parse_matcher(
    delivered = set(), expired = set(received))

def test_virtual_regex_forward(parse_matcher):
  assert exim.get_addresses(["to-test@kruskal.net", "test2.com@kruskal.net"], conf_suffix="mock") == \
    parse_matcher(
      delivered = {"test@kruskal.net", "test2@kruskal.net"},
      forwarded = {"test@kruskal.net", "test2@kruskal.net"},
      accepted = set(),
      bounced = set())

def test_mailbox_forward(parse_matcher):
  assert exim.get_addresses(["test@kruskal.net", "test2.com@kruskal.net"], conf_suffix="mock") == \
    parse_matcher(
      delivered = {"test@kruskal.net", "test2@kruskal.net"},
      forwarded = "test2@kruskal.net",
      accepted = "test@kruskal.net",
      bounced = set())

def test_bounce_valid(parse_matcher):
  assert exim.get_addresses(["test@kruskal.net", "test2.com@kruskal.net", "invalid@kruskal.net"], conf_suffix="mock") == \
    parse_matcher(
      delivered = {"test@kruskal.net", "test2@kruskal.net"},
      forwarded = "test2@kruskal.net",
      accepted = "test@kruskal.net",
      bounced = "invalid@kruskal.net")
