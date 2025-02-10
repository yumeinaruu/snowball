import argparse

parser = argparse.ArgumentParser(prog='Snowball bot')
parser.add_argument('--create_db', action=argparse.BooleanOptionalAction)
parser.add_argument('--recreate', action=argparse.BooleanOptionalAction)

args = parser.parse_args()
