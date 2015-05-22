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
 * version 0.1.3
 * date: 2015-05-22
 * compiling: gcc -std=gnu11 -o fens2pgn.elf fens2pgn.c
 */

/* TODO list (http://www6.chessclub.com/help/PGN-spec):
 * 
 * 8.2.3.4: Disambiguation ("Note that..." paragraph)
 *   absolute pin is disambiguation itself
 * 8.2.3.5: Check and checkmate indication characters
 */

#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#define VERSION 0.1.3

#define MAX_PLACEMENT_LENGHT 70
/* to store the longest hypothetical piece placement field in FEN:
 * "1r1k1b1r/p1n1q1p1/1p1n1p1p/P1p1p1P1/1P1p1P1P/B1P1P1K1/1N1P1N1R/R1Q2B1b"
 */
#define MAX_FEN_LENGHT 87  // after adding " b KQkq - 100 120"

#define STORE_SPACE_SIZE 6  // stands for the longest " 100. "
#define STORE_MOVE_SIZE 8  // stands for the longest "Qa1xb2++"

#define STR(x) STR_2(x)
#define STR_2(x) # x

enum read_parameters_exit_codes {
	P_Do_Nothing, P_Error, P_Help, P_Usage, P_Version
};

enum find_competiting_piece_exit_codes {
	F_None, F_In_Line, F_In_Column, F_Both, F_Other,
	F_Pawn_None, F_Pawn_Capture, F_Pawn_Promotion, F_Pawn_Capture_Promotion
};

struct structure_field {
	char alphabetical;
	signed char numerical;
	char piece_before;
	char piece_after;
};

struct structure_parameters {
	bool validate;  // TODO: make use of this variable in structure 'parameters'
	bool quiet;
	bool verbose;
	char *read_from_file;
	char *write_to_file;
};

char capitalized(char letter)
{
	if (letter >= 'a')
		return letter - 0x20;
	return letter;
}

static inline signed char compare_boards(const char (*array_1)[8], const char (*array_2)[8], struct structure_field distinctions[])
{
	signed char differences = 0;
	for (signed char i = 0; i < 8; ++i)
		for (signed char j = 0; j < 8; ++j)
			if (array_1[i][j] != array_2[i][j]) {
				++differences;
				if (differences > 4)  // array 'distinctions' is too small to hold all differences
					continue;
				distinctions[differences - 1].alphabetical = 'a' + j;
				distinctions[differences - 1].numerical = 8 - i;
				distinctions[differences - 1].piece_before = array_1[i][j];
				distinctions[differences - 1].piece_after = array_2[i][j];
			}
	return differences;
}

static inline void fen2board(char *fen, char board[8][8])
{
	memset(board, ' ', 8 * 8);
	for (signed char i = 0; i < 8; ++i, ++fen)
		for (signed char j = 0; j < 8; ++fen) {
			if (*fen >= '1' && *fen <= '8')
				j += *fen - '0';
			else
				board[i][j++] = *fen;
		}
	return;
}

static inline void find_competiting_piece_knight(const struct structure_field *field, const struct structure_field *previous_field, const char board[8][8], bool *is_other, bool *in_line, bool *in_column)
{
	char piece = field->piece_after;
	signed char a = field->alphabetical - 'a', b = field->numerical - 1;
	signed char previous_a = previous_field->alphabetical - 'a', previous_b = previous_field->numerical - 1;
	struct structure_instruction {
		signed char to_x;
		signed char to_y;
	} instructions[8] = {{-2, 1}, {1, 1}, {2, 0}, {1, -1}, {0, -2}, {-1, -1}, {-2, 0}, {-1, 1}};
	for (signed char x = a, y = b, i = 0; i < 8; ++i) {
		x += instructions[i].to_x;
		y += instructions[i].to_y;
		if (x < 0 || x >= 8 || y < 0 || y >= 8 || x == a && y == b)
			continue;
		if (board[8 - (y + 1)][x] == piece) {
			if (x == previous_a)
				*in_column = 1;
			if (y == previous_b)
				*in_line = 1;
			*is_other = 1;
		}
	}
	return;
}

void increment_and_check(char piece, signed char a, signed char b, signed char previous_a, signed char previous_b, const char board[8][8], bool *is_other, bool *in_line, bool *in_column, const signed char to_x, const signed char to_y)
{
	for (signed char x = a, y = b; x >= 0 && x < 8 && y >= 0 && y < 8 && !(x == a && y == b); x += to_x, y += to_y)
		if (board[8 - (y + 1)][x] == piece) {
			if (x == previous_a)
				*in_column = 1;
			if (y == previous_b)
				*in_line = 1;
			*is_other = 1;
		}
	return;
}

