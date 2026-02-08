import time, os, sys, platform
from fuzzywuzzy import fuzz
os.system('clear' if platform.system() == 'Linux' else 'cls')
version = '2.0.18'
print('Foxy translator', version)
print()
def arg_check(args):
	global line, type, pstring
	if args == []:
		print(error(line, pstring))
		exit()
def insert_com(element : str):
	"""Inserts list of commands"""
	global line
	strings[(line+1):(line+1)] = element	

def error(line, string):
	err = f'''An error occured on line {line}:
{line}| {string} '''
	return err

#sys.stderr = open('interpretation_errors.txt', 'w')
RED = '\033[31m\b'
RST = '\033[0m\b'
ORNG = '\033[38;5;208m\b'
GRN = '\033[32m\b'
GRY = '\033[90m'
BLU = '\033[33;44m'
shinfo = True
sherr = True
shwarn = True
debuger = True

memsize = 64
mem = [0]*memsize

funcs = {}
labels = {}
const_table = {}
com_table = {}
layout = 0
counter = 0
counter_max = 0
comment = ''
counter_label = ''

class_m = {
	'_type':'CLASS',
	'_name':'Noname',
	'_methods':{},
	'_parent':None
}


builds = {
	'class':{**class_m},
	'method':{
		**class_m,
		'_callable':True,
		'_call':None,
		'_callfile':None,
		'_lib':False,
		'_parent':None,		
	}
}


mem_pos = 0

tag = ''
ret_cl = 'NONE'
file = input('Input path: ')
file = 'main.fx'
prog = open(file).read()
path = './libs/'
strings = prog.split('\n')
line = -1
 
print('Running file', file)
print('> : stdout')
print('< : stdin')
print(RED, '\berr> : errors')
print(ORNG, '\bwarn> : warnings')
print(GRN, '\binfo> : info')
print(GRY, '\bComments')
print(BLU, '\bValues from vars' , RST)
print()

print()
print('Line Command	  Args		Comment')


