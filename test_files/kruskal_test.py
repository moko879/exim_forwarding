import pytest
import exim

@pytest.mark.parametrize("received,expected", [
    ("michael@kruskal.net", "michael879@gmail.com"),
    ("elliot@kruskal.net", "ekruskal@gmail.com"),
    ("vincent@kruskal.net", "kruskal@gmail.com"),
    ("joan@kruskal.net", "jbkessler@gmail.com"),
    ("sue@kruskal.net", "sueacano@gmail.com"),
    ("jody@kruskal.net", "jodykr@gmail.com"),
    ("michael_not_expired@kruskal.net", "michael879@gmail.com"),
    ("michael_eternal@kruskal.net", "michael879@gmail.com"),
])
def test_main_forwards(received, expected, parse_matcher):
  assert exim.get_addresses({received}, conf_suffix="test") == \
    parse_matcher(
      forwarded = expected,
      accepted = set(),
      bounced = set())
  assert exim.verify_addresses({received}, conf_suffix="test") == {received}

@pytest.mark.parametrize("received,expected", [
    ("sueandmichael@kruskal.net", {"michael879@gmail.com", "sueacano@gmail.com"}),
    ("joanandvincent@kruskal.net", {"kruskal@gmail.com", "jbkessler@gmail.com"}),
])
def test_groups(received, expected, parse_matcher):
  assert exim.get_addresses({received}, conf_suffix="test") > \
    parse_matcher(
      forwarded = expected,
      accepted = set(),
      bounced = set())
  assert exim.verify_addresses({received}, conf_suffix="test") == {received}

@pytest.mark.parametrize("received,expected", [
    ("amazon.com@kruskal.net", "kruskal@gmail.com"),
    ("michael-amazon@kruskal.net", "michael879@gmail.com"),
    ("michael-spam@kruskal.net", "kruskal.spam@gmail.com"),
])
def test_regex(received, expected, parse_matcher):
  assert exim.get_addresses({received}, conf_suffix="test") > \
    parse_matcher(
      forwarded = {expected},
      accepted = set(),
      bounced = set())
  assert exim.verify_addresses({received}, conf_suffix="test") == {received}

@pytest.mark.parametrize("received,expected", [
    ("bloomingdales.com@kruskal.net", "jbkessler@gmail.com"),
    ("boston.gov@kruskal.net", "michael879@gmail.com"),
])
def test_regex_exceptions(received, expected, parse_matcher):
  assert exim.get_addresses({received}, conf_suffix="test") == \
    parse_matcher(
      forwarded = expected,
      accepted = set(),
      bounced = set())
  assert exim.verify_addresses({received}, conf_suffix="test") == {received}

@pytest.mark.parametrize("received,expected", [
    ("sueandmichael@kruskal.net", {"michael879@gmail.com", "sueacano@gmail.com"}),
    ("joanandvincent@kruskal.net", {"kruskal@gmail.com", "jbkessler@gmail.com"}),
])
def test_groups(received, expected, parse_matcher):
  assert exim.get_addresses({received}, conf_suffix="test") > \
    parse_matcher(
      forwarded = expected,
      accepted = set(),
      bounced = set())
  assert exim.verify_addresses({received}, conf_suffix="test") == {received}

@pytest.mark.parametrize("tld", ["com", "edu", "gov", "info", "net", "org", "us"])
def test_tld_valid(tld, parse_matcher):
  email = "something.%s@kruskal.net"%tld
  assert exim.get_addresses({email}, conf_suffix="test") > \
    parse_matcher(
      forwarded = "kruskal@gmail.com",
      accepted = set(),
      bounced = set())
  assert exim.verify_addresses({email}, conf_suffix="test") == {email}

def test_tld_invalid(parse_matcher):
  invalid = "something.ooo@kruskal.net"
  assert exim.get_addresses({invalid}, conf_suffix="test") == \
    parse_matcher(
      forwarded = set(),
      accepted = set(),
      bounced = invalid)
  assert exim.verify_addresses({invalid}, conf_suffix="test") == set()

@pytest.mark.parametrize("expired", [
    "expired@kruskal.net",
    "michael-expired@kruskal.net",
])
def test_tld_invalid(expired, parse_matcher):
  assert exim.get_addresses({expired}, conf_suffix="test") == \
    parse_matcher(
      forwarded = set(),
      accepted = set(),
      bounced = set(),
      expired = expired)
  assert exim.verify_addresses({expired}, conf_suffix="test") == set()
