#!//usr/bin/python3
#
# Author: Vincent Lombardi
# Course: CPSC 326, Spring 2019
# Assignment: 4
# Description:
# this program takes in a lexer and uses it to tokenize
# commands from a file. The program then checks the tokens
# to see if they conform to mypl's grammar rules.
# --------------------------------------------------------

import mypl_error as error
import mypl_lexer as lexer
import mypl_token as token
import mypl_ast as ast


class Parser(object):

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None

    # starts analyzing the syntactical order of the program
    def parse(self):
        """succeeds if program is syntactically well-formed"""
        stmt_list_node = ast.StmtList()

        self.__advance()
        self.__stmts(stmt_list_node)
        self.__eat(token.EOS, 'expecting end of file')
        return stmt_list_node

    # moves to the next character
    def __advance(self):
        self.current_token = self.lexer.next_token()

    # checks if the next character is syntactically correct
    # and advances if true. otherwise this function spits out and error
    def __eat(self, tokentype, error_msg):
        if self.current_token.tokentype == tokentype:
            self.__advance()
        else:
            self.__error(error_msg)

    # this function prints an error message containing
    # the expected character, the character found instead
    # of the expected character and the location of hte error
    # in thj file
    def __error(self, error_msg):
        s = error_msg + ', found "' + self.current_token.lexeme + '" in parser'
        l = self.current_token.line
        c = self.current_token.column
        raise error.MyPLError(s, l, c)

    # Beginning of recursive descent functions
    def __stmts(self, stmt_list_node):
        """"<stmts> ::= <stmt> <stmts> | e"""

        if self.current_token.tokentype != token.EOS:
            self.__stmt(stmt_list_node)
            self.__stmts(stmt_list_node)

    def __stmt(self, stmt_list_node):
        """<stmt> ::= <sdecl> | <fdecl> | <bstmt>"""
        if self.current_token.tokentype == token.STRUCTTYPE:
            self.__advance()
            self.__sdecl(stmt_list_node)
        elif self.current_token.tokentype == token.FUN:
            self.__advance()
            self.__fdecl(stmt_list_node)
        else:
            stmt_list_node.stmts.append(self.__bstmt())

    def __sdecl(self, stmt_list_node):
        # 〈sdecl〉::= STRUCTTYPE ID〈vdecls〉END
        var_list = []
        struct_node = ast.StructDeclStmt()
        struct_node.struct_id = self.current_token
        self.__eat(token.ID, "expecting an ID")
        self.__vdecls(var_list)
        struct_node.var_decls = var_list
        stmt_list_node.stmts.append(struct_node)
        self.__eat(token.END, "expecting end")

    def __fdecl(self, stmt_list_node):
        fun_node = ast.FunDeclStmt()
        fun_node.stmt_list = ast.StmtList()
        if self.current_token.tokentype == token.NIL:
            fun_node.return_type = self.current_token
            self.__advance()
        else:
            fun_node.return_type = self.__type()
        fun_node.fun_name = self.current_token
        self.__eat(token.ID, "expecting an ID")
        self.__eat(token.LPAREN, "expecting '('")
        fun_node.params = self.__params()
        self.__eat(token.RPAREN, "expecting ')'")

        self.__bstmts(fun_node.stmt_list)
        self.__eat(token.END, "expecting end")
        stmt_list_node.stmts.append(fun_node)  # check

    def __bstmts(self, temp_stmt_list):
        # this function will run unless it finds one of these tokens
        tokenrel = [token.EOS, token.END, token.ELSE, token.ELIF]
        if self.current_token.tokentype not in tokenrel:
            temp_stmt_list.stmts.append(self.__bstmt())
            self.__bstmts(temp_stmt_list)

    def __bstmt(self):

        if self.current_token.tokentype == token.VAR:
            self.__advance()
            return self.__vdecl()
        elif self.current_token.tokentype == token.SET:
            self.__advance()
            return self.__assign()
        elif self.current_token.tokentype == token.IF:
            self.__advance()
            return self.__cond()
        elif self.current_token.tokentype == token.WHILE:
            self.__advance()
            return self.__while()
        elif self.current_token.tokentype == token.RETURN:
            self.__advance()
            return self.__exit()
        else:
            temp_expr = self.__expr()
            self.__eat(token.SEMICOLON, "expecting ';'")
            return temp_expr

    def __cond(self):
        if_node = ast.IfStmt()
        basic_if_node = ast.BasicIf()
        basic_if_node.bool_expr = ast.BoolExpr()
        basic_if_node.stmt_list = ast.StmtList()
        self.__bexpr(basic_if_node.bool_expr)
        self.__eat(token.THEN, "expecting then")
        self.__bstmts(basic_if_node.stmt_list)
        if_node.if_part = basic_if_node
        self.__condt(if_node)
        self.__eat(token.END, "expecting end")
        return if_node

    def __condt(self, if_node):
        if_node.else_stmts = ast.StmtList()
        basic_if_node = ast.BasicIf()
        basic_if_node.bool_expr = ast.BoolExpr()
        if self.current_token.tokentype == token.ELIF:
            basic_if_node.stmt_list = ast.StmtList()
            self.__advance()
            self.__bexpr(basic_if_node.bool_expr)
            self.__eat(token.THEN, "expecting then")
            self.__bstmts(basic_if_node.stmt_list)
            if_node.elseifs.append(basic_if_node)
            self.__condt(if_node)
        elif self.current_token.tokentype == token.ELSE:
            if_node.has_else = True
            self.__advance()
            self.__bstmts(if_node.else_stmts)

    def __bexpr(self, bexpr_node):
        if self.current_token.tokentype == token.NOT:
            bexpr_node.negated = True
            self.__advance()
            self.__bexpr(bexpr_node)
            self.__bexprt(bexpr_node)

        elif self.current_token.tokentype == token.LPAREN:
            bexpr_node.first_expr = ast.BoolExpr()
            self.__advance()
            # in this specific instance bexpr_node.first_expr must be a Bool expr
            self.__bexpr(bexpr_node.first_expr)
            self.__eat(token.RPAREN, "expecting ')'")
            self.__bconnct(bexpr_node)
        else:
            bexpr_node.first_expr = self.__expr()
            self.__bexprt(bexpr_node)

    def __bexprt(self, bexpr_node):
        boolrel = [token.EQUAL, token.LESS_THAN,
                   token.LESS_THAN_EQUAL, token.GREATER_THAN_EQUAL,
                   token.GREATER_THAN, token.NOT_EQUAL]
        if self.current_token.tokentype in boolrel:
            bexpr_node.bool_rel = self.current_token
            self.__advance()
            bexpr_node.second_expr = self.__expr()
            self.__bconnct(bexpr_node)
        else:
            self.__bconnct(bexpr_node)

    def __bconnct(self, bexpr_node):
        temp_bool_expr = ast.BoolExpr()
        if (self.current_token.tokentype == token.AND
                or self.current_token.tokentype == token.OR):
            bexpr_node.bool_connector = self.current_token
            self.__advance()
            self.__bexpr(temp_bool_expr)
            bexpr_node.rest = temp_bool_expr

    def __while(self):
        while_node = ast.WhileStmt()
        while_node.bool_expr = ast.BoolExpr()
        self.__bexpr(while_node.bool_expr)
        while_node.stmt_list = ast.StmtList()
        self.__eat(token.DO, "expecting do")
        self.__bstmts(while_node.stmt_list)
        self.__eat(token.END, "expecting end")
        return while_node

    def __exit(self):
        return_node = ast.ReturnStmt()
        if self.current_token.tokentype != token.SEMICOLON:
            return_node.return_expr = self.__expr()
        return_node.return_token = self.current_token
        self.__eat(token.SEMICOLON, "expecting ';'")
        return return_node

    def __vdecls(self, var_list):
        if self.current_token.tokentype == token.VAR:
            self.__advance()
            var_list.append(self.__vdecl())
            self.__vdecls(var_list)

    def __vdecl(self):
        var_decl_node = ast.VarDeclStmt()
        var_decl_node.var_id = self.current_token
        self.__eat(token.ID, "expecting ID")
        var_decl_node.var_type = self.__tdecl()
        self.__eat(token.ASSIGN, "expecting '='")
        var_decl_node.var_expr = self.__expr()
        self.__eat(token.SEMICOLON, "expecting ';'")
        return var_decl_node

    def __tdecl(self):
        token_type = token.NIL
        if self.current_token.tokentype == token.COLON:
            self.__advance()
            token_type = self.__type()
        return token_type

    def __expr(self):
        simple_expr_node = ast.SimpleExpr()
        if self.current_token.tokentype == token.LPAREN:
            self.__advance()
            simple_expr_node.term = self.__expr()
            self.__eat(token.RPAREN, "expecting ')'")
        else:
            simple_expr_node.term = self.__rvalue()

        mathrels = [token.PLUS, token.MINUS,
                    token.DIVIDE, token.MULTIPLY, token.MODULO]
        if self.current_token.tokentype in mathrels:
            complex_expr_node = ast.ComplexExpr()
            complex_expr_node.first_operand = simple_expr_node
            complex_expr_node.math_rel = self.current_token
            self.__advance()
            complex_expr_node.rest = self.__expr()
            return complex_expr_node
        return simple_expr_node

    def __rvalue(self):
        # this is the one exception I made to advancing
        # before calling the function
        simple_rval_node = ast.SimpleRValue()
        if self.current_token.tokentype == token.NIL:
            simple_rval_node.val = self.current_token
            self.__advance()
            return simple_rval_node
        elif self.current_token.tokentype == token.NEW:
            self.__advance()
            new_rval_node = ast.NewRValue()
            new_rval_node.struct_type = self.current_token
            self.__eat(token.ID, "expecting an ID")
            return new_rval_node
        elif self.current_token.tokentype == token.STRINGVAL:
            simple_rval_node.val = self.current_token
            self.__advance()
            return simple_rval_node
        elif self.current_token.tokentype == token.INTVAL:
            simple_rval_node.val = self.current_token
            self.__advance()
            return simple_rval_node
        elif self.current_token.tokentype == token.BOOLVAL:
            simple_rval_node.val = self.current_token
            self.__advance()
            return simple_rval_node
        elif self.current_token.tokentype == token.FLOATVAL:
            simple_rval_node.val = self.current_token
            self.__advance()
            return simple_rval_node
        else:
            return self.idrval()

    def idrval(self):
        id_node = ast.IDRvalue()
        call_rvalue_node = ast.CallRValue()
        id_node.path.append(self.current_token)
        self.__eat(token.ID, "expecting an ID")
        if self.current_token.tokentype == token.DOT:

            while self.current_token.tokentype == token.DOT:
                self.__advance()
                id_node.path.append(self.current_token)
                self.__eat(token.ID, "expecting an ID")
            return id_node
        elif self.current_token.tokentype == token.LPAREN:
            call_rvalue_node.fun = id_node.path[0]
            self.__advance()
            if self.current_token.tokentype != token.RPAREN:
                self.__expr_list(call_rvalue_node)
            self.__eat(token.RPAREN, "expecting ')'")
            return call_rvalue_node
        return id_node

    def __expr_list(self, call_rvalue_node):
        call_rvalue_node.args.append(self.__expr())
        while self.current_token.tokentype == token.COMMA:
            self.__advance()
            call_rvalue_node.args.append(self.__expr())

    def __type(self):
        temp_token = ''
        if self.current_token.tokentype == token.ID:
            temp_token = self.current_token
            self.__advance()
            return temp_token
        elif self.current_token.tokentype == token.INTTYPE:
            temp_token = self.current_token
            self.__advance()
            return temp_token
        elif self.current_token.tokentype == token.FLOATTYPE:
            temp_token = self.current_token
            self.__advance()
            return temp_token
        elif self.current_token.tokentype == token.BOOLTYPE:
            temp_token = self.current_token
            self.__advance()
            return temp_token
        elif self.current_token.tokentype == token.STRINGTYPE:
            temp_token = self.current_token
            self.__advance()
            return temp_token
        else:
            self.__error("expecting type")
            return temp_token

    def __params(self):
        param_list = []
        param_node = ast.FunParam()
        if self.current_token.tokentype == token.ID:
            param_node.param_name = self.current_token
            self.__advance()
            self.__eat(token.COLON, "expecting ':'")
            param_node.param_type = self.__type()
            param_list.append(param_node)
            while self.current_token.tokentype == token.COMMA:
                param_node = ast.FunParam()
                self.__advance()
                param_node.param_name = self.current_token
                self.__eat(token.ID, "expecting an ID")
                self.__eat(token.COLON, "expecting ':'")
                param_node.param_type = self.__type()
                param_list.append(param_node)
        return param_list

    def __assign(self):
        assign_node = ast.AssignStmt()
        assign_node.lhs = self.__lvalue()
        self.__eat(token.ASSIGN, "expecting '='")
        assign_node.rhs = self.__expr()
        self.__eat(token.SEMICOLON, "expecting ';'")
        return assign_node

    def __lvalue(self):
        lval_node = ast.LValue()
        lval_node.path.append(self.current_token)
        self.__eat(token.ID, "expecting an ID")
        while self.current_token.tokentype == token.DOT:
            self.__advance()
            lval_node.path.append(self.current_token)
            self.__eat(token.ID, "expecting an ID")
        return lval_node