while True:
	comment = ''
	
	if counter > counter_max:
		line = int(labels[counter_label]) - 1
	line += 1
	
	if line > len(strings)-1:
		print('<Program finished>')
		break
		
	
	pstring = strings[line].replace(':@', str(mem[mem_pos - 1])).replace('@:', str(mem[mem_pos + 1])).replace('@', str(mem[mem_pos])).replace('#', tag).replace('$', str(ret_cl))
	
	
	
		
	if pstring.startswith('//'):
		comment = pstring.replace('//', '')
		print(line, '|\t', '\t'*3, GRY, '\b', comment, RST, sep = '')
		comment = ''
		continue 
	elif pstring.startswith('/!'):
		if not shinfo: continue
		print(GRN, '\bInformation signature on line', line, ':')
		print(GRN, '\binfo>', pstring.replace('/!', ''), RST)
		continue
	elif pstring.startswith('/err'):
		if not sherr: exit()
		print(RED, '\bAn error occured on line', line - 1, ':', end = '\n')
		print(line - 1, '| ', strings[line-1], sep = '')
		print(line, '| ', RED, pstring, RST, sep = '')
		print(RED, 'err>', pstring.replace('/err', ''), RST, sep = '')
		exit()

	elif pstring.startswith('/warn'):
		if not shwarn: continue
		print(ORNG, 'Warning on line ', line, ' :', sep = '')
		print('warn>', pstring.replace('/warn ', ''), RST)
		line = line + 1
		continue
	
	string = pstring.split()
	for i in string:
		if i.startswith('v:'):
			var = i.replace('v:', '')
			if '.' in i:
				names = var.split('.')
				mainname = builds[names[0]]
				if isinstance(mainname, dict):
					if names[1] not in mainname:
						insert_com([f'/err AttrErr: class "{names[0]}" has no attribute "{names[1]}"'])
						continue
					res = mainname[names[1]]
					
			else: res = builds[var]
			string[string.index(i)] = BLU + str(res) + RST
		
	if string == []:
		continue
	
	com = string[0].upper()
	args = string[1:]
	
	for arg in args:
		if arg.startswith('//'):
			comment = comment + arg.replace('//', '')
			comment = ' '.join(args[args.index(arg):])
			args = args[:args.index(arg)]
			
	print(line, '|\t', com, '\t|', ', '.join(args), '\t|', GRY, '\b', comment, RST, sep = '', flush = True)
	time.sleep(0.025)
	lowers = {}
	for k in builds:
		lowers[k.upper()] = builds[k]
		
	for arg in args:
		args[args.index(arg)] = arg.replace(BLU, '').replace(RST, '')
	match com:
		
		case 'MOV' :
			arg_check(args)
			mem_pos = int(args[0])
			
		case 'JMP':
			mem_pos = mem_pos + 1
			
		case 'COPY':
			arg_check(args)
			mem[mem_pos] = mem[int(args[0])]	
		case 'DEL':
			mem[mem_pos] = 0
		
		case 'PAUSE':
			input()	
			
		case 'STR':
			arg_check(args)
			mem[mem_pos] = ' '.join(args[0:])
		case 'INT':
			arg_check(args)
			mem[mem_pos] = int(args[0])
		case 'BOOL':
			arg_check(args)
			mem[mem_pos] = (True if args[0].upper() == 'TRUE' else False)
		case 'VAL':
			arg_check(args)
			mem[mem_pos] = eval(''.join(args[0:]))
		case 'FLOAT':
			mem[mem_pos] = float(args[0])
			
		case 'LNK':
			arg_check(args)
			match args[0].upper():
				case 'CREATE':
			 		mem[mem_pos] = 'LINK:' + args[1]
				case 'OPEN':
			 		mem_pos = int(mem[mem_pos].split(':')[1])
				case e: insert_com([f'/err CommandErr: Command  {com} got unknown argument {e}'])
				
		case 'MULTILINE':
			line = line + 1
			mem[mem_pos] = ''
			while True:
				if line > len(strings): break
				elif strings[line] == '/end': break
				else: mem[mem_pos] = mem[mem_pos] + '\n' + strings[line]
				line += 1
				
		case 'CLASS':
			match args[0].upper():
				case 'GET':
					mem[mem_pos] = klass[args[1]]
				case 'DEFINE':
					klass = mem[mem_pos]
				case 'CREATE':
					mem[mem_pos] = {**builds['class']}
				case 'UPDATE':
					mem[mem_pos] = klass
				case 'SETSUB':
					klass = klass[args[1]]
				case 'USE':
					ret_cl = mem[mem_pos][args[1]]
				case 'CLOSE':
					klass = ret_cl = None
				case 'ADD':
					match args[1].upper():
						case 'ATTR':
							klass[args[2]] = mem[mem_pos]
						case 'SUB':
							 klass[args[2]] = {**builds['class']}
				case e: insert_com([f'/err CommandErr: Command  {com} got unknown argument {e}'])		 	
		case 'WITH':
			tag = ' '.join(args[0:])
			
		case 'OUT':
			print('>', end = '')
			if isinstance(mem[mem_pos], dict):
				if '_out' in mem[mem_pos]:
					print(mem[mem_pos]['_out'])
				else: print(f'<{mem[mem_pos]["_type"]} {mem[mem_pos]["_name"]} in memory case {mem_pos}>')
			else: print(mem[mem_pos])

			
		case 'IN':
			mem[mem_pos] = input('<')
		case 'INLABEL':
			print('<', end = '')
			mem[mem_pos] = input(f'{mem[mem_pos]} ')
		case 'EXIT':
			exit()	
					
		case 'MEM':
			arg_check(args)
			match args[0].upper():
				case 'OUT':
					print(mem)
				case 'CAP':
					mem = [0]*int(args[1])
				case 'CONN':
					match args[1].upper():
						case 'FILE':
							mem = mem + open(args[2], 'r').readlines()
						case 'MEM':
							mem = mem + [0]*int(args[2])
				case 'GET_POS':
					mem[mem_pos] = mem_pos
				case e: insert_com([f'/err CommandErr: Command  {com} got unknown argument {e}'])
					
		case 'PASS':
			continue				
		case 'CONST':
			arg_check(args)
			match args[0].upper():
				case 'CONN':
					tbl = open(args[1], 'r').readlines()
					for name in tbl:
						name = name.split(':')
						const_table[name[0]] = [name[1].replace('\n', ''), name[2].replace('\n', '')]
				case 'EXPORT':
					with open(args[1], 'w') as f:
						for i in const_table:
							data, dtype = const_table[i]
							f.write(f'{i}:{dtype}:{data}\n')
				case 'APPEND':
					with open(args[1], 'a') as f:
						for i in const_table:
							data, dtype = const_table[i]
							f.write(f'{i}:{dtype}:{data}\n')
				
				case 'PUT':
					match args[1].upper():
						case 'FLOAT':
							const_table[args[2]] = [float(mem[mem_pos]), 'FLOAT']
						case 'STR':
							const_table[args[2]] = [str(mem[mem_pos]), 'STR']
						case 'INT':
							const_table[args[2]] =[int(mem[mem_pos]), 'INT']
						case 'BOOL':
							const_table[args[2]] = [mem[mem_pos], 'BOOL']
						case 'CLASS':
							const_table[args[2]] = [mem[mem_pos], 'CLASS']
						case e: insert_com([f'/err CommandErr: Command  {com} got unknown argument {e}'])
				case 'GET':
					mem[mem_pos] = const_table[args[1]][0]
				case 'DEL':
					del const_table[args[1]]
				case e: insert_com([f'/err CommandErr: Command  {com} got unknown argument {e}'])
					
		case 'GOTO':
			arg_check(args)
			match args[0].upper():
				case 'LINE':
					line = int(args[1]) - 1
				case 'LABEL':
					line = labels[args[1]]
				case 'REL':
					line = line + int(args[1]) + 1
				case e: insert_com([f'/err CommandErr: Command  {com} got unknown argument {e}'])
		case 'LABEL':
			labels[args[0]] = line
			
		case 'TARGET':
			labels[args[0]] = int(args[1])	
			
		case 'CNT':
			match args[0].upper():
				case 'SET_MAX':
					counter_max = int(args[1])
				case 'SET_LABEL':
					counter_label = args[1]
				case '+':
					counter += 1
		

			
		case 'IF':
			pexp = args[0]
			else_exp = args[2:]
			print(else_exp)	
			if eval(pexp):
				pass
			else:
				insert_com([' '.join(else_exp)])
				
		case 'TYPEOF': 
			if mem[mem_pos] == 0:
				mem[mem_pos] = 'NONE'
				
			if isinstance(mem[mem_pos], str):
				mem[mem_pos] = 'STR'
				
			if isinstance(mem[mem_pos], int):
				mem[mem_pos] = 'INT'
				
			if isinstance(mem[mem_pos], bool):
				mem[mem_pos] = 'BOOL'
				
			if isinstance(mem[mem_pos], dict):
				mem[mem_pos] = mem[mem_pos]['_type']

		case 'GET':
			cands = {}
			if args[0] not in builds:
				for i in builds:
					cands[fuzz.ratio(args[0], i)] = i
				m = max([*cands])
				like = cands[m]
				insert_com([f'/err VarErr: no var named "{args[0]}". Mabye you mean "{like}"?'])
				continue
			if '.' in args[0]:
				names = args[0].split('.')
				mainname = builds[names[0]]
				if isinstance(mainname, dict):
					if names[1] not in mainname:
						insert_com([f'/err AttrErr: class "{names[0]}" has no attribute "{names[1]}"'])
						continue
					res = mainname[names[1]]
			else: res = builds[args[0]]
			mem[mem_pos] = res
						
		case 'VAR':
			builds[args[0]] = mem[mem_pos] 
		
		case 'IMPORT':
			print('Importing module', args[0])
			try:
				if os.path.isdir(path + args[0]):
					if os.path.exists(path + args[0] + '/init.fx'):
						print('Running init.fx...')
						init = open(path + args[0] + '/init.fx').read()
						insert_com(init.split('\n'))
					else: insert_com(['/err ImportErr: Initializing file (init.fx) does not exists'])
				else: insert_com([f'/err ImportErr: no module named {args[0]}'])
			finally:
				pass
		case x if x.startswith('C:'):
			obj = lowers[com.replace('C:', '')]
			print('Running object ', '"', obj['_name'], '"', ' from builds, ', '"', com.replace('C::', ''), '":', sep = '')
			if '_callable' in list(obj):
				if obj['_callable']:
					if obj['_call'] != None:
						insert_com(obj['_call'].replace('\\n', '\n').split('\\n'))
					if obj['_call'] == None:
						if (obj['_lib'] == False) or ('_lib' not in obj):
							insert_com(open(obj['_callfile']).read().replace('\\n', '\n').split('\n'))
						if obj['_lib']:
							insert_com(open(path + obj['_callfile']).read().replace('\\n', '\n').split('\n'))
				if obj['_callable'] == False:
					insert_com('/warn Object is not callable')
					
		case x if x in lowers:
			obj = lowers[x]
			
			ik = 0
			for i in args:
				builds[f'_arg{ik}'] = i
				ik =+ 1
			if '_callable' in list(obj):
				if obj['_callable']:
					if obj['_call'] != None:
						if obj['_parent'] != None:
							for i in builds[obj['_parent']]:
								builds[f'_parent_attr_{i}'] = builds[obj['_parent']][i]
						insert_com(obj['_call'].replace('\\n', '\n').split('\n'))
					if obj['_call'] == None:
						if (obj['_lib'] == False) or ('_lib' not in obj):
							insert_com(open(obj['_callfile']).read().replace('\\n', '\n').split('\n'))
						if obj['_lib']:
							insert_com(open(path + obj['_callfile']).read().replace('\\n', '\n').split('\n'))		
				if obj['_callable'] == False:
					insert_com(['/warn CallWarn: Object is not callable'])
				
		case x:
			insert_com([f'/err CommandErr: Unknown command {x} '])
		

	
