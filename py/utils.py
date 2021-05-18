import os
import shutil
import math
import matplotlib.pyplot as plt

def get_length(constants, var):
	for c, val in constants.items():
		full_name = 'n_%s' % var
		if full_name.startswith(c):
			return val
	return 1

def plot(tvec, names, dynamics, destination, const_vals, title='', multiply_by_len=False, col_num=5):
	num = len(names)
	num_cols = min(num, col_num)
	num_rows = int(math.ceil(num / float(num_cols)))
	plt.figure(figsize=(2.5*num_cols, 2.5*num_rows))
	for idx, _id in names.items():
		dyn = dynamics[_id]
		if multiply_by_len:
			_len = float(get_length(const_vals, _id))
			dyn = [d * _len for d in dyn]
		plt.subplot(num_rows, num_cols, idx+1)
		plt.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
		plt.plot(tvec, dyn, '-')
		plt.title(_id)
	plt.tight_layout()
	plt.suptitle(title)
	# plt.show()
	plt.savefig(destination, type='pdf')

def copy_model(_from, _to, delete=True):
	if delete:
		for _file in os.listdir(_to):
			if os.path.isdir('%s/%s' % (_to, _file)):
				shutil.rmtree('%s/%s' % (_to, _file))
			elif _file == 'bocop':
				continue
			else:
				os.remove('%s/%s' % (_to, _file))
	for _file in os.listdir(_from):
		if os.path.isfile('%s/%s' % (_from, _file)):
			shutil.copyfile('%s/%s' % (_from, _file), '%s/%s' % (_to, _file))

