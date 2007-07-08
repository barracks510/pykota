#! /usr/bin/python
#
# itcprint.py
# (c) 2007 George Farris <farrisg@shaw.ca>	
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#


# This documents and provides a demo of the protocol used to maniplulate
# the ITC Print  2015 smart card reader, http://www.itcsystems.com/smart-card-stored.html
# The  2015 is connected to the serial port of the PC to charge for things like 
# computer time usage, pay-for-print, cash registers sales, etc.
#
# The following description assumes that "Host" is the PC and Reader is the 2015
#
# ----------------------------------------------------------------------------------------------------- 
# Poll card reader for indication of card insertion 
# -----------------------------------------------------------------------------------------------------
#   Transmit from Host
#     Char line      : <STX><NUL><SOH><SOH><ETX><NUL><BEL><EOT> 
#     Hex translation: 0x02 0x00 0x01 0x01 0x03 0x00 0x07 0x04
#   Receive from Reader
#     No card inserted
#       Char line      : <STX><NUL><SOH>@<ETX><NUL>F<EOT> 
#       Hex translation: 0x02 0x00 0x01 0x40 0x03 0x00 0x46 0x04
#     Card Inserted
#       Char line      : <STX><NUL><SOH>@<ETX><NUL>F<EOT> 
#       Hex translation: 0x02 0x00 0x01 0x40 0x03 0x00 0x46 0x04
# =====================================================================================================


# ----------------------------------------------------------------------------------------------------- 
# Request current dollar(1) value stored on card
# ----------------------------------------------------------------------------------------------------- 
#   Transmit from Host
#     Char line      : <STX><NUL><SOH>!<ETX><NUL>'<EOT> 
#     Hex translation: 0x02 0x00 0x01 0x21 0x03 0x00 0x27 0x04
#   Receive from Reader
#     Char line      : <STX><NUL><SOH><NUL><NUL><NUL><NUL><NUL><NUL><DLE>h<SOH><ETX><NUL><DEL><EOT> 
#     Hex translation: 0x02 0x00 0x01 0x00 0x00 0x00 0x00 0x00 0x00 0x10 0x68 0x01 0x03 0x00 0x7F 0x04
#                                     [  Dollar value in this case 0x10 0x68 ]
#                                     [     0x1068 = 4200 = $4.20            ]
#                                     [______________________________________]
# =====================================================================================================


# -----------------------------------------------------------------------------------------------------
# Update Reader with new dollar value - must be less than what is stored on card
# -----------------------------------------------------------------------------------------------------
#   Transmit from Host 
#     Char line      : <STX><NUL><SOH>$<NUL><NUL><NUL><NUL><NUL><NUL><DLE><EOT><SOH><ETX><NUL>?<FF> 
#     Hex translation: 0x02 0x00 0x01 0x24 0x00 0x00 0x00 0x00 0x00 0x00 0x10 0x04 0x01 0x03 0x00 0x3F 0x0C
#                                          [  Dollar value in this case 0x10 0x04 ]
#                                          [     0x1004 = 4100 = $4.10            ]
#                                          [______________________________________]
#
#   Receive from successful transaction from Reader
#     Char line      : <STX><NUL><SOH><SYN><ETX><NUL><FS><BS>
#     Hex translation: 0x02 0x00 0x01 0x16 0x03 0x00 0x1C 0x08
# =====================================================================================================


# -----------------------------------------------------------------------------------------------------
# Eject card from Reader
# -----------------------------------------------------------------------------------------------------
#   Transmit from Host 
#     Char line      : <STX><NUL><SOH><SPACE><ETX><NUL>&<EOT>
#     Hex translation: 0x02 0x00 0x01 0x20 0x03 0x00 0x26 0x04
#   Receive from Reader
#     Char line      : <STX><NUL><SOH><SYN><ETX><NUL><FS><BS> 
#     Hex translation: 0x02 0x00 0x01 0x16 0x03 0x00 0x1C 0x08 
# =====================================================================================================

# (1) Currency can be set from the card reader keypad

import sys, os, serial, string, binascii, time
import gtk, gtk.glade, gobject, pg

# Database server settings
HOST = 'localhost'
PORT = 5432
DBNAME = 'pykota'
USER = 'pykotaadmin'
PASS = 'secret'