void find_competiting_piece_diagonally(const struct structure_field *field, const struct structure_field *previous_field, const char board[8][8], bool *is_other, bool *in_line, bool *in_column)
{
	char piece = field->piece_after;
	signed char a = field->alphabetical - 'a', b = field->numerical - 1;
	signed char previous_a = previous_field->alphabetical - 'a', previous_b = previous_field->numerical - 1;
	increment_and_check(piece, a, b, previous_a, previous_b, board, is_other, in_line, in_column, 1, 1);
	increment_and_check(piece, a, b, previous_a, previous_b, board, is_other, in_line, in_column, -1, 1);
	increment_and_check(piece, a, b, previous_a, previous_b, board, is_other, in_line, in_column, 1, -1);
	increment_and_check(piece, a, b, previous_a, previous_b, board, is_other, in_line, in_column, -1, -1);
	return;
}

void find_competiting_piece_horizontally_and_vertically(const struct structure_field *field, const struct structure_field *previous_field, const char board[8][8], bool *is_other, bool *in_line, bool *in_column)
{
	char piece = field->piece_after;
	signed char a = field->alphabetical - 'a', b = field->numerical - 1;
	signed char previous_a = previous_field->alphabetical - 'a', previous_b = previous_field->numerical - 1;
	increment_and_check(piece, a, b, previous_a, previous_b, board, is_other, in_line, in_column, 1, 0);
	increment_and_check(piece, a, b, previous_a, previous_b, board, is_other, in_line, in_column, 0, 1);
	increment_and_check(piece, a, b, previous_a, previous_b, board, is_other, in_line, in_column, -1, 0);
	increment_and_check(piece, a, b, previous_a, previous_b, board, is_other, in_line, in_column, 0, -1);
	return;
}

/* Function determines if in the 'board' there are pieces of type 'field->piece_after',
 * which can in one move go to the coordinates ('field->alphabetical', 'field->numerical')
 * and if their coordinates (previous_field->alphabetical, previous_field->numerical) collide with them.
 * Pawn is instead treated specially.
 */
