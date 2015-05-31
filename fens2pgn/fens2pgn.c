/* fens2pgn - converts multiple FENs into single PGN file
 * Copyright (C) 2015 Paweł Zacharek
 * 
 * -----------------------------------------------------------------------
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 * -----------------------------------------------------------------------
 * 
 * version 0.3.0
 * date: 2015-05-31
 * compiling: gcc -std=gnu11 -o fens2pgn.elf fens2pgn.c
 */

#include <ctype.h>
#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define VERSION 0.3.0

/* to store the longest hypothetical piece placement field in FEN:
 * "1r1k1b1r/p1n1q1p1/1p1n1p1p/P1p1p1P1/1P1p1P1P/B1P1P1K1/1N1P1N1R/R1Q2B1b" */
#define MAX_PLACEMENT_LENGHT 70
#define MAX_FEN_LENGHT 87  // after adding " b KQkq - 100 120"

#define STORE_SPACE_SIZE 6  // stands for the longest " 100. "
#define STORE_MOVE_SIZE 6  // stands for the longest "Qa1xb2"

#define STR(x) STR_2(x)
#define STR_2(x) # x

enum find_competiting_piece_exit_codes {
	F_None, F_In_Line, F_In_Column, F_Both, F_Other,
	F_Pawn_None, F_Pawn_Capture, F_Pawn_Promotion, F_Pawn_Capture_Promotion,
	F_Discard_FEN
};

enum read_parameters_exit_codes {
	P_Do_Nothing, P_Error, P_Help, P_Usage, P_Version
};

struct structure_field {
	char alphabetical;
	signed char numerical;
	char piece_before;
	char piece_after;
};

struct structure_instruction {
	char to_x;
	signed char to_y;
};

// lists directions in which a bishop can move
struct structure_instruction instructions_bishop[4] = {{1, 1}, {1, -1}, {-1, -1}, {-1, 1}};
// lists directions in which a king can move
struct structure_instruction instructions_king[8] = {{1, 0}, {1, 1}, {0, 1}, {-1, 1}, {-1, 0}, {-1, -1}, {0, -1}, {1, -1}};
// instructions how to "jump" to all fields reachable by a knight
struct structure_instruction instructions_knight[8] = {{-2, 1}, {1, 1}, {2, 0}, {1, -1}, {0, -2}, {-1, -1}, {-2, 0}, {-1, 1}};
// lists directions in which a rook can move
struct structure_instruction instructions_rook[4] = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};
/* lists directions in which an attacking pawn can be found
 * even numbered fields in array {0, 2} stands for white pawn */
struct structure_instruction instructions_pawn[4] = {{-1, -1}, {1, -1}, {-1, 1}, {1, 1}};

struct structure_parameters {
	bool validate;
	bool quiet;
	bool verbose;
	char *read_from_file;
	char *write_to_file;
};

struct structure_suffixes {
	char st[3];
	char nd[3];
	char rd[3];
	char th[3];
} suffixes = {"st", "nd", "rd", "th"};

// Determines if field (x, y) is inside chess board.
bool are_coords_valid(char x, signed char y)
{
	if (x >= 'a' && x <= 'h' && y >= 1 && y <= 8)
		return 1;
	return 0;
}

// Function writes all (if not too many) differences between boards to array 'distinctions'.
static inline signed char compare_boards(const char (*board_1)[8], const char (*board_2)[8], struct structure_field distinctions[])
{
	signed char differences = 0;
	for (signed char y = 0; y < 8; ++y)
		for (signed char x = 0; x < 8; ++x)
			if (board_1[y][x] != board_2[y][x]) {  // two boards differ in that field
				if (++differences > 4)  // checks if array 'distinctions' is too small to hold all differences
					continue;
				distinctions[differences - 1].alphabetical = 'a' + x;
				distinctions[differences - 1].numerical = 8 - y;
				distinctions[differences - 1].piece_before = board_1[y][x];
				distinctions[differences - 1].piece_after = board_2[y][x];
			}
	return differences;
}

