import re
from functools import reduce
#import cProfile, pstats, io
#from pstats import SortKey



def input_formula():
    # get input formula
    formula_phi = str(input(
                        "Type input formula phi with \n"
                        "T, F as top, bottom \n "
                        "small letters a,b,c,... optionally ending with with numbers a0,b0,c0,... as boolean variables, \n"
                        "() for parentheses (precedence): \n"
                        "not()  not operator (negation), \n"
                        "& and operator (conjunction), \n"
                        "_ box operator (possibility), \n"
                        "phi = "
                        )
                    )
    return formula_phi

"""
    regular expression patterns
        ""
        [TF],
        [a-z]+[0-9]*,
        (.*)
        not(.*)
        &
        _
"""

def tableux_representation(phi):
    """recursive function that parses input formula string into a tableux representation that can be easily evaluated for satisfiability.
    input: formula phi of type string in specified input format.
    output:
        empty list                      in case of empty string
        single element list             in case of top, bottom, (not-)literal
        (sub-)formula string            in case of (not-)literal
        one recurisve call              in case of parenthesis (no branching)
        one recursive call              in case of double negation, not-rule application (no branching)
        list of two recursive calls     in case of and-operator (conjunction), and-rule application (and branching), (or node)
        3-tuple of two recursive calls    in case of or-operator (disjunction), not-and-rule application (or branching), (or node)
        1-tuple of one recursive call     in case of box-operator (necessity)
        2-tuple of one recursive call       in case of not-box-operator, box-rule applicattion (and node)
    """

    # remove whitespaces
    phi = phi.replace(" ", "")
    
    ### case distinction on phi
    # phi is the empty string
    if not phi:
        return []
    # phi is top or bottom
    elif phi in ['T', 'F', 'not(T)', 'not(F)']:
        return [phi]
    # phi is a single positive literal
    elif re.fullmatch(r"[a-z]+[0-9]*", phi):
        return [phi]
    # phi starts with a parenthesis
    # the parenthesis expression either spans the whole formula or a subformula. The subformula must be a conjunct.
    elif phi.startswith("("):
        # determine if parenthesis spans the whole formula and if not
        # split the formula into the two highest level conjuncts that are determined by the position of the closing parenthesis of the first opening parenthesis
        phi_list = first_parenthesised_subformula(phi)
        # spans whole formula
        if len(phi_list) == 1:
            # remove parenthesis
            phi = phi.removeprefix("(")
            phi = phi.removesuffix(")")
            return tableux_representation(phi)
        # spans a top-level conjunct
        if len(phi_list) == 3:
            # apply and-rule
            # list to indicate conjunction
            return [tableux_representation(phi_list[0]), tableux_representation(phi_list[2])]
    # phi starts with not-parenthesis
    # spans whole formula or subformula (top-level conjunct)
    elif phi.startswith("not("):
        phi_list = first_parenthesised_subformula(phi)

        # spans whole formula, thus either not-literal, not-rule application, not-and-rule application, not-box-rule application
        if len(phi_list) == 1:
            # remove the not-parenthesis
            phi = phi.removeprefix("not(").removesuffix(")")

            # not-literal
            # regular expression matches only a literal
            if re.fullmatch(r"[a-z]+[0-9]*", phi):
                # return not-literal as a single element list
                return ["not(" + phi + ")"]

            # not-rule or not-and-rule
            elif phi.startswith("not("):
                phi_list_3 = first_parenthesised_subformula(phi)
                # second not-parenthesis spans whole formula, not-rule applies
                if len(phi_list_3) == 1:
                    # not-rule
                    # remove second not-parenthesis
                    phi = phi.removeprefix("not(")
                    phi = phi.removesuffix(")")
                    return tableux_representation(phi)
                # second not-parenthesis does not span whole formula, not-and-rule applies
                elif len(phi_list_3) == 3:
                    # tuple to indicate or-node
                    return ('or', tableux_representation(negate(phi_list_3[0])), tableux_representation(negate(phi_list_3[2])))
            
            # not-box or not-and-rule
            elif phi.startswith('_'):

                count_boxes = 0
                while phi.startswith('_'):
                    count_boxes += 1
                    phi = phi.removeprefix('_')
                assert not phi.startswith('_')

                phi_list_4 = first_parenthesised_subformula(phi)
                # box is not parenthesised
                # either literal and thus not-box or not-and
                # literal, not-box
                if re.fullmatch(r'[a-z]+[0-9]*', phi):
                    assert count_boxes > 0
                    return ('not', tableux_representation(negate('_' * (count_boxes-1) + phi)))
                #
                elif phi.startswith('not('):
                    pass
                # not parenthesised, not-and
                elif re.match(r'[a-z]+[0-9]*', phi):
                    phi_tuple_5 = phi.partition('&')
                    assert phi_tuple_5[1] and phi_tuple_5[2]
                    return ('or', tableux_representation(negate('_' * count_boxes + phi_tuple_5[0])), tableux_representation(negate(phi_tuple_5[2])))
                
                # not-box
                if len(phi_list_4) == 1:
                    assert count_boxes > 0
                    return ('not', tableux_representation(negate('_' * (count_boxes-1) + phi)))
                # not-and
                elif len(phi_list_4) == 3:
                    return ('or', tableux_representation(negate('_' * count_boxes + phi_list_4[0])), tableux_representation(negate(phi_list_4[2])))
                else:
                    assert False
                
            else:
                # finds top-level "&" to which it applies, similar behaviour to string method partition
                phi_list_6 = first_parenthesised_subformula(phi)
                if len(phi_list_6) == 3:
                    # tuple to indicate or-node
                    return ('or', tableux_representation(negate(phi_list_6[0])), tableux_representation(negate(phi_list_6[2])))
                elif parenthesised_formula(phi):
                    return tableux_representation('not' + phi)
                else:
                     # first and-operator & is on highest level
                    phi_tuple_7 = phi.partition("&")

                     # tuple to indicate or-node
                    return ('or', tableux_representation(negate(phi_tuple_7[0])), tableux_representation(negate(phi_tuple_7[2])))
        # and-case
        elif len(phi_list) == 3:
            # apply and-rule
            # list to indicate and-node
            return [tableux_representation(phi_list[0]), tableux_representation(phi_list[2])]
    
    # starts with a literal and must continue with an and-connective or must be an axiom
    elif re.match(r"[a-z]+[0-9]*", phi) or (phi.partition('&')[0] in ['T', 'F', 'not(T)', 'not(F)']):
        if re.fullmatch(r"[a-z]+[0-9]*", phi): # formula is one literal
            return phi
        else:
            # and-rule applies
            # first occurence of and-connective is a top-level connective
            phi_list = phi.partition("&")
            return [tableux_representation(phi_list[0]), tableux_representation(phi_list[2])] # list to indicate and-node
    
    # box-case
    elif phi.startswith("_"):

        count_boxes = 0
        while phi.startswith('_'):
            count_boxes += 1
            phi = phi.removeprefix('_')
        assert not phi.startswith('_')
        
        phi_list = first_parenthesised_subformula(phi)

        # continues with literal, box-case
        if re.fullmatch(r'[a-z]+[0-9]*', phi):
            return ret_tuple(phi, count_boxes)
        elif phi.startswith('not('):
            pass
        # and-case
        elif re.match(r'[a-z]+[0-9]*', phi):
            phi_tuple = phi.partition('&')
            assert phi_tuple[1] and phi_tuple[2]
            return [tableux_representation('_' * count_boxes + phi_tuple[0]), tableux_representation(phi_tuple[2])]
        
        # continues with parenthesis or not-parenthesis
        assert phi_list
        # spans whole formula, box-case
        if len(phi_list) == 1:
            return ret_tuple(phi, count_boxes)
        # spans subformula, and-case
        elif len(phi_list) == 3:
            assert phi_list[0] and phi_list[1] and phi_list[2]
            return [tableux_representation('_' * count_boxes + phi_list[0]), tableux_representation(phi_list[2])]
        else:
            assert False

