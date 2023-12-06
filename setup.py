from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
	name='deeprtalign',
	version="1.2.2",
	packages=find_packages(),
	python_requires='>=3.4',
	install_requires=[
						'xlrd==1.2.0',
						'pandas>=0.24',
		],

	package_data={
		'deeprtalign': ['data/params.pt']
		},

	author='Yi Liu',
	author_email='leoicarus@163.com',
	description='retention time alignment tool for large cohort LC-MS data analysis',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/FineLiu/deeprtalign',
	license='GPLv3',
	entry_points = {
		'console_scripts': ['deeprtalign=deeprtalign.__main__:get_arg_and_run']
		}
)