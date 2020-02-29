# Lint as: python3
"""A script that draws various burst capacity lines for knative revision

The script generates a plot with various modeled characteristics of the 
revision versus load.
To model load with default values:
  * python3 tbc.py 
To model with lots of params:
  * python3 tbc.py --target_utilization=0.75 --max_traffic=2000 -target=400 --step_count=400

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



def main(argv):
  # Alias and verify.
  min_t, max_t = FLAGS.min_traffic, FLAGS.max_traffic
  if min_t >= max_t:
    raise app.UsageError(
        'min_t_traffic {0} must be less than max_t_traffic {1}'.format(min, max))

  # Compute the step size and adjust number of steps, if a step
  # is less than 1.
  num_steps = FLAGS.step_count
  step = (max_t - min_t) / FLAGS.step_count
  if step == 0:
    step = 1

  ts = np.arange(min_t, max_t+step, step)
  zero = np.arange(0, 0, step)
  # #pods = ceil(traffic / (target * tu))
  num_pods = np.ceil(ts/(FLAGS.target*FLAGS.target_utilization)).astype(int)

  # total capacity is #pods*target
  total_cap = num_pods*FLAGS.target
  # useful capacity is #pods*target*tu

  util_cap = total_cap*FLAGS.target_utilization
  fig, graphs = plt.subplots(4)
  fig.suptitle('Knative Revision Load Characteristics')
  graphs[0].set_title('Number of Pods vs Traffic')
  graphs[0].set_ylabel('Num Pods')
  graphs[0].step(ts, num_pods, where='post', label='Num Pods')

  graphs[1].set_ylabel('Requests')
  graphs[1].set_title('Target Capacity vs Total Capacity')
  graphs[1].step(ts, total_cap, where='post', label='Total Capacity')
  graphs[1].step(ts, util_cap, where='post', label='Target Capacity')


  # available capacity is difference between total capacity and traffic.
  avl_cap = total_cap-ts
  # excess capacity is available capacity minus tbc.
  exc_cap = avl_cap-FLAGS.tbc
  graphs[2].set_ylabel('Requests')
  graphs[2].set_title('Available vs Excess Burst Capacity')
  graphs[2].plot(ts, ts-ts, 'ro', linewidth=1.5)
  graphs[2].step(ts, exc_cap, where='post', label='Excess Capacity')
  graphs[2].step(ts, avl_cap, where='post', label='Available Capacity')

  # if excess capacity is positive, proxy is not enabled.
  proxy = -exc_cap / np.absolute(exc_cap)
  graphs[3].set_ylabel('Proxy Mode?')
  graphs[3].step(ts, proxy, 'g^', where='post', label='Proxy?')

  for g in graphs:
    g.legend()
    g.grid(True)
    g.set_xlabel('Concurrent Requests')
    g.set_xlim([ts.min(), ts.max()])
  plt.show()

if __name__ == '__main__':
  app.run(main)


