import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--size', choices=['10','20','50','100','200','500','1000'], default='10')
parser.add_argument('--ntruck', choices=['1','2','3','10'], default='1')
parser.add_argument('--dataset', choices=['1','2','3'], default='1')
args = parser.parse_args()