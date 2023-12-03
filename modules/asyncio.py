import sys
import asyncio

def report_on_fail(task):
  try:
    task.result()
  except asyncio.CancelledError:
    pass
  except Exception as e:
    print(type(e).__name__, ": ", str(e), ", occured on", task.get_name(), file=sys.stderr)

def exit_on_fail(task):
  try:
    task.result()
  except asyncio.CancelledError:
    pass
  except Exception as e:
    print(type(e).__name__, ": ", str(e), ", occured on", task.get_name(), file=sys.stderr)
    sys.exit(1)

__all__ = (
  report_on_fail,
  exit_on_fail,
)
