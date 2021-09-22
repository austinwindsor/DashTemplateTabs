from importlib import import_module
import os
from glob import glob

import sys

from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from collections import OrderedDict

from app import app

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
	return {func: {"parameters": func_param_dtypes, "description": func_parsers.prog}}


def param_to_dash_elem(argparse_store_action, param_name, function_name):
	"""
	This method converts an Argparse.parser._StoreAction object into an appropriate input field. 
	A integer,string parameter will use a empty field.
	A parameter with specific choices to choose from will use a dcc.dropdown field.
	A parameter with many entries is still unclear how to handle.
	All parameters with default values will have that value prepopulated in the input field.
	"""
	param_name = param_name.replace('-','')
	dtype = argparse_store_action.type
	default = argparse_store_action.default
	help_str = argparse_store_action.help

	id_name = 'parameter_%s_%s' % (function_name, param_name)
	type_map = {int: 'number', str: 'text', float: 'number'}

	if argparse_store_action.choices is None:
		output_dash_elem = dbc.Row([ dbc.Col(html.Label(pretty_format(param_name), title=help_str)), dbc.Col(dcc.Input(id=id_name, 
																		type=type_map.get(dtype,'text'), 
																		placeholder=str(default)))])
	else:
		output_dash_elem = dbc.Row([ dbc.Col(html.Label(pretty_format(param_name), title=help_str)), 
									dbc.Col(dcc.Dropdown(id=id_name, options=[{'label':c, 'value':c} 
																		for c in argparse_store_action.choices]
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
						dbc.CardBody(html.P(id={"type":"logging", "name":function_name+"-"+"log1"}), id=function_name+"-"+"log")
		])
	param_screen = dbc.Card(children=[
						dbc.CardHeader("Input Parameters"),
						dbc.CardBody([
							param_to_dash_elem(store_action, param_name, function_name) for param_name, store_action
							in parameters.items()
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
											dbc.Row( dbc.Col(html.Button("Execute %s" % func_pretty_name, 
												id=function_name+"-"+"button")) )]))

def build_tab_per_function(module_paths, argparse_parser='parser', argparse_help_commands=['--help','-h']):
	"""
	function to create a list of dcc.Tabs where each tab contains input elements for each function parameter

	:param module_paths: a list of the paths to each function to visualize
	:param argparse_parser: the name of the variable of the Argparse.parser object in the scripts
	:param argparse_help_commands: the helper command line arguments to exclude when visualizing the command line arguments
	"""
	func_parameters = list(map(lambda func: get_argparse_parameters(func, argparser_parser=argparse_parser),
						[f.replace("/",'.').replace('\\','.') for f in module_paths]))
	tabs = list(map(dash_tab_for_cmd_args, func_parameters))
	return tabs


def build_dynamic_callbacks(module_paths, argparse_parser='parser', argparse_help_commands=['--help','-h']):
	"""
	function to create many dynamic callback functions linked to each element explicitly

	:param module_paths: a list of the paths to each function to visualize
	:param argparse_parser: the name of the variable of the Argparse.parser object in the scripts
	:param argparse_help_commands: the helper command line arguments to exclude when visualizing the command line arguments
	"""
	func_parameters = list(map(lambda func: get_argparse_parameters(func, argparser_parser=argparse_parser),
						[f.replace("/",'.').replace('\\','.') for f in module_paths]))
	# print(func_parameters)
	for func in func_parameters:
		parameters = list(func.values())[0]['parameters']#list(list(func.values())[0].keys())

		func_path = list(func.keys())[0].replace('.','/') +".py"
		clean_func_name = list(func.keys())[0].replace('-','').split('.')[-1]

		@app.callback(
			Output(clean_func_name+"-log", "children"),
			Input("%s-button" % clean_func_name, "n_clicks"),
			[State("parameter_%s_%s" % (clean_func_name, inp.replace("-","")),'value') for inp in parameters]
			)
		def func(nclicks, *args, parameters=parameters, func_path=func_path):
			arguments = args
			nclicks = nclicks
			if nclicks:
				parameter_str = ' '.join(['%s "%s"' % (str(param), str(value)) for param, value in zip(parameters, arguments)])
				command = 'python %s %s' % (func_path, parameter_str)
				print(command)
				os.system(command)
				return command
		
		globals()['execute_%s' % clean_func_name] = func


# @app.callback(
# 	Output({"type":"logging"}, "children"),
# 	[Input({"type":"parameter"}, "value"),
# 	 Input("Consolidate_files", "nclicks"),
# 	 Input("Consolidate_files", "label")]
# 	)
# def execute_function(values, nclicks, button_name):
# 	command = "python %s %s" % (button_name, ' '.join(values))
# 	return command


# print(dash_tab_for_cmd_args(list(output)[0]))