def ret_tuple(phi, count_boxes, not_box=False):
    """wraps formula phi in the number of 1-tupel given by positional argument count boxes."""
    assert count_boxes > 0
    ret = (tableux_representation(phi),)
    count_boxes -= 1
    while count_boxes > 0:
        ret = (ret,)
        count_boxes -= 1
    return ret

def first_parenthesised_subformula(phi):
    """ input: 
            formula phi of type string
            formula phi starts with '(' or 'not('
            input formula starts neither with '(' nor 'not(' -> no parenthesis outputs empty list, 
        output:
            empty list []
            single element list (opening parenthesis is only closed at the end of the string)
            three element list: splits string into two conjuncts after first opening parenthesis is closed
    """
    phi = phi.replace(" ", "")
    # start counting parenthesis at the position of the first opening parenthesis
    i = phi.find("(")
    if i >= 0:
        count = 0
        for j,c in enumerate(phi[i:]):
            if c == "(":
                count += 1
            elif c == ")":
                count -= 1
            elif count == 0:
                # phi does not end with a closing parenthesis ")"
                return [phi[:(i+j)], phi[(i+j)], phi[(i+j+1):]]
        # phi ends with a closing parenthesis ")"
        return [phi]
    return []

def negate(subphi):
    """negates the input subformula phi of type string. Either adds a not-parenthesis or removes a not-parenthesis.
    negate("(p & not(p))") -> not((p & not(p))), not(p & not(p))
    negate("p & not(p)") -> not(p & not(p))
    negate("not(p) & not(q)") -> not(not(p) & not(q))"""
    if subphi.startswith('not(') and subphi.endswith(')') and len(first_parenthesised_subformula(subphi)) == 1:
        return subphi.removeprefix('not(').removesuffix(')')
    else:
        return 'not(' + subphi + ')'