// Reads FEN string and fill in the array representing chess board.
static inline void fen2board(char *fen, char (*board)[8])
{
	memset(board, ' ', 8 * 8 * sizeof(char));
	for (signed char y = 0; y < 8; ++y, ++fen)
		for (signed char x = 0; x < 8; ++fen) {
			if (*fen >= '1' && *fen <= '8')
				x += *fen - '0';
			else
				board[y][x++] = *fen;
		}
	return;
}

/* Writes to structure of type 'structure_field' coordinates of the first found
 * piece of type 'piece'; useful in finding kings. */
bool find_piece(char piece, struct structure_field *field, const char (*board)[8])
{
	for (signed char y = 0; y < 8; ++y)
		for (signed char x = 0; x < 8; ++x)
			if (board[y][x] == piece) {
				field->alphabetical = 'a' + x;
				field->numerical = 8 - y;
				field->piece_after = piece;
				field->piece_before = '?';
				return 1;
			}
	return 0;
}

/* Returns the first piece encountered by simultaneously incrementing coordinates
 * by values 'to_x' and 'to_y'. If no piece has been found, the function returns
 * space sign. Used to determine if king is under attack */
char increment_and_return_encountered_piece(char x, signed char y, char to_x, signed char to_y, const char (*board)[8])
{
	for (x += to_x, y += to_y; are_coords_valid(x, y); x += to_x, y += to_y)
		if (board[8 - y][x - 'a'] != ' ')
			return board[8 - y][x - 'a'];
	return ' ';
}

// Determines if king is under attack.
signed char is_king_checked(char king, char x, signed char y, const char (*board)[8])
{
	const char Base = 'k' - king;
	char encountered_piece, tmp_x;
	signed char number_of_checks = 0, tmp_y;
	for (signed char i = 0; i < 4; ++i) {  // is there any ROOK or QUEEN attacking king?
		encountered_piece = increment_and_return_encountered_piece(x, y, instructions_rook[i].to_x, instructions_rook[i].to_y, board);
		if (encountered_piece == Base + 'R' || encountered_piece == Base + 'Q')
			if (++number_of_checks >= 2)
				return number_of_checks;
	}
	for (signed char i = 0; i < 4; ++i) {  // is there any BISHOP or QUEEN attacking king?
		encountered_piece = increment_and_return_encountered_piece(x, y, instructions_bishop[i].to_x, instructions_bishop[i].to_y, board);
		if (encountered_piece == Base + 'B' || encountered_piece == Base + 'Q')
			if (++number_of_checks >= 2)
				return number_of_checks;
	}
	for (signed char i = 0; i < 8; ++i) {  // is there any KING attacking king?
		tmp_x = x + instructions_king[i].to_x;
		tmp_y = y + instructions_king[i].to_y;
		if (are_coords_valid(tmp_x, tmp_y) && board[8 - tmp_y][tmp_x - 'a'] == Base + 'K')
			if (++number_of_checks >= 2)
				return number_of_checks;
	}
	for (signed char i = (king == 'k' ? 0 : 1); i < 4; i += 2) {  // is there any PAWN attacking king?
		tmp_x = x + instructions_pawn[i].to_x;
		tmp_y = y + instructions_pawn[i].to_y;
		if (are_coords_valid(tmp_x, tmp_y) && board[8 - tmp_y][tmp_x - 'a'] == Base + 'P')
			if (++number_of_checks >= 2)
				return number_of_checks;
	}
	for (signed char i = 0; i < 8; ++i) {  // is there any KNIGHT attacking king?
		x += instructions_knight[i].to_x;
		y += instructions_knight[i].to_y;
		if (are_coords_valid(x, y) && board[8 - y][x - 'a'] == Base + 'N')
			if (++number_of_checks >= 2)
				return number_of_checks;
	}
	return number_of_checks;
}

