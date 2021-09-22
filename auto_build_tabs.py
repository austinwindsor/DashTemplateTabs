"""Summary
"""
from importlib import import_module
import os
from glob import glob

import sys
import re

from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from collections import OrderedDict

from app import app
import docstring_parser

import pandas as pd

import logging

#### PARAMETERS #####
# FUNCTIONS_DIR = 'funcs'
# FILE_HANDLE = ".py"
# ARGPARSE_PARSER = "parser"

# ARGPARSE_HELP_COMMANDS = ['--help','-h']

# tabs = [f for f in os.listdir(FUNCTIONS_DIR) if FILE_HANDLE in f.lower()]

def pretty_format(string):
	return string.replace("_"," ").title()

def get_argparse_parameters(script, argparser_parser='parser', file_handle='.py', 
									argparse_help_commands = ['--help','-h']):
	"""
	this function will import a function with an Argparse.parser object and return a dicitonary of its command line
	arguments and their data types

	:param script: the script denoted as a submodule (ex: module.submodule)
	:param argparser_parser: the variable name in which the Argparse.parser object is stored (default: 'parser')
	:param file_handle: this cleans the script name in case the file hand in included by accident (default: '.py')
	:argparse_help_commands: this is a list of ineligible command line arguments to consider in the output
	"""
	func = script.replace(file_handle,'')
	func_parsers = getattr( import_module(func), argparser_parser)
	func_param_dtypes = OrderedDict([(k,v) for k,v in func_parsers._option_string_actions.items()
						if k not in argparse_help_commands])
	# print( {func: func_param_dtypes} )
	return {func: {"parameters": func_param_dtypes, "description": func_parsers.prog}}\

def get_method_parameters(module, run_method='run', display_name=""):
    """Summary
    
    Args:
        method_name (TYPE): Description
    """
    display_name = display_name if display_name else module.__name__.split('.')[0]
    method_parsing = docstring_parser.parse(getattr(module,run_method).__doc__)
    parameters = method_parsing.params
    description = method_parsing.short_description +'\n'+method_parsing.long_description
    return {display_name: {'parameters':[param for param in parameters], "description": description}}


def param_to_dash_elem(argparse_store_action, function_name):
	"""
	This method converts an Argparse.parser._StoreAction object into an appropriate input field. 
	A integer,string parameter will use a empty field.
	A parameter with specific choices to choose from will use a dcc.dropdown field.
	A parameter with many entries is still unclear how to handle.	
	All parameters with default values will have that value prepopulated in the input field.
	"""
	param_name = argparse_store_action.arg_name
	dtype = str(argparse_store_action.type_name)
	default = argparse_store_action.default
	help_str = argparse_store_action.description
	optional_status = argparse_store_action.is_optional
	choices = set(re.findall("\{(.+)\}", help_str)[0].split(',')) if len(re.findall("\{(.+)\}", help_str))>0 else None
	print(help_str, choices)

	id_name = 'parameter_%s_%s' % (function_name, param_name)
	type_map = {'int': 'number', 'str': 'text', 'float': 'number'}

	if choices is None:
		output_dash_elem = dbc.Row([ dbc.Col(html.Label(pretty_format(param_name), title=help_str)), 
											dbc.Col(dcc.Input(id=id_name, 
															type=type_map.get(dtype,'text'), 
															placeholder=str(default)))])
	else:
		output_dash_elem = dbc.Row([ dbc.Col(html.Label(pretty_format(param_name), title=help_str)), 
									dbc.Col(dcc.Dropdown(id=id_name, options=[{'label':c, 'value':c} 
																				for c in choices]
														, value=default))])
	# print(output_dash_elem)
	return output_dash_elem