def parenthesised_formula(phi):
    return phi.startswith('(') and phi.endswith(')') and (len(first_parenthesised_subformula(phi)) == 1)



### apply tableux method to representation of parsed input formula string

def tableux_method(repr):
    """tableux representation is a list or tuple of lists or tuples and is binary since logical operators and and or are binary."""
    assert type(repr) == list or type(repr) == tuple

    #print(repr)

    # initialisation
    if type(repr) != list:
        return tableux_method([repr])
    
    # empty list
    elif not repr:
        return False

    new_repr_1 = []
    new_repr_2 = []

    boxes = False

    for i in range(len(repr)):
        clause = repr[i]
        # literal
        if type(clause) == str:
            new_repr_1.append(clause)
        # one element list is a literal
        elif type(clause) == list and len(clause) == 1:
            assert type(clause[0]) == str
            new_repr_1.append(clause[0])
        elif type(clause) == list and len(clause) == 2:
            new_repr_1.append(clause[0])
            new_repr_1.append(clause[1])
            return tableux_method(new_repr_1 + repr[i+1:])
        
        elif type(clause) == tuple:
            #assert len(clause) == 2

            if len(clause) == 3:
                new_repr_2 = new_repr_1.copy()
                new_repr_1.append(clause[1])
                new_repr_2.append(clause[2])
                branch_1 = tableux_method(new_repr_1 + repr[i+1:])
                #print(branch_1)
                if branch_1:
                    return branch_1
                else:
                    return tableux_method(new_repr_2 + repr[i+1:])
            else:
                assert len(clause) == 1 or len(clause) == 2
                boxes = True
                new_repr_1.append(clause)
    
    assert new_repr_2 == []
    
    
    # clashes
    for expr in new_repr_1:
        if type(expr) == str:
            if expr == 'F':
                return False
            #assert re.fullmatch(r'[a-z]+[0-9]*', expr.removeprefix('not(').removesuffix(')'))
            if expr.startswith('not(') and expr.endswith(')'):
                if expr.removeprefix('not(').removesuffix(')') in new_repr_1:
                    return False
                elif negate(expr) in new_repr_1:
                    return False
                else:
                    continue
                    


    # propositionally saturated and some boxes
    if boxes:
        and_node = apply_box_rule(new_repr_1)
        assert len(and_node) >= 1
        if not and_node[0]:
            return True
        else:
            if len(and_node) == 1:
                return tableux_method(and_node[0])
            else:
                return reduce(lambda a, b: a and b, map(tableux_method, and_node))
    
    # only literals, leaf of tableux tree, apply axiom/clash rule
    else:
        return eval_lits(new_repr_1)

        