// Determines if king cannot move.
bool does_king_cannot_move(const struct structure_field *field, char (*board)[8])
{
	const char Base = field->piece_after - ('K' - 'A');
	const char A = field->alphabetical;
	const signed char B = field->numerical;
	board[8 - B][A - 'a'] = ' ';  // king is temporarily removed
	for (signed char i = 0, x, y; i < 8; ++i) {
		x = A + instructions_king[i].to_x;
		y = B + instructions_king[i].to_y;
		if (are_coords_valid(x, y) == 0)  // we're out of the board
			continue;
		if (board[8 - y][x - 'a'] >= Base && board[8 - y][x - 'a'] <= Base + ('Z' - 'A'))  // king can't capture it's own piece
			continue;
		if (is_king_checked(field->piece_after, x, y, (const char (*)[8])board) != 0)  // this field is attacked
			continue;
		board[8 - B][A - 'a'] = field->piece_after;  // king returns to it's field
		return 0;  // king can escape
	}
	board[8 - B][A - 'a'] = field->piece_after;  // king returns to it's field
	return 1;  // king can't escape
}

/* This function exists for disambiguation purposes.
 * Piece 'piece' from coords (previous_x, previous_y) didn't move. Instead we'll
 * move the same type of piece from coords (new_x, new_y). The question is:
 * Does after this move our king will be save? */
bool is_king_defended_after_move(char piece, char new_x, signed char new_y, char previous_x, signed char previous_y, const char (*board)[8])
{
	char king = (piece >= 'A' && piece <= 'Z' ? 'K' : 'k');  // white king can't be under attack after white's move
	char (*new_board)[8] = (char (*)[8])malloc(8 * 8 * sizeof(char));
	memcpy(new_board, board, 8 * 8 * sizeof(char));
	new_board[8 - previous_y][previous_x - 'a'] = piece;
	new_board[8 - new_y][new_x - 'a'] = ' ';
	struct structure_field king_placement;
	if (find_piece(king, &king_placement, (const char (*)[8])new_board))
		if (is_king_checked(king, king_placement.alphabetical, king_placement.numerical, (const char (*)[8])new_board) == 0) {
			free(new_board);
			return 1;
		}
	free(new_board);
	return 0;
}

// Searches horizontally, vertically or diagonally for a competing piece from the field we just moved into.
void increment_and_check(char piece, char x, signed char y, char previous_x, signed char previous_y, const char (*board)[8], bool *is_other, bool *in_line, bool *in_column, char to_x, signed char to_y)
{
	while (are_coords_valid(x, y) && !(x == previous_x && y == previous_y)) {
		if (board[8 - y][x - 'a'] == piece)  // we found the same type of piece in the same color
			if (is_king_defended_after_move(piece, x, y, previous_x, previous_y, board)) {  // we must disambiguate our last move
				if (x == previous_x)
					*in_column = 1;
				if (y == previous_y)
					*in_line = 1;
				*is_other = 1;
			}
		x += to_x;
		y += to_y;
	}
	return;
}

/* Function determines if in the 'board' there are pieces of type 'field->piece_after',
 * which can in one move go to the coordinates ('field->alphabetical', 'field->numerical')
 * and if their coordinates (previous_field->alphabetical, previous_field->numerical) collide with them.
 * Pawn is instead treated specially. */  // TODO: make use of 'validate' parameter
