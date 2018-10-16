# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

registry = {}

def register(importer):
    name = importer.name()
    assert name not in registry, name
    registry[name] = importer


def get(name):
    return registry[name]
