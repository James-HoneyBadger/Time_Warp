#!/usr/bin/env python3
"""
TimeWarp Native Compilers
==========================

A unified compiler framework for converting TimeWarp IDE languages
(BASIC, Logo, PILOT) into standalone Linux executables.
"""

from .base import BaseCompiler, CodeGenerator, CompilerResult, Language
from .basic_compiler import BasicCompiler
from .logo_compiler import LogoCompiler
from .pilot_compiler import PilotCompiler


def create_compiler(language: Language) -> BaseCompiler:
    """Factory function to create appropriate compiler"""
    if language == Language.BASIC:
        return BasicCompiler()
    elif language == Language.LOGO:
        return LogoCompiler()
    elif language == Language.PILOT:
        return PilotCompiler()
    else:
        raise ValueError(f"Unsupported language: {language}")


__all__ = [
    'BaseCompiler',
    'CodeGenerator',
    'CompilerResult',
    'Language',
    'create_compiler',
    'BasicCompiler',
    'LogoCompiler',
    'PilotCompiler',
]