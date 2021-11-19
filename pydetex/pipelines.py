"""
PyDetex
https://github.com/ppizarror/PyDetex

PIPELINES
Defines the pipelines which apply parsers.
"""

__all__ = [
    'simple',
    'strict',
    'PipelineType'
]

import pydetex.parsers as par
from pydetex.utils import ProgressBar
from typing import Callable
import sys

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class Options(TypedDict):
    """
    Pipeline options.
    """
    progressbar: ProgressBar
    remove_common_tags: bool
    replace_defs: bool
    replace_pydetex_tags: bool
    show_progress: bool


PipelineType = Callable[[str, str, Options], str]


def simple(
        s: str,
        lang: str = 'en',
        show_progress: bool = False,
        replace_pydetex_tags: bool = True,
        remove_common_tags: bool = True,
        **kwargs: Options
) -> str:
    """
    The most simple pipeline ever.

    :param s: String latex
    :param lang: Language tag of the code
    :param show_progress: Show progress bar
    :param replace_pydetex_tags: Replace cite tags
    :param remove_common_tags: Call ``remove_common_tags`` parser
    :return: String with no latex!
    """
    if len(s) == 0:
        return s
    pb = kwargs.get('progressbar', ProgressBar(steps=16))
    if not show_progress:
        pb = None
    s = '\n'.join(s.splitlines())  # Removes \r\n
    s = par.process_inputs(s, pb=pb)
    s = par.remove_comments(s, pb=pb)
    s = par.process_begin_document(s, pb=pb)
    s = par.simple_replace(s, pb=pb)
    s = par.process_def(s, pb=pb, replace=kwargs.get('replace_defs', False))
    if remove_common_tags:
        s = par.remove_common_tags(s, pb=pb)
    s = par.process_cite(s, pb=pb)
    s = par.process_ref(s, pb=pb)
    s = par.process_labels(s, pb=pb)
    s = par.process_items(s, pb=pb)
    s = par.process_quotes(s, pb=pb)
    s = par.process_chars_equations(s, lang, True, pb=pb)
    s = par.unicode_chars_equations(s, pb=pb)
    s = par.remove_comments(s, pb=pb)  # comments, replace tags, strip
    if replace_pydetex_tags:
        s = par.replace_pydetex_tags(s, pb=pb)
    s = par.strip_punctuation(s, pb=pb)
    if s[-1] == '\\':
        s = s[0:len(s) - 1]
    return s


def strict(
        s: str,
        lang: str = 'en',
        show_progress: bool = False,
        **kwargs: Options
) -> str:
    """
    Apply simple + removes all commands.

    :param s: String latex
    :param lang: Language tag of the code
    :param show_progress: Show progress bar
    :return: String with no latex!
    """
    pb = ProgressBar(steps=21)
    if 'progressbar' not in kwargs.keys():
        # noinspection PyTypeChecker
        kwargs['progressbar'] = pb
    s = simple(s, lang, replace_pydetex_tags=False, remove_common_tags=False,
               show_progress=show_progress, **kwargs)
    s = par.process_chars_equations(s, lang, False, pb=pb)
    s = par.remove_equations(s, pb=pb)
    s = par.remove_environments(s, pb=pb)
    s = par.remove_commands_param(s, lang, pb=pb)
    s = par.remove_commands_param_noargv(s, pb=pb)
    s = par.remove_comments(s, pb=pb)
    s = par.replace_pydetex_tags(s, pb=pb)
    s = par.strip_punctuation(s, pb=pb)
    return s
