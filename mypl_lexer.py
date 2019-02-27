#!/usr/bin/python3
#
# Author: Vincent Lombardi
# Course: CPSC 326, Spring 2019
# Assignment: 3
# Description: This file splits up source code into tokens
# and it checks for basic lexical errors.
# --------------------------------------------------------

import mypl_token as token
import mypl_error as error


class Lexer(object):
    def __init__(self, input_stream):
        self.line = 1
        self.column = 0  # index of a tokens first character
        self.input_stream = input_stream
        self.column_index = 0
        # index of pointer in the input stream

    def __peek(self):
        pos = self.input_stream.tell()
        symbol = self.input_stream.read(1)
        self.input_stream.seek(pos)
        return symbol

    def __read(self):
        if self.__peek() == '\n':
            self.line += 1
            self.column = 0
            self.column_index = 0
        else:
            self.column_index += 1
        return self.input_stream.read(1)

    # this function checks to see if there are
    #  any unusual characters that should end the token
    def check_char(self):
        if self.__peek() == '':
            return 0
        elif self.__peek() == ",":
            return 0
        elif self.__peek() == '=':
            return 0
        elif self.__peek() == "#":
            return 0
        elif self.__peek() == '>':
            return 0
        elif self.__peek() == '<':
            return 0
        elif self.__peek() == '!':
            return 0
        elif self.__peek() == "'":
            return 0
        elif self.__peek() == ":":
            return 0
        elif self.__peek() == "/":
            return 0
        elif self.__peek() == ".":
            return 0
        elif self.__peek() == "(":
            return 0
        elif self.__peek() == ")":
            return 0
        elif self.__peek() == "-":
            return 0
        elif self.__peek() == "%":
            return 0
        elif self.__peek() == "*":
            return 0
        elif self.__peek() == "+":
            return 0
        elif self.__peek() == ";":
            return 0
        elif self.__peek() == " ":
            return 0
        elif self.__peek() == "\n":
            return 0
        else:
            return 1

    # this function checks for comments
    def __comment_check(self):
        while self.__peek() == '#':
            while self.__peek() != '\n' and self.__peek() != '':
                self.__read()
            self.__read()  # remove newline after comment
            while self.__peek().isspace():  # removes space characters
                self.__read()

    # defines the next token
    def next_token(self):
        tokentype = token.ID
        item = ''
        isStringVal = False  # makes sure that string values are set as string values
        error_message = "Lexer Error "

        while self.__peek().isspace():
            # increments column for every character of whitespace found
            if self.__peek() == " ":
                self.column += 1
            self.__read()

        self.__comment_check()

        if self.__peek() == '':  # EOS end of file
            tokentype = token.EOS

        # special character such as plus or minus
        if self.check_char() == 0:
            self.column += 1
            item += self.__read()

            # checks for and invalid dot
            if item == "." and str(self.__peek()).isnumeric():
                error_message += "invalid float value"
                e = error.MyPLError(error_message, self.line, self.column_index - 1)
                raise e
            # checks for comparison operators
            if item == '=' or item == '>' or item == '<' or item == '!':
                if self.__peek() == '=':
                    item += self.__read()

        elif self.__peek() == '"':  # string value
            self.column += 1  # increments column to a tokens starting index
            self.__read()
            while self.__peek() != '"':
                if self.__peek() == '\n':
                    error_message += "reached newline character in string"
                    e = error.MyPLError(error_message, self.line, self.column_index)
                    raise e
                elif self.__peek() == '':
                    error_message += "reached EOS character in string"
                    e = error.MyPLError(error_message, self.line, self.column_index)
                    raise e
                else:
                    item += self.__read()
            self.__read()
            tokentype = token.STRINGVAL
            isStringVal = True;
        else:  # any other type of character
            self.column += 1  # increments column to a tokens starting index
            isnum = False   # tracks if you are entering a number
            item += self.__read()
            # sets while loop to true if you are entering a number

            if item.isnumeric():
                isnum = True
            if self.check_char() == 1:
                # checks for characters that should end the token
                # checks if a number starts with zero
                # the previous if statement will check if the next
                # character is a decimal point
                if isnum and item == '0':
                    error_message += "unexpected symbol '" + str(self.__peek()) + "'"
                    e = error.MyPLError(error_message, self.line, self.column_index)
                    raise e
                # runs until it reaches a character that marks the end of the token

                while self.check_char() != 0 and self.__peek() != '"':
                    if isnum and not item.isnumeric():
                        error_message += "unexpected value '" + str(item[len(item) - 1]) + "'"
                        e = error.MyPLError(error_message, self.line, self.column_index - 1)
                        raise e
                    else:
                        self.__comment_check()
                        item += self.__read()
        if not isStringVal:
            if item == "string": # strips spaces
                tokentype = token.STRINGTYPE
            else:
                item = item.strip()

        if item.isnumeric() and tokentype != token.STRINGVAL:  # int and float check
            if self.__peek() == ".":
                item += self.__read()
                decimal = str(self.__peek())
                if not decimal.isnumeric():  # checks for an invalid float character
                    error_message += "missing digit in float value"
                    e = error.MyPLError(error_message, self.line, self.column_index - 1)
                    raise e
                while decimal.isnumeric and (self.check_char() != 0 or self.__peek() == "."):

                    decimal += self.__peek()
                    if not decimal.isnumeric() and self.__peek() != ";":
                        self.__peek()
                        error_message += "unexpected character '" + str(self.__peek()) + "'"
                        e = error.MyPLError(error_message, self.line, self.column_index + 1)
                        raise e
                    else:
                        item += self.__read()

            item = item.strip()
            if item.count('.', 0, len(item)):
                tokentype = token.FLOATVAL
            else:
                tokentype = token.INTVAL
        # checks if the token is a special character and sets token type accordingly
        if not isStringVal:
            if item == "=":
                tokentype = token.ASSIGN
            elif item == ",":
                tokentype = token.COMMA
            elif item == ":":
                tokentype = token.COLON
            elif item == "/":
                tokentype = token.DIVIDE
            elif item == ".":
                tokentype = token.DOT
            elif item == "==":
                tokentype = token.EQUAL
            elif item == ">":
                tokentype = token.GREATER_THAN
            elif item == ">=":
                tokentype = token.GREATER_THAN_EQUAL
            elif item == "<":
                tokentype = token.LESS_THAN
            elif item == "<=":
                tokentype = token.LESS_THAN_EQUAL
            elif item == "!=":
                tokentype = token.NOT_EQUAL
            elif item == "(":
                tokentype = token.LPAREN
            elif item == ")":
                tokentype = token.RPAREN
            elif item == "-":
                tokentype = token.MINUS
            elif item == "%":
                tokentype = token.MODULO
            elif item == "*":
                tokentype = token.MULTIPLY
            elif item == "+":
                tokentype = token.PLUS
            elif item == "true" or item == "false":
                tokentype = token.BOOLVAL
            elif item == ";":
                tokentype = token.SEMICOLON
            elif item == "bool":
                tokentype = token.BOOLTYPE
            elif item == "int":
                tokentype = token.INTTYPE
            elif item == "float":
                tokentype = token.FLOATTYPE
            elif item == "struct":
                tokentype = token.STRUCTTYPE
            elif item == "and":
                tokentype = token.AND
            elif item == "or":
                tokentype = token.OR
            elif item == "not":
                tokentype = token.NOT
            elif item == "while":
                tokentype = token.WHILE
            elif item == "do":
                tokentype = token.DO
            elif item == "if":
                tokentype = token.IF
            elif item == "then":
                tokentype = token.THEN
            elif item == "else":
                tokentype = token.ELSE
            elif item == "elif":
                tokentype = token.ELIF
            elif item == "end":
                tokentype = token.END
            elif item == "fun":
                tokentype = token.FUN
            elif item == "var":
                tokentype = token.VAR
            elif item == "set":
                tokentype = token.SET
            elif item == "return":
                tokentype = token.RETURN
            elif item == "new":
                tokentype = token.NEW
            elif item == "nil":
                tokentype = token.NIL

        final_token = token.Token(tokentype, item, self.line, self.column)
        self.column = self.column_index  # sets column to new value

        if tokentype == token.EOS:  # sets column to 0 at the end of the line
            self.column = 0

        return final_token