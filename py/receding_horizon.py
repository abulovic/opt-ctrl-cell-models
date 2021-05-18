import os
import sys
import math 
import tarfile
import shutil
import datetime
from collections import defaultdict
import matplotlib.pyplot as plt


from generate_variables import get_problem
from load_result import get_dynamics
from create_bocop_files import *
from BocopUtils import *
from utils import *


# for when running the script from the ./py directory of the repo
BUILD_FILE = "./build.sh"

MODEL_NUM = 8
MODELS_DIR = '../cell_models_mRNA/'
model_directory = '%s/model_%d' % (MODELS_DIR, MODEL_NUM)
RUN = 'run_directory'

clean = 1
debug = 0
verbose = 1

index_to_take = 1


T_VEC = [27, 40]
TIMESTEP = 300
STOP_TIME = TIMESTEP * len(T_VEC)

PLOT_COMPARISON = False


def save_to_file(time, _ids, dynamics, dest_file):
	with open(dest_file, 'w') as fout:
		fout.write('Time\n')
		fout.write(';'.join([str(num) for num in time]))
		fout.write('\n')
		for _idx in sorted(_ids.keys()):
			_id = _ids[_idx]
			fout.write('%s\n' % _id)
			fout.write(';'.join([str(val) for val in dynamics[_id]]))
			fout.write('\n')


def store_results(run_directory, storage_dir, time_vector, rh_state_dynamics, rh_control_dynamics, rh_algebraic_dynamics, rh_adjoint_dynamics):

	for _dir in ('./_bocop', './_json', './_plots', './_results'):
		if os.path.isdir(_dir):
			shutil.rmtree(_dir)
		os.mkdir(_dir)

	problem_def_fpath = '%s/problem.def' % run_directory
	problem_sol_fpath = '%s/problem.sol' % run_directory
	states, controls, algebraic_vars, parameters, constants, boundary_conds, constraints = get_problem(problem_def_fpath)
	state_dynamics, control_dynamics, algebraic_dynamics, adjoint_dynamics, constant_values, time,final_time = get_dynamics(problem_def_fpath, problem_sol_fpath)
	model = 'v%d' % MODEL_NUM

	if not os.path.isdir(storage_dir):
		os.mkdir(storage_dir)

	now = str(datetime.datetime.now())
	now = now.split('.')[0]
	dest_dir = '%s/%s-%s' % (storage_dir, model, now)
	os.mkdir(dest_dir)

	save_to_file(time_vector, states, rh_state_dynamics, '%s/states.txt' % dest_dir)
	save_to_file(time_vector, controls, rh_control_dynamics, '%s/controls.txt' % dest_dir)
	save_to_file(time_vector, algebraic_vars, rh_algebraic_dynamics, '%s/algebraic.txt' % dest_dir)

	plot(time_vector, states, rh_state_dynamics, '%s/states.pdf' % dest_dir, constant_values, multiply_by_len=True)
	plot(time_vector, controls, rh_control_dynamics, '%s/controls.pdf' % dest_dir, constant_values)
	plot(time_vector, algebraic_vars, rh_algebraic_dynamics, '%s/algebraic.pdf' % dest_dir, constant_values)
	plot(time_vector, states, rh_adjoint_dynamics, '%s/adjoint.pdf' % dest_dir, constant_values)

	bocop_files_to_store = ['problem.def',
					  'problem.sol',
					  'problem.bounds',
					  'problem.constants',
					  'boundarycond.tpp',
					  'dynamics.tpp',
					  'pathcond.tpp',
					  'criterion.tpp']
	

	fp = tarfile.open('model.tar.gz', 'w:gz')
	# Add Bocop files
	for fname in bocop_files_to_store:
		shutil.copyfile('%s/%s' % (run_directory, fname), '_bocop/%s' % fname)
		fp.add('_bocop/%s' % fname)
	# Add JSON files
	shutil.copyfile('%s/t0/model_%d_t0.json' % (model_directory, MODEL_NUM),
		            '_json/model_%d_t0.json' % MODEL_NUM)
	fp.add('_json/model_%d_t0.json' % MODEL_NUM)
	shutil.copyfile('%s/t-non0/model_%d_t_non0.json' % (model_directory, MODEL_NUM),
		            '_json/model_%d_t_non0.json' % MODEL_NUM)
	fp.add('_json/model_%d_t_non0.json' % MODEL_NUM)
	# Add plots & results in text format
	for suffix, folder in {'pdf': '_plots', 'txt': '_results'}.items():
		for _file in ('states', 'controls', 'algebraic'):
			shutil.copyfile('%s/%s.%s' % (dest_dir, _file, suffix),
				            '%s/%s.%s' % (folder, _file, suffix))
			fp.add('%s/%s.%s' %  (folder, _file, suffix))

	fp.close()
	shutil.move('model.tar.gz', '%s/model.tar.gz' % dest_dir)
	for _dir in ('./_bocop', './_json', './_plots', './_results'):
		shutil.rmtree(_dir)
		os.mkdir(_dir)


