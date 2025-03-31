from typing import Dict, Callable
from typing import get_type_hints
import inspect

def check_data_types(data_type_dict: Dict[str, str], local_vars: Dict[str, str], **kwargs):
    """Should be included in every function, automatically checks if the
       specified datatypes coincide with the actual given datatypes
    Args:
        data_type_dict (Dict[str, str]): the expected, given datatypes
        local_vars (Dict[str, str]): the actual given arguments with their datatypes
    Raises:
        TypeError: Raise if mismatch between specified and actual datatype
        KeyError: Raise if argument not specified
    """
    frame_info, file_name = None, None
    # Get the name of the parent function
    if kwargs:
        parent_function_name = kwargs.get("parent_function_name")
    else:
        for frame_info in inspect.stack():
            if frame_info.function not in ['check_data_types', '<module>']:
                parent_function_name = frame_info.function
                break    
    if frame_info is not None:
        file_name = frame_info.filename
    for var_name, expected_type in data_type_dict.items():
        if var_name == "return" or expected_type is inspect._empty:
            continue
        if var_name in local_vars:
            if local_vars[var_name] is not None:
                actual_value = type(local_vars[var_name])
                if not actual_value == expected_type:
                    if "__name__" in dir(expected_type):
                        raise_string = f"{var_name} is not of type: {expected_type.__name__}"
                    else:
                        raise_string = f"{var_name} is not of type: {expected_type}"
                    # Add the parent function name explicitly for better tracking
                    raise_string = f'{raise_string} in function: {parent_function_name} in file: {file_name}'
                    if "__origin__" in dir(expected_type):
                        if not actual_value == expected_type.__origin__:
                            raise TypeError(raise_string)
                    else:
                        raise TypeError(raise_string)
        else:
            raise KeyError(f"{var_name} is not in the provided arguments for function: {parent_function_name} in file: {file_name}")

# The following function retrives the function (type) annotations
def retrieve_function_annotations() -> Dict[str, Callable]:
    # Get the current frame
    frame = inspect.currentframe()
    # Get the function object from the frame
    func = frame.f_back.f_globals[frame.f_back.f_code.co_name]
    annotation_dict = get_type_hints(func)
    return annotation_dict


def check_data_types_decorator(func: Callable):
    def wrapper(*args, **kwargs):
        signature = inspect.signature(func)
        annotations = {k: v.annotation for k, v in signature.parameters.items()}
        annotations['return'] = signature.return_annotation
        local_vars = kwargs.copy()
        local_vars.update(dict(zip(signature.parameters, args)))
        check_data_types(data_type_dict=annotations, local_vars=local_vars, parent_function_name=func.__name__)
        return func(*args, **kwargs)
    return wrapper


def apply_decorator_to_methods(decorator):
    def class_decorator(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value):
                setattr(cls, attr_name, decorator(attr_value))
        return cls
    return class_decorator
