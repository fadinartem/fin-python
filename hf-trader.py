# -*- coding: <utf-8> -*-
import ctypes
import codecs
import collections
import tkinter as tk
from tkinter import ttk

from bs4 import BeautifulSoup


class Command():
	def __init__(self):
		self.message = ""
		
	def edit(self, tag, value):
		soup = BeautifulSoup (self.message)
		soup.find(tag).string.replace_with(value)
		self.message = str(soup)
		print("\nNew command:")
		print(soup.prettify())
		
	def show(self):
		print(self.message)
		
class Xml_connect(Command):
	def __init__(self, login, password, host, port):
		self.message = '<command id="connect">\
		<login>{0}</login>\
		<password>{1}</password>\
		<host>{2}</host>\
		<port>{3}</port>\
		<autopos>false</autopos>\
		<micex_registers>false</micex_registers>\
		<milliseconds>false</milliseconds>\
		<utc_time>false</utc_time>\
		<rqdelay>100</rqdelay>\
		<session_timeout>120</session_timeout>\
		<request_timeout>30</request_timeout>\
		</command>'.format(login, password, host, port)
		
class Xml_disconnect(Command):
	def __init__(self):
		self.message = '<command id="disconnect"/>'
		
class Xml_server_status(Command):
	def __init__(self):
		self.message = '<command id="server_status"/>'
		
class Xml_get_securities(Command):
	def __init__(self):
		self.message = '<command id="get_securities"/>'
		
class Xml_subscribe(Command):
	def __init__(self, board1, seccode1,board2,seccode2):
		self.message = '<command id="subscribe"> \
		<alltrades>\
			<security>\
				<board>{0}</board>\
				<seccode>{1}</seccode>\
			</security>\
			<security>\
				<board>{2}</board>\
				<seccode>{3}</seccode>\
			</security>\
		</alltrades> \
		<quotations>\
			<security>\
				<board>{0}</board>\
				<seccode>{1}</seccode>\
			</security>\
			<security>\
				<board>{2}</board>\
				<seccode>{3}</seccode>\
			</security>\
		</quotations> \
		<quotes>\
			<security>\
				<board>{0}</board>\
				<seccode>{1}</seccode>\
			</security>\
			<security>\
				<board>{2}</board>\
				<seccode>{3}</seccode>\
			</security>\
		</quotes>\
		</command>'.format(board1,seccode1,board2,seccode2)	
				
class Xml_unsubscribe(Xml_subscribe):		
	def __init__(self):
		self.soup = BeautifulSoup('<command id="unsubscribe"> \
		<alltrades></alltrades> \
		<quotations></quotations> \
		<quotes></quotes> \
		</command>')	
		self.message = ''
		
	def no_more(self, object):
		self.soup = BeautifulSoup(object.message, 'html5lib')
		self.soup.find('command')['id'] = 'unsubscribe'
		self.message = str(self.soup)
		return self.message
		
class Xml_get_history_data(Command):	
	def __init__(self, board, seccode, period, count, reset='false'):
		self.message = '<command id="gethistorydata"> \
		<security> \
			<board>%s</board> \
			<seccode>%s</seccode> \
		</security> \
		<period>%s</period> \
		<count>%s</count> \
		<reset>%s</reset> \
		</command>' % (board, seccode, period, count, reset)
		
class Xml_neworder(Command):
	def __init__(self, action, price, lots, board, seccode, client):
	#action format: "B" or "S"
		if price == 0:
			price_tag = '<bymarket/>'
		else:	
			price_tag = '<price>price</price>'
		self.message = '<command id="neworder">\
		<security>\
		<board> {0} </board>\
		<seccode> {1}</seccode>\
		</security>\
		<client>{5}</client>\
		{2}\
		<quantity>{3}</quantity>\
		<buysell>{4}</buysell>\
		</command>'.format(board, seccode, price_tag, lots, action, client) 
		#validafter = 0: immediate validity
		#immorcancel removed after demo warning
		
class Xml_cancelorder(Command):
	def __init__(self, transactionid):
		self.message = '<command id="cancelorder">\
		<transactionid>%s</transactionid>\
		</command>' % transactionid
		