def solve_problem(problem_definition, problem_dir, build=False):
	'''
	Using the existing problem definition provided as an argument,
	the function builds (if necessary) and solves the optimization 
	problem.
	In case the optimization run is unsuccessful, it increases the 
	number of optimization steps used.
	This number is restored at the end of the run.
	'''
	current_dir = os.getcwd()
	original_timesteps = problem_definition['discretization']['steps']
	shutil.copyfile(BUILD_FILE, '%s/build.sh' % problem_dir)
	os.chdir(problem_dir)

	if not os.path.isdir('./init'):
		os.mkdir('init')
	if build:
		buildProblem(clean, debug, verbose=0)
		print('Problem built.')
	status = -1
	while status != 0:
		status = launchProblem(1, 1000, 0)
		if status == 0:
			break
		new_step_count = problem_definition['discretization']['steps'] + 1
		print('\tIncreasing number of discretization steps to %d.' % new_step_count)

		problem_definition['discretization']['steps'] = new_step_count
		create_def_file(problem_definition, './')

	# state_dynamics, control_dynamics, algebraic_dynamics, constant_values, time,final_time
	result = get_dynamics('problem.def', 'problem.sol')
	problem_definition['discretization']['steps'] = original_timesteps
	create_def_file(problem_definition, './')
	os.chdir(current_dir)
	return result



def check_consistency(t0_model_file, t_non0_model_file):

	prob_t0 = load_description_file(t0_model_file)
	prob_t_non0 = load_description_file(t_non0_model_file)

	things_to_check = {
	'states': 'expression',
	'constants': 'value',
	'boundarycond': 'expression',
	'pathconstraints': 'expression'
	}

	for category, to_check in things_to_check.items():
		name2to_check_t0 = {c['name']: c[to_check] for c in prob_t0[category]}
		name2to_check_t_non0 = {c['name']: c[to_check] for c in prob_t_non0[category]}
		common = set(name2to_check_t0.keys()) & set(name2to_check_t_non0.keys())

		for thing in common:
			if name2to_check_t0[thing] != name2to_check_t_non0[thing]:
				print('Value for %s %s different in two models.' % (category, thing))
				print('T0: %s' % str(name2to_check_t0[thing]))
				print('T-non0: %s' % str(name2to_check_t_non0[thing]))
				print()



