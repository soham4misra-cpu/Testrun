import random


def _make_choices(correct, spread=5):
    choices = {correct}
    while len(choices) < 4:
        delta = random.randint(-spread, spread)
        if delta == 0:
            continue
        choices.add(correct + delta)
    choices = list(choices)
    random.shuffle(choices)
    return choices


def _signed_term(value):
    return f" + {value}" if value >= 0 else f" - {abs(value)}"


def _solve_linear_equation():
    a = random.randint(2, 9)
    x = random.randint(-10, 10)
    b = random.randint(-10, 10)
    c = a * x + b
    question = f"Solve for x: {a}x{_signed_term(b)} = {c}"
    return question, x


def _evaluate_expression():
    a = random.randint(2, 9)
    b = random.randint(-10, 10)
    x = random.randint(-10, 10)
    answer = a * x + b
    question = f"If x = {x}, what is {a}x{_signed_term(b)}?"
    return question, answer


def _combine_like_terms():
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    x = random.randint(-10, 10)
    answer = (a + b) * x
    question = f"If x = {x}, what is {a}x + {b}x?"
    return question, answer


_GENERATORS = [_solve_linear_equation, _evaluate_expression, _combine_like_terms]


def generate_question():
    question, answer = random.choice(_GENERATORS)()
    choices = _make_choices(answer)
    return question, answer, choices