class Xml_stoploss(Command):
	def __init__(self, action, a_price, o_price, linked, board, 
	seccode, client):
		#by market!!!
		self.message = '<command id="newstoporder">\
		<security>\
		<board> {0} </board>\
		<seccode> {1} </seccode>\
		</security>\
		<client>{2}</client>\
		<buysell>{4}</buysell>\
		<linkedorderno>{3}</linkedorderno>\
		<stoploss>\
		<activationprice>{5}</activationprice>\
		<orderprice>{6}</orderprice>\
		<bymarket\>\
		<quantity>100%</quantity>\
		</stoploss>\
		</command>'.format(board, seccode, client, linked, action, a_price, o_price)
		
class Xml_subscribe_ticks(Command):
	def __init__(self, board1, seccode1, board2, seccode2):
		self.message = '<command id="subscribe_ticks">\
		<security>\
			<board>{0}</board>\
			<seccode>{1}</seccode>\
			<tradeno>0</tradeno>\
		</security>\
		<security>\
			<board>{2}</board>\
			<seccode>{3}</seccode>\
			<tradeno>0</tradeno>\
		</security>\
		<filter>false</filter>\
		</command>'.format(board1, seccode1, board2, seccode2)
		
class Xml_get_portfolio_mct(Command):
	def __init__(self, client):
		self.message = '<command id="get_portfolio_mct" client={0}/>'.format(client)
		
class Xml_get_servtime_difference(Command):
	def __init__(self):
		self.message = '<command id="get_servtime_difference"/>'
		
class Smart_container():
#class based on a deque which calls another function when appended
	def __init__(self, another_function, maxlen):
		self.deque = collections.deque(maxlen=maxlen)
		self.anotherfunc = another_function
	def __getitem__ (self, key):
		return self.deque[key]
	def __len__(self):
		return len(self.deque)
	def append(self, item):
		self.deque.append(item)
		self.anotherfunc()
	def nullify(self):
		self.deque.clear()
		
class Order():
	def __init__(self, type, mn, ev):
		self.orderno = False
		self.tradeno = False
		self.board = False
		self.seccode = False
		self.status = False
		self.buysell = type
		self.time = False
		self.price = False
		self.quantity = False
		self.filled = False
		self.magic_number = mn
		self.event = ev
		self.profit = None
		
class Trade():
	def __init__(self):
		self.orderno = False
		self.buysell = False
		self.time = False
		self.price = False
		
