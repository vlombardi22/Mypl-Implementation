#!/usr/bin/python3
#
# Author: Vincent Lombardi
# Course: CPSC 326, Spring 2019
# Assignment: 3
# Description: This file defines and prints out error
# messages.
# --------------------------------------------------------

class MyPLError(Exception):

    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        msg = self.message
        line = self.line
        column = self.column
        return 'error: %s at line %i column %i' % (msg, line, column)