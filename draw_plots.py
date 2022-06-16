from utils import Kilid

ob_k=Kilid('postgres','password')

ob_k.plot_dailyclose('testdb','newtable','outputs/dailyclose.png')
ob_k.plot_candels('testdb','newtable','outputs/candels.png')
