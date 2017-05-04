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
                    )

def PrettyASTPrint(root, level=0):
    for query in root.queries.queries:
        PrettyASTQPrint(query, level)
        print('\n')

def PrettyASTQPrint(query, level):
    if type(query) is AST_QChain:
        node_print(query.qchain, level)
        PrettyASTQPrint(query.left, level + 1)
        PrettyASTQPrint(query.right, level + 1)
    else:
        QueryPrettyPrint(query, level)

def QueryPrettyPrint(query, level):
    node_print('SELECT', level)
    node_print('Select Attributes', level + 1)
    for selector in query.qselect.selectors:
        node_print(str(selector), level + 2)
    node_print('From Tables', level + 1)
    for table in query.qfrom.tables:
        node_print(str(table), level + 2)

    if query.qwhere:
        node_print('Where Condition', level + 1)
        for e, c in zip(query.qwhere.boolExprs, query.qwhere.boolComps):
            if c:
                node_print(str(c) + ' ' + str(e), level + 2)
            else:
                node_print(str(e), level + 2)

    if query.qgb:
        node_print('Group By', level + 1)
        node_print(str(query.qgb)[9:], level + 2)

        if query.qhaving:
            node_print('Having', level + 1)
            for e, c in zip(query.qhaving.boolExprs, query.qhaving.boolComps):
                if c:
                    node_print(str(c) + ' ' + str(e), level + 2)
                else:
                    node_print(str(e), level + 2)

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
    return str(chain.qchain) + '(' + RACommandPrint(chain.left, tables) + ', ' + RACommandPrint(chain.right, tables) + ')'

def RAQueryString(query, tables):
    closeParens = ')'

    def selector_to_str(selector):
        if(str(selector) == "*"):
            tableIndex = [t.name for t in tables].index(query.qfrom.tables[0].name)
            return ', '.join(map(lambda el: str(el).split(":")[0], tables[tableIndex].attributes))
        else:
            return str(selector)

    project = 'ProjectFunc ' + ', '.join(map(selector_to_str, query.qselect.selectors)) + '('

    select = ''
    if query.qwhere:
        closeParens += ')'
        select = 'SelectFunc ' + str(query.qwhere)[6:] + '('

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

    sql_tables = ' x '.join([table.name for table in query.qfrom.tables])

    query_str = project + groupby + select + sql_tables + closeParens

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
    node_print(str(node.qchain), level)
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

    if query.qwhere:
        level += 1
        node_print('SelectFunc ' + str(query.qwhere)[6:], level)

    if len(query.qfrom.tables) > 1:
        level += 1
        node_print('x', level)
    level += 1
    for table in query.qfrom.tables:
        node_print(table.name, level)

"""
Standard Printing Functions
"""
def node_print(text, level):
    print('\t'*level + text)

def QChainString(qc):
    if qc == 'INTERSECT':
        return 'intersect'
    elif qc == 'UNION':
        return 'U'
    elif qc == 'ADD':
        return '+'
    elif qc == 'EXCEPT':
        return '-'