if __name__ == '__main__':
	# Files
	t0_model_file = '%s/t0/model_%d_t0.json' % (model_directory, MODEL_NUM)
	t_non0_model_file = '%s/t-non0/model_%d_t_non0.json' % (model_directory, MODEL_NUM)
	run_directory = '%s/%s' % (model_directory, RUN)
	storage_directory = '%s/results' % model_directory

	check_consistency(t0_model_file, t_non0_model_file)
	# Get problem definition
	problem_definition_t0 = load_description_file(t0_model_file)

	# SET UP INITIAL TEMPERATURE
	for constant in problem_definition_t0['constants']:
		if constant['name'] == 'T':
			constant['value'] = T_VEC[0]



	# Create t0 model in the test directory
	# create_bocop_problem('%s/t0/model_%d_t0.json' % (model_directory, MODEL_NUM),
						 # run_directory)
	create_bocop_files(problem_definition_t0, run_directory)
	print('Initial t0 Bocop problem created in run directory')

	(states, controls, algebraic, adjoints, _, time, final_time) = solve_problem(problem_definition_t0, 
																	   run_directory,
																	   build=True)

	first_index_to_take = 1

	time_vector = [time[0], time[first_index_to_take]]
	
	print('Initial problem simulated.')
	print('Time = %f' % time_vector[-1])
	print('mu = %e' % algebraic['mu'][1])

	rh_state_dynamics = defaultdict(list)
	rh_control_dynamics = defaultdict(list)
	rh_algebraic_dynamics = defaultdict(list)
	rh_adjoint_dynamics = defaultdict(list)

	for state, dyn in states.items():
		rh_state_dynamics[state].append(dyn[0])
		rh_state_dynamics[state].append(dyn[first_index_to_take])
	for ctrl, dyn in controls.items():
		rh_control_dynamics[ctrl].append(dyn[0])
		rh_control_dynamics[ctrl].append(dyn[first_index_to_take])
	for alg, dyn in algebraic.items():
		rh_algebraic_dynamics[alg].append(dyn[0])
		rh_algebraic_dynamics[alg].append(dyn[first_index_to_take])
	for ad_state, dyn in adjoints.items():
		rh_adjoint_dynamics[ad_state].append(dyn[0])
		rh_adjoint_dynamics[ad_state].append(dyn[first_index_to_take])



	# Non zero time now
	problem_definition_t_non0 = load_description_file(t_non0_model_file)
	initial = True
	step = 1
	while(time_vector[-1] < STOP_TIME):

		t_idx = int(time_vector[-1]) // TIMESTEP
		new_T = T_VEC[t_idx]

		if new_T > 0:
			for constant in problem_definition_t_non0['constants']:
				if constant['name'] == 'T':
					constant['value'] = new_T

		for state, dyn in rh_state_dynamics.items():
			constant_name = '%s_0' % state
			for constant in problem_definition_t_non0['constants']:
				if constant['name'] == constant_name:
					constant['value'] = dyn[-1]

		create_bocop_files(problem_definition_t_non0, run_directory)
		print('Bocop files created for step %d.' % step)
		if initial:
			(states, controls, algebraic, adjoints, _, time, final_time) = solve_problem(problem_definition_t_non0,
								run_directory,
								build=True)
			initial = False
		else:
			(states, controls, algebraic, adjoints, _, time, final_time) = solve_problem(problem_definition_t_non0,
								run_directory,
								build=False)
		print('Bocop problem ran for step %d.' % step)
		print('Time = %f' % time_vector[-1])
		print('mu = %e' % algebraic['mu'][1])

		for state, dyn in states.items():
			rh_state_dynamics[state].append(dyn[index_to_take])
		for ctrl, dyn in controls.items():
			rh_control_dynamics[ctrl].append(dyn[index_to_take])
		for alg, dyn in algebraic.items():
			rh_algebraic_dynamics[alg].append(dyn[index_to_take])
		for ad_state, dyn in adjoints.items():
			rh_adjoint_dynamics[ad_state].append(dyn[index_to_take])
		time_vector.append(time[index_to_take] + time_vector[-1])
		step = step + 1


	store_results(run_directory, 
				  storage_directory,
				  time_vector,
				  rh_state_dynamics,
				  rh_control_dynamics,
				  rh_algebraic_dynamics,
				  rh_adjoint_dynamics)

	if PLOT_COMPARISON:
		_dir = model_directory + '/opt-ctrl/'
		states, controls, algebraic_vars, parameters, constants, boundary_conds, constraints = get_problem('%s/problem.def' % _dir)
		state_dynamics, control_dynamics, algebraic_dynamics, adjoint_dyanmics, constant_values, time, final_time = get_dynamics('%s/problem.def' % _dir, '%s/problem.sol' % _dir)
		selected_states = ['R', 'C', 'P', 'E_sf', 'E_ca_f', 'E_ts_f']
		num_cols = len(selected_states) + 1
		num_rows = 2
		plt.figure(figsize=(2.5*num_cols, 2.5*num_rows))
		ax = plt.gca()
		ax.set_facecolor('#ffffff')
		plt.subplot(num_rows, num_cols, 1)
		plt.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
		plt.plot(time, algebraic_dynamics['mu'], '-')
		plt.title('mu')

		# plot the states
		for idx, state in enumerate(selected_states, 2):
			plt.subplot(num_rows, num_cols, idx)
			plt.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
			_len = float(get_length(constant_values, state))
			dyn = [d * _len for d in state_dynamics[state]]
			plt.plot(time, dyn, '-')
			plt.title(state)

		# plot mu from receding horizon
		plt.subplot(num_rows, num_cols, num_cols + 1)
		plt.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
		plt.plot(time_vector, rh_algebraic_dynamics['mu'], '-')

		# plot the states
		for idx, state in enumerate(selected_states, 2):
			plt.subplot(num_rows, num_cols, num_cols + idx)
			plt.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
			_len = float(get_length(constant_values, state))
			dyn = [d * _len for d in rh_state_dynamics[state]]
			plt.plot(time_vector, dyn, '-')

		plt.tight_layout()

		plt.savefig('comparison.pdf', type='pdf')
		plt.savefig('comparison.svg', type='svg')