def eval_lits(repr):
    if len(repr) == 1:
        s = repr[0]
        assert type(s) == str
        if s == 'T':
            return True
        elif s == 'F':
            return False
        else:
            return True
    else:
        for lit in repr:
            if lit.startswith('not(') and lit.endswith(')'):
                if lit.removeprefix('not(').removesuffix(')') in repr:
                    return False
            else:
                if 'not(' + lit + ')' in repr:
                    return False
        return True


def apply_box_rule(repr):
    # return a and-node as a list of list
    # remove literals and the highest-level boxes and not-boxes
    # not-boxes are branching
    new_repr = [[]]
    # check if there is a not box
    not_box = False
    for expr in repr:
        assert type(expr) == str or type(expr) == tuple
        if type(expr) == tuple:
            assert len(expr) == 1 or len(expr) == 2
            if len(expr) == 2:
                not_box = True
                break
    
    if not not_box:
        # node is true only boxes and not not-box, satisfiability is trivial
        return new_repr
    
    else:
        for expr in repr:
            if type(expr) == tuple:
                # box
                if len(expr) == 1:
                    for branch in new_repr:
                        assert type(branch) == list
                        branch.append(expr[0])
                elif len(expr) == 2:
                    assert type(expr) == list or type(expr) == tuple
                    assert type(expr) != str
                    new_repr += [new_repr[0] + [expr[1]]]
                else:
                    raise Exception("tuple length unequal 1 or 2.")
    
    return new_repr[1:]

    





### formula series


def generate_formula_series_1(n):
    ret = ["p0"]
    for i in range(1, n+1):
        phi = ret[-1] + "&" \
        + ('_' * (i-1)) \
        + "not(p" + str(i-1) + "&" \
        + "not(" \
        + "not(_not(p" + str(i) + "& q" + str(i) + "))" + "&"\
        + "not(_not(p" + str(i) + "& not(q" + str(i) + ")))" + "&" \
        + generate_formula(i) \
        + "))"
        ret.append(phi)
    return ret

def generate_formula(n):
    phi = "T" #"\n"
    for i in range(1, n+1):
        qi = "q" + str(i)
        phi += "&" "(" \
               + "not(" + qi + "&" "not(" "_" + qi + ")" ")" "&" \
               + "not(" "not(" + qi + ")" "&" + "not(" "_" "not(" + qi + ")" ")" ")" \
                                                                         ")" \
                                                                         #"\n"
    return phi

def generate_formula_series_2(n):
    ret = ["p0"]
    for i in range(1, n+1):
        phi = ret[-1] + "&" \
        + ('_' * (i-1)) \
        + "not(p" + str(i-1) + "&" \
        + "not(" \
        + "not(_not(p" + str(i) + "& q" + str(i) + "))" + "&"\
        + "not(_not(p" + str(i) + "& not(q" + str(i) + ")))" + "&" \
        + "))"
        ret.append(phi)
    return ret

def generate_formula_series_3(n):
    return [generate_formula(i) for i in range(n+1)]

def generate_formula_series_4(n):
    return [generate_formula(i) + '&F' for i in range(n+1)]


### test formulae

"""test_formula_1 = ""
test_formula_2 = "()"
test_formula_3 = "T"
test_formula_4 = "(T)"
test_formula_5 = "F"
test_formula_6 = "(F)"
test_formula_7 = "p"
test_formula_8 = "(p)"
test_formula_9 = "abc9"
test_formula_10 = "(abc123)"
test_formula_11 = "a123"
test_formula_12 = ""
test_formula_13 = "not(p)"
test_formula_14 = "not(not(p))"
test_formula_15 = "p & q"
test_formula_16 = "p & not(q)"
test_formula_17 = "p & not(p)"
test_formula_18 = "not(p) & q"
test_formula_19 = "not(p) & p"
test_formula_20 = "not(p) & not(q)"
test_formula_21 = "not(not(not(not(not(p))))) & not(not(not(not(p))))"
test_formula_22 = "not(p & q)"
test_formula_23 = "not(p & not(p))"
test_formula_24 = "not(p & q & r)"
test_formula_25 = "p & not(p & p)"
test_formula_26 = "p & not(not(p) & p)"
test_formula_27 = "not(not(q) & not(p))"
test_formula_28 = "p&q&r"
test_formula_29 = "p&q&r&not(p)"
test_formula_30 = "not((p))"
#test_formula_30 = "not((p & not(p)) & not(not(r)))"
test_formula_31 = "not((p & not(q)) & not(not(r) & r))"
test_formula_32 = "not((p & not(p)) & not(not(r) & r))"
test_formula_33 = "not((p & not(p)) & (not(r) & r))"
test_formula_34 = "not(p&not(p))"
test_formula_35 = "(p&q)&(q&r)"
test_formula_36 = "(p&q)&(not(q)&r)"
test_formula_37 = "not(not(u) & not(p) & not(q))"
"""

