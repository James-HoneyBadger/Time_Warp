"""
Time_Warp IDE Standard Library - Core Module
Provides essential built-in functions and constants
"""

import math
import random
import time
import os
import sys
from typing import Any, Dict, Callable, Union, Optional
from ..errors.error_manager import (
    TimeWarpRuntimeError,
    TimeWarpTypeError,
    create_runtime_error,
    create_type_error,
)


class StandardLibrary:
    """Registry for built-in functions and constants"""

    def __init__(self):
        self.functions: Dict[str, Callable] = {}
        self.constants: Dict[str, Any] = {}
        self._register_core_functions()
        self._register_constants()

    def register_function(self, name: str, func: Callable, overwrite: bool = False):
        """Register a built-in function"""
        if name in self.functions and not overwrite:
            raise ValueError(f"Function '{name}' already registered")
        self.functions[name] = func

    def register_constant(self, name: str, value: Any, overwrite: bool = False):
        """Register a built-in constant"""
        if name in self.constants and not overwrite:
            raise ValueError(f"Constant '{name}' already registered")
        self.constants[name] = value

    def get_function(self, name: str) -> Optional[Callable]:
        """Get a built-in function"""
        return self.functions.get(name)

    def get_constant(self, name: str) -> Any:
        """Get a built-in constant"""
        if name not in self.constants:
            error = create_runtime_error(f"Undefined constant '{name}'")
            raise TimeWarpRuntimeError(error)
        return self.constants[name]

    def get_all_names(self) -> list:
        """Get all registered names"""
        return list(self.functions.keys()) + list(self.constants.keys())

    def _register_core_functions(self):
        """Register core mathematical and utility functions"""

        # Mathematical functions
        self.register_function("SIN", self._safe_math_func(math.sin))
        self.register_function("COS", self._safe_math_func(math.cos))
        self.register_function("TAN", self._safe_math_func(math.tan))
        self.register_function("ASIN", self._safe_math_func(math.asin))
        self.register_function("ACOS", self._safe_math_func(math.acos))
        self.register_function("ATAN", self._safe_math_func(math.atan))
        self.register_function("SQRT", self._safe_sqrt)
        self.register_function("ABS", abs)
        self.register_function("INT", self._safe_int)
        self.register_function("ROUND", self._safe_round)
        self.register_function("FLOOR", self._safe_math_func(math.floor))
        self.register_function("CEIL", self._safe_math_func(math.ceil))
        self.register_function("LOG", self._safe_log)
        self.register_function("LOG10", self._safe_math_func(math.log10))
        self.register_function("EXP", self._safe_math_func(math.exp))
        self.register_function("POW", pow)
        self.register_function("MIN", min)
        self.register_function("MAX", max)

        # Random functions
        self.register_function("RND", lambda: random.random())
        self.register_function("RANDINT", lambda a, b: random.randint(int(a), int(b)))
        self.register_function("CHOICE", lambda lst: random.choice(list(lst)))

        # String functions
        self.register_function("LEN", len)
        self.register_function("LEFT$", self._left_string)
        self.register_function("RIGHT$", self._right_string)
        self.register_function("MID$", self._mid_string)
        self.register_function("UPPER$", lambda s: str(s).upper())
        self.register_function("LOWER$", lambda s: str(s).lower())
        self.register_function("TRIM$", lambda s: str(s).strip())
        self.register_function(
            "REPLACE$", lambda s, old, new: str(s).replace(str(old), str(new))
        )
        self.register_function("FIND", lambda s, sub: str(s).find(str(sub)))
        self.register_function("SPLIT$", lambda s, sep=" ": str(s).split(str(sep)))
        self.register_function(
            "JOIN$", lambda lst, sep="": str(sep).join(str(x) for x in lst)
        )

        # Type conversion functions
        self.register_function("STR$", str)
        self.register_function("VAL", self._safe_val)
        self.register_function("CHR$", chr)
        self.register_function("ASC", ord)

        # System functions
        self.register_function("TIME$", lambda: time.strftime("%H:%M:%S"))
        self.register_function("DATE$", lambda: time.strftime("%Y-%m-%d"))
        self.register_function("DATETIME$", lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
        self.register_function("TIMESTAMP", lambda: int(time.time()))
        self.register_function("SLEEP", time.sleep)

        # File system functions
        self.register_function("EXISTS", os.path.exists)
        self.register_function("ISFILE", os.path.isfile)
        self.register_function("ISDIR", os.path.isdir)
        self.register_function("GETCWD", os.getcwd)
        self.register_function("LISTDIR", os.listdir)

        # Array/List functions
        self.register_function("APPEND", lambda lst, item: list(lst).append(item))
        self.register_function("REMOVE", lambda lst, item: list(lst).remove(item))
        self.register_function("INDEX", lambda lst, item: list(lst).index(item))
        self.register_function("COUNT", lambda lst, item: list(lst).count(item))
        self.register_function("REVERSE", lambda lst: list(reversed(lst)))
        self.register_function("SORT", lambda lst: sorted(lst))

    def _register_constants(self):
        """Register mathematical and system constants"""
        self.register_constant("PI", math.pi)
        self.register_constant("E", math.e)
        self.register_constant("TAU", math.tau)
        self.register_constant("INF", math.inf)
        self.register_constant("NAN", math.nan)
        self.register_constant("TRUE", True)
        self.register_constant("FALSE", False)
        self.register_constant("NULL", None)

    # Safe wrapper functions with error handling
    def _safe_math_func(self, func):
        """Wrapper for math functions with error handling"""

        def wrapper(x):
            try:
                return func(float(x))
            except (ValueError, TypeError) as e:
                error = create_runtime_error(f"Math error: {e}")
                raise TimeWarpRuntimeError(error)

        return wrapper

    def _safe_sqrt(self, x):
        """Safe square root function"""
        try:
            x = float(x)
            if x < 0:
                error = create_runtime_error(
                    "Cannot take square root of negative number"
                )
                raise TimeWarpRuntimeError(error)
            return math.sqrt(x)
        except (ValueError, TypeError) as e:
            error = create_runtime_error(f"Math error: {e}")
            raise TimeWarpRuntimeError(error)

    def _safe_log(self, x, base=math.e):
        """Safe logarithm function"""
        try:
            x = float(x)
            if base != math.e:
                base = float(base)
            if x <= 0:
                error = create_runtime_error(
                    "Cannot take logarithm of non-positive number"
                )
                raise TimeWarpRuntimeError(error)
            if base != math.e and base <= 0:
                error = create_runtime_error("Logarithm base must be positive")
                raise TimeWarpRuntimeError(error)
            return math.log(x) if base == math.e else math.log(x, base)
        except (ValueError, TypeError) as e:
            error = create_runtime_error(f"Math error: {e}")
            raise TimeWarpRuntimeError(error)

    def _safe_int(self, x):
        """Safe integer conversion"""
        try:
            if isinstance(x, str):
                x = x.strip()
            return int(float(x))
        except (ValueError, TypeError) as e:
            error = create_runtime_error(f"Cannot convert to integer: {e}")
            raise TimeWarpRuntimeError(error)

    def _safe_round(self, x, digits=0):
        """Safe rounding function"""
        try:
            return round(float(x), int(digits))
        except (ValueError, TypeError) as e:
            error = create_runtime_error(f"Rounding error: {e}")
            raise TimeWarpRuntimeError(error)

    def _safe_val(self, s):
        """Safe value conversion from string"""
        try:
            s = str(s).strip()
            if not s:
                return 0
            # Try integer first
            if "." not in s and "e" not in s.lower():
                return int(s)
            else:
                return float(s)
        except (ValueError, TypeError) as e:
            error = create_runtime_error(f"Cannot convert '{s}' to number")
            raise TimeWarpRuntimeError(error)

    def _left_string(self, s, n):
        """Get leftmost n characters"""
        try:
            return str(s)[: int(n)]
        except (ValueError, TypeError) as e:
            error = create_runtime_error(f"String function error: {e}")
            raise TimeWarpRuntimeError(error)

    def _right_string(self, s, n):
        """Get rightmost n characters"""
        try:
            n = int(n)
            return str(s)[-n:] if n > 0 else ""
        except (ValueError, TypeError) as e:
            error = create_runtime_error(f"String function error: {e}")
            raise TimeWarpRuntimeError(error)

    def _mid_string(self, s, start, length=None):
        """Get substring starting at position"""
        try:
            s = str(s)
            start = int(start) - 1  # Convert to 0-based indexing
            if start < 0:
                start = 0
            if length is None:
                return s[start:]
            else:
                length = int(length)
                return s[start : start + length]
        except (ValueError, TypeError) as e:
            error = create_runtime_error(f"String function error: {e}")
            raise TimeWarpRuntimeError(error)


# Global instance
std_lib = StandardLibrary()
