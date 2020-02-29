# Lint as: python3
"""A script that draws various actual, target and effective burst capacities.


Requirements: abls, mathplotlib, numpy.
"""


from absl import app
from absl import flags
from math import ceil

import numpy as np
import matplotlib.pyplot as plt



FLAGS = flags.FLAGS

flags.DEFINE_integer('target', 100, 'The target concurrency', lower_bound=1)
flags.DEFINE_float(
    'target_utilization', 0.7, 'The target utilization rate: [0.01, 1] range',
    lower_bound=0.01, upper_bound=1)
flags.DEFINE_integer('tbc', 200, 'The target burst capacity', lower_bound=1)

flags.DEFINE_integer(
    'min_traffic', 0, ' Traffic range lower bound for plotting', lower_bound=0)
flags.DEFINE_integer(
    'max_traffic', 1000, 'Traffic range uppper bound for plotting',
    upper_bound=10**8, lower_bound=1)
flags.DEFINE_integer(
    'step_count', 100, 'Max number of points for plotting',
    lower_bound=5, upper_bound=500)
flags.DEFINE_integer(
    'pod_range', 15, 'For imprecise graph: max number of pods',
    lower_bound=2, upper_bound=1000)


def capacities(cc, target, tu, tbc):
    """Computes various capacity values given average concurrency.

    Given paramters for the revision, the fucntion returns total,
    available and effective capacities.

    Args:
        cc: current average concurrency, i.e. traffic
        target: the scaling target for the revision
        tu: target utilization for the revision
        tbc: target burst capacity for the revision
    Returns:
        tuple(total, average, target, effective) capacities.
    """
    tc = target * 1.0 # ensure floats.
    nump = np.ceil(cc/(tc*tu))

    tot_cap = nump*target
    target_cap = tot_cap*tu
    av_cap = tot_cap - cc
    eff_cap = tot_cap - cc - tbc
    return (tot_cap, av_cap, target_cap, eff_cap)


def plot_imprecise(max_t):
  nump = np.arange(1, max_t+1, 1)
  total = nump*FLAGS.target
  caps = (
          total,
          nump*FLAGS.target*FLAGS.target_utilization,
          total*(1-FLAGS.target_utilization),
          total*(1-FLAGS.target_utilization)-FLAGS.target+1)
          
  print(caps[2])
  plt.subplot(1, 2, 1)
  plt.plot(nump, caps[0], label='Total')
  plt.plot(nump, caps[1], label='Target')
  plt.plot(nump, caps[2], label='Excess Pod Min Loaded')
  plt.plot(nump, caps[3], '--', label='Excess Pod Max Loaded')
  plt.plot(nump, [FLAGS.tbc]*len(nump), 'r-', linewidth=2.5, label='TBC')
  plt.xlabel("Number of Pods")
  plt.ylabel("Capacity")
  plt.grid()
  plt.legend()


def plot_precise(min_t, max_t, step):
  ts = np.arange(min_t, max_t+step, step)

  caps = capacities(
          ts, FLAGS.target, FLAGS.target_utilization, FLAGS.tbc)

  plt.subplot(1, 2, 2)
  plt.plot(ts, caps[0], label='Total')
  plt.plot(ts, caps[1], label='Available')
  plt.plot(ts, caps[2], label='Target')
  plt.plot(ts, caps[3], label='Effective')
  plt.plot(ts, [FLAGS.tbc]*len(ts), 'r-', linewidth=2.5, label='TBC')
  plt.plot(ts, [0]*len(ts), '--p', linewidth=1.5, label='0')
  plt.xlabel("Request Concurrency")
  plt.ylabel("Capacity")
  plt.grid()
  plt.legend()

def main(argv):
  # Alias and verify.
  min_t, max_t = FLAGS.min_traffic, FLAGS.max_traffic
  if min_t >= max_t:
    raise app.UsageError(
        'min_t_traffic {0} must be less than max_t_traffic {1}'.format(min, max))

  # Compute the step size and adjust number of steps, if a step
  # is less than 1.
  num_steps = FLAGS.step_count
  step = round(max_t - min_t) / FLAGS.step_count
  if step < 1:
    step = 1

  plot_precise(min_t, max_t, step)
  plot_imprecise(FLAGS.pod_range)
  plt.show()


if __name__ == '__main__':
  app.run(main)


