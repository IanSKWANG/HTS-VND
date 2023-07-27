import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--size', choices=['10','20','50','100','200','500','1000'], default='10')
parser.add_argument('--ntruck', choices=['1','2','3','10'], default='1')
parser.add_argument('--dataset', choices=['1','2','3'], default='1')
parser.add_argument('--itermax', choices=['1000','10000','100','500','10'], default='100')
parser.add_argument('--tabu_size', choices=['20','40','80','100'], default='20')
parser.add_argument('--shake', choices=['0', '1'], default='0')
args = parser.parse_args()