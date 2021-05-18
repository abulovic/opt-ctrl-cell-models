import json
from collections import OrderedDict


def get_list_for_tpp(item_list, datatype, list_name, line_prefix, id_suffix=''):
	first_string = '%s%s %s;' % (line_prefix, datatype, ', '.join('%s%s' % (item['name'], id_suffix) for item in item_list))
	str_list = [first_string]
	for idx, item in enumerate(item_list):
		str_list.append('%s%s%s = %s[%s];' % (line_prefix, item['name'], id_suffix, list_name, idx))
	return '\n'.join(str_list)


def create_def_file(problem_description, dest_folder):
	dest_file = '%s/problem.def' % dest_folder
	with open(dest_file, 'w') as fout:
		# Time information
		fout.write('# Initial and final time :\n')
		fout.write('time.free string %s\n' % problem_description['time']['free'])
		fout.write('time.initial double %f\n' % problem_description['time']['initial'])
		fout.write('time.final double %f\n' % problem_description['time']['final'])

		# Problem dimensions
		fout.write('\n# Dimensions:\n')
		fout.write('state.dimension integer %d\n' % len(problem_description['states']))
		fout.write('control.dimension integer %d\n' % len(problem_description['controls']))
		fout.write('algebraic.dimension integer %d\n' % len(problem_description['algebraic']))
		fout.write('parameter.dimension integer %d\n' % len(problem_description['parameters']))
		fout.write('constant.dimension integer %d\n' % len(problem_description['constants']))
		fout.write('boundarycond.dimension integer %d\n' % len(problem_description['boundarycond']))
		fout.write('constraint.dimension integer %d\n' % len(problem_description['pathconstraints']))

		# Discretization
		fout.write('\n# Discretization: \n')
		fout.write('discretization.steps integer %d\n' % problem_description['discretization']['steps'])
		fout.write('discretization.method string %s\n' % problem_description['discretization']['method'])

		# Further numerical details:
		fout.write('%s\n' % problem_description['fixed_part'])

		# All identifiers
		classes = OrderedDict()
		classes['states'] = 'state'
		classes['controls'] = 'control'
		classes['algebraic'] = 'algebraic'
		classes['parameters'] = 'parameter'
		classes['constants'] = 'constant'
		classes['boundarycond'] = 'boundarycond'
		classes['pathconstraints'] = 'constraint'
		for _class, prefix in classes.items():
			fout.write("\n# %s: \n" % _class)
			for idx, _item in enumerate(problem_description[_class]):
				fout.write('%s.%d string %s\n' % (prefix, idx, _item['name']))

		fout.write('\nsolution.file string %s\n' % problem_description['solution']['file'])


def create_bounds_file(problem_description, dest_folder):
	dest_file = '%s/problem.bounds' % dest_folder
	with open(dest_file, 'w') as fout:
		fout.write('''# This file contains all the bounds of your problem.
# Bounds are stored in standard format : 
# [lower bound]  [upper bound] [type of bound]

# Dimensions (i&f conditions, y, u, z, p, path constraints) :\n'''
	)
		order = ['boundarycond', 'states', 'controls', 'algebraic', 'parameters', 'pathconstraints']
		dimensions = ' '.join([str(len(problem_description[item])) for item in order])
		fout.write('%s\n' % dimensions)

		for _class in order:
			fout.write('\n# %s\n' % _class)
			for _item in problem_description[_class]:
				fout.write('%.0e %.0e %s\n' % (_item['bound']['lb'], _item['bound']['ub'], _item['bound']['type']))


def create_constants_file(problem_description, dest_folder):
	dest_file = '%s/problem.constants' % dest_folder
	with open(dest_file, 'w') as fout:
		fout.write('''# This file contains the values of the constants of your problem.
# Number of constants used in your problem : \n''')
		fout.write('%d\n\n' % len(problem_description['constants']))

		for _const in problem_description['constants']:
			fout.write('# %s\n' % _const['name'])
			fout.write('%e\n' % _const['value'])

# def get_list_for_tpp(item_list, datatype, list_name, line_prefix, id_suffix=''):
 
