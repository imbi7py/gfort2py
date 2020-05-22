# SPDX-License-Identifier: GPL-2.0+
import builtins
import ctypes
import numpy as np

try:
    import bigfloat as bf
    has_bf = True
except ImportError:
    print("Bigfloat not installed quad precision not fully supported")
    has_bf = False

from .errors import IgnoreReturnError


class fVar():
    def __init__(self, obj):
        self.var = obj['var']
        if 'mangled_name' in obj:
            self.mangled_name = obj['mangled_name']
        if 'name' in obj:
            self.name = obj['name']

        self.ctype = self.var['ctype']
        self.pytype = self.var['pytype']

        if self.pytype == 'quad':
            self.ctype = ctypes.c_byte * 16
        elif self.pytype == 'bool':
            self.pytype = bool
            self.ctype = ctypes.c_int32
        else:
            self.pytype = getattr(builtins, self.pytype)
            self.ctype = getattr(ctypes, self.ctype)


    def convert_to_py(self,ctype):
        if self.pytype == 'quad':
            if has_bf:
                return _bytes2quad(ctype)
            else:
                raise ValueError("Must install BigFloat first")
        else:
            if hasattr(ctype, 'value'):
                return self.pytype(ctype.value)
            else:
                return self.pytype(ctype)


    def convert_from_py(self,pytype):
        if self.pytype == 'quad':
            if has_bf:
                return _bytes2quad(ctype)
            else:
                raise ValueError("Must install BigFloat first")
        else:
            return self.ctype(self.pytype(pytype))

    def from_address(self, addr):
        """
        Given an address, return a ctype object from that address.

        addr -- integer address

        Returns:
        A ctype representation of the variable
        """
        return self.convert_to_py(self.ctype.from_address(addr).value)

    def set_from_address(self, addr, value):
        """
        Given an address set the variable to value

        addr -- integer address
        value -- python object that can be coerced into self.pytype

        """
        self.ctype.from_address(addr).value = self.convert_from_py(value).value

    def from_param(self, value):
        """
        Returns a ctype object needed by a function call

        This is a pointer to self.ctype(value).

        If the function argument is optional, and value==None we return None
        else we return the pointer.

        value -- python object that can be coerced into self.pytype

        """

        if 'optional' in self.var:
            if self.var['optional'] and value is None:
                return None

        ct = self.convert_from_py(value)

        if 'value' in self.var and self.var['value']:
            return ct
        else:
            ct = ctypes.pointer(ct)
            if 'pointer' in self.var and self.var['pointer']:
                return ctypes.pointer(ct)
            else:
                return ct

    def from_func(self, pointer):
        """
        Given the pointer to the variable return the python type

        We raise IgnoreReturnError when we get something that should not be returned,
        like the hidden string length that's at the end of the argument list.

        """
        x = pointer
        if hasattr(pointer, 'contents'):
            if hasattr(pointer.contents, 'contents'):
                x = pointer.contents.contents
            else:
                x = pointer.contents

        if hasattr(x, 'value'):
            x = x.value

        if x is None:
            return None

        try:
            return self.convert_to_py(x)
        except AttributeError:
            raise IgnoreReturnError

    def in_dll(self, lib):
        return self.convert_to_py(self.ctype.in_dll(lib, self.mangled_name))

    def set_in_dll(self, lib, value):
        self.ctype.in_dll(lib, self.mangled_name).value = self.convert_from_py(value).value


class fParam():
    def __init__(self, obj):
        self.param = obj['param']
        self.value = self.param['value']
        self.pytype = self.param['pytype']
        if self.pytype == 'quad':
            self.pytype = np.longdouble
        elif self.pytype == 'bool':
            self.pytype = bool
            self.ctype = 'c_int32'
        else:
            self.pytype = getattr(builtins, self.pytype)

    def set_in_dll(self, lib, value):
        """
        Can't set a parameter
        """
        raise ValueError("Can't alter a parameter")

    def in_dll(self, lib):
        """
        A parameters value is stored in the objects dict, as we can't access them
        from the shared lib.
        """
        return self.pytype(self.value)


def _bytes2quad(bytearr):
    bb=[]
    for i in bytearray(bytearr)[::-1]:
        bb.append(bin(i)[2:].rjust(8,'0'))

    bb=''.join(bb)

    sign = bb[0]
    exp = bb[1:16]
    sig = bb[16:]

    a = int(exp,base=2)-16383
    b = bf.BigFloat(1,bf.quadruple_precision) 
    for idx,i in enumerate(sig):
        b = b + int(i)*bf.BigFloat(2,bf.quadruple_precision)**(-((idx+1))) 
    r = 2**a * b
    if sign == '0':
        return r
    else:
        return -r


def _quad2bytes(quad):
    raise ValueError("Can't set quad yet")