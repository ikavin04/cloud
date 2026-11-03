"""Compatibility support for Nose 1.3.7 on modern Python versions."""

import collections
import collections.abc


if not hasattr(collections, "Callable"):
    collections.Callable = collections.abc.Callable
