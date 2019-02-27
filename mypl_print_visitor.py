#!//usr/bin/python3
#
# Author: Vincent Lombardi
# Course: CPSC 326, Spring 2019
# Assignment: 4
# Description:
# Visitor class prints out the code in a pretty
# format
# --------------------------------------------------------


import mypl_token as token
import mypl_ast as ast


class PrintVisitor(ast.Visitor):
    """An AST pretty printer"""
    def __init__(self, output_stream):
        self.indent = 0                      # to increase/decrease indent level
        self.output_stream = output_stream   # where printing to

    def __indent(self):
        """Get default indent of four spaces"""
        return '    ' * self.indent

    def __write(self, msg):
        if msg is not None:
            self.output_stream.write(msg)

    def visit_stmt_list(self, stmt_list):
        for stmt in stmt_list.stmts:
            self.__write(self.__indent())
            stmt.accept(self)
            # I did this here to ensure that a newline character is printed
            # at the end of the complex Expr
            if type(stmt) is ast.ComplexExpr:
                self.__write(";\n")

    def visit_expr_stmt(self, expr_stmt):
        expr_stmt.expr.accept(self)

    def visit_var_decl_stmt(self, var_decl):
        temp_indent = self.indent  # saves current indent level
        self.__write(self.__indent())
        self.indent = 0  # sets indent to 0 to prevent indents in the middle of a line
        if var_decl.var_type != token.NIL:  # if the type is declared
            self.__write("var " + str(var_decl.var_id.lexeme) + ": ")
            self.__write(str(var_decl.var_type.lexeme) + " = ")
        else:  # if there is no type declared
            self.__write("var " + str(var_decl.var_id.lexeme) + " = ")
        var_decl.var_expr.accept(self)
        self.__write(';\n')
        self.indent = temp_indent

    def visit_assign_stmt(self, assign_stmt):
        temp_indent = self.indent  # saves current indent level
        self.__write(self.__indent())
        self.indent = 0  # sets indent to 0 to prevent indents in the middle of a line
        self.__write("set ")
        assign_stmt.lhs.accept(self)
        self.__write(" = ")
        assign_stmt.rhs.accept(self)
        self.__write(";\n")
        self.indent = temp_indent

    def visit_struct_decl_stmt(self, struct_decl):
        self.__write("struct " + struct_decl.struct_id.lexeme)
        self.__write("\n")
        self.indent += 1  # increment indent level by one
        # print out all statements in the struct
        for stmt in struct_decl.var_decls:
            stmt.accept(self)
        self.indent -= 1  # decrement indent level by one
        self.__write("end \n\n")

    def visit_fun_decl_stmt(self, fun_decl):
        self.__write("fun " + fun_decl.return_type.lexeme)
        self.__write(" " + fun_decl.fun_name.lexeme)
        self.__write('(')
        comma_count = 0  # counts the number of commas needed in parameter statement
        for item in fun_decl.params:  # prints out parameters
            item.accept(self)
            if comma_count < (len(fun_decl.params) - 1):
                self.__write(",")
            comma_count += 1
        self.__write(')\n')
        for stmt in fun_decl.stmt_list.stmts: # prints out items in the function body
            self.indent += 1  # increments indent level by one
            stmt.accept(self)
            if type(stmt) is ast.ComplexExpr:
                self.__write(";\n")
            self.indent -= 1  # decrements indent level by one
        self.__write("end\n\n")

    def visit_return_stmt(self, return_stmt):
        temp_indent = self.indent  # saves current indent level
        self.__write(self.__indent())
        self.indent = 0  # sets indent to 0 to prevent indents in the middle of a line
        self.__write("return")
        if return_stmt.return_expr is not None:
            self.__write(" ")
            self.__write(return_stmt.return_expr.accept(self))
        self.__write(";\n")
        self.indent = temp_indent

    def visit_while_stmt(self, while_stmt):
        self.__write(self.__indent())
        self.__write("while ")
        while_stmt.bool_expr.accept(self)
        self.__write(' do \n')
        for stmt in while_stmt.stmt_list.stmts:  # prints out stmts in loop
            self.indent += 1  # increment indent level by one
            stmt.accept(self)
            # prints out a semicolon and a newline if its a complex or simple expr
            if type(stmt) is ast.ComplexExpr or type(stmt) is ast.SimpleExpr:
                self.__write(";\n")
            self.indent -= 1  # decrement indent level by one
        self.__write(self.__indent())
        self.__write("end\n")

    def visit_if_stmt(self, if_stmt):
        self.__write(self.__indent())
        self.__write('if ')
        if_stmt.if_part.accept(self)
        for item in if_stmt.elseifs:  # print out elif statements
            self.__write(self.__indent())
            self.__write("elif ")
            item.accept(self)
        if if_stmt.has_else:  # print out else stmts
            self.__write(self.__indent())
            self.__write("else \n")
            for stmt in if_stmt.else_stmts.stmts:  # prints out stmts in if stmt
                self.indent += 1  # increment indent level by one
                stmt.accept(self)
                # prints out a semicolon and a newline if its a complex or simple expr
                if type(stmt) is ast.ComplexExpr or type(stmt) is ast.SimpleExpr:
                    self.__write(";\n")
                self.indent -= 1  # decrement indent level by one
            self.__write(self.__indent())
            self.__write("end\n")
        else:
            self.__write(self.__indent())
            self.__write("end\n")

    def visit_basic_if_stmt(self, basic_if_stmt):
        basic_if_stmt.bool_expr.accept(self)
        self.__write(' then \n')
        for stmt in basic_if_stmt.stmt_list.stmts:
            self.indent += 1

            if type(stmt) is ast.ComplexExpr or type(stmt) is ast.SimpleExpr:
                self.__write(";\n")
            self.indent -= 1

    def visit_simple_expr(self, simple_expr):
        simple_expr.term.accept(self)

    def visit_complex_expr(self, complex_expr):
        temp_indent = self.indent  # saves current indent level
        self.__write(self.__indent())
        self.indent = 0  # sets indent to 0 to prevent indents in the middle of a line
        complex_expr.first_operand.accept(self)
        self.__write(" " + str(complex_expr.math_rel.lexeme) + " ")
        complex_expr.rest.accept(self)
        self.indent = temp_indent

    def visit_bool_expr(self, bool_expr):
        if bool_expr.negated:  # if the expression is negated
            self.__write("not ")
        # places an Rparen if there is a bool_connector
        if bool_expr.bool_connector is not None:
            self.__write('(')
        # places an Lparen if there is a bool_rel
        if bool_expr.bool_rel is not None:
            self.__write('(')
        bool_expr.first_expr.accept(self)  # print first expression
        if bool_expr.bool_rel is not None:
            self.__write(" " + bool_expr.bool_rel.lexeme + " ")
            bool_expr.second_expr.accept(self)
            self.__write(')')  # close expression after second operand
        if bool_expr.bool_connector is not None:
            self.__write(" " + bool_expr.bool_connector.lexeme + " ")
            bool_expr.rest.accept(self)
            self.__write(')')  # close expression after rest

    def visit_lvalue(self, lval):
        dot_count = 0
        for items in lval.path:
            self.__write(str(items.lexeme))
            if dot_count < (len(lval.path) - 1):
                self.__write(".")
            dot_count += 1

    def visit_fun_param(self, fun_param):  # print out the function param
        self.__write(fun_param.param_name.lexeme)
        self.__write(": " + fun_param.param_type.lexeme)

    def visit_simple_rvalue(self, simple_rvalue):
        if simple_rvalue.val.tokentype == token.STRINGVAL:
            self.__write('"' + str(simple_rvalue.val.lexeme) + '"')
        else:
            self.__write(str(simple_rvalue.val.lexeme))

    def visit_new_rvalue(self, new_rvalue):
        self.__write(self.__indent())  # saves current indent level
        self.__write("new " + new_rvalue.struct_type.lexeme)

    def visit_call_rvalue(self, call_rvalue):
        self.__write(self.__indent())
        temp_indent = self.indent  # saves current indent level
        self.indent = 0  # sets indent to 0 to prevent indents in the middle of a line
        comma_count = 0  # counts the number of commas needed
        self.__write(str(call_rvalue.fun.lexeme) + "(")
        for items in call_rvalue.args:
            items.accept(self)
            if comma_count < (len(call_rvalue.args) - 1):
                self.__write(",")
            comma_count += 1
        self.__write(")")
        self.indent = temp_indent

    def visit_id_rvalue(self, id_rvalue):
        message = ''
        for val in id_rvalue.path:
            message += str(val.lexeme)
        self.__write(message)
