"""
Michael Harrington
Grant Broadwater

This file handles abstract syntax tree printing
"""

"""
AST SQL Printing
"""
from sql_ast import AST_Aggregate

def PrettyASTPrint(root):
    for query in root.queries.queries:
        QueryPrettyPrint(query)
        print('\n')

def QueryPrettyPrint(query):
    node_print('SELECT', 0)
    node_print('Select Attributes', 1)
    for selector in query.qselect.selectors:
        node_print(str(selector), 2)
    node_print('From Tables', 1)
    for table in query.qfrom.tables:
        node_print(str(table), 2)

    if query.qwhere:
        node_print('Where Condition', 1)
        for e, c in zip(query.qwhere.boolExprs, query.qwhere.boolComps):
            if c:
                node_print(str(c) + ' ' + str(e), 2)
            else:
                node_print(str(e), 2)

    if query.qgb:
        node_print('Group By', 1)
        node_print(str(query.qgb)[9:], 2)

        if query.qhaving:
            node_print('Having', 1)
            for e, c in zip(query.qhaving.boolExprs, query.qhaving.boolComps):
                if c:
                    node_print(str(c) + ' ' + str(e), 2)
                else:
                    node_print(str(e), 2)

    if query.qchain:
        node_print(query.qchain, 0)
        QueryPrettyPrint(query.child)

"""
Relational Algebra Printing
"""
def RAPrint(root):
    for command in root.queries.queries:
        print(RAQueryString(command, root.tables.tables))
        print('\n')

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

    if query.qchain:
        query_str += ' ' + QChainString(query.qchain) + ' ' + RAQueryString(query.child, tables)

    return query_str

"""
Query Tree Printing
"""
def RAQsTreePrint(root):
    for query in root.queries.queries:
        RAQTreePrint(query, root.tables.tables)
        print('\n')

def RAQTreePrint(query, tables, level=-1):
    hold_level = level
    if query.qchain:
        level += 1
        node_print(QChainString(str(query.qchain)), level)

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

    if query.qchain:
        level = hold_level
        level += 1
        RAQTreePrint(query.child, tables, level)

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