class Connector():
	def __init__(self, new=False):
		if new:
			dll = 'txcn.dll'
		else:
			dll = 'txmlconnector.dll'
		ctypes.windll.LoadLibrary("C://Users/Administrator/Desktop/connector/%s" % dll)
		self.conn = ctypes.WinDLL("%s" % dll)
		self.back = ''
		self.account = {'client_id':'',
			'portfolio_client':'', 
			'trade_client':'', 
			'password':'',
			'HOST':'',
			'PORT':'',
			}
		
		self.securities = {}
		self.rouble_account = {'client_id':'id1',
			'portfolio_client':'id2', #for getting the portfolio
			'trade_client':'id3', #for trading
			'password':'password',
			'HOST':'89.202.47.152',
			'PORT':'3900',
			}
		self.demo_account = {'client_id':'id1',
			'portfolio_client':'id2', #for getting the portfolio
			'trade_client':'id3', #for trading
			'password':'password',
			'HOST':'78.41.194.72',
			'PORT':'3939',
			}
		self.ruboil_arbitrage = {'indep_seccode':'FUTBRENTNOV15',
			'indep_board':'MCT',
			'dep_seccode':'RTSSiZ5',
			'dep_board':'MCT',
			}	
		self.demo_stocks = {'indep_seccode':'GAZP',
			'indep_board':'TQBR',
			'dep_seccode':'SBER',
			'dep_board':'TQBR',
			}
			
		
	def print_callback(self, response):
		print(codecs.decode(response,'utf-8'))
		return ctypes.c_bool(True)
	
	def set_callback_print(self):	
		type_callback = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_char_p)
		self.c_callback = type_callback(self.print_callback)
		return self.conn.SetCallback(self.c_callback)
		
	def set_callback(self, trading_class):
	#accepts an object of the trading class and sets its 'catch' as the new callback
		type_callback = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_char_p)
		self.c_callback = type_callback(trading_class.catch)
		return self.conn.SetCallback(self.c_callback)		
		
	def get_service_info(self):
		request = ctypes.c_char_p(b"<request><value>queue_size</value><value>queue_mem_used</value>\
		<value>version</value></request>")
		response = ctypes.c_char_p()
		i = self.conn.GetServiceInfo (request, ctypes.byref(response))
		if i is 0: return response.value.decode('utf-8') #0 is success code; output the result
		else: return "Error code %i, xml response: %s" % (i, 
		response.value.decode('utf-8')) 
		#non-0 code signifies failure, we return the xml error comment
	
	def initialize(self, path='C:\\\\Users\\Administrator\\Desktop\\connector\\Logs\\\0', 
		level=2):
		log_path = ctypes.c_char_p(bytes(path, encoding='utf-8'))
		log_level = ctypes.c_int(level)
		i = self.conn.Initialize(log_path,log_level)
		if i is 0: 
			print('connector initialized;')
			return i #returns 0 in case of success
		else: 
			try:
				return i.contents.value.decode('utf-8') #returns a pointer to xml error comment
			except:
				return i
		
	def uninitialize(self):
		i = self.conn.UnInitialize(None)
		if i is 0: return i #returns 0 in case of success
		else: 
			try:
				return i.contents.value.decode('utf-8') #returns a pointer to xml error comment
			except:
				return i
	
	def set_log_level(self, new_level):
		c_lev = ctypes.c_int(new_level)
		i = self.conn.SetLogLevel(c_lev)
		if i is 0: return i #returns 0 in case of success
		else: 
			try:
				return i.contents.value.decode('utf-8') #returns a pointer to xml error comment
			except:
				return i 
		
	def send_command(self, xml_command):
		c_command = ctypes.c_char_p(bytes(xml_command,encoding='utf-8'))
		self.conn.SendCommand.restype = ctypes.c_char_p 
		#declaring that the function returns a pointer to a string
		i = self.conn.SendCommand(c_command)
		return i.decode('utf-8')
		
	def connect(self, login, password, host, port):
		comm = Xml_connect(login, password, host, port)
		print(self.send_command(comm.message))
		
	def disconnect(self):
		dis = Xml_disconnect()
		print(self.send_command(dis.message))
		
	def finish(self):
		disconnect = Xml_disconnect()
		self.send_command(disconnect.message)
		self.uninitialize()
		
	def subscribe(self, board1, seccode1, board2, seccode2):
		sbsc = Xml_subscribe_ticks(board1, seccode1, board2, seccode2)
		print(self.send_command(sbsc.message))
		self.unsubscribe_message = '<command id="subscribe_ticks"></command>'
		
	def cancel_subscription(self):
		print(self.send_command(self.unsubscribe_message))	
		
	def order(self, action, board, seccode, client, price=0, lots=1): 
		ord = Xml_neworder(action, price, lots, board, seccode, client)
		response = self.send_command(ord.message)
		return response
		
	def cancel_order(self, transactionid):
		cncl = Xml_cancelorder(transactionid)
		print(self.send_command(cncl.message))
			
	def portfolio(self, client):
		p = Xml_get_portfolio_mct(client)
		self.send_command(p.message)
		
	def server_time_difference(self):
		pi = Xml_get_servtime_difference()
		print(self.send_command(pi.message))
				