"""test_formulae = [test_formula_1, test_formula_2, test_formula_3, test_formula_4, test_formula_5, test_formula_6, test_formula_7, test_formula_8, test_formula_9,
                 test_formula_10, test_formula_11, test_formula_12, test_formula_13, test_formula_14, test_formula_15, test_formula_16, test_formula_17, test_formula_18, test_formula_19,
                 test_formula_20, test_formula_21, test_formula_22, test_formula_23, test_formula_24, test_formula_25, test_formula_26, test_formula_27, test_formula_28, test_formula_29,
                 test_formula_30, test_formula_31, test_formula_32, test_formula_33, test_formula_34, test_formula_35, test_formula_36, test_formula_37]"""



###


"""# ex. 1 sheet 1 formula 1 ((p ∧ q) → ¬r) ∧ (¬p → r) ∧ (¬q → r) ∧ ¬(q → ¬r), satisfiable
test_formula_101 = "not((p & q) & not(not(r))) &\
    not(not(p) & not(r)) &\
    not(not(q) & not(r)) &\
    not(not(q & not(not(r))))"

# ex. 1 sheet 1 formula 2 {¬p, q, r}, {¬q, u}, {¬r, u}, {¬u, ¬p, ¬q}, {¬r, ¬p}, {q, p}, {¬u, p}, unsatisfiable
test_formula_102 = "not(not(not(p)) & not(q) & not(r)) &\
    not(not(not(q)) & not(u)) &\
    not(not(not(r)) & not(u)) &\
    not(not(not(u)) & not(not(p)) & not(not(q))) &\
    not(not(not(r)) & not(not(p))) &\
    not(not(q) & not(p)) &\
    not(not(not(u)) & not(p))"

#test_formula_102 = "not(not(p) & q & r) & not(not(q) & u) & not(not(r) & u) &\
#    not(not(u) & not(p) & not(q)) & not(not(r) & not(p)) & not(q & p) & not(not(u) & p)"


test_formulae_2 = [test_formula_101, test_formula_102]"""



###

"""modal_test_formula_1 = "_p"
modal_test_formula_2 = "_(p)"
modal_test_formula_3 = "_not(p)"
modal_test_formula_4 = "_(not(p))"
modal_test_formula_5 = "not(_p)"
modal_test_formula_6 = "not(_not(p))"
modal_test_formula_7 = "_p&q"
modal_test_formula_8 = "_(p&q)" # 7 and 8 should be different formula?
modal_test_formula_9 = "_not(p&q)"
modal_test_formula_10 = "not(_p&q)"
modal_test_formula_11 = "not(_(p&q))" # 10 and 11 should be different
modal_test_formula_12 = "not(_p&not(p))"
modal_test_formula_13 = "not(_(p&not(p)))"
modal_test_formula_14 = "not(_not(p&not(p)))"
modal_test_formula_15 = "_not(p & (_not(q) & _not(r)))"
modal_test_formula_16 = "not(_not((p & q)))"
modal_test_formula_17 = "not(__not((not(not(q) & not(r)) & not(p))))"
modal_test_formula_18 = "not(__not((not(not(p) & not(r)) & not(p))))"
modal_test_formula_19 = "not(__not(((p & not(r)) & not(p))))"
modal_test_formula_20 = "_not(q & not(_not(p)))"
"""

