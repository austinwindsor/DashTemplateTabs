import argparse
import pandas as pd 
from glob import glob
import os

parser = argparse.ArgumentParser(description='Sample Function')
parser.add_argument('--dir_path', type=str,
                    help='path to the directory that contains the files to consolidate vertically')
parser.add_argument('--file_type', 
                    type=str,
                    help='file type to consolidate within the specified directory', choices=["csv","excel"], default="A")
parser.add_argument('--rundate', 
                    type=str,
                    help='the date of the command YYYYMMDD', default="20210918")

args = parser.parse_args()

def read(filename):
	"""
	read in a file based upon the file handle

	:param filename: str of the filepath
	"""
	file_handle = filename.split('.')[-1].lower()
	if file_handle in ['xlsx','xls']:
		df = pd.read_excel(filename)
	elif file_handle in ['csv']:
		df = pd.read_csv(filename)
	return df

def consolidate_files(dir_path, file_type):
	"""
	This file loads in all the files of the specified file type and concatonates them all vertically

	:param dir_path: the directory path contains all the files to consolidate
	:param file_type: the type of files to consolidate of the files in the dir_path
	"""
	df_all = pd.DataFrame()
	for f in glob("%s/*%s" % (dir_path, file_type)):
		df_temp = read(f)
		df_temp['Filename'] = f.split(os.sep)[-1]
		df_all = pd.concat([df_all, df_temp], sort=False)
	return df_all


def main(args):
	"""
	wrapper function to consolidate files
	"""
	consolidate_files(args.dir_path, args.file_type).to_excel("%s/Consolidated %s_%s.xlsx" % (args.dir_path, 
																								args.dir_path.split(os.sep)[-1],
																								 args.rundate), 
															index=False)


if __name__ == "__main__":
	main(args)