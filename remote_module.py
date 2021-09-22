"""
This module manages packages, which involves 
	1. installing them via pip
	2. accessing their doc strings
	3. returning said modules as objects
"""
import httpimport
import importlib

class RemoteModule:
	def __init__(self, source='github', user='austinwindsor', module_name='SampleModule',branch='master'):
		"""
		Args:
		    source (str): github, bitbucket, gitlab CURRENTLY NOT IMPLEMENTED
		    user (str): user of the source where the module is stored remotely
		    module_name (str): module name, where submodules can be accessed by module.submodule convention
		    branch (str): branch of the module to use
		
		"""
		self.source = source
		self.user = user
		self.module_name = module_name
		self.branch = branch

	def __str__(self):
		return "RemoteModule( source=%s, user=%s, module_name=%s, branch=%s)" % (source, user, module_name, branch)

	def load(self, return_module=True):
		with httpimport.github_repo(self.user, self.module_name.split('.')[0], branch=self.branch):
			module = importlib.import_module(self.module_name)
			globals()[self.module_name.split('.')[-1]] = module
			if return_module:
				return module