class gui:
	def __init__(self):
		self.cardstate = 0  # 0 not inserted, 1 inserted
		
		self.gladefile = "itcprint.glade"  
		self.xml = gtk.glade.XML(self.gladefile) 

		self.window = self.xml.get_widget("MainWindow")
		self.utext = self.xml.get_widget("UsernameEntry")
		self.cardlabel = self.xml.get_widget("CardBalanceLabel")
		self.printlabel = self.xml.get_widget("PrintBalanceLabel")
		self.spinbutton = self.xml.get_widget("Spinbutton")
		
		self.cardlabel.set_label('<big><b>unknown</b></big>')
		self.printlabel.set_label('<big><b>unknown</b></big>')
		
		self.cardbalance = ''
		self.username = ''
		self.addbalance = ''
		self.pykotauid = ''
		self.pykotabalance = 0.0
		
		# TODO put try  except around here
		#connect([dbname], [host], [port], [opt], [tty], [user], [passwd])
		try:
			self.sql = pg.connect(dbname=DBNAME, host=HOST, port=PORT, user=USER, passwd=PASS)
		except:
			pass
				
#		query = self.sql.query("""SELECT printername FROM printers WHERE printername='cc200-LaserJet' """)
		#query = db.get(printers, "cc200-laserjet")
#		if len(query.getresult()) > 0:
#			d2 = query.dictresult()
#			print d2 #['username']

		self.sc = smartcard(self.sql)
		
		#If you wanted to pass an argument, you would use a tuple like this:
    	# dic = { "on button1_clicked" : (self.button1_clicked, arg1,arg2) }
		dic = { "on_TransferButton_clicked" : self.xferbutton_clicked,
				"on_GetbalanceButton_clicked" : self.getcardbalance_clicked,
				"on_EjectButton_clicked" : self.ejectbutton_clicked,
				"on_quit_activate" : (gtk.main_quit),
				"on_UsernameEntry_changed" : self.username_changed,
				"on_UsernameEntry_focus_out_event" : self.username_entered,
				"on_ItcPrint_destroy" : (gtk.main_quit) }
				
		self.xml.signal_autoconnect (dic)
		
		return

  	# I might want to do username search as you type later
	def username_changed (self, widget):
		print "Text is now ->", self.utext.get_text()

	def username_entered (self, widget, event):
		self.username = self.utext.get_text()
		print "Username is ->", self.username
		# This is where we need to look up username in wbinfo
		
		try:
			query = self.sql.query("SELECT id FROM users WHERE username='%s'" % (self.username))
			self.pykotauid = (query.dictresult()[0])['id']
			print "User ID is  ->", self.pykotauid
		except:
			print "Username is invalid"
			result = gtk.RESPONSE_CANCEL
			dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL |
				gtk.DIALOG_DESTROY_WITH_PARENT,gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, 
				"Your username is invalid or does not exist.\nPlease try re-entering it", )
			result = dlg.run()
			dlg.destroy()
		try:
			query = self.sql.query("SELECT balance FROM users WHERE id='%s'" % (self.pykotauid))
			self.pykotabalance = float((query.dictresult()[0])['balance'])
			self.printlabel.set_label("%s%.2f%s" % ("<big><b>$",self.pykotabalance,"</b></big>"))
		except:
			print "balance sql error..."
		try:
			query = self.sql.query("SELECT lifetimepaid FROM users WHERE id='%s'" % (self.pykotauid))
			self.pykotalifebalance = float((query.dictresult()[0])['lifetimepaid'])
			print "%s%.2f" % ("$", self.pykotalifebalance)
		except:
			print "lifetimepaid sql error..."



	def xferbutton_clicked (self, widget):
		print "xfer button clicked...."
		self.addbalance = self.spinbutton.get_value()
		newbalance = self.addbalance + self.pykotabalance
		lifetimebalance = self.pykotalifebalance + self.addbalance
		self.sc.set_balance(newbalance, lifetimebalance, self.pykotauid)
		self.ejectbutton_clicked(None)
				
	def getcardbalance_clicked(self, widget):
		if self.sc.checkforcardready():
			self.sc.waitforcardready()
			self.cardbalance = self.sc.get_balance()
			self.cardlabel.set_label("%s%.2f%s" % ("<big><b>$",self.cardbalance,"</b></big>"))
			self.cardstate = 1
			self.source_id = gobject.timeout_add(2000, self.sc.inhibit_eject)
			self.spinbutton.set_range(0,float(self.cardbalance))
			
	def ejectbutton_clicked(self, widget):
		# TODO put a pop dialog here
		self.sc.eject_card()
		self.cardlabel.set_label('<big><b>unknown</b></big>')
		self.printlabel.set_label('<big><b>unknown</b></big>')
		self.cardstate = 0
		self.cardbalance = 0.0
		self.username = ''
		self.utext.set_text('')
		self.addbalance = 0.0
		self.pykotabalance = 0.0
		self.pykotalifebalance = 0.0
		self.spinbutton.set_range(0,0)
		
		# Is it possible this might not be set
		try:
			gobject.source_remove(self.source_id)
		except:
			pass
		
		
		
