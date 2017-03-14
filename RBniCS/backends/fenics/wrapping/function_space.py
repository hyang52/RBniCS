# Copyright (C) 2015-2017 by the RBniCS authors
#
# This file is part of RBniCS.
#
# RBniCS is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RBniCS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with RBniCS. If not, see <http://www.gnu.org/licenses/>.
#
## @file functions_list.py
#  @brief Type for storing a list of FE functions.
#
#  @author Francesco Ballarin <francesco.ballarin@sissa.it>
#  @author Gianluigi Rozza    <gianluigi.rozza@sissa.it>
#  @author Alberto   Sartori  <alberto.sartori@sissa.it>

import types
from dolfin import FunctionSpace as dolfin_FunctionSpace

def FunctionSpace(*args, **kwargs):
    if "components" in kwargs:
        components = kwargs["components"]
        del kwargs["components"]
    else:
        components = None
    output = dolfin_FunctionSpace(*args, **kwargs)
    if components is not None:
        _enable_string_components(components, output)
    return output
    
def _enable_string_components(components, function_space):
    _init_component_to_index(components, function_space)
    
    original_sub = function_space.sub
    def custom_sub(self_, i):
        assert i is not None
        i_int = _convert_component_to_int(self_, i)
        if i_int is None:
            def custom_collapse(self_, collapsed_dofs=False):
                assert not collapsed_dofs
                return self_
            self_.collapse = types.MethodType(custom_collapse, self_)
            return self_
        assert isinstance(i_int, (int, tuple))
        if isinstance(i_int, int):
            output = original_sub(i_int)
        else:
            output = self_.extract_sub_space(i_int)
        if isinstance(i, str):
            components = {i: None}
            _init_component_to_index(components, output)
        return output
        
    function_space.sub = types.MethodType(custom_sub, function_space)
    
    original_extract_sub_space = function_space.extract_sub_space
    def custom_extract_sub_space(self_, i):
        i_int = _convert_component_to_int(self_, i)
        output = original_extract_sub_space(i_int)
        if isinstance(i, str):
            components = {i: None}
            _init_component_to_index(components, output)
        return output
    function_space.extract_sub_space = types.MethodType(custom_extract_sub_space, function_space)
    
def _init_component_to_index(components, function_space):
    assert isinstance(components, (list, dict))
    if isinstance(components, list):
        function_space._component_to_index = dict()
        for (index, component) in enumerate(components):
            _init_component_to_index__recursive(component, function_space._component_to_index, index)
    else:
        function_space._component_to_index = components
    def component_to_index(self_, i):
        return self_._component_to_index[i]
    function_space.component_to_index = types.MethodType(component_to_index, function_space)
    
    original_collapse = function_space.collapse
    def custom_collapse(self_, collapsed_dofs=False):
        if not collapsed_dofs:
            output = original_collapse(collapsed_dofs)
        else:
            output, collapsed_dofs_dict = original_collapse(collapsed_dofs)
        if hasattr(self_, "_component_to_index"):
            _init_component_to_index(self_._component_to_index, output)
        if not collapsed_dofs:
            return output
        else:
            return output, collapsed_dofs_dict
    function_space.collapse = types.MethodType(custom_collapse, function_space)
    
def _init_component_to_index__recursive(components, component_to_index, index):
    assert isinstance(components, (str, tuple, list))
    if isinstance(components, str):
        if isinstance(index, list):
            component_to_index[components] = tuple(index)
        else:
            assert isinstance(index, int)
            component_to_index[components] = index
    elif isinstance(components, list):
        for component in components:
            _init_component_to_index__recursive(component, component_to_index, index)
    elif isinstance(components, tuple):
        for (subindex, subcomponent) in enumerate(components):
            full_index = list()
            if isinstance(index, int):
                full_index.append(index)
            else:
                full_index.extend(index)
            full_index.append(subindex)
            _init_component_to_index__recursive(subcomponent, component_to_index, full_index)
            
def _convert_component_to_int(function_space, i):
    if isinstance(i, str):
        return function_space._component_to_index[i]
    else:
        return i