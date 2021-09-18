# author: Austin Windsor

import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc

import pandas as pd 

import json
from  base64 import urlsafe_b64encode, urlsafe_b64decode
import os
from glob import glob
from importlib import import_module

import auto_build_tabs
from app import app

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

dynamic_tabs = auto_build_tabs.build_tab_per_function(list(glob("funcs/*.py")))

# print(dynamic_tabs)
app.layout = html.Div(children =[
		html.Div('Austin Windsor Template'),
		dcc.Tabs(id='parent-tab', value='tabP',
			children = dynamic_tabs),
	])

auto_build_tabs.build_dynamic_callbacks(list(glob("funcs/*.py")))




if __name__ == '__main__':
    app.run_server(debug=False)
