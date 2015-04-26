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
		for field in fieldsdict:
			if not boardin[fieldsdict[field]]==boardout[fieldsdict[field]]:
				changed[field]=(boardin[fieldsdict[field]],boardout[fieldsdict[field]])
		print changed #debug
		appear = [] ; disappear = [] ; replace = [] ; anything = False
		figappe = set() ; figdisappe = set() ; figreplfrom = set() ; figreplto = set()
		for ch in changed:
			if changed[ch][0]=='_':
				appear.append({'g':ch,'f':changed[ch][1]})
				figappe.update(changed[ch][1])
				anything=True
			elif changed[ch][1]=='_':
				disappear.append({'g':ch,'f':changed[ch][0]})
				figdisappe.update(changed[ch][0])
				anything = True
			else:
				replace.append({'g':ch,'f':(changed[ch][0],changed[ch][1])})
				figreplfrom.update(changed[ch][0])
				figreplto.update(changed[ch][1])
				anything = True
		else:
			if not anything: return None
		print "Appeared",appear,"Disappeared",disappear,"Replaced",replace
		print "a",figappe,"d",figdisappe,"rf",figreplfrom,"rt",figreplto
		figadd = set(list(figappe)+list(figreplto))
		figdel = set(list(figdisappe)+list(figreplfrom))
		ruchy = []


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