def create_boundarycond_file(problem_description, dest_folder):
	dest_file = '%s/boundarycond.tpp' % dest_folder
	with open(dest_file, 'w') as fout:
		fout.write('#include "header_boundarycond"\n')
		fout.write('#include <math.h>\n')
		fout.write('{\n')

		fout.write(get_list_for_tpp(problem_description['constants'], 'double', 'constants', '\t'))
		fout.write('\n\n')
		fout.write(get_list_for_tpp(problem_description['states'], 'Tdouble', 'initial_state', '\t', '_t0'))
		fout.write('\n\n')
		fout.write(get_list_for_tpp(problem_description['states'], 'Tdouble', 'final_state', '\t', '_tf'))
		fout.write('\n\n')

		for idx, boundarycond in enumerate(problem_description['boundarycond']):
			fout.write('\t// %s\n' % boundarycond['name'])
			fout.write('\tboundary_conditions[%d] = %s;\n' % (idx, boundarycond['expression']))

		fout.write('\n}\n')

def create_dynamics_file(problem_description, dest_folder):
	dest_file = '%s/dynamics.tpp' % dest_folder
	with open(dest_file, 'w') as fout:
		fout.write('#include "header_dynamics"\n')
		fout.write('{\n')

		fout.write(get_list_for_tpp(problem_description['algebraic'], 'Tdouble', 'algebraicvars', '\t'))
		fout.write('\n\n')
		fout.write(get_list_for_tpp(problem_description['constants'], 'double', 'constants', '\t'))
		fout.write('\n\n')
		fout.write(get_list_for_tpp(problem_description['states'], 'Tdouble', 'state', '\t'))
		fout.write('\n\n')
		fout.write(get_list_for_tpp(problem_description['controls'], 'Tdouble', 'control', '\t'))
		fout.write('\n\n')

		for idx, state in enumerate(problem_description['states']):
			fout.write('\t// %s\n' % state['name'])
			fout.write('\tstate_dynamics[%d] = %s;\n' % (idx, state['expression']))

		fout.write('\n}\n')
	

def create_pathcond_file(problem_description, dest_folder):
	dest_file = '%s/pathcond.tpp' % dest_folder
	with open(dest_file, 'w') as fout:
		fout.write('#include "header_pathcond"\n')
		fout.write('#include <math.h>\n')
		fout.write('{\n')

		fout.write(get_list_for_tpp(problem_description['algebraic'], 'Tdouble', 'algebraicvars', '\t'))
		fout.write('\n\n')
		fout.write(get_list_for_tpp(problem_description['constants'], 'double', 'constants', '\t'))
		fout.write('\n\n')
		fout.write(get_list_for_tpp(problem_description['states'], 'Tdouble', 'state', '\t'))
		fout.write('\n\n')
		fout.write(get_list_for_tpp(problem_description['controls'], 'Tdouble', 'control', '\t'))
		fout.write('\n\n')

		for idx, pathconstraint in enumerate(problem_description['pathconstraints']):
			fout.write('\t// %s\n' % pathconstraint['name'])
			fout.write('\tpath_constraints[%d] = %s;\n' % (idx, pathconstraint['expression']))

		fout.write('\n}\n')

def create_criterion_file(problem_description, dest_folder):
	dest_file = '%s/criterion.tpp' % dest_folder
	with open(dest_file, 'w') as fout:
		fout.write('#include "header_criterion"\n')
		fout.write('{\n')

		fout.write(get_list_for_tpp(problem_description['states'], 'Tdouble', 'final_state', '\t'))
		fout.write('\n\n')
		fout.write('\tcriterion = %s;\n' % problem_description['criterion'])

		fout.write('\n}\n')
	


def create_bocop_files(problem_description, dest_folder):
	create_def_file(problem_description, dest_folder)
	create_bounds_file(problem_description, dest_folder)
	create_constants_file(problem_description, dest_folder)
	create_boundarycond_file(problem_description, dest_folder)
	create_dynamics_file(problem_description, dest_folder)
	create_pathcond_file(problem_description, dest_folder)
	create_criterion_file(problem_description, dest_folder)


def load_description_file(descr_fpath):
	with open(descr_fpath) as fin:
		problem_description = json.loads(fin.read())
	return problem_description

def create_bocop_problem(descr_fpath, dest_folder):
	problem_description = load_description_file(descr_fpath)
	create_bocop_files(problem_description, dest_folder)


if __name__ == '__main__':
	import sys 

	if len(sys.argv) < 3:
		print("\nUsage: python create_bocop_files.py [PROBLEM_DEF_JSON_FILE] [DESTINATION_DIR]\n")
		sys.exit()
	create_bocop_problem(sys.argv[1], sys.argv[2])