int find_competiting_piece(const char (*board)[8], const struct structure_field *field, const struct structure_field *previous_field, bool validate)
{
	bool is_other = 0, in_line = 0, in_column = 0;
	char piece = field->piece_after;
	const char A = field->alphabetical, Previous_A = previous_field->alphabetical;
	const signed char B = field->numerical, Previous_B = previous_field->numerical;
	if (previous_field->piece_before != field->piece_after)  // pawn promotion
		piece = '@';  // from this time '@' stands for a pawn promotion
	switch (piece) {
		case '@':
			return (field->piece_before != ' ' ? F_Pawn_Capture_Promotion : F_Pawn_Promotion);
		case 'p':
		case 'P':
			return (field->piece_before != ' ' ? F_Pawn_Capture : F_Pawn_None);
		case 'r':
		case 'R':
			for (signed char i = 0; i < 4; ++i)
				increment_and_check(piece, A, B, Previous_A, Previous_B, board, &is_other, &in_line, &in_column, instructions_rook[i].to_x, instructions_rook[i].to_y);
			break;
		case 'n':
		case 'N':
			for (signed char x = A, y = B, i = 0; i < 8; ++i) {
				x += instructions_knight[i].to_x;
				y += instructions_knight[i].to_y;
				if (are_coords_valid(x, y) == 0 || x == Previous_A && y == Previous_B)
					continue;
				if (board[8 - y][x - 'a'] == piece)  // an competing knight is found
					if (is_king_defended_after_move(piece, x, y, Previous_A, Previous_B, board)) {  // we must disambiguate our last move
						if (x == Previous_A)
							in_column = 1;
						if (y == Previous_B)
							in_line = 1;
						is_other = 1;
					}
			}
			break;
		case 'b':
		case 'B':
			for (signed char i = 0; i < 4; ++i)
				increment_and_check(piece, A, B, Previous_A, Previous_B, board, &is_other, &in_line, &in_column, instructions_bishop[i].to_x, instructions_bishop[i].to_y);
			break;
		case 'q':
		case 'Q':
			for (signed char i = 0; i < 4; ++i)
				increment_and_check(piece, A, B, Previous_A, Previous_B, board, &is_other, &in_line, &in_column, instructions_rook[i].to_x, instructions_rook[i].to_y);
			for (signed char i = 0; i < 4; ++i)
				increment_and_check(piece, A, B, Previous_A, Previous_B, board, &is_other, &in_line, &in_column, instructions_bishop[i].to_x, instructions_bishop[i].to_y);
			break;
		case 'k':
		case 'K':
			break;
	}
	if (in_column == 1 && in_line == 1)
		return F_Both;
	if (in_column == 1 && in_line == 0)
		return F_In_Column;
	if (in_column == 0 && in_line == 1)
		return F_In_Line;
	if (is_other == 1)
		return F_Other;
	return F_None;
}

char *ordinal_number_suffix(int number)
{
	if (number % 100 >= 11 && number % 100 <= 13)
		return suffixes.th;
	if (number % 10 == 1)
		return suffixes.st;
	if (number % 10 == 2)
		return suffixes.nd;
	if (number % 10 == 3)
		return suffixes.rd;
	return suffixes.th;
}

static inline int read_parameters(int argc, char *argv[], struct structure_parameters *parameters)
{
	if (argc < 2)
		return P_Help;
	bool omit_next_parameter = 0;
	for (int i = 1; i < argc; ++i) {
		if (omit_next_parameter == 1) {
			omit_next_parameter = 0;
			continue;
		}
		if (strncmp(&argv[i][0], "-h", 2) == 0 || strncmp(&argv[i][0], "--help", 6) == 0)
			return P_Help;
		else if (strncmp(&argv[i][0], "--usage", 6) == 0)
			return P_Usage;
		else if (strncmp(&argv[i][0], "--version", 6) == 0)
			return P_Version;
		else if (argv[i][0] == '-') {
			for (int j = 1; argv[i][j] != '\0'; ++j)
				switch (argv[i][j]) {
					case 'f':
						parameters->validate = 1;
						break;
					case 'o':
						if (i + 1 < argc) {
							parameters->write_to_file = argv[i + 1];
							omit_next_parameter = 1;
						} else
							return P_Error;
						break;
					case 'q':
						parameters->quiet = 1;
						parameters->verbose = 0;
						break;
					case 'v':
						parameters->quiet = 0;
						parameters->verbose = 1;
						break;
					default:
						return P_Error;
				}
		} else if (i == argc - 1)  // if it's the last parameter (input file name)
			parameters->read_from_file = argv[i];
		else
			return P_Error;
	}
	return P_Do_Nothing;
}