class Trader():
	def __init__(self, connector_instance):
		self.oil = Smart_container(self.decide, 20)
		self.usd = collections.deque(maxlen=20)
		self.usd_open = Smart_container(self.decide, 15)
		self.positions_open = False
		self.orders = {}
		self.trades = []
		self.conner = connector_instance
		self.commission = 0.9
		#for the entire open-close deal
		self.move_threshold = 1
		self.trading = False
		self.decision = 'No decision'
		self.balance = 'Not retreived'
		self.pnl = 'Not calculated'
		
		
		
	def sort_ticks(self, bs_obj):
	#receives a tick message, identifies the instrument and the price 
	#and puts it into the corresponding price container
		if str(bs_obj.find('seccode').string) == self.conner.securities['indep_seccode']:
			self.oil.append(float(str(bs_obj.find('price').string)))
			#appending the deque with the found price
		elif str(bs_obj.find('seccode').string) == self.conner.securities['dep_seccode']:
			self.usd.append(float(str(bs_obj.find('price').string)))
			if self.positions_open:
				self.usd_open.append(float(str(bs_obj.find('price').string)))
					
	def sort_trades(self, bs_obj):
		newtrade = Trade()
		newtrade.orderno = int(str(bs_obj.find('orderno').string))
		newtrade.buysell = str(bs_obj.find('buysell').string)
		newtrade.time = str(bs_obj.find('time').string)
		newtrade.price = int(str(bs_obj.find('price').string))
		self.trades.append(newtrade)
		

	
	def catch(self, message):
	#receives a raw server response and processes it
		soup = BeautifulSoup(codecs.decode(message,'utf-8'), 'html5lib')
		ticks = soup.find_all('tick')
		if len(ticks) is not 0:
			for tick in ticks:
				self.sort_ticks(tick)
		trades = soup.find_all('trade')
		if len(trades) is not 0:
			for trade in trades:
				self.sort_trades(trade)
		portfolio = soup.find('portfolio_mct')
		if portfolio:
			self.balance = float(str(portfolio.capital.string))
			self.pnl = float(str(portfolio.pnl_intraday.string))
		return ctypes.c_bool(True)
			

	def angle_analyse(self, vector, depth):
		d = int(depth)
		if len(vector)<d:
			return 0
		else:
			return (vector[-1]-vector[-d])/d
	
	def decide(self):
	#now the logic is inverted, watch out for this. 
	#Also the cosing orders are unconditional, ineffective!
		if not self.trading:
			return 
		if not self.positions_open:
			if self.angle_analyse(self.oil, 6) > self.move_threshold / 100:
			# if average cent movement exceeds threshold in cents
				self.trade(1, 'open')
				self.decision = 'LONG'
				self.positions_open = 'long'
				print('open long at %s' % self.usd[-1])
			elif self.angle_analyse(self.oil, 6) < -self.move_threshold / 100:
				self.trade(-1, 'open')
				self.decision = 'SHORT'
				self.positions_open = 'short'
				print('open short at %s' % self.usd[-1])
			else:
				self.decision = 'WAIT'
		elif self.positions_open:
			if len(self.usd_open) >= 10 and self.positions_open == 'long':
				# closing after 20 ticks
				self.trade(-1, 'close')
				self.positions_open = False
				self.usd_open.nullify()
				print('close long at %s' % self.usd[-1])
			elif len(self.usd_open) >= 10 and self.positions_open == 'short':
				self.trade(1,'close')
				self.positions_open = False
				self.usd_open.nullify()
				print('close short at %s' % self.usd[-1])
			
	def trade(self, command, event):
	#takes a command: 1 for long, -1 for short, and places trading orders
		if command == 1:
			self.place('B', event)
		elif command == -1:
			self.place('S', event)
		
		
	def place(self, type, event=''):
	#this function calls the Connector's Order function and creates an order 
	#instance for further tracking
		result = self.conner.order(type, board=self.conner.securities['dep_board'], 
			seccode=self.conner.securities['dep_seccode'], 
			client=self.conner.account['trade_client'])
		soup = BeautifulSoup(result, 'html5lib')
		if soup.result['success'] == 'true':
			print('Order placed')
			#self.orders[soup.result['transactionid']] = Order(type, mn, event)
		else:
			print('Error placing an order')
	
	def clear_trade_history(self):
		self.trades = []
		
	def close_positions(self):
		pass
			
