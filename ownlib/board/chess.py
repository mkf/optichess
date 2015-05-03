# -*- coding: utf-8 -*-
__author__ = 'ArchieT'
from ownlib.board import GameEye,EmptyFieldInGame,FigureInGame
from numpy import array,ndarray
def pola():
	literkipol = ['A','B','C','D','E','F','G','H']
	for litpol in range(0,8):
		for numpol in range(0,8):
			yield (str("%s%s" % (literkipol[litpol][0],str(numpol+1)[0])),(numpol,litpol))
fieldsdict = {l: k for l,k in pola()}
class Chess(GameEye):
	startpoz = ""
	def __init__(self,fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"): pass
	@staticmethod
	def fenboard2array(fen,whiteup=True):
		# use whiteup=False if you want to have a realistic view in str(boardarray)
		if isinstance(fen,ndarray) and fen.shape==(8,8): return fen
		wholebfen = str(fen).split(' ')[0] ; linebfen = wholebfen.split('/') ; lista = []
		for line in (reversed(linebfen) if whiteup else linebfen):
			for char in list(line):
				if char in ['1','2','3','4','5','6','7','8']:
					pustych = int(char) ; pleft = pustych
					while pleft>=1: pleft-=1; lista.append('_')
				elif char in ['r','R','n','N','b','B','q','Q','k','K','p','P']: lista.append(char)
				else: raise ValueError
		assert len(lista)==64,str([len(lista),' ',''.join(lista),' ',linebfen,' ',wholebfen])
		boardarray = array(lista)
		boardshaped = boardarray.reshape(8,8)
		return boardshaped
	def fenparse(self,fen):
		assert isinstance(fen,str)
		nfen = str(fen).split(' ')
		nboard = self.fenboard2array(nfen[0])
		if nfen[1]=='w': nactcol = 'w'
		elif nfen[1]=='b': nactcol = 'b'
		else: raise AssertionError
		ncast = {capos:bool(capos in nfen[2]) for capos in ['K','Q','k','q']}
		nenpass = False if nfen[3]=='-' else nfen[3].upper()
		nhalfmoveclock = int(nfen[4])
		nfullclock = int(nfen[5])
		return {'board': nboard,'activecolor':nactcol,'castling':ncast,'enpassant':nenpass,'halfmoveclock':nhalfmoveclock,'fullclock':nfullclock}
	def findmove(self,boardin,boardout,color,castling,enpassant):
		changed = {}
		promotionmaybea = False
		promotionmaybeb = False
		promotionmaybe = None
		promoorcapt = None
		for field in fieldsdict:
			if not boardin[fieldsdict[field]]==boardout[fieldsdict[field]]:
				changed[field]=(boardin[fieldsdict[field]],boardout[fieldsdict[field]])
		print changed #debug
		appear = [] ; disappear = [] ; replace = [] ; anything = False
		figappe = [] ; figdisappe = [] ; figreplfrom = [] ; figreplto = []
		for ch in changed:
			if changed[ch][0]=='_':
				appear.append({'g':ch,'f':changed[ch][1]})
				figappe.append(changed[ch][1])
				anything=True
			elif changed[ch][1]=='_':
				disappear.append({'g':ch,'f':changed[ch][0]})
				figdisappe.append(changed[ch][0])
				anything = True
			else:
				replace.append({'g':ch,'f':(changed[ch][0],changed[ch][1])})
				figreplfrom.append(changed[ch][0])
				figreplto.append(changed[ch][1])
				anything = True
		else:
			if not anything: return None
		print "Appeared",appear,"Disappeared",disappear,"Replaced",replace
		print "appe",figappe,"disappe",figdisappe,"replfrom",figreplfrom,"replto",figreplto
		figadd = figappe+figreplto
		figdel = figdisappe+figreplfrom
		ruchy = []
		print "add",figadd,"del",figdel
		sameprzemiesingle = {}
		sameprzemiemultiskad = {}
		sameprzemiemultidokad = {}
		sameprzemiemultioptions = {}
		if sorted(figadd)==sorted(figdel):
			figplus = []; figminus = []; sameones = True; apper = False; disapper = False
			assert len(replace)==0
			#if set([figadd.count(i)==1 for i in set(figadd)])=={True}:
			if figadd==list(set(figadd)):
				for i in set(figadd):
					for j in disappear:
						if j['f']==i: skad = j['g'] ; break
					else: raise AssertionError
					for j in appear:
						if j['f']==i: dokad = j['g'] ; break
					else: raise AssertionError
					sameprzemiesingle.update({i: tuple([skad,dokad])})
			else:
				pojedyncze = set() ; wielokrotne = {}
				for i in set(figadd):
					ileichjest = figadd.count(i)
					if ileichjest==1: pojedyncze.update(i)
					elif ileichjest>1: wielokrotne.update({i:ileichjest})
					else: raise AssertionError
				for i in pojedyncze:
					for j in disappear:
						if j['f']==i: skad = j['g'] ; break
					else: raise AssertionError
					for j in appear:
						if j['f']==i: dokad = j['g'] ; break
					else: raise AssertionError
					sameprzemiesingle.update({i: tuple([skad,dokad])})
				for i in wielokrotne:
					skad = set()
					for j in disappear:
						if j['f']==i: skad.update(j['g'])
					dokad = set()
					for j in appear:
						if j['f']==i: dokad.update(j['g'])
					assert len(skad)==len(dokad)!=0
					sameprzemiemultiskad[i] = skad
					sameprzemiemultidokad[i] = dokad
					mopt = set()
					for k in skad:
						for j in dokad:
							mopt.add(tuple([k,j]))
					sameprzemiemultioptions[i] = mopt
			#TODO
			if len(figadd)>2: raise TooManyMoved(boardin,boardout)
			if len(figadd)==2:
				castleprobably = True
				if figadd=={'k','r'}:
					blackcastleprobably = True
					if sameprzemiesingle=={'r':('H8','F8'),'k':('E8','G8')}: blackcastleKprobably = True
					elif sameprzemiesingle=={'r':('A8','D8'),'k':('E8','C8')}: blackcastleQprobably = True
					print "cast:k" if blackcastleKprobably else "cast:q" if blackcastleQprobably else None
					print castling
				elif figadd=={'K','R'}:
					whitecastleprobably = True
					if sameprzemiesingle=={'R':('H1','F1'),'K':('E1','G1')}: whitecastleKprobably = True
					elif sameprzemiesingle=={'R':('A1','D1'),'K':('E1','C1')}: whitecastleQprobably = True
					print "cast:K" if whitecastleKprobably else "cast:Q" if whitecastleQprobably else None
					print castling
			sameprzemieoptions = {}
			sameprzemieoptions.update(sameprzemiemultioptions)
			sameprzemieoptions.update({p: {sameprzemiesingle[p]} for p in sameprzemiesingle})
			#TODO
		else:
			figplus = list(figadd)
			for i in figdel:
				if i in figplus: figplus.remove(i)
			if sorted(figplus)!=sorted(figreplto): raise SomeNewFigureIsNotAReplacement(boardin,boardout)
			else: promotionmaybea = True
			figminus = list(figdel)
			for i in figadd:
				if i in figminus: figminus.remove(i)
			if sorted(figminus)==sorted(figreplfrom):
				promoorcapt = True
			sameones = False
			apper = len(figplus)>0
			disapper = len(figminus)>0
			if apper: print "+",figplus
			if disapper: print "-",figminus
			assert apper or disapper
			#TODO
		#TODO


class EmptyFieldInChess(EmptyFieldInGame):
	def __init__(self,pos):
		assert isinstance(pos,str) and len(pos)==2
class ChessFigure(FigureInGame):
	def __init__(self,pos):
		assert isinstance(pos,str) and len(pos)==2
		self.pos = pos
	def move(self,to,boardofinstances):
		assert isinstance(to,str) and len(to)==2
		assert 'tability' in dir(self)
		by = (fieldsdict[self.pos][0]-fieldsdict[to][0],fieldsdict[self.pos][1]-fieldsdict[to][1])
		if not self.tability(by[0],by[1]): return False
		#if not
class BlackChessFigure(ChessFigure): pass
class WhiteChessFigure(ChessFigure): pass
class RookChessFigure(ChessFigure):
	@staticmethod
	def moving(machinepkg): return machinepkg.fR
	@staticmethod
	def tability(x,y): return (x==0 or y==0) and (x!=0 or y!=0)
	@staticmethod
	def bability(a,b,instboard,castling=False): pass
class KnightChessFigure(ChessFigure):
	@staticmethod
	def moving(machinepkg): return machinepkg.fN
	@staticmethod
	def tability(x,y): return (abs(x)==2 and abs(y)==1) or (abs(y)==2 and abs(x)==1)
class BishopChessFigure(ChessFigure):
	@staticmethod
	def moving(machinepkg): return machinepkg.fB
	@staticmethod
	def tability(x,y): return abs(x)==abs(y)!=0
class QueenChessFigure(ChessFigure):
	@staticmethod
	def moving(machinepkg): return machinepkg.fQ
	@staticmethod
	def tability(x,y): return ((x==0 or y==0) and (x!=0 or y!=0)) or abs(x)==abs(y)!=0
class KingChessFigure(ChessFigure):
	@staticmethod
	def moving(machinepkg): return machinepkg.fK
	@staticmethod
	def tability(x,y): return x==1 or y==1
class PawnChessFigure(ChessFigure):
	@staticmethod
	def moving(machinepkg): return machinepkg.fP
	@staticmethod
	def tability(x,y): return abs(y)==1

class R_ChFig(RookChessFigure,WhiteChessFigure): Z = 'R'
class r_ChFig(RookChessFigure,BlackChessFigure): Z = 'r'
class N_ChFig(KnightChessFigure,WhiteChessFigure): Z = 'N'
class n_ChFig(KnightChessFigure,BlackChessFigure): Z = 'n'
class B_ChFig(BishopChessFigure,WhiteChessFigure): Z = 'B'
class b_ChFig(BishopChessFigure,BlackChessFigure): Z = 'b'
class Q_ChFig(QueenChessFigure,WhiteChessFigure): Z = 'Q'
class q_ChFig(QueenChessFigure,BlackChessFigure): Z = 'q'
class K_ChFig(KingChessFigure,WhiteChessFigure): Z = 'K'
class k_ChFig(KingChessFigure,BlackChessFigure): Z = 'k'
class P_ChFig(PawnChessFigure,WhiteChessFigure): Z = 'P'
class p_ChFig(PawnChessFigure,BlackChessFigure): Z = 'p'
class ChessMove: pass
class ChessWalk: pass
class ChessCapture: pass
class ChessCaptEnPassant: pass
class ChessPromotion: pass
class ChessCastling: pass
class ChessReset: pass

class ChessLegalException(Exception):
	def __init__(self,beforeboard,afterboard):
		self.beforeboard = self.bef = beforeboard
		self.afterboard = self.aft = afterboard
	def __str__(self): return "\n###############\n BEFORE  \n"+str(repr(self.bef))+"\n\n AFTER  \n"+str(repr(self.aft))+"\n----------------\n"
class TooManyMoved(ChessLegalException): pass
class TwoMovedAndNotCastling(ChessLegalException): pass
class SomeNewFigureIsNotAReplacement(ChessLegalException): pass