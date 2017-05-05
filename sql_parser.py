"""
Michael Harrington
Grant Broadwater

Lexer for sql like input for assignment
"""

import sys

from base_parser import ParserException, Parser
from sql_lexer import Lexer
from sql_ast import ( AST_TableDecl,
                      AST_AttributeDecl,
                      AST_TableDecls,
                      AST_SQL,
                      AST_SqlQueries,
                      AST_SqlQuery,
                      AST_Select,
                      AST_Attribute,
                      AST_From,
                      AST_FromTable,
                      AST_Where,
                      AST_BoolExpr,
                      AST_GroupBy,
                      AST_Aggregate,
                      AST_Having,
                      AST_BoolFullExpr,
                      AST_QChain,
                      AST_NestQuery,
                    )

def parse_sql(inputStr):
    parser = SqlParser(inputStr)
    return parser.parse()

class SqlParser(Parser):
    def __init__(self, inputStr):
        super(self.__class__, self).__init__()
        self.tokens = Lexer.tokenize(inputStr)

    def parse(self):
        super(self.__class__, self).parse()

        success = True
        ast = None
        try:
            ast = self.parse_StartSymbol()
            self.parse_EndSymbol()
        except ParserException:
            success = False

        return ast

    """
    Parse methods for lexer
    """

    def parse_Identifier(self):
        identifier = self.token
        if Lexer.identifier(self.token):
            self.getToken()
        else:
            raise ParserException('Identifier')
        return identifier

    def parse_NonKeyword(self):
        if self.token not in Lexer.keywords:
            self.getToken()
        else:
            raise ParserException('NonKeyword')

    def parse_Attribute(self):
        token = self.token
        if Lexer.attribute(self.token):
            self.getToken()
        else:
            raise ParserException('Attribute')
        return AST_Attribute(token)

    def parse_Value(self):
        token = self.token
        if Lexer.value(self.token):
            self.getToken()
        else:
            raise ParserException('Value')
        return token

    """
    Parse methods build from sql like grammar
    """

    def parse_StartSymbol(self):
        return self.parse_sqlInput()

    def parse_EndSymbol(self):
        if self.token != Lexer.sentinelToken:
            raise ParserException('Not properly terminated')

    def parse_sqlInput(self):
        ast_tableDecls = self.parse_TableStatements()
        ast_queries = self.parse_SqlCommands()

        return AST_SQL(ast_tableDecls, ast_queries)

    def parse_SqlCommands(self):
        success = True
        ast_queries = AST_SqlQueries()

        while success:
            success, ast_query = self.try_SqlCommand()
            if success:
                ast_queries.addQuery(ast_query)

        return ast_queries

    def parse_SqlCommand(self):
        ast_q = self.parse_SqlQuery()

        self.try_Terminal(';')

        return ast_q

    def parse_QChain(self):
        success, ast_qchain = self.try_Keyword('INTERSECT')
        if success:
            return ast_qchain
        success, ast_qchain = self.try_Keyword('UNION')
        if success:
            return ast_qchain
        success, ast_qchain = self.try_Keyword('EXCEPT')
        if success:
            return ast_qchain
        return self.parse_Keyword('ADD')

    def parse_SqlQuery(self):
        success, _ = self.try_Terminal('(')
        if success:
            ast_q = self.parse_SqlQuery()
            self.parse_Terminal(')')
            success, ast_qchain = self.try_QChain()
            if success:
                ast_q_n = self.parse_SqlQuery()
                return AST_QChain(ast_qchain, ast_q, ast_q_n)
            return ast_q
        else:
            return self.parse_SqlQueryInner()

    def parse_SqlQueryInner(self):
        ast_qselect = self.parse_SqlQuerySelect()
        ast_qfrom = self.parse_SqlQueryFrom()
        ast_query = AST_SqlQuery(ast_qselect, ast_qfrom)

        success, ast_qwhere = self.try_SqlQueryWhere()
        if success:
            ast_query.setWhere(ast_qwhere)
            
        success, ast_qgb = self.try_SqlQueryGroupBy()
        if success:
            ast_query.setGroupBy(ast_qgb)

        success, ast_hv = self.try_SqlQueryHaving()
        if success:
            ast_query.setHaving(ast_hv)

        success, ast_qchain = self.try_QChain()
        if success:
            ast_q = self.parse_SqlQuery()

            return AST_QChain(ast_qchain, ast_query, ast_q)

        return ast_query

    def parse_SqlQuerySelect(self):
        success = True
        ast_select = AST_Select()

        self.parse_Keyword('SELECT')
        while success:
            ast_selector = self.parse_QSelector()
            ast_select.addSelector(ast_selector)
            success, _ = self.try_Terminal(',')

        return ast_select

    def parse_QSelector(self):
        agg_list = ['AVG', 'MAX', 'MIN', 'COUNT', 'AVG']

        for keyword in agg_list:
            success, _ = self.try_Keyword(keyword)
            if( success ):
                self.parse_Terminal('(')
                attr = self.parse_Attribute()
                self.parse_Terminal(')')
                return AST_Aggregate(keyword, attr)


        return self.parse_Attribute()

    def parse_SqlQueryFrom(self):
        success = True
        ast_from = AST_From()

        self.parse_Keyword('FROM')
        while success:
            ast_fromTable = self.parse_FromTable()
            ast_from.addTable(ast_fromTable)
            success, _ = self.try_Terminal(',')

        return ast_from

    def parse_FromTable(self):
        tableName = self.parse_Identifier()
        ast_fromTable = AST_FromTable(tableName)
        if self.try_Keyword('AS')[0]:
            alias = self.parse_Identifier()
            ast_fromTable.setAlias(alias)

        return ast_fromTable

    def parse_SqlQueryHaving(self):
        ast_where = AST_Having()

        self.parse_Keyword('HAVING')
        ast_bfe = self.parse_BoolFullExpr()
        ast_where.addBoolExpr(ast_bfe, None)

        return ast_where

    def parse_SqlQueryWhere(self):
        ast_where = AST_Where()

        self.parse_Keyword('WHERE')
        ast_bfe = self.parse_BoolFullExpr()
        ast_where.addBoolExpr(ast_bfe, None)

        return ast_where

    def parse_BoolFullExpr(self):
        ast_bc = None
        ast_bfe = AST_BoolFullExpr()

        success, _ = self.try_Keyword('NOT')
        if success:
            ast_bfe.invert = True
        success = True
        while success:
            s, _ = self.try_Terminal('(')
            if s:
                ast_bfei = self.parse_BoolFullExpr()
                self.parse_Terminal(')')
            else:
                ast_bfei = self.parse_BoolFullExprInner()

            ast_bfe.addBoolExpr(ast_bfei, ast_bc)
            success, ast_bc = self.try_BoolChain()

        return ast_bfe

    def parse_BoolFullExprInner(self):
        success = True
        ast_bc = None
        ast_bfe = AST_BoolFullExpr()
        while success:
            ast_boolClause = self.parse_BoolClause()
            ast_bfe.addBoolExpr(ast_boolClause, ast_bc)
            success, ast_bc = self.try_BoolChain()

        return ast_bfe

    def parse_BoolClause(self):
        success, _ = self.try_Terminal('(')
        if success:
            ast_bfe = self.parse_BoolFullExpr()

            self.parse_Terminal(')')
            return ast_bfe

        success, ast_nestQuery = self.try_NestQuery()
        if success:
            return ast_nestQuery
        else:
            lhs = self.parse_BoolTerm()
            comp = self.parse_BoolComp()
            rhs = self.parse_BoolTerm()

            return AST_BoolExpr(lhs, comp, rhs)

    def parse_NestQuery(self):
        keyword = self.parse_Keyword('EXISTS')
        ast_query = self.parse_SqlQuery()
        return AST_NestQuery(keyword, ast_query)

    def parse_BoolTerm(self):
        success, ast_bt = self.try_QSelector()
        if success:
            return ast_bt
        ast_bt = self.parse_Value()
        return ast_bt

    def parse_BoolComp(self):
        success, ast_bc = self.try_Terminal('=')
        if success:
            return ast_bc
        success, ast_bc = self.try_Terminal('<')
        if success:
            return ast_bc
        success, ast_bc = self.try_Terminal('>')
        if success:
            return ast_bc
        success, ast_bc = self.try_Terminal('<=')
        if success:
            return ast_bc
        success, ast_bc = self.try_Terminal('>=')
        if success:
            return ast_bc
        ast_bc = self.parse_Terminal('<>')
        return ast_bc

    def parse_BoolChain(self):
        success, ast_bc = self.try_Keyword('AND')
        if success:
            return ast_bc
        ast_bc = self.parse_Keyword('OR')
        return ast_bc

    def parse_SqlQueryGroupBy(self):
        self.parse_Keyword('GROUP')
        self.parse_Keyword('BY')

        ast_gb = AST_GroupBy()

        success = True
        while success:
            ast_attr = self.parse_Attribute()
            ast_gb.addAttribute(ast_attr)
            success, _ = self.try_Terminal(',')

        return ast_gb

    def parse_TableStatements(self):
        ast_tables = AST_TableDecls()
        success = True

        while success:
            success, ast_table = self.try_TableStatement()
            if success:
                ast_tables.addTable(ast_table)

        return ast_tables

    def parse_TableStatement(self):
        success = True

        tableName = self.parse_Identifier()
        ast_table = AST_TableDecl(tableName)
        self.parse_Terminal('(')
        while success:
            attribute = self.parse_TableStmntAttribute()
            ast_table.addAttribute(attribute)
            success, _ = self.try_Terminal(',')
            
        self.parse_Terminal(')')

        return ast_table

    def parse_TableStmntAttribute(self):
        name = self.parse_Identifier()
        self.parse_Terminal(':')
        att_type = self.parse_Identifier()

        return AST_AttributeDecl(name, att_type)

