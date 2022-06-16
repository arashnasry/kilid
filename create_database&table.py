from utils import Kilid

ob_k=Kilid('postgres','password')
ob_k.create_database('testdb')
ob_k.create_table('testdb','newtable')
