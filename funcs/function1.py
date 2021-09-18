import argparse

parser = argparse.ArgumentParser(description='Sample Function')
parser.add_argument('--integer', type=int, default=100,
                    help='the number of time to print the message')
parser.add_argument('--string', 
                    type=str,
                    help='the string to print', choices=["A","B"], default="A")

args = parser.parse_args()

def main(args):
	"""
	placeholder sample function to demonstrate purpose of this visual
	"""
	print( args.string*args.integer)

if __name__ == "__main__":
	main(args)