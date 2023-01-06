import pytest

@pytest.fixture()
def parse_matcher():
  def _parse_matcher(**kwargs):
    args = ['forwarded', 'accepted', 'delivered', 'bounced', 'expired', 'undelivered']
    for key,val in kwargs.items():
      assert key in args, "Unknown argument passed to parse_matcher"
      if not isinstance(val, set):
        kwargs[key] = set([val])
    class _Matcher:
      def __init__(self):
        pass

      def __eq__(self, result):
        for key,val in kwargs.items():
          if val != getattr(result, key):
            return False
        return True
    
      def __ne__(self, result):
        return not (self == result)
    
      def __lt__(self, result):
        for key,val in kwargs.items():
          if not val.issubset(getattr(result, key)):
            return False
        return True

      def __le__(self, result):
        return self == result or self < result
      
      def __gt__(self, result):
        for key,val in kwargs.items():
          if not val.issuperset(getattr(result, key)):
            return False
        return True

      def __ge__(self, result):
        return self == result or self > result

      def __repr__(self):
        repr = "Matcher("
        for key,val in kwargs.items():
          repr += key+" = "+str(val) + ", "
        return repr[:-2]+")"
      
    return _Matcher()
  return _parse_matcher
