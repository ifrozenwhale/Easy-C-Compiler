from enum import Enum


class ErrorType(Enum):
    undefined = 0  # ok
    already_defined_var = 1  # ok
    already_defined_func = 2  # ok
    uninitialized_var = 3  # ok
    unsupported_operation = 4  # ok
    incompatible_type = 5  # ok
    mismatched_params = 6  # ok
    mismatched_type = 7  # ok


class UndefinedError:
    def __init__(self, var_name):
        self.var_name = var_name

    def __repr__(self):
        return f"undefined variable {self.var_name}"


class UndefinedFuncError:
    def __init__(self, func_name):
        self.func_name = func_name

    def __repr__(self):
        return f"undefined function {self.func_name}"


class AlreadyDefinedVar:
    def __init__(self, var_name, first_defined_position):
        self.var_name = var_name
        self.first_defined_position = first_defined_position

    def __repr__(self):
        return f"variable {self.var_name} is already defined in position {self.first_defined_position}"


class AlreadyDefinedFunc:
    def __init__(self, func_name, first_defined_position):
        self.func_name = func_name
        self.first_defined_position = first_defined_position

    def __repr__(self):
        return f"function {self.func_name} is already defined in position {self.first_defined_position}"


class UninitializedVar:
    def __init__(self, var_name):
        self.var_name = var_name

    def __repr__(self):
        return f"variable {self.var_name} is uninitialized but used here"


class UnsupportedOperation:
    def __init__(self, var_name, var_type, op):
        self.var_name = var_name
        self.var_type = var_type
        self.op = op

    def __repr__(self):
        return f"variable {self.var_name} (self.var_type) don't support operation {self.op}"


class IncompatibleType:
    def __init__(self, var_name, var_type, rvalue_type):
        self.var_name = var_name
        self.var_type = var_type
        self.rvalue_type = rvalue_type

    def __repr__(self):
        return f"variable {self.var_name} ({self.var_type}) cannot be assigned with type {self.rvalue_type}"


class MismatchedParams:
    def __init__(self, func_name, params, expected_params):
        self.func_name = func_name
        self.params = params
        self.expected_params = expected_params

    def __repr__(self):
        return f"function {self.func_name} received params ({self.params}), expected params {self.expected_params}"


class MismatchedType:
    def __init__(self, var_type1, var_type2, op):
        self.var_type1 = var_type1
        self.var_type2 = var_type2
        self.op = op

    def __repr__(self):
        return f"variable ({self.var_type1}) and variable ({self.var_type2}) don't " \
               f"support operation {self.op} "


class Error:
    def __init__(self, err, position: tuple):
        self.err = err
        self.position = position

    def __repr__(self):
        return f"[ERROR] at position {self.position}, caused by: {str(self.err)}"


class ErrorManager:
    def __init__(self):
        self.errors = []

    def add_error(self, err: Error):
        self.errors.append(err)

    def count(self):
        return len(self.errors)

    def print(self):
        for err in self.errors:
            print(err)