int find_competiting_piece(const char board[8][8], const struct structure_field *field, const struct structure_field *previous_field)
{
	bool is_other = 0, in_line = 0, in_column = 0;
	char piece = field->piece_after;
	if (previous_field->piece_before != field->piece_after)  // pawn promotion
		piece = '@';  // from this time '@' stands for pawn promotion
	switch (piece) {
		case '@':
			return (field->piece_before != ' ' ? F_Pawn_Capture_Promotion : F_Pawn_Promotion);
		case 'p':
		case 'P':
			return (field->piece_before != ' ' ? F_Pawn_Capture : F_Pawn_None);
		case 'r':
		case 'R':
			find_competiting_piece_horizontally_and_vertically(field, previous_field, board, &is_other, &in_line, &in_column);
			break;
		case 'n':
		case 'N':
			find_competiting_piece_knight(field, previous_field, board, &is_other, &in_line, &in_column);
			break;
		case 'b':
		case 'B':
			find_competiting_piece_diagonally(field, previous_field, board, &is_other, &in_line, &in_column);
			break;
		case 'q':
		case 'Q':
			find_competiting_piece_horizontally_and_vertically(field, previous_field, board, &is_other, &in_line, &in_column);
			find_competiting_piece_diagonally(field, previous_field, board, &is_other, &in_line, &in_column);
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
	int exit_code = read_parameters(argc, argv, &parameters);
	switch (exit_code) {
		case P_Error:
			fputs("Invalid argument(s) found.\n", stderr);
			return EINVAL;
		case P_Help:
			puts("fens2pgn - converts multiple FENs into single PGN file\n"
			"Syntax: fens2pgn [arguments] [output file] [input file]\n"
			"Arguments:\n"
			"  -f    force validity of every FEN (unused so far)\n"
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
			"Copyright (C) 2014 Paweł Zacharek\n", STR(VERSION));
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
	struct structure_field distinctions[4], *field, *previous_field;
	signed char number_of_differences;
	char control_character, whose_move = 'w';
	char control_string[8 + 1], result[7 + 1];
	result[0] = '\0';
	bool metadata_included = 0, fens_are_incomplete = 0, first_move_number_already_written = 0;
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
		if (sscanf(fen_buffer, "%*[1-8/rnbqkpRNBQKP] %c %*s %*s %*d %d", &whose_move, &move_number) != 2) {  // FENs are incomplete
			fens_are_incomplete = 1;
			if (parameters.quiet != 1)
				fputs("FENs considered incomplete.\n", stderr);  // not corrupts redirected output
			move_number = 1;
			whose_move = 'w';
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
				fprintf(stderr, "Skipped \"%s\" (%d%s FEN).\n", fen_buffer, fen_number, fen_number % 10 == 1 ? "st" : fen_number % 10 == 2 ? "nd" : "th");
			continue;
		}
		if (number_of_differences > 4) {
			fprintf(stderr, "Can't compare \"%s\" (%d%s FEN) with the previous one.\n", fen_buffer, fen_number, fen_number % 10 == 1 ? "st" : fen_number % 10 == 2 ? "nd" : "th");
			return EILSEQ;
		}
		if (first_move_number_already_written == 1)
			strcpy(store_space, whose_move == 'w' && number_of_written_moves % 7 == 0 ? "\n" : " ");
		if (whose_move == 'w' || first_move_number_already_written == 0)
			snprintf(store_space + (first_move_number_already_written ? 1 : 0), STORE_SPACE_SIZE + 1 - (first_move_number_already_written ? 1 : 0), "%d. ", move_number);
		switch (number_of_differences) {
			case 2:  // ordinary move or capture
				if (distinctions[0].piece_after != ' ') {
					field = &distinctions[0];
					previous_field = &distinctions[1];
				} else {  // it means that (distinctions[1].piece_after != ' ')
					field = &distinctions[1];
					previous_field = &distinctions[0];
				}
				exit_code = find_competiting_piece((const char (*)[8])board_2, (const struct structure_field *)field, (const struct structure_field *)previous_field);
				switch (exit_code) {
					case F_Pawn_None:
						snprintf(store_move, STORE_MOVE_SIZE + 1, "%c%hhd", field->alphabetical, field->numerical);
						break;
					case F_Pawn_Capture:
						snprintf(store_move, STORE_MOVE_SIZE + 1, "%cx%c%hhd", previous_field->alphabetical, field->alphabetical, field->numerical);
						break;
					case F_Pawn_Promotion:
						snprintf(store_move, STORE_MOVE_SIZE + 1, "%c%hhd=%c", field->alphabetical, field->numerical, field->piece_after);
						break;
					case F_Pawn_Capture_Promotion:
						snprintf(store_move, STORE_MOVE_SIZE + 1, "%cx%c%hhd=%c", previous_field->alphabetical, field->alphabetical, field->numerical, field->piece_after);
						break;
					case F_None:
						snprintf(store_move, STORE_MOVE_SIZE + 1, field->piece_before != ' ' ? "%cx%c%hhd" : "%c%c%hhd", capitalized(field->piece_after), field->alphabetical, field->numerical);
						break;
					case F_In_Line:
					case F_Other:
						snprintf(store_move, STORE_MOVE_SIZE + 1, field->piece_before != ' ' ? "%c%cx%c%hhd" : "%c%c%c%hhd", capitalized(field->piece_after), previous_field->alphabetical, field->alphabetical, field->numerical);
						break;
					case F_In_Column:
						snprintf(store_move, STORE_MOVE_SIZE + 1, field->piece_before != ' ' ? "%c%hhdx%c%hhd" : "%c%hhd%c%hhd", capitalized(field->piece_after), previous_field->numerical, field->alphabetical, field->numerical);
						break;
					case F_Both:
						snprintf(store_move, STORE_MOVE_SIZE + 1, field->piece_before != ' ' ? "%c%c%hhdx%c%hhd" : "%c%c%hhd%c%hhd", capitalized(field->piece_after), previous_field->alphabetical, previous_field->numerical, field->alphabetical, field->numerical);
						break;
					}
				break;
			case 3:  // en passant capture
				if (whose_move == 'w')
					snprintf(store_move, STORE_MOVE_SIZE + 1, "%cx%c%hhd", distinctions[2].alphabetical, distinctions[0].alphabetical != distinctions[2].alphabetical ? distinctions[0].alphabetical : distinctions[1].alphabetical, distinctions[2].numerical + 1);
				else
					snprintf(store_move, STORE_MOVE_SIZE + 1, "%cx%c%hhd", distinctions[0].alphabetical, distinctions[1].alphabetical != distinctions[0].alphabetical ? distinctions[1].alphabetical : distinctions[2].alphabetical, distinctions[0].numerical + 1);
				break;
			case 4:  // castling
				snprintf(store_move, STORE_MOVE_SIZE + 1, distinctions[0].alphabetical == 'a' ? "O-O-O" : "O-O");
				break;
		}
		fprintf(output, "%s%s", store_space, store_move);
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