class smartcard:
	def __init__(self, sql):
		self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
		self.scsql = sql
		
	# Need comms to contiune to keep card in machine.
	# This loop keeps the card in until it stops so basically the print 
	# job can release the card after it is finished
	def checkforcardready(self):
		self.ser.write(binascii.a2b_hex("0200010103000704"))
		s = self.ser.read(8)

		if binascii.b2a_hex(s) == "0200014003004604":
			result = gtk.RESPONSE_CANCEL
			dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL |
				gtk.DIALOG_DESTROY_WITH_PARENT,gtk.MESSAGE_INFO, gtk.BUTTONS_OK_CANCEL, "Please insert your card...", )
			result = dlg.run()
			if (result==gtk.RESPONSE_OK):
				dlg.destroy()
				return 1
			else:
				dlg.destroy()
				return 0
		if binascii.b2a_hex(s) == "0200016c0300721c":
			return 1
				
	def waitforcardready(self):
		print "  Waiting for card to be inserted..."
		self.ser.write(binascii.a2b_hex("0200010103000704"))
		s = self.ser.read(8)

		while binascii.b2a_hex(s) == "0200014003004604":
			#time.sleep(2)
			#print binascii.b2a_hex(s)
			self.ser.write(binascii.a2b_hex("0200010103000704"))
			#print "Tx -> 0200010103000704"
			s = self.ser.read(8)
			#print "Rx -> %s" % binascii.b2a_hex(s)
		
		if binascii.b2a_hex(s) == "0200016c0300721c":
			print "  Card is inserted..."
			return 1
		else:
			print "  Card Error..."
			return 0

	# Get current value from card
	def get_balance(self):
		self.ser.write(binascii.a2b_hex("0200012103002704"))
		s1 = self.ser.read(16)
		print "  %s%.2f" % ("Card valued at -> $",float(string.atoi(binascii.b2a_hex(s1[3:11]), 16))/1000)
		return float(string.atoi(binascii.b2a_hex(s1[3:11]), 16))/1000

	def set_balance(self, new, life, uid):
		#self.ser.write(binascii.a2b_hex("0200012400000000000010040103003F0C"))
		#s2 = self.ser.read(8)
		#print binascii.b2a_hex(s2)

		try:
			query = self.scsql.query("UPDATE users SET balance=%s, lifetimepaid=%s WHERE id='%s'" % 
				(new, life, uid))
		except:
			print "sql error..."
			result = gtk.RESPONSE_CANCEL
			dlg = gtk.MessageDialog(None,gtk.DIALOG_MODAL |
				gtk.DIALOG_DESTROY_WITH_PARENT,gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, 
				"An error was encountered while updating your record.\nPlease contact technical support.")
			result = dlg.run()
			dlg.destroy()
	
	"""
	def writeUserAccountBalance(self, user, newbalance, newlifetimepaid=None) :    
        #Sets the new account balance and eventually new lifetime paid.
        if newlifetimepaid is not None :
            self.doModify("UPDATE users SET balance=%s, lifetimepaid=%s WHERE id=%s" % (self.doQuote(newbalance), self.doQuote(newlifetimepaid), self.doQuote(user.ident)))
        else :    
            self.doModify("UPDATE users SET balance=%s WHERE id=%s" % (self.doQuote(newbalance), self.doQuote(user.ident)))
            
    def writeNewPayment(self, user, amount, comment="") :
        #Adds a new payment to the payments history.
        self.doModify("INSERT INTO payments (userid, amount, description) VALUES (%s, %s, %s)" % (self.doQuote(user.ident), self.doQuote(amount), self.doQuote(comment)))
	
	"""
	
	def eject_card(self):
		print "  Ejecting card ..."
		self.ser.write(binascii.a2b_hex("0200012003002604"))
		s2 = self.ser.read(8)
		#print "Rx -> %s" % binascii.b2a_hex(s2)

	def inhibit_eject(self):
		self.ser.write(binascii.a2b_hex("0200010103000704"))
		s = self.ser.read(8)
		return True

	def close_port(self):	
		self.ser.close()


if __name__ == "__main__":
	hwg = gui()
	gtk.main()
	hwg.sql.close()	
	print "Goodbye..."
