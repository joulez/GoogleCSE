# Copyright (c) 2014 Julian Paul Glass. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class ItemIndexTree(list):
    "Tree based list type."""
    def __init__(self, items=None):
        if items and not isinstance(items, list):
            raise ValueError('Index Items must be a list()')
        elif items:
            for i in items:
                self.__setitem__(i)
        self.parent = None
        self._current_index = None

    def _check_ins(self, item):
        if not isinstance(item, ItemIndexTree):
            raise TypeError('Item must be of type {0}'.format(str(self.__class__)))

    def __add__(self, item):
        self._check_ins(item)
        item.parent = self
        list.__add__(self, item)

    def __len__(self):
        return list.__len__(self)

    def __setitem__(self, item):
        self._check_ins(item)
        item.parent = self
        list.__add__(self, item)

    def append(self, item):
        self._check_ins(item)
        item.parent = item
        list.append(self, item)

    def __getitem__(self, item):
        v = list.__getitem__(self, item)
        try:
            return ItemIndexTree(v)
        except TypeError:
            return v

    @property
    def current(self):
        """Return current item."""
        if self._current_index is None and list.__len__(self) > 0:
            self._current_index = 0
        elif list.__len__(self) == 0:
            raise IndexError('item contains no values.')
        return list.__getitem__(self, self._current_index)

    def next(self):
        if self._current_index is None:
            self._current_index = 0
        elif self._current_index + 2 > list.__len__(self):
            raise IndexError('Out of range - No more next values')
        else:
            self._current_index += 1
        return self._current_index

    def previous(self):
        if self._current_index == 0:
            raise IndexError('Out of range - No more previous values.')
        else:
            self._current_index -= 1


