# -*- coding: utf-8 -*-
__author__ = 'ArchieT'
from ownlib.board import GameEye,EmptyFieldInGame,FigureInGame
from numpy import array,ndarray
class Chess(GameEye):
	startpoz = ""
	def __init__(self,fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
		def pola():
			literkipol = ['A','B','C','D','E','F','G','H']
			for litpol in range(0,8):
				for numpol in range(0,8):
					yield (str("%s%s" % (literkipol[litpol][0],str(numpol+1)[0])),(numpol,litpol))
		self.fields = {l: k for l,k in pola()}
	@staticmethod
	def fen2array(fen,whiteup=True):
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
		nboard = self.fen2array(nfen[0])
		if nfen[1]=='w': nactcol = 'w'
		elif nfen[1]=='b': nactcol = 'b'
		else: raise AssertionError
		ncast = {capos:bool(capos in nfen[2]) for capos in ['K','Q','k','q']}
		nenpass = False if nfen[3]=='-' else nfen[3].upper()
		nhalfmoveclock = int(nfen[4])
		nfullclock = int(nfen[5])


class EmptyFieldInChess(EmptyFieldInGame): pass
class ChessFigure(FigureInGame): pass
class BlackChessFigure(ChessFigure): pass
class WhiteChessFigure(ChessFigure): pass
class RookChessFigure(ChessFigure):
	@staticmethod
	def moving(machinepkg): return machinepkg.fR
class KnightChessFigure(ChessFigure):
	@staticmethod
	def moving(machinepkg): return machinepkg.fN
class BishopChessFigure(ChessFigure):
	@staticmethod
	def moving(machinepkg): return machinepkg.fB
class QueenChessFigure(ChessFigure):
	@staticmethod
	def moving(machinepkg): return machinepkg.fQ
class KingChessFigure(ChessFigure):
	@staticmethod
	def moving(machinepkg): return machinepkg.fK
class PawnChessFigure(ChessFigure):
	@staticmethod
	def moving(machinepkg): return machinepkg.fP
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