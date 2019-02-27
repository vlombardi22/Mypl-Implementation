#!/usr/bin/python3#
#  Author:
#  Assignment: 5
#  Description: A visitor class that checks for type errors.
# ----------------------------------------------------------------------


import mypl_token as token
import mypl_ast as ast
import mypl_error as error
import mypl_symbol_table as symbol_table


class TypeChecker(ast.Visitor):
    """A MyPL type checker visitor implementation where struct type
    stake the form: type_id -> {v1:t1, ..., vn:tn} and function types
    take the form: fun_id -> [[t1, t2, ..., tn,], return_type]"""
    def __init__(self):
        # initialize the symbol table (for ids -> types)
        self.sym_table = symbol_table.SymbolTable()
        # current_type holds the type of the last expression type
        self.current_type = None
        # global env (for return)
        self.sym_table.push_environment()
        # set global return type to int
        self.sym_table.add_id('return')
        self.sym_table.set_info('return', token.INTTYPE)
        # load in built-in function types
        # println is used in the test cases so I included it
        self.sym_table.add_id('println')
        self.sym_table.set_info('println', [[token.STRINGTYPE], token.NIL])
        self.sym_table.add_id('print')
        self.sym_table.set_info('print', [[token.STRINGTYPE], token.NIL])
        self.sym_table.add_id('length')
        self.sym_table.set_info('length', [[token.STRINGTYPE], token.INTTYPE])
        self.sym_table.add_id('get')
        self.sym_table.set_info('get', [[token.INTTYPE, token.STRINGTYPE], token.STRINGTYPE])
        self.sym_table.add_id('itof')
        self.sym_table.set_info('itof', [[token.INTTYPE], token.FLOATTYPE])
        self.sym_table.add_id('itos')
        self.sym_table.set_info('itos', [[token.INTTYPE], token.STRINGTYPE])
        self.sym_table.add_id('ftos')
        self.sym_table.set_info('ftos', [[token.FLOATTYPE], token.STRINGTYPE])
        self.sym_table.add_id('reads')
        self.sym_table.set_info('reads', [[], token.STRINGTYPE])
        self.sym_table.add_id('readi')
        self.sym_table.set_info('readi', [[], token.INTTYPE])
        self.sym_table.add_id('readf')
        self.sym_table.set_info('readf', [[], token.FLOATTYPE])
        self.sym_table.add_id('stoi')
        self.sym_table.set_info('stoi', [[token.STRINGTYPE], token.INTTYPE])
        self.sym_table.add_id('stof')
        self.sym_table.set_info('stof', [[token.STRINGTYPE], token.FLOATTYPE])

    def __error(self, error_msg, target_token):
        s = error_msg
        l = target_token.line
        c = target_token.column
        raise error.MyPLError(s, l, c)

    def visit_stmt_list(self, stmt_list):
        # add new block (scope)
        self.sym_table.push_environment()
        for stmt in stmt_list.stmts:
            stmt.accept(self)

        # remove new block
        self.sym_table.pop_environment()

    def visit_expr_stmt(self, expr_stmt):
        expr_stmt.expr.accept(self)

    def visit_var_decl_stmt(self, var_decl):
        type_rel = [token.INTTYPE, token.STRINGTYPE, token.FLOATTYPE, token.BOOLTYPE]
        self.sym_table.add_id(var_decl.var_id.lexeme)
        var_decl.var_expr.accept(self)

        if var_decl.var_type != token.NIL:  # if the type is declared

            # if the current type is nil and an object or struct is being declared
            if self.current_type == token.NIL and var_decl.var_type.tokentype not in type_rel:
                self.sym_table.set_info(var_decl.var_id.lexeme, var_decl.var_type.lexeme)

            # standard case of the current type equals the declaration type
            elif self.current_type == var_decl.var_type.tokentype or self.current_type == token.NIL:
                self.sym_table.set_info(var_decl.var_id.lexeme, var_decl.var_type.tokentype)

            # if you are declaring a new struct
            elif self.sym_table.id_exists(self.current_type) and self.current_type == var_decl.var_type.lexeme:
                self.sym_table.set_info(var_decl.var_id.lexeme, self.current_type)
            else:
                msg = 'mismatch type in assignment'
                self.__error(msg, var_decl.var_id)
        else:
            # using implicit declarations with nil
            if self.current_type == token.NIL:
                msg = 'variable with undefined type'
                self.__error(msg, var_decl.var_id)
            self.sym_table.set_info(var_decl.var_id.lexeme, self.current_type)

    def visit_assign_stmt(self, assign_stmt):
        assign_stmt.rhs.accept(self)
        rhs_type = self.current_type
        assign_stmt.lhs.accept(self)
        lhs_type = self.current_type
        if rhs_type != token.NIL and rhs_type != lhs_type and lhs_type:
            msg = 'mismatch type in assignment'
            self.__error(msg, assign_stmt.lhs.path[0])

    def visit_struct_decl_stmt(self, struct_decl):
        self.sym_table.add_id(struct_decl.struct_id.lexeme)
        self.sym_table.push_environment()
        item_list = {} # list of struct variables
        for items in struct_decl.var_decls:
            items.accept(self)
            if items.var_id.lexeme not in item_list: # checks for repeat declarations
                item_list[items.var_id.lexeme] = self.sym_table.get_info(items.var_id.lexeme)
            else:
                msg = 'repeat declaration'
                self.__error(msg, struct_decl.struct_id)
        self.sym_table.pop_environment()
        self.sym_table.set_info(struct_decl.struct_id.lexeme, item_list)

    def visit_fun_decl_stmt(self, fun_decl):
        self.sym_table.add_id(fun_decl.fun_name.lexeme)

        self.sym_table.push_environment()
        self.sym_table.add_id('return')
        self.sym_table.set_info('return', fun_decl.return_type.tokentype)

        info_list = [] # function type information
        item_list = [] # list of parameters
        name_list = [] # list of parameter names
        index = 0
        for item in fun_decl.params:

            item.accept(self)
            item_list.append(self.current_type)
            # checks for repeat declarations
            if fun_decl.params[index].param_name.lexeme not in name_list:
                name_list.append(fun_decl.params[index].param_name.lexeme)
            else:
                msg = 'repeat declaration'
                self.__error(msg, fun_decl.fun_name)
            index += 1

        info_list.append(item_list)
        info_list.append(fun_decl.return_type.tokentype)
        self.sym_table.set_info(fun_decl.fun_name.lexeme, info_list)
        fun_decl.stmt_list.accept(self)
        # checks for wrong return type
        if self.current_type != fun_decl.return_type.tokentype:
            msg = 'wrong return type'
            self.__error(msg, fun_decl.return_type)
        self.sym_table.pop_environment()

    def visit_return_stmt(self, return_stmt):
        return_stmt.return_expr.accept(self)

    def visit_while_stmt(self, while_stmt):
        self.sym_table.push_environment()
        while_stmt.bool_expr.accept(self)
        for stmt in while_stmt.stmt_list.stmts:
            stmt.accept(self)
        self.sym_table.pop_environment()

    def visit_if_stmt(self, if_stmt):
        # create a new environment for every if statement block
        self.sym_table.push_environment()
        if_stmt.if_part.accept(self)
        self.sym_table.pop_environment()
        for item in if_stmt.elseifs:
            self.sym_table.push_environment()
            item.accept(self)
            self.sym_table.pop_environment()
        if if_stmt.has_else:
            self.sym_table.push_environment()
            for stmt in if_stmt.else_stmts.stmts:
                stmt.accept(self)
            self.sym_table.pop_environment()

    def visit_basic_if_stmt(self, basic_if_stmt):
        basic_if_stmt.bool_expr.accept(self)
        for stmt in basic_if_stmt.stmt_list.stmts:
            stmt.accept(self)

    def visit_simple_expr(self, simple_expr):
        simple_expr.term.accept(self)

    def visit_complex_expr(self, complex_expr):
        complex_expr.first_operand.accept(self)
        lhs_type = self.current_type
        complex_expr.rest.accept(self)
        rhs_type = self.current_type
        op_token = complex_expr.math_rel.tokentype

        if lhs_type == token.BOOLTYPE or rhs_type == token.BOOLTYPE:
            msg = 'mismatch type in assignment'
            self.__error(msg, complex_expr.math_rel)

        # prevents Nil values from being compared with each other
        if lhs_type == token.NIL and rhs_type == token.NIL:
            msg = 'mismatch type in assignment'
            self.__error(msg, complex_expr.math_rel)

        # ensures that strings can only be used with plus
        if lhs_type == token.STRINGTYPE and op_token != token.PLUS:
            msg = 'invalid string operator'
            self.__error(msg, complex_expr.math_rel)

        # ensures modulo is only used on ints
        if (lhs_type != token.INTTYPE or rhs_type != token.INTTYPE) and op_token == token.MODULO:
            msg = 'invalid use of modulo'
            self.__error(msg, complex_expr.math_rel)

        if rhs_type != token.NIL and rhs_type != lhs_type:
            msg = 'mismatch type in assignment'
            self.__error(msg, complex_expr.math_rel)

    def visit_bool_expr(self, bool_expr):
        bool_expr.first_expr.accept(self)
        lhs_type = self.current_type
        if bool_expr.bool_rel is not None:
            bool_expr.second_expr.accept(self)
            rhs_type = self.current_type

            bool_type = bool_expr.bool_rel.tokentype

            # checks if rhs_type == lhs_type or NIL
            if rhs_type != token.NIL and rhs_type != lhs_type:
                msg = 'invalid comparison'
                self.__error(msg, bool_expr.bool_rel)
            else:
                if rhs_type == token.NIL:
                    if bool_type != token.NOT_EQUAL and bool_type != token.EQUAL:
                        msg = 'invalid comparison'
                        self.__error(msg, bool_expr.bool_rel)
        if bool_expr.bool_connector is not None:
            bool_expr.rest.accept(self)

    def visit_lvalue(self, lval):
        # check the first id in the path
        var_token = lval.path[0]
        length = len(lval.path)
        if not self.sym_table.id_exists(var_token.lexeme):
            msg = 'undefined variable "%s"' % var_token.lexeme
            self.__error(msg, var_token)
        self.current_type = self.sym_table.get_info(var_token.lexeme)
        # check if struct for a longer path expression
        if length > 1:
            index = 1
            while index < length:
                struct_name = self.sym_table.get_info(lval.path[index - 1].lexeme)
                counter = index - 1
                # I just check for the parent struct has a type that should exist
                while struct_name is None:
                    struct_name = self.sym_table.get_info(lval.path[counter].lexeme)
                    counter -= 1
                struct_dict = self.sym_table.get_info(struct_name)
                if lval.path[index].lexeme not in struct_dict: # checks for undefined variables
                    msg = 'undefined variable "%s"' % lval.path[index].lexeme
                    self.__error(msg, lval.path[index])
                self.current_type = struct_dict.get(lval.path[index].lexeme)
                index += 1

    def visit_fun_param(self, fun_param):
        self.current_type = fun_param.param_type.tokentype
        self.sym_table.add_id(fun_param.param_name.lexeme)
        self.sym_table.set_info(fun_param.param_name.lexeme, fun_param.param_type.tokentype)

    def visit_simple_rvalue(self, simple_rvalue):
        if simple_rvalue.val.tokentype == token.INTVAL:
            self.current_type = token.INTTYPE
        elif simple_rvalue.val.tokentype == token.FLOATVAL:
            self.current_type = token.FLOATTYPE
        elif simple_rvalue.val.tokentype == token.BOOLVAL:
            self.current_type = token.BOOLTYPE
        elif simple_rvalue.val.tokentype == token.STRINGVAL:
            self.current_type = token.STRINGTYPE
        elif simple_rvalue.val.tokentype == token.NIL:
            self.current_type = token.NIL

    def visit_new_rvalue(self, new_rvalue):
        self.current_type = new_rvalue.struct_type.lexeme

    def visit_call_rvalue(self, call_rvalue):

        param_types = self.sym_table.get_info(call_rvalue.fun.lexeme)
        if param_types is None:
            msg = 'invalid function call'
            self.__error(msg, call_rvalue.fun)

        param_list = param_types[0]
        param_index = 0

        # checks parameter length
        if len(call_rvalue.args) != len(param_list):
            msg = 'invalid number of parameters'
            self.__error(msg, call_rvalue.fun)

        for params in call_rvalue.args:
            params.accept(self)
            # checks if parameters match
            if not param_list[param_index] == self.current_type:
                msg = 'invalid parameter'
                self.__error(msg, call_rvalue.fun)
            param_index += 1
        self.current_type = param_types[1]

    def visit_id_rvalue(self, id_rvalue):
        length = len(id_rvalue.path)
        # checks if the value exists
        if not self.sym_table.id_exists(id_rvalue.path[0].lexeme):
            msg = 'undefined variable "%s"' % id_rvalue.path[0].lexeme
            self.__error(msg, id_rvalue.path[0])

        if length > 1:
            index = 1
            while index < length:
                struct_name = self.sym_table.get_info(id_rvalue.path[index - 1].lexeme)
                counter = index - 1
                # I just check for the parent struct has a type that should exist
                while struct_name is None:
                    struct_name = self.sym_table.get_info(id_rvalue.path[counter].lexeme)
                    counter -= 1
                struct_dict = self.sym_table.get_info(struct_name)

                # checks if current_type is a member of the struct
                if id_rvalue.path[index].lexeme not in struct_dict:
                    msg = 'undefined variable "%s"' % id_rvalue.path[index].lexeme
                    self.__error(msg, id_rvalue.path[index])
                self.current_type = struct_dict.get(id_rvalue.path[index].lexeme)
                index += 1
        else:
            # implicit declarations
            self.current_type = self.sym_table.get_info(id_rvalue.path[0].lexeme)