// USAGE: swap_pointers((void **)&pointer_1, (void **)&pointer_2);
static inline void swap_pointers(void **pointer_1, void **pointer_2)
{
	void *store = *pointer_1;
	*pointer_1 = *pointer_2;
	*pointer_2 = store;
	return;
}

int main(int argc, char *argv[])
{
	struct structure_parameters parameters = {0, 0, 0, '\0', '\0'};
	switch (read_parameters(argc, argv, &parameters)) {
		case P_Error:
			fputs("Invalid argument(s) found.\n", stderr);
			return EINVAL;
		case P_Help:
			puts("fens2pgn - converts multiple FENs into single PGN file\n"
			"Syntax: fens2pgn [arguments] [output file] [input file]\n"
			"Arguments:\n"
			"  -f    force validity of every chess move\n"
			"  -o    take next argument as output file\n"
			"  -q    quiet - don't display information about omitted FENs and such to stderr\n"
			"  -v    verbose - notify of every skipped FEN\n"
			"  -h, --help    print this help text\n"
			"  --usage       short usage information\n"
			"  --version     display program version");
			return 0;
		case P_Usage:
			puts("Syntax: fens2pgn [-foqvh] [--help] [--usage] [--version]\n"
			"                 [-o OUTPUT_FILE] [INPUT_FILE]");
			return 0;
		case P_Version:
			printf("fens2pgn %s\n"
			"Copyright (C) 2015 Paweł Zacharek\n", STR(VERSION));
			return 0;
	}
	FILE *input = (parameters.read_from_file == '\0' ? stdin : fopen(parameters.read_from_file, "r"));
	FILE *output = (parameters.write_to_file == '\0' ? stdout : fopen(parameters.write_to_file, "w"));
	if (input == '\0') {
		fprintf(stderr, "Can't open file \"%.255s\" for reading.\n", parameters.read_from_file);
		return ENOENT;
	}
	if (output == '\0') {
		fprintf(stderr, "Can't open file \"%.255s\" for writing.\n", parameters.read_from_file);
		return EACCES;
	}
	char fen_buffer[MAX_FEN_LENGHT + 1], fen_placement_buffer[MAX_PLACEMENT_LENGHT + 1];
	char store_space[STORE_SPACE_SIZE + 1], store_move[STORE_MOVE_SIZE + 1];
	char board_buffer_1[8][8], board_buffer_2[8][8];
	char (*board_1)[8] = board_buffer_1, (*board_2)[8] = board_buffer_2;
	int fen_number = 1, move_number = 1, number_of_written_moves = 0;
	struct structure_field distinctions[4], *field, *previous_field, king_placement;
	signed char number_of_differences;
	char control_character, whose_move = 'w', castling_prospects[4 + 1] = "KQkq", en_passant_field[2 + 1] = "-";
	char control_string[8 + 1], result[7 + 1];  // to store respectively "Result \"" and "1/2-1/2"
	result[0] = '\0';
	bool metadata_included = 0, fens_are_incomplete = 0, first_move_number_already_written = 0, move_is_invalid = 0;
	// beginning of METADATA section
	fscanf(input, " %c", &control_character);
	while (control_character == '[') {
		metadata_included = 1;
		putc('[', output);
		if (fscanf(input, "%8[^\n]", control_string) == 1) {
			if (strncmp(control_string, "Result \"", 8) == 0 && fscanf(input, "%7[-01/2*]", result) == 1)
				fprintf(output, "%s%s", control_string, result);
			else
				fputs(control_string, output);
		}
		for (int character; (character = getc(input)) != EOF;) {
			putc(character, output);
			if (character == '\n')
				break;
		}
		fscanf(input, " %c", &control_character);
	}
	ungetc(control_character, input);
	// beginning of GAME section
	if (fscanf(input, "%" STR(MAX_FEN_LENGHT) "[-0-9a-h/rnqkpRNBQKP w]", fen_buffer) != 1) {  // reading the first FEN
		fputs("No valid FEN found.", stderr);
		return EILSEQ;
	}
	++fen_number;
	sscanf(fen_buffer, "%" STR(MAX_PLACEMENT_LENGHT) "[1-8/rnbqkpRNBQKP]", fen_placement_buffer);
	if (strncmp(fen_buffer, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 56) != 0) {  // it isn't classical complete FEN
		if (sscanf(fen_buffer, "%*[1-8/rnbqkpRNBQKP] %c %4s %2s %*d %d", &whose_move, castling_prospects, en_passant_field, &move_number) != 4) {  // FENs are incomplete
			fens_are_incomplete = 1;
			if (parameters.quiet != 1)
				fputs("FENs considered incomplete.\n", stderr);  // not corrupts redirected output
			whose_move = 'w';
			strcpy(castling_prospects, "KQkq");
			strcpy(en_passant_field, "-");
			move_number = 1;
		}
		if (fens_are_incomplete == 0 || strncmp(fen_buffer, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", 43) != 0)  // starting position isn't classical
			fprintf(output, "[SetUp \"1\"]\n[FEN \"%s\"]\n", fen_buffer);
	}
	if (metadata_included == 1)
		putc('\n', output);
	fen2board(fen_placement_buffer, board_1);
	for (;;) {
		if (fscanf(input, " %" STR(MAX_FEN_LENGHT) "[-0-9a-h/rnqkpRNBQKP w]", fen_buffer) != 1)
			break;
		++fen_number;
		sscanf(fen_buffer, "%" STR(MAX_PLACEMENT_LENGHT) "[1-8/rnbqkpRNBQKP]", fen_placement_buffer);
		fen2board(fen_placement_buffer, board_2);
		number_of_differences = compare_boards((const char (*)[8])board_1, (const char (*)[8])board_2, distinctions);
		if (number_of_differences < 2) {
			if (parameters.verbose == 1)
				fprintf(stderr, "Skipped \"%s\" (%d%s FEN).\n", fen_buffer, fen_number, ordinal_number_suffix(fen_number));
			continue;
		}
		if (number_of_differences > 4) {
			fprintf(stderr, "Can't compare \"%s\" (%d%s FEN) with the previous one.\n", fen_buffer, fen_number, ordinal_number_suffix(fen_number));
			return EILSEQ;
		}
		switch (number_of_differences) {
			case 2:  // ordinary move or capture
				if (distinctions[0].piece_after != ' ') {
					field = &distinctions[0];
					previous_field = &distinctions[1];
				} else {  // it means that (distinctions[1].piece_after != ' ')
					field = &distinctions[1];
					previous_field = &distinctions[0];
				}
				switch (find_competiting_piece((const char (*)[8])board_2, (const struct structure_field *)field, (const struct structure_field *)previous_field, parameters.validate)) {
					case F_Pawn_None:
						snprintf(store_move, STORE_MOVE_SIZE + 1, "%c%hhd", field->alphabetical, field->numerical);
						break;
					case F_Pawn_Capture:
						snprintf(store_move, STORE_MOVE_SIZE + 1, "%cx%c%hhd", previous_field->alphabetical, field->alphabetical, field->numerical);
						break;
					case F_Pawn_Promotion:
						snprintf(store_move, STORE_MOVE_SIZE + 1, "%c%hhd=%c", field->alphabetical, field->numerical, toupper(field->piece_after));
						break;
					case F_Pawn_Capture_Promotion:
						snprintf(store_move, STORE_MOVE_SIZE + 1, "%cx%c%hhd=%c", previous_field->alphabetical, field->alphabetical, field->numerical, toupper(field->piece_after));
						break;
					case F_None:
						snprintf(store_move, STORE_MOVE_SIZE + 1, field->piece_before != ' ' ? "%cx%c%hhd" : "%c%c%hhd", toupper(field->piece_after), field->alphabetical, field->numerical);
						break;
					case F_In_Line:
					case F_Other:
						snprintf(store_move, STORE_MOVE_SIZE + 1, field->piece_before != ' ' ? "%c%cx%c%hhd" : "%c%c%c%hhd", toupper(field->piece_after), previous_field->alphabetical, field->alphabetical, field->numerical);
						break;
					case F_In_Column:
						snprintf(store_move, STORE_MOVE_SIZE + 1, field->piece_before != ' ' ? "%c%hhdx%c%hhd" : "%c%hhd%c%hhd", toupper(field->piece_after), previous_field->numerical, field->alphabetical, field->numerical);
						break;
					case F_Both:
						snprintf(store_move, STORE_MOVE_SIZE + 1, field->piece_before != ' ' ? "%c%c%hhdx%c%hhd" : "%c%c%hhd%c%hhd", toupper(field->piece_after), previous_field->alphabetical, previous_field->numerical, field->alphabetical, field->numerical);
						break;
					case F_Discard_FEN:
						move_is_invalid = 1;
						break;
					}
				break;
			case 3:  // en passant capture
				if (parameters.validate != 1) {
					if (whose_move == 'w')
						snprintf(store_move, STORE_MOVE_SIZE + 1, "%cx%c%hhd", distinctions[0].alphabetical == distinctions[2].alphabetical ? distinctions[1].alphabetical : distinctions[2].alphabetical, distinctions[0].alphabetical, distinctions[0].numerical);
					else
						snprintf(store_move, STORE_MOVE_SIZE + 1, "%cx%c%hhd", distinctions[0].alphabetical == distinctions[2].alphabetical ? distinctions[1].alphabetical : distinctions[0].alphabetical, distinctions[2].alphabetical, distinctions[2].numerical);
				} else {
					char all_fields[6 + 1];
					snprintf(all_fields, 6 + 1, "%c%c%c%c%c%c", distinctions[0].piece_before, distinctions[0].piece_after, distinctions[1].piece_before, distinctions[1].piece_after, distinctions[2].piece_before, distinctions[2].piece_after);
					if (whose_move == 'w' && distinctions[0].alphabetical == distinctions[2].alphabetical && en_passant_field[0] == distinctions[0].alphabetical && en_passant_field[1] == distinctions[0].numerical && memcmp(all_fields, " PP p ", 6) == 0)  // NOTE: even now some conditions are missing
						snprintf(store_move, STORE_MOVE_SIZE + 1, "%cx%c%hhd", distinctions[1].alphabetical, distinctions[0].alphabetical, distinctions[0].numerical);
					else if (whose_move == 'w' && distinctions[0].alphabetical != distinctions[2].alphabetical && en_passant_field[0] == distinctions[0].alphabetical && en_passant_field[1] == distinctions[0].numerical && memcmp(all_fields, " Pp P ", 6) == 0)  // NOTE: even now some conditions are missing
						snprintf(store_move, STORE_MOVE_SIZE + 1, "%cx%c%hhd", distinctions[2].alphabetical, distinctions[0].alphabetical, distinctions[0].numerical);
					else if (whose_move == 'b' && distinctions[0].alphabetical == distinctions[2].alphabetical && en_passant_field[0] == distinctions[2].alphabetical && en_passant_field[1] == distinctions[2].numerical && memcmp(all_fields, "P p  p", 6) == 0)  // NOTE: even now some conditions are missing
						snprintf(store_move, STORE_MOVE_SIZE + 1, "%cx%c%hhd", distinctions[1].alphabetical, distinctions[2].alphabetical, distinctions[2].numerical);
					else if (whose_move == 'b' && distinctions[0].alphabetical != distinctions[2].alphabetical && en_passant_field[0] == distinctions[2].alphabetical && en_passant_field[1] == distinctions[2].numerical && memcmp(all_fields, "p P  p", 6) == 0)  // NOTE: even now some conditions are missing
						snprintf(store_move, STORE_MOVE_SIZE + 1, "%cx%c%hhd", distinctions[0].alphabetical, distinctions[2].alphabetical, distinctions[2].numerical);
					else
						move_is_invalid = 1;
				}
				break;
			case 4:  // castling
				if (parameters.validate != 1)
					snprintf(store_move, STORE_MOVE_SIZE + 1, distinctions[0].alphabetical == 'a' ? "O-O-O" : "O-O");
				else {
					if (distinctions[0].alphabetical == 'a' && (  // NOTE: even now some conditions are missing
						whose_move == 'w' && strchr(castling_prospects, 'Q') != '\0' && memcmp(&board_1[8 - 1][0], "R   K", 5) == 0 && memcmp(&board_2[8 - 1][0], "  KR ", 5) == 0
						|| whose_move == 'b' && strchr(castling_prospects, 'q') != '\0' && memcmp(&board_1[8 - 8][0], "r   k", 5) == 0 && memcmp(&board_2[8 - 8][0], "  kr ", 5) == 0
					))
						snprintf(store_move, STORE_MOVE_SIZE + 1, "O-O-O");
					else if (distinctions[3].alphabetical == 'h' && (  // NOTE: even now some conditions are missing
						whose_move == 'w' && strchr(castling_prospects, 'K') != '\0' && memcmp(&board_1[8 - 1][4], "K  R", 4) == 0 && memcmp(&board_2[8 - 1][0], " RK ", 4) == 0
						|| whose_move == 'b' && strchr(castling_prospects, 'k') != '\0' && memcmp(&board_1[8 - 8][4], "k  r", 4) == 0 && memcmp(&board_2[8 - 8][0], " rk ", 4) == 0
					))
						snprintf(store_move, STORE_MOVE_SIZE + 1, "O-O");
					else
						move_is_invalid = 1;
				}
				break;
		}
		if (move_is_invalid == 1) {
			move_is_invalid = 0;
			if (parameters.quiet != 1)
				fprintf(stderr, "Skipped \"%s\" (%d%s FEN) because the calculated move is invalid.\n", fen_buffer, fen_number, ordinal_number_suffix(fen_number));
			continue;
		}
		if (first_move_number_already_written == 1)
			strcpy(store_space, whose_move == 'w' && number_of_written_moves % 7 == 0 ? "\n" : " ");
		if (whose_move == 'w' || first_move_number_already_written == 0)
			snprintf(store_space + (first_move_number_already_written ? 1 : 0), STORE_SPACE_SIZE + 1 - (first_move_number_already_written ? 1 : 0), "%d. ", move_number);
		fprintf(output, "%s%s", store_space, store_move);
		if (find_piece(whose_move == 'w' ? 'k' : 'K', &king_placement, (const char (*)[8])board_2)) {
			switch (is_king_checked(king_placement.piece_after, king_placement.alphabetical, king_placement.numerical, (const char (*)[8])board_2)) {
				case 2:
					if (does_king_cannot_move((const struct structure_field *)&king_placement, board_2) == 1)
						putc('#', output);
					else
						fputs("++", output);
					break;
				case 1:  // TODO: check for a checkmate
					putc('+', output);
				default:
					break;
			}
		}
		first_move_number_already_written = 1;
		if (whose_move == 'b') {
			++move_number;
			++number_of_written_moves;
		}
		whose_move = (whose_move == 'b' ? 'w' : 'b');
		swap_pointers((void **)&board_1, (void **)&board_2);
	}
	if (result[0] != '\0')
		fprintf(output, " %s\n", result);
	else
		fputs(" *\n", output);
	if (parameters.read_from_file != '\0')
		fclose(input);
	if (parameters.write_to_file != '\0')
		fclose(output);
	return 0;
}