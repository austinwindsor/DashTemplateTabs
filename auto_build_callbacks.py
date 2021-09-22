from importlib import import_module
import os
from glob import glob

from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from collections import OrderedDict
from auto_build_tabs import get_argparse_parameters

def build_dynamic_callbacks(module_paths, argparse_parser='parser', argparse_help_commands=['--help','-h']):
	func_parameters = list(map(lambda func: get_argparse_parameters(func, argparser_parser=argparse_parser),
						[f.replace("/",'.').replace('\\','.') for f in module_paths]))
	for func in func_parameters:

		@app.callback(
			Output()
			)