class Interface():
	def __init__(self):
		self.conner = Connector()
		self.tinst = Trader(self.conner)
		self.root = tk.Tk()
		self.shape_windows()
		self.get_ready()
		self.make_menu()
		self.make_elements()
		self.make_grid()
		self.make_bindings()
		self.show_info()
		self.prompt_account()
		
		
	def account_choice(self, choice):
		if choice == 'real':
			self.conner.account = self.conner.rouble_account
			self.conner.securities = self.conner.ruboil_arbitrage
		elif choice == 'demo':
			self.conner.account = self.conner.demo_account
			self.conner.securities = self.conner.demo_stocks
		self.dialog.grab_release()
		self.dialog.withdraw()
		self.win.lift()
	
	def prompt_account(self):
		self.dialog = tk.Toplevel(self.root)
		self.dialog.geometry('200x100+300+200')
		self.dialog.wm_title("Choose account")
		self.gui_btn_demo = ttk.Button(self.dialog, text='Demo account')
		self.gui_btn_real = ttk.Button(self.dialog, text='Real account')
		self.gui_btn_demo.bind('<Button-1>',lambda e: self.account_choice('demo'))
		self.gui_btn_real.bind('<Button-1>',lambda e: self.account_choice('real'))
		self.gui_btn_demo.pack()
		self.gui_btn_real.pack()
		self.dialog.grab_set()
		self.dialog.lift(self.win)
		
	
	def shape_windows(self):
		self.root.withdraw()
		self.win = tk.Toplevel(self.root)
		self.win.wm_title("ORSOM algorithmic arbitrageur")
		self.win.geometry('800x600+0+0')
		#self.another = tk.Toplevel(self.root)
		#self.another.resizable(tk.FALSE, tk.TRUE)
		#self.another.wm_title("ORSOM callback dump")
		#self.another.withdraw()
		
	def get_ready(self):
		self.conner.initialize()
		self.callback_to_CLI()
	
	def make_menu(self):
		self.root.option_add('*tearOff', tk.FALSE)
		self.menubar = tk.Menu(self.win)
		self.win['menu'] = self.menubar
		self.menu_commands = tk.Menu(self.menubar)
		self.menubar.add_cascade(menu=self.menu_commands, label='Commands')
		self.menu_commands.add_command(label='Connect', 
			command=lambda: self.conner.connect(login=self.conner.account['client_id'], 
				password=self.conner.account['password'], 
				host=self.conner.account['HOST'], port=self.conner.account['PORT']))
		self.menu_commands.add_command(label='Disconnect', command=self.conner.disconnect)
		self.menu_commands.add_command(label='Callback to CLI', command=self.callback_to_CLI)
		self.menu_commands.add_command(label='Callback to the trader', command=self.callback_to_trader)
		self.menu_commands.add_command(label='Service info', command=self.print_service_info)
		self.menu_commands.add_command(label='Subscribe', 
			command=lambda: self.conner.subscribe(board1=self.conner.securities['indep_board'], 
				seccode1=self.conner.securities['indep_seccode'],board2=self.conner.securities['dep_board'],
				seccode2=self.conner.securities['dep_seccode']))
		self.menu_commands.add_command(label='Unsubscribe', command=self.conner.cancel_subscription)
		self.menu_commands.add_command(label='Get available securities', command=self.get_securities)
		
	def get_securities(self):
		g = Xml_get_securities()
		self.conner.send_command(g.message)
	
	def callback_to_CLI(self):
		self.conner.set_callback_print()
		#self.another.deiconify()
		print('Printing callback here')
		
	def print_service_info(self):
		print(self.conner.get_service_info())
	
	def callback_to_trader(self):
		self.conner.set_callback(self.tinst)
		#self.another.withdraw()
		print('Callback being received by the trader')
		
	def enable_trading(self):
		self.tinst.trading = True
		print('Trading: %s' % self.tinst.trading)
		
	def stop(self):
		self.tinst.trading = False
		print('Trading: %s' % self.tinst.trading)
		
	def set_threshold(self):
		new = self.gui_ent_threshold.get()
		self.tinst.move_threshold = float(new)
		
	
	def make_elements(self):
		s = ttk.Style()
		s.configure('TLabel', background='white', borderwidth=10)
		self.gui_l1 = ttk.Label(self.win, text='OIL', style='TLabel', anchor='n')
		self.gui_l2 = ttk.Label(self.win, text='USD', style='TLabel', anchor='n')
		self.gui_oil = ttk.Label(self.win, text='No data', style='TLabel', anchor='n')
		self.gui_usd = ttk.Label(self.win, text='No data', style='TLabel', anchor='n')
		self.gui_btn_analyse = ttk.Button(self.win, text = 'start analysing')
		self.gui_lbl_threshold = ttk.Label(self.win, text='Threshold', anchor='e')
		self.gui_ent_threshold = ttk.Entry(self.win)
		self.gui_ent_threshold.insert(0,self.tinst.move_threshold)
		self.gui_rec_pos = ttk.Label(self.win, text='No decision yet', style='TLabel', anchor='n')
		self.gui_btn_trade =  ttk.Button(self.win, text = 'trade')
		self.gui_positions = ttk.Label(self.win, text='', style='TLabel', anchor='nw')
		self.gui_orders = ttk.Label(self.win, text='', style='TLabel', anchor='nw')
		self.gui_btn_close =  ttk.Button(self.win, text = 'close positions')
		self.gui_btn_stop =  ttk.Button(self.win, text = 'STOP')
		self.gui_record = ttk.Label(self.win, text='', style='TLabel', anchor='nw')
		self.gui_account = ttk.Label(self.win, style='TLabel', anchor='nw')
		self.gui_btn_clear = ttk.Button(self.win, text='clear history')
		#self.text_dump = tk.Text(self.another)
		#self.s_bar = tk.Scrollbar(self.another, orient=tk.VERTICAL, command=self.text_dump.yview)
		#self.text_dump.configure(yscrollcommand=self.s_bar.set)
			
	def make_bindings(self):
		#self.gui_btn_analyse.bind('<Button-1>', lambda e:self.tinst.analyse()) 
		#functions to be written
		self.gui_btn_trade.bind('<Button-1>', lambda e:self.enable_trading())
		self.gui_btn_close.bind('<Button-1>', lambda e:self.tinst.close_positions())
		self.gui_btn_stop.bind('<Button-1>', lambda e:self.stop())
		self.gui_btn_clear.bind('<Button-1>', lambda e:self.tinst.clear_trade_history())
		self.gui_ent_threshold.bind('<Return>', lambda e:self.set_threshold())
		
	def show_info(self):
		self.oil = self.deque_into_text(self.tinst.oil)
		self.usd = self.deque_into_text(self.tinst.usd)
		try:
			self.gui_oil.configure(text=self.oil)
		except:
			self.gui_oil.configure(text='No data')
		try:
			self.gui_usd.configure(text=self.usd)
		except:
			self.gui_usd.configure(text='No data')
		self.gui_rec_pos.configure(text=self.tinst.decision)
		#self.text_dump.insert(tk.END, self.conner.back)
		#o = self.Orders_to_text(self.tinst.orders)
		#self.gui_orders.configure(text=o)
		#ps = self.Orders_to_text(self.tinst.orders, trade=True, limit=7)
		ps = self.trades_to_text()
		self.gui_positions.configure(text=ps)
		#ts = self.trade_stats_to_text()
		#self.gui_record.configure(text=ts)
		self.gui_account.configure(text="Balance: %s RUB\nToday's income: %s RUB" % 
			(self.tinst.balance, self.tinst.pnl))
		
		
			
	def make_grid(self):
		self.win.columnconfigure(0,weight=1)
		self.win.columnconfigure(1,weight=1)
		self.win.columnconfigure(2,weight=1)
		for i in range(4):
			self.win.rowconfigure(i,weight=2)
		for i in range(6,8):
			self.win.rowconfigure(i,weight=2)
		self.gui_l1.grid(row=0, column=0, rowspan=1, columnspan=1, 
			sticky=tk.W+tk.E+tk.S+tk.N)
		self.gui_l2.grid(row=0, column=1, rowspan=1, columnspan=1, 
			sticky=tk.W+tk.E+tk.S+tk.N)
		self.gui_oil.grid(row=1, column=0,rowspan=4, columnspan=1, 
			sticky=tk.W+tk.E+tk.S+tk.N)
		self.gui_usd.grid(row=1, column=1,rowspan=4, columnspan=1, 
			sticky=tk.W+tk.E+tk.S+tk.N)
		self.gui_lbl_threshold.grid(row=5, column=0,rowspan=1, columnspan=1, 
			sticky=tk.W+tk.E+tk.S+tk.N)
		self.gui_ent_threshold.grid(row=5, column=1, rowspan=1, columnspan=1, 
			sticky=tk.W+tk.E+tk.S+tk.N)
		self.gui_rec_pos.grid(row=6, column=0, columnspan=2, rowspan=2, 
			sticky=tk.W+tk.E+tk.S+tk.N)
		self.gui_btn_trade.grid(row=8, column=0, columnspan=2, rowspan=1, 
			sticky=tk.W+tk.E+tk.S+tk.N)
		self.gui_orders.grid(row=0,column=2,rowspan=3,columnspan=1, 
			sticky=tk.W+tk.E+tk.S+tk.N)
		self.gui_positions.grid(row=3,column=2,rowspan=1,columnspan=1, 
			sticky=tk.W+tk.E+tk.S+tk.N)
		self.gui_btn_close.grid(row=5, column=2, columnspan=1, rowspan=1, 
			sticky=tk.W+tk.E+tk.S+tk.N)
		self.gui_record.grid(row=6, column=2,rowspan=1,columnspan=1, 
			sticky=tk.W+tk.E+tk.S+tk.N)
		self.gui_account.grid(row=7, column=2,rowspan=1,columnspan=1,
			sticky=tk.W+tk.E+tk.S+tk.N)
		self.gui_btn_stop.grid(row=8, column=2, columnspan=1, rowspan=1, 
			sticky=tk.W+tk.E+tk.S+tk.N)
		self.gui_btn_clear.grid(row=4,column=2,sticky=tk.W+tk.E+tk.S+tk.N)

		
	def deque_into_text(self, deque):
		text = ''
		for i in deque:
			text += '%s\n' % i
		return text
		
	def Orders_to_text(self, l, trade=False, limit=0):
	#takes a dict with Orders instances and returns text for the gui
	#limit=0 means printing the entire list
	#not used now
		lines = []
		if len(l)>0:
		#i.e. if there are orders
			for i in (x for x in l if l[x].filled == trade and l[x].status):
			#active or matched orders, filled or unfilled depending on the 
			#function parameter
				o = l[i]
				line = ''
				line += '%s: %s %s %s' % (o.time, o.buysell, o.quantity, o.seccode)
				if o.filled == True:
				#if filled, show the price
					line += ' @ %s' % (o.price)
				lines.append(line)
		if limit: 
			return self.deque_into_text(lines[-limit:])
		else:
			return self.deque_into_text(lines)
		
	def trade_stats_to_text(self):
	#not used now
		trades = [self.tinst.orders[i].profit for i in self.tinst.orders 
		if self.tinst.orders[i].profit is not None]
		num_trades = len(trades)
		try:
			avg_profit = sum(trades)/len(trades)
			return '%s trades avg %s%%\n' % (num_trades, avg_profit*100)
		except:
			return '%s trades' % (num_trades)
			
	def trades_to_text(self):
		text = ''
		for trade in self.tinst.trades:
			text += '%s at %s\n' % (trade.buysell,trade.price)
		return text
		
def refresh_screens():
	gui.show_info()
	gui.root.after(100,refresh_screens)
	
def request_balance():
	gui.conner.portfolio(client=gui.conner.account['portfolio_client'])
	gui.root.after(10000,request_balance)


if __name__ == '__main__':
	try:
		gui = Interface()
		refresh_screens()
		request_balance()
		gui.root.mainloop()
	except Exception as e:
		print(e)
		input('Enter to exit')
	



	
	


	
