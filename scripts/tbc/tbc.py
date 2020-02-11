# Lint as: python3
"""A script that draws various burst capacity lines for knative revision


"""


from absl import app
from absl import flags
from math import ceil

import numpy as np
import matplotlib.pyplot as plt



FLAGS = flags.FLAGS

flags.DEFINE_integer('target', 100, 'The target concurrency', lower_bound=1)
flags.DEFINE_float('target_utilization', 0.7, 'The target utilization rate: [0.01, 1] range',
                   lower_bound=0.01, upper_bound=1)
flags.DEFINE_integer('tbc', 200, 'The target burst capacity', lower_bound=1)

flags.DEFINE_integer('min_traffic', 0, ' Traffic range lower bound for plotting', lower_bound=0)
flags.DEFINE_integer('max_traffic', 1000, 'Traffic range uppper bound for plotting', upper_bound=10**8, lower_bound=1)
flags.DEFINE_integer('step_count', 100, 'Max number of points for plotting', lower_bound=5, upper_bound=500)



def main(argv):
  min_t, max_t = FLAGS.min_traffic, FLAGS.max_traffic
  if min_t >= max_t:
    raise app.UsageError('min_t_traffic {0} must be less than max_t_traffic {1}'.format(min, max))

  # Compute the step size and adjust number of steps, if a step
  # is less than 1.
  num_steps = FLAGS.step_count
  step = (max_t - min_t) / FLAGS.step_count
  if step == 0:
    step = 1
    num_steps = max_t-min_t

  ts = np.arange(min_t, max_t+step, step)
  num_pods = (ts/int(ceil((FLAGS.target*FLAGS.target_utilization)))).astype(int)
  total_cap = num_pods*FLAGS.target
  util_cap = total_cap*FLAGS.target_utilization
  fig, graphs = plt.subplots(4)
  graphs[0].set_title('Number of Pods vs Traffic')
  graphs[0].set_ylabel('Num Pods')
  graphs[0].step(ts, num_pods, where='post', label='Num Pods')

  graphs[1].set_ylabel('Requests')
  graphs[1].set_title('Effective vs Total Capacity')
  graphs[1].step(ts, total_cap, where='post', label='Total Capacity')
  graphs[1].step(ts, util_cap, where='post', label='Effective Capacity')


  avl_cap = total_cap-ts
  exc_cap = avl_cap-FLAGS.tbc
  graphs[2].set_ylabel('Requests')
  graphs[2].set_title('Available vs Excess Capacity')
  graphs[2].step(ts, exc_cap, where='post', label='Excess Capacity')
  graphs[2].step(ts, avl_cap, where='post', label='Available Capacity')

  proxy = exc_cap / np.absolute(exc_cap)
  graphs[3].set_ylabel('Proxy Mode?')
  graphs[3].step(ts, proxy, 'g^', where='post', label='Proxy?')


  for g in graphs:
    g.legend()
    g.grid(True)
    g.set_xlabel('Concurrent Requests')
  plt.show()

if __name__ == '__main__':
  app.run(main)