def dash_tab_for_cmd_args(function_parameters):
	"""
	This method will iterate through a function command line arguments and return a tab layout for the function
	
	:param function_parameters: a dict of dicts, the funciton name : [{ argument: Argparse._StoreAction }]
	"""
	function_name = list(function_parameters.keys())[0].replace('-','').split('.')[-1]
	func_pretty_name = pretty_format(function_name)
	parameters = list(function_parameters.values())[0]['parameters']
	description = list(function_parameters.values())[0]['description']
	logging_screen = dbc.Card([
						dbc.CardHeader("Logging Screen"),
						dbc.CardBody(dcc.Markdown(id=function_name+"-"+"log1"), id=function_name+"-"+"log")
		])
	param_screen = dbc.Card(children=[
						dbc.CardHeader("Input Parameters"),
						dbc.CardBody([
							param_to_dash_elem(store_action, function_name) for store_action
							in parameters
							])
		])
	description_screen = dbc.Card(children=[
						dbc.CardHeader("Description"),
						dbc.CardBody(dcc.Markdown(description))

		])
	return dcc.Tab(id=function_name+"-"+"tab",
					label=func_pretty_name,
					children = html.Div( [  dbc.Row( dbc.Col(description_screen)),
											dbc.Row([ dbc.Col(param_screen), dbc.Col(logging_screen)]),
											dbc.Row( [dbc.Col(html.Button("Execute %s" % func_pretty_name, 
																			id=function_name+"-"+"button")),
													dbc.Col([html.Button("Download Output", 
																			id=function_name+"-"+"downloadButton"),
															dcc.Download(id=function_name+"-"+"download")]) ]),
											dcc.Interval(id=function_name+"-"+'loggingInterval', interval=1*1000, n_intervals=0)
											]))

def build_tab_per_function(module_objs, run_method='run', ignore_parameters=['--help','-h']):
	"""
	function to create a list of dcc.Tabs where each tab contains input elements for each function parameter
	
	Args:
	    module_objs (list of [modules]): modules or submodules for which to create a Dash Plotly interface
	    run_method (str): name of the method that contains the run parameters for task
	    ignore_parameters (list of [str], optional): list of parameters to not include in visualization
	
	Returns:
	    list of [dash_core_component.Tab]: a list of the tabs to visualize
	"""
	func_parameters = list(map(lambda func: get_method_parameters(func['module'], run_method=run_method, 
																	display_name=func['display_name']),
							[f for f in module_objs]))
	tabs = list(map(dash_tab_for_cmd_args, func_parameters))
	return tabs


def build_dynamic_callbacks(module_objs, run_method='run', argparse_help_commands=['--help','-h']):
	"""
	function to create many dynamic callback functions linked to each element explicitly

	:param module_paths: a list of the paths to each function to visualize
	:param argparse_parser: the name of the variable of the Argparse.parser object in the scripts
	:param argparse_help_commands: the helper command line arguments to exclude when visualizing the command line arguments
	"""
	func_parameters = list(map(lambda func: get_method_parameters(func['module'], run_method=run_method, 
																	display_name=func['display_name']),
							[f for f in module_objs]))
	modules = [f['module'] for f in module_objs]

	for mod, func in zip( modules, func_parameters):
		parameters = list(func.values())[0]['parameters']#list(list(func.values())[0].keys())

		func_path = list(func.keys())[0].replace('.','/') +".py"
		clean_func_name = list(func.keys())[0]

		@app.callback(
			Output(clean_func_name+"-download", "data"),
			Input("%s-button" % clean_func_name, "n_clicks"),
			[State("parameter_%s_%s" % (clean_func_name, inp.arg_name),'value') for inp in parameters]
			)
		def func(nclicks, *args, parameters=parameters, func_path=func_path):
			arguments = args
			nclicks = nclicks
			if nclicks:
				parameter_str = ' '.join(['%s "%s"' % (str(param.arg_name), str(value)) for param, value in zip(parameters, arguments)])
				data = getattr(mod, run_method)(**{param.arg_name:a for param, a in zip(parameters, args)})
				command = 'python %s %s' % (func_path, parameter_str)
				logging.info(command)
				# os.system(command)
				# print(globals()['log_capture_string'].get_value())
				return  dcc.send_data_frame(data.to_excel, 'sample.xlsx')

		# @app.callback(
		# 	Output(clean_func_name+"-download","data"),
		# 	Input(clean_func_name+"-downloadButton", "n_clicks"),
		# 	prevent_initial_callback=True
		# 	)
		# def download(n_clicks):
		# 	df = pd.DataFrame({'a':[1,2]})
		# 	return dcc.send_data_frame(df.to_excel, 'sample.xlsx')

		@app.callback(
			Output(clean_func_name+'-log1', 'children'),
			Input(clean_func_name+'-loggingInterval', 'n_intervals')
			)
		def log_screen(*args):
			with open('app.log', 'r') as f:
				return f.read()
		
		globals()['execute_%s' % clean_func_name] = func
		globals()['log_%s' % clean_func_name] = log_screen

