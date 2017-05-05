"""
Michael Harrington
Grant Broadwater

This file handles abstract syntax tree printing
"""

"""
AST SQL Printing
"""
from sql_ast import ( AST_Aggregate,
                      AST_QChain,
                      AST_SqlQuery,
                      AST_NestQuery,
                    )

def PrettyASTPrint(root, level=0):
    for query in root.queries.queries:
        print('\n'.join(PrettyASTQPrint(query, level)))
        print('\n')

def PrettyASTQPrint(query, level):
    if type(query) is AST_QChain:
        yield node_string(query.qchain, level)
        for line in PrettyASTQPrint(query.left, level + 1):
            yield line
        for line in PrettyASTQPrint(query.right, level + 1):
            yield line
    else:
        for line in QueryPrettyPrint(query, level):
            yield line

def QueryPrettyPrint(query, level):
    yield node_string('SELECT', level)
    yield node_string('Select Attributes', level + 1)
    for selector in query.qselect.selectors:
        yield node_string(str(selector), level + 2)
    yield node_string('From Tables', level + 1)
    for table in query.qfrom.tables:
        yield node_string(str(table), level + 2)

    if query.qwhere:
        yield node_string('Where Condition', level + 1)
        def handler(ast_nq):
            yield 'EXISTS ('
            for line in PrettyASTQPrint(ast_nq.query, level + 3):
                yield line
            yield node_string(')', level + 3)
        for e, c in zip(query.qwhere.boolExprs, query.qwhere.boolComps):
            if c:
                yield node_string(str(c) + ' ' + e.mystring(handler), level + 2)
            else:
                yield node_string(e.mystring(handler), level + 2)

    if query.qgb:
        yield node_string('Group By', level + 1)
        yield node_string(str(query.qgb)[9:], level + 2)

        if query.qhaving:
            yield node_string('Having', level + 1)
            for e, c in zip(query.qhaving.boolExprs, query.qhaving.boolComps):
                if c:
                    yield node_string(str(c) + ' ' + str(e), level + 2)
                else:
                    yield node_string(str(e), level + 2)

"""
Relational Algebra Printing
"""
def RAPrint(root):
    for command in root.queries.queries:
        print(RACommandPrint(command, root.tables.tables))
        print('\n')

def RACommandPrint(command, tables):
    if type(command) is AST_QChain:
        return RAChainString(command, tables)
    else:
        return RAQueryString(command, tables)

def RAChainString(chain, tables):
    return '(' + RACommandPrint(chain.left, tables) + ' ' + QChainString(chain.qchain) + ' ' + RACommandPrint(chain.right, tables) + ')'

def RAQueryString(query, tables):
    closeParens = ')'

    def selector_to_str(selector):
        if(str(selector) == "*"):
            tableIndex = [t.name for t in tables].index(query.qfrom.tables[0].name)
            return ', '.join(map(lambda el: str(el).split(":")[0], tables[tableIndex].attributes))
        else:
            return str(selector)

    project = 'ProjectFunc ' + ', '.join(map(selector_to_str, query.qselect.selectors)) + '('

    nested_queries = []

    select = ''
    if query.qwhere:
        def handler(ast_nq):
            nested_queries.append(ast_nq.query)
            yield ast_nq.query.qwhere.mystring(handler)
        closeParens += ')'
        select = 'SelectFunc ' + query.qwhere.mystring(handler) + '('

    groupby = ''
    if query.qgb:
        closeParens += ')'
        aggregators = [str(s) for s in query.qselect.selectors if type(s) == AST_Aggregate]
        aggregators.extend(map(str, query.qgb.attributes))
        if query.qhaving:
            aggregators.extend(query.qhaving.aggregators)

            closeParens += ')'
            groupby = 'SelectFunc ' + str(query.qhaving)[7:] + ' (GroupByFunc ' + ', '.join(aggregators) + '('
        else:        
            groupby = 'GroupByFunc ' + ', '.join(aggregators) + '('

    sql_tables = list(query.qfrom.tables)
    for q in nested_queries:
        sql_tables.extend(q.qfrom.tables)
    table_string = ' x '.join([table.name for table in sql_tables])

    query_str = project + groupby + select + table_string + closeParens

    return query_str

"""
Query Tree Printing
"""
def RAQsTreePrint(root):
    for node in root.queries.queries:
        RANTreePrint(node, root.tables.tables)
        print('\n')

def RANTreePrint(node, tables, level=-1):
    if type(node) is AST_QChain:
        RACTreePrint(node, tables, level)
    else:
        RAQTreePrint(node, tables, level)

def RACTreePrint(node, tables, level):
    level += 1
    node_print(QChainString(node.qchain), level)
    RANTreePrint(node.left, tables, level)
    RANTreePrint(node.right, tables, level)

def RAQTreePrint(query, tables, level=-1):
    def selector_to_str(selector):
        if(str(selector) == "*"):
            tableIndex = [t.name for t in tables].index(query.qfrom.tables[0].name)
            return ', '.join(map(lambda el: str(el).split(":")[0], tables[tableIndex].attributes))
        else:
            return str(selector)

    level += 1
    node_print('ProjectFunc ' + ', '.join(map(selector_to_str, query.qselect.selectors)), level)

    if query.qgb:
        aggregators = [str(s) for s in query.qselect.selectors if type(s) == AST_Aggregate]
        aggregators.extend(map(str, query.qgb.attributes))
        if query.qhaving:
            aggregators.extend(query.qhaving.aggregators)
            level += 1
            node_print('SelectFunc ' + str(query.qhaving)[7:], level)
        level += 1
        node_print('GroupByFunc ' + ', '.join(aggregators), level)

    nested_queries = []
    if query.qwhere:
        def handler(ast_nq):
            nested_queries.append(ast_nq.query)
            yield ast_nq.query.qwhere.mystring(handler)
        level += 1
        node_print('SelectFunc ' + query.qwhere.mystring(handler), level)

    if len(query.qfrom.tables) > 1:
        level += 1
        node_print('x', level)

    sql_tables = list(query.qfrom.tables)
    for q in nested_queries:
        sql_tables.extend(q.qfrom.tables)
    level += 1
    for table in sql_tables:
        node_print(table.name, level)

"""
Standard Printing Functions
"""
def node_print(text, level):
    print('\t'*level + str(text))

def node_string(text, level):
    return '\t'*level + str(text)

def QChainString(qc):
    if qc == 'INTERSECT':
        return 'intersect'
    elif qc == 'UNION':
        return 'U'
    elif qc == 'ADD':
        return '+'
    elif qc == 'EXCEPT':
        return '-'
