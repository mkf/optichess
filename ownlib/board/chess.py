# -*- coding: utf-8 -*-
__author__ = 'ArchieT'
from ownlib.board import GameEye,EmptyFieldInGame,FigureInGame
class Chess(GameEye):
	startpoz = ""
	def __init__(self,fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
		pass
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