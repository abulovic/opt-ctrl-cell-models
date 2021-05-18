import sys
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

from generate_variables import get_problem


def get_dynamics(def_fpath, sol_fpath):

	states, controls, algebraic_vars, parameters, constants, boundary_conds, constraints = get_problem(def_fpath)

	state_dynamics = defaultdict(list)
	control_dynamics = defaultdict(list)
	algebraic_dynamics = defaultdict(list)
	adjoint_dynamics = defaultdict(list)
	constant_values = dict()


	num_constants = len(constants)
	with open(sol_fpath) as fin:
		for line in fin:
			line = line.strip()
			if line.startswith('# # Values of the constants :'):
				for i in range(num_constants):
					constant = constants[i]
					constant_values[constant] = float(fin.readline()[2:])


	mu = list()
	final_time = 0
	time_steps = 0
	load = False
	load_final_time = True
	counter = 0
	with open(sol_fpath, 'r') as fin:
		for line in fin:
			line = line.strip()
			if line.startswith('# discretization.steps integer'):
				time_steps = int(line.split()[-1])

			if load_final_time and line.startswith('# time.final double'):
				final_time = float(line.split()[-1])
				load_final_time = False

			if load:
				for i in range(time_steps):
					repo[_id].append(float(line))
					line = fin.readline()
				load = False

			if line.startswith('# State'):
				num = int(line.split()[-1])
				repo = state_dynamics
				_id = states[num]
				load = True

			if line.startswith('# Control'):
				num = int(line.split()[-1])
				repo = control_dynamics
				_id = controls[num]
				load = True

			if line.startswith('# Parameters'):
				load_final_time = True

			if line.startswith('# Algebraic'):
				num = int(line.split()[-1])
				repo = algebraic_dynamics
				_id = algebraic_vars[num]
				load = True

			if line.startswith('# Adjoint state'):
				num = int(line.split()[-1])
				repo = adjoint_dynamics
				_id = states[num]
				load = True

	dt = 1. / time_steps
	time = np.linspace(0, final_time, time_steps)
	return state_dynamics, control_dynamics, algebraic_dynamics, adjoint_dynamics, constant_values, time, final_time


if __name__ == '__main__':

	def_fpath = sys.argv[1]
	sol_fpath = sys.argv[2]

	states, controls, algebraic_vars, parameters, constants, boundary_conds, constraints = get_problem(def_fpath)
	state_dynamics, control_dynamics, algebraic_dynamics, constant_values, time,final_time = get_dynamics(def_fpath, sol_fpath)

	num = len(state_dynamics) + 1
	cols = 2
	rows = int(np.ceil(num / float(cols)))

	c1 = next(plt.gca()._get_lines.prop_cycler)['color']
	c2 = next(plt.gca()._get_lines.prop_cycler)['color']
	c3 = next(plt.gca()._get_lines.prop_cycler)['color']

	for i in range(rows):
		for j in range(cols):
			idx = i * cols + j
			if idx == num-1:
				ax = plt.subplot(rows, cols, idx+1)
				plt.ticklabel_format(axis='y', style='sci', scilimits=(-3, 3))
				ax.plot(time, np.array(algebraic_dynamics['mu']) * 60, color=c3)
				ax.set_ylabel('growth rate')
				break
			
			state = states[idx]
			if state in ('X', 'S_ext'):
				color = c2
			else:
				color = c1
			ax = plt.subplot(rows, cols, idx+1)
			plt.ticklabel_format(axis='y', style='sci', scilimits=(-3, 3))
			ax.plot(time, state_dynamics[state], color=color)
			ax.set_ylabel(state)


	plt.tight_layout()
	plt.suptitle('tf=%.2f, Xf=%e' % (final_time, state_dynamics['X'][-1]))
	plt.show()

	#density_occupancy =  constant_values['n_HP'] * np.array(state_dynamics['HP']) / constant_values['D_c']
	#plt.plot(time, density_occupancy)
	#plt.ticklabel_format(axis='y', style='plain')
	#plt.show()

	print (state_dynamics['X'][-1])

