# author: Austin Windsor
import logging
logger = logging.basicConfig(filename='app.log', filemode='w',format='%(name)s - %(levelname)s - %(message)s    ')

import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc

import pandas as pd 

import json
from  base64 import urlsafe_b64encode, urlsafe_b64decode
import os, sys
from glob import glob
from importlib import import_module

import auto_build_tabs
from remote_module import RemoteModule
from app import app
from collections import OrderedDict


import io


### Send log messages. 
logging.debug('debug message')
logging.info('info message')
logging.warning('warn message')
logging.error('error message')
logging.critical('critical message')

######## PARAMETERS ###########
tab_dir = "tabs"
layout_var = "app_layout"
tab_script_common_str = "tab"


# app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# this config is necessary for multi file dash apps
app.config['suppress_callback_exceptions'] = True


# dynamic_tabs = [ getattr( 
# 					import_module(tab_dir+'.'+sub_mod.replace('.py','')), 
# 					layout_var)
# 				for sub_mod in os.listdir(tab_dir) 
# 				if tab_script_common_str in sub_mod]



modules = [{'display_name':'Project Aspen',
			'module': getattr(RemoteModule(source='github',user='austinwindsor',
									module_name='samplemodule.run',
									branch='master').load(),'Run')}]




dynamic_tabs = auto_build_tabs.build_tab_per_function(modules)

# print(dynamic_tabs)
app.layout = html.Div(children =[
		html.H3('CMS PIFO Audit Automation Dashboard'),
		dcc.Tabs(id='parent-tab', value='tabP',
			children = dynamic_tabs),
	])

auto_build_tabs.build_dynamic_callbacks(modules)




if __name__ == '__main__':
    app.run_server(debug=True)