"""# □(p → (♢q ∨ ♢r)) ∧ ♢(p ∧ q) ∧ □□((q ∨ r) → p) ∧ □(q → □¬p)
# _not(p & (_not(q) & _not(r))) & not(_not((p & q))) & __not((not(not(q) & not(r)) & not(p))) & _not(q & not(_not(p)))
modal_test_formula_101 = "_not(p & (_not(q) & _not(r))) &" \
                 " not(_not((p & q))) &" \
                 " __not((not(not(q) & not(r)) & not(p))) &" \
                 " _not(q & not(_not(p)))"
#□(p → (♢q ∨ ♢r)) ∧ ♢⊤ ∧ □(¬p → □¬p) ∧ □□(p ∧ ¬r) ∧ ((□¬p) → ♢♢⊤).
#_not(p & (_not(q) & _not(r))) & not(_not(T)) & _not(not(p) & not(_not(p))) & __(p & not(r)) & not((_not(p)) & not(not(__not(⊤))))
modal_test_formula_102 = "_not(p & (_not(q) & _not(r))) & " \
                 "not(_not(T)) &" \
                 "_not(not(p) & not(_not(p))) &" \
                 "__(p & not(r)) &" \
                 "not((_not(p)) & not(not(__not('T'))))"
"""


"""modal_test_formulae = [modal_test_formula_1, modal_test_formula_2, modal_test_formula_3, modal_test_formula_4, modal_test_formula_5, 
                       modal_test_formula_6, modal_test_formula_7, modal_test_formula_8, modal_test_formula_9, modal_test_formula_10,
                       modal_test_formula_11, modal_test_formula_12, modal_test_formula_13, modal_test_formula_14, modal_test_formula_15,
                       modal_test_formula_16, modal_test_formula_17, modal_test_formula_18, modal_test_formula_19, modal_test_formula_20]


modal_test_formulae_2 = [modal_test_formula_101, modal_test_formula_102]"""




if __name__ == '__main__':


    ### prompt for input formula
    phi = input_formula()
    satisfiable = tableux_method(tableux_representation(phi))
    print("Input formula satisfiable:", satisfiable)

    ### test formulae

    """for n, test_formula in enumerate(test_formulae):
            print(n+1)
            print(test_formula)
            #print(first_parenthesised_subformula(test_formula))
            r = tableux_representation(test_formula)
            print(r)
            print(tableux_satisfiability(r))
            print(tableux_method(r))
            print()"""
    

    """for n, test_formula in enumerate(test_formulae_2):
            print(101 + n)
            print(test_formula)
            #print(first_parenthesised_subformula(test_formula))
            r = tableux_representation(test_formula)
            print(r)
            #print(tableux_satisfiability(r))
            print(tableux_method(r))
            print()"""

    
    """for n, test_formula in enumerate(modal_test_formulae[]):
            print('modal', n+1)
            print(test_formula)
            #print(first_parenthesised_subformula(test_formula))
            r = tableux_representation(test_formula)
            print(r)
            print(tableux_method(r))
            print()"""

    
    """for n, test_formula in enumerate(modal_test_formulae_2):
            print('modal', n+101)
            print(test_formula)
            #print(first_parenthesised_subformula(test_formula))
            r = tableux_representation(test_formula)
            print(r)
            print(tableux_method(r))
            print()"""
    

    ### performance measure
    
    """n=6

    formula_series_list = [
        generate_formula_series_1(n),
        generate_formula_series_2(n),
        generate_formula_series_3(n),
        generate_formula_series_4(n)
    ]"""

    """
    ou = []
    for formula_series in formula_series_list:
        ou.append([])
        for formula in formula_series:
            pr = cProfile.Profile()
            pr.enable()
            # ... do something ...
            tableux_method(tableux_representation(formula))
            pr.disable()
            s = io.StringIO()
            sortby = SortKey.CUMULATIVE
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            ps.print_stats()
            print(s.getvalue())
            ti = s.getvalue().partition('\n')[0].strip()
            #print(ti) 
            sp = ti.split(' ')
            #di = (sp[0], sp[-2])
            di = sp[-2]
            ou[-1].append(di)
    
    print(ou)
    """


