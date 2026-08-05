"""Surfaces: every way a bank is presented, and every one of them a client.

A surface renders, collects a response, and asks the runtime what it means. None
of them parses a bank a second way and none of them decides whether an answer is
correct. That rule is the whole reason this package is separate from `model` and
`runtime`: when the browser page was inside the same file as the scorer, it grew
a scorer of its own without anybody deciding to give it one.
"""
