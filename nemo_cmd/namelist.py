"""
Fortran namelist parser. Converts namelists to Python dictionaries.

Based on https://gist.github.com/krischer/4943658.

Should be fairly robust. Cannot be used for verifying fortran namelists as it
is rather forgiving.

Error messages during parsing are kind of messy right now.

Usage
=====

>>> from namelist import namelist2dict
>>> namelist_dict = namelist2dict("fortran_list.txt")

Can deal with filenames, open files and file-like object (StringIO).


Works with Python 2.7 and has not further dependencies.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013

:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
QUOTE_CHARS = ["'", '"']


class Token(object):
    """
    Base class for all token types.
    """

    def __str__(self):
        name = self.__class__.__name__
        if hasattr(self, "value"):
            return "%s(%s)" % (name, str(self.value))
        return name

    def __repr__(self):
        return self.__str__()


class StringToken(Token):
    def __init__(self, value):
        self.value = value


class AssignmentToken(Token):
    pass


class GroupEndToken(Token):
    pass


class GroupStartToken(Token):
    def __init__(self, value):
        self.value = value


class IntegerToken(Token):
    def __init__(self, value):
        self.value = int(value)


class FloatToken(Token):
    def __init__(self, value):
        self.value = float(value)


class BooleanToken(Token):
    def __init__(self, value):
        self.value = bool(value)


class NameToken(Token):
    def __init__(self, value):
        self.value = str(value)


class ComplexNumberToken(Token):
    def __init__(self, real, imag):
        self.value = complex(real, imag)


class ArrayIndexToken(Token):
    def __init__(self, value):
        self.value = int(value)


def auto_token(value):
    """
    Instantiates the correct token type based on the passed value string.
    """
    value = value.strip()
    if value.startswith("&"):
        return GroupEndToken() if value[1:] == "end" else GroupStartToken(value[1:])
    elif value.lower() == ".true." or value.lower() == "true":
        return BooleanToken(True)
    elif value.lower() == ".false." or value.lower() == "false":
        return BooleanToken(False)
    try:
        return IntegerToken(int(value))
    except:
        pass
    try:
        return FloatToken(float(value))
    except:
        pass
    return NameToken(value)


def tokenizer(file_object):
    """
    The lexer - a generator yielding tokens.
    """
    for line in file_object:
        line = line.strip()
        if not line:
            continue
        in_name = True
        in_string = False
        in_complex_number = False
        current_token = []
        for letter in line:
            # Handle strings.
            if letter in QUOTE_CHARS:
                if in_string is True:
                    yield StringToken("".join(current_token))
                    current_token = []
                    in_string = False
                else:
                    in_string = True
                continue
            elif in_string is True:
                current_token.append(letter)

            # Handle array indices and complex numbers.
            elif letter == "(":
                if current_token:
                    yield auto_token("".join(current_token))
                    current_token = []
                if not in_name:
                    in_complex_number = True
            elif letter == ")":
                if in_name:
                    # Finished array element index
                    yield ArrayIndexToken("".join(current_token))
                    current_token = []
                    in_name = False
                else:
                    # Parse the complex number.
                    real, imag = map(float, "".join(current_token).split(","))
                    yield ComplexNumberToken(real, imag)
                    current_token = []
                    in_complex_number = False
            elif in_complex_number is True:
                current_token.append(letter)

            # Everything from now on is neither string nor complex number.
            elif letter == "!":
                break
            elif not letter.strip():
                if current_token:
                    yield auto_token("".join(current_token))
                    current_token = []
            elif letter == ",":
                if current_token:
                    yield auto_token("".join(current_token))
                    current_token = []
            elif letter == "=":
                if current_token:
                    yield auto_token("".join(current_token))
                    current_token = []
                in_name = False
                yield AssignmentToken()
            elif letter == "/":
                if current_token:
                    yield auto_token("".join(current_token))
                    current_token = []
                yield GroupEndToken()
            else:
                current_token.append(letter)
        if current_token:
            yield auto_token("".join(current_token))


def group_generator(tokens):
    """
    Generator yielding one dictionary per found group.
    """
    current_group = {}
    current_group_name = None
    current_assignment = []
    for token in tokens:
        if isinstance(token, GroupStartToken):
            if current_group_name:
                msg = "Starting new group without ending old one."
                raise ValueError(msg)
            current_group_name = token.value
            continue
        elif isinstance(token, GroupEndToken):
            if current_assignment:
                parse_assignment(current_assignment, current_group)
                current_assignment = []
            if current_group and current_group_name:
                yield (current_group_name, current_group)
            current_group = {}
            current_group_name = None
            continue
        elif isinstance(token, NameToken):
            if current_assignment:
                parse_assignment(current_assignment, current_group)
                current_assignment = []
        current_assignment.append(token)


def parse_assignment(assignment, group):
    """
    Parses all tokens for one assignment. Will write the result to the passed
    group dictionary.
    """
    if len(assignment) < 3:
        msg = "Invalid assignment."
        raise ValueError(msg)
    if not isinstance(assignment[0], NameToken):
        msg = "Assignment must start with a name."
        raise ValueError(msg)
    if isinstance(assignment[1], AssignmentToken):
        values = assignment[2:]
        array_assignment = False
    elif all(
        (
            isinstance(assignment[1], ArrayIndexToken),
            isinstance(assignment[2], AssignmentToken),
        )
    ):
        array_index = assignment[1].value - 1
        values = assignment[3:]
        array_assignment = True
    else:
        msg = "Assignment must contain an AssignmentToken."
        raise ValueError(msg)
    values = [_i.value for _i in values]
    if len(values) == 1:
        values = values[0]
    if not array_assignment:
        group[assignment[0].value] = values
    else:
        try:
            group[assignment[0].value].insert(array_index, values)
        except KeyError:
            if array_index != 0:
                msg = "Array element assignments must start at element 1"
                raise IndexError(msg)
            group[assignment[0].value] = [values]
        except IndexError:
            msg = "Array elements must be asigned in order"
            raise IndexError(msg)


def namelist2dict(file_or_file_object):
    """Return a Fortran namelist as a dict data structure.

    :param file_or_file_object: File name or handle of the namelist to read.
    :type file_or_file_object: :py:class:`str` or `file object`_

    .. _file object: https://docs.python.org/3/glossary.html#term-file-object
    """
    if hasattr(file_or_file_object, "read"):
        return _namelist2dict(file_or_file_object)
    with open(file_or_file_object, "r") as open_file:
        return _namelist2dict(open_file)


def _namelist2dict(file_object):
    """
    Converts a file_object containing a namelist to a dictionary.
    """
    namelist_dict = {}
    for group_name, group_values in group_generator(tokenizer(file_object)):
        namelist_dict.setdefault(group_name, [])
        namelist_dict[group_name].append(group_values)
    return namelist_dict


def get_namelist_value(key, lines):
    """Return the value corresponding to key in lines, and the index
    at which key was found.

    lines is expected to be a NEMO namelist in the form of a list of strings.

    :param str key: The namelist key to find the value and line number of.

    :param list lines: The namelist lines.

    :returns: The value corresponding to key,
              and the index in lines at which key was found.
    :rtype: 2-tuple
    """
    line_index = [
        i for i, line in enumerate(lines) if line.strip() and line.split()[0] == key
    ][-1]
    value = lines[line_index].split()[2]
    return value, line_index
