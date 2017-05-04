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
    for qcommand in root.queries.queries:
        QCPrettyPrint(qcommand)
        print('\n')

def QCPrettyPrint(ast_qc):
    for query, qc in zip(ast_qc.queries, ast_qc.qChains):
        QueryPrettyPrint(query)
        if qc:
            print(qc)

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

"""
Relational Algebra Printing
"""
def RAPrint(root):
    for command in root.queries.queries:
        RACommPrint(command, root.tables.tables)
        print('\n')

def RACommPrint(command, tables):
    for query, qc in zip(command.queries, command.qChains):
        RAQueryPrint(query, tables)
        if qc == 'INTERSECT':
            print('intersect')
        elif qc == 'UNION':
            print('U')
        elif qc == 'ADD':
            print('+')
        elif qc == 'EXCEPT':
            print('-')

def RAQueryPrint(query, tables):
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

    tables = ' x '.join([table.name for table in query.qfrom.tables])

    print(project + groupby + select + tables + closeParens)

"""
Query Tree Printing
"""
def RAQsTreePrint(root):
    for query in root.queries.queries:
        RAQTreePrint(query, root.tables.tables)
        print('\n')

def RAQTreePrint(command, tables):
    level = -1

    if command.qChains[0]:
        level += 1
        node_print(str(command.qChains[0]), level)
    hold_level = level
    for query in command.queries:
        level = hold_level

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
