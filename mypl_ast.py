#!//usr/bin/python3
#
# Author: Vincent Lombardi
# Course: CPSC 326, Spring 2019
# Assignment: 4
# Description:
# contains the classes for the AST Node.
# --------------------------------------------------------

import mypl_token as token


class ASTNode(object):
    """The base class for the abstract syntax tree."""
    def accept(self, visitor): pass


class Stmt(ASTNode):
    """The base class for all statement nodes."""
    def accept(self, visitor): pass


class StmtList(ASTNode):
    """A statement list consists of a list of statements."""
    def __init__(self):
        self.stmts = []

    def accept(self, visitor):
        visitor.visit_stmt_list(self)


class Expr(ASTNode):
    def accept(self, visitor): pass


class ExprStmt(Stmt):
    def __init__(self):
        self.expr = None

    def accept(self, visitor):
        visitor.visit_expr_stmt(self)


class VarDeclStmt(Stmt):
    def __init__(self):
        self.var_id = None  # Token (ID)
        self.var_type = None    # Token (STRINGTYPE, ..., ID)
        self.var_expr = None    # Expr node

    def accept(self, visitor):
        visitor.visit_var_decl_stmt(self)


class AssignStmt(Stmt):
    def __init__(self):
        self.lhs = None
        self.rhs = None

    def accept(self, visitor):
        visitor.visit_assign_stmt(self)


class StructDeclStmt(Stmt):
    def __init__(self):
        self.struct_id = None
        self.var_decls = []

    def accept(self, visitor):
        visitor.visit_struct_decl_stmt(self)


class FunDeclStmt(Stmt):
    def __init__(self):
        self.fun_name = None
        self.params = []
        self.return_type = None
        self.stmt_list = StmtList()

    def accept(self, visitor):

        visitor.visit_fun_decl_stmt(self)


class ReturnStmt(Stmt):
    def __init__(self):
        self.return_expr = None
        self.return_token = None

    def accept(self, visitor):
        visitor.visit_return_stmt(self)


class WhileStmt(Stmt):
    def __init__(self):
        self.bool_expr = None
        self.stmt_list = StmtList()

    def accept(self, visitor):
        visitor.visit_while_stmt(self)


class IfStmt(Stmt):
    def __init__(self):
        self.if_part = BasicIf()
        self.elseifs = []
        self.has_else = False
        self.else_stmts = StmtList()

    def accept(self, visitor):
        visitor.visit_if_stmt(self)


class SimpleExpr(Expr):
    def __init__(self):
        self.term = None

    def accept(self, visitor):
        visitor.visit_simple_expr(self)


class ComplexExpr(Expr):
    def __init__(self):
        self.first_operand = None
        self.math_rel = None
        self.rest = None

    def accept(self, visitor):
        visitor.visit_complex_expr(self)


class BoolExpr(ASTNode):
    def __init__(self):
        self.first_expr = None
        self.bool_rel = None
        self.second_expr = None
        self.bool_connector = None
        self.rest = None
        self.negated = False

    def accept(self, visitor):
        visitor.visit_bool_expr(self)


class LValue(ASTNode):
    def __init__(self):
        self.path = []

    def accept(self, visitor):
        visitor.visit_lvalue(self)


class FunParam(Stmt):
    def __init__(self):
        self.param_name = None
        self.param_type = None

    def accept(self, visitor):
        visitor.visit_fun_param(self)


class BasicIf(object):
    def __init__(self):
        self.bool_expr = None
        self.stmt_list = StmtList()

    def accept(self, visitor):
        visitor.visit_basic_if_stmt(self)


class RValue(ASTNode):
    def accept(self, visitor): pass


class SimpleRValue(RValue):
    def __init__(self):
        self.val = None

    def accept(self, visitor):
        visitor.visit_simple_rvalue(self)


class NewRValue(RValue):
    def __init__(self):
        self.struct_type = None

    def accept(self, visitor):
        visitor.visit_new_rvalue(self)


class CallRValue(RValue):
    def __init__(self):
        self.fun = None
        self.args = []

    def accept(self, visitor):
        visitor.visit_call_rvalue(self)


class IDRvalue(RValue):
    """An identifier rvalue consists of a path of one or more identifiers."""
    def __init__(self):
        self.path = []          # List of Token (id)

    def accept(self, visitor):
        visitor.visit_id_rvalue(self)


class Visitor(object):

    """The base class for AST visitors."""
    def visit_stmt_list(self, stmt_list): pass

    def visit_expr_stmt(self, expr_stmt): pass

    def visit_var_decl_stmt(self, var_decl): pass

    def visit_assign_stmt(self, assign_stmt): pass

    def visit_struct_decl_stmt(self, struct_decl): pass

    def visit_fun_decl_stmt(self, fun_decl): pass

    def visit_return_stmt(self, return_stmt): pass

    def visit_while_stmt(self, while_stmt): pass

    def visit_if_stmt(self, if_stmt): pass

    def visit_simple_expr(self, simple_expr): pass

    def visit_complex_expr(self, complex_expr): pass

    def visit_bool_expr(self, bool_expr): pass

    def visit_lvalue(self, lval): pass

    def visit_fun_param(self, fun_param): pass

    def visit_simple_rvalue(self, simple_rvalue): pass

    def visit_new_rvalue(self, new_rvalue): pass

    def visit_call_rvalue(self, call_rvalue): pass

    def visit_id_rvalue(self, id_rvalue): pass

    def visit_basic_if_stmt(self, basic_if_stmt): pass