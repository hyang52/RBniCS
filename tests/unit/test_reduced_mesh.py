# Copyright (C) 2015-2016 by the RBniCS authors
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
## @file 
#  @brief 
#
#  @author Francesco Ballarin <francesco.ballarin@sissa.it>
#  @author Gianluigi Rozza    <gianluigi.rozza@sissa.it>
#  @author Alberto   Sartori  <alberto.sartori@sissa.it>

import os
from numpy import isclose
from dolfin import *
set_log_level(PROGRESS)
from fenicstools import DofMapPlotter
from RBniCS.backends.fenics import ReducedMesh
from RBniCS.backends.fenics.evaluate import evaluate_and_vectorize_sparse_matrix_at_dofs

# Possibly disable saving to file. This bool can be used to 
# check loading with a number of processors different from
# the one originally used when saving.
skip_reduced_mesh_save = False

# Make output directory, if necessary
try: 
    os.makedirs("test_reduced_mesh.output_dir")
except OSError:
    if not os.path.isdir("test_reduced_mesh.output_dir"):
        raise

mesh = UnitSquareMesh(3, 3)

# ~~~ Elliptic case ~~~ #
V = FunctionSpace(mesh, "CG", 2)

"""
dmp = DofMapPlotter(V)
dmp.plot()
dmp.show()
"""

reduced_mesh = ReducedMesh((V, V))
dofs = [(1, 2), (11, 12), (48, 12), (41, 41)]

for pair in dofs:
    log(PROGRESS, "Adding " + str(pair))
    reduced_mesh.append(pair)
    
    """
    plot(reduced_mesh.reduced_mesh_cells_marker)
    interactive()
    plot(reduced_mesh.get_reduced_mesh())
    interactive()
    """
    """
    dmp = DofMapPlotter(reduced_mesh.get_reduced_function_spaces()[0])
    dmp.plot()
    dmp.show()
    """
    
    if not skip_reduced_mesh_save:
        reduced_mesh.save("test_reduced_mesh.output_dir", "test_reduced_mesh_elliptic")

def compute_elliptic_error(reduced_mesh):
    reduced_V = reduced_mesh.get_reduced_function_spaces()
    dofs = reduced_mesh.get_dofs_list()
    reduced_dofs = reduced_mesh.get_reduced_dofs_list()

    u = TrialFunction(V)
    v = TestFunction(V)

    trial = 1
    test = 0
    u_N = TrialFunction(reduced_V[trial])
    v_N = TestFunction(reduced_V[test])

    A = assemble((u.dx(0)*v + u*v)*dx)
    A_N = assemble((u_N.dx(0)*v_N + u_N*v_N)*dx)

    A_dofs = evaluate_and_vectorize_sparse_matrix_at_dofs(A, dofs)
    A_N_reduced_dofs = evaluate_and_vectorize_sparse_matrix_at_dofs(A_N, reduced_dofs)

    log(PROGRESS, "A at dofs:\n" + str(A_dofs))
    log(PROGRESS, "A_N at reduced dofs:\n" + str(A_N_reduced_dofs))
    log(PROGRESS, "Error:\n" + str(A_dofs - A_N_reduced_dofs))
    
    assert isclose(A_dofs, A_N_reduced_dofs).all()

log(PROGRESS, "*** Elliptic case, offline computation ***")
compute_elliptic_error(reduced_mesh)

# Also test I/O
reduced_mesh_loaded = ReducedMesh((V, V))
reduced_mesh_loaded.load("test_reduced_mesh.output_dir", "test_reduced_mesh_elliptic")

log(PROGRESS, "*** Elliptic case, online computation ***")
compute_elliptic_error(reduced_mesh_loaded)


# ~~~ Mixed case ~~~ #
element_0 = VectorElement("Lagrange", mesh.ufl_cell(), 2)
element_1 = FiniteElement("Lagrange", mesh.ufl_cell(), 1)
element   = MixedElement(element_0, element_1)
V = FunctionSpace(mesh, element)

"""
dmp = DofMapPlotter(V)
dmp.plot()
dmp.show()
"""

reduced_mesh = ReducedMesh((V, V))
dofs = [(1, 2), (31, 33), (48, 12), (42, 42)]

for pair in dofs:
    log(PROGRESS, "Adding " + str(pair))
    reduced_mesh.append(pair)
    
    """
    plot(reduced_mesh.reduced_mesh_cells_marker)
    interactive()
    plot(reduced_mesh.get_reduced_mesh())
    interactive()
    """
    """
    dmp = DofMapPlotter(reduced_mesh.get_reduced_function_spaces()[0])
    dmp.plot()
    dmp.show()
    """
    
    if not skip_reduced_mesh_save:
        reduced_mesh.save("test_reduced_mesh.output_dir", "test_reduced_mesh_mixed")

def compute_mixed_error(reduced_mesh):
    reduced_V = reduced_mesh.get_reduced_function_spaces()
    dofs = reduced_mesh.get_dofs_list()
    reduced_dofs = reduced_mesh.get_reduced_dofs_list()

    u = TrialFunction(V)
    v = TestFunction(V)
    (u_0, u_1) = split(u)
    (v_0, v_1) = split(v)

    trial = 1
    test = 0
    u_N = TrialFunction(reduced_V[trial])
    v_N = TestFunction(reduced_V[test])
    (u_N_0, u_N_1) = split(u_N)
    (v_N_0, v_N_1) = split(v_N)

    A = assemble(u_0[0]*v_0[0]*dx + u_0[0]*v_0[1]*dx + u_0[1]*v_0[0]*dx + u_0[1]*v_0[1]*dx + u_1*v_1*dx + u_0[0]*v_1*dx + u_1*v_0[1]*dx)
    A_N = assemble(u_N_0[0]*v_N_0[0]*dx + u_N_0[0]*v_N_0[1]*dx + u_N_0[1]*v_N_0[0]*dx + u_N_0[1]*v_N_0[1]*dx + u_N_1*v_N_1*dx + u_N_0[0]*v_N_1*dx + u_N_1*v_N_0[1]*dx)

    A_dofs = evaluate_and_vectorize_sparse_matrix_at_dofs(A, dofs)
    A_N_reduced_dofs = evaluate_and_vectorize_sparse_matrix_at_dofs(A_N, reduced_dofs)

    log(PROGRESS, "A at dofs:\n" + str(A_dofs))
    log(PROGRESS, "A_N at reduced dofs:\n" + str(A_N_reduced_dofs))
    log(PROGRESS, "Error:\n" + str(A_dofs - A_N_reduced_dofs))
    
    assert isclose(A_dofs, A_N_reduced_dofs).all()

log(PROGRESS, "*** Mixed case, offline computation ***")
compute_mixed_error(reduced_mesh)

# Also test I/O
reduced_mesh_loaded = ReducedMesh((V, V))
reduced_mesh_loaded.load("test_reduced_mesh.output_dir", "test_reduced_mesh_mixed")

log(PROGRESS, "*** Mixed case, online computation ***")
compute_mixed_error(reduced_mesh_loaded)

# ~~~ Collapsed case ~~~ #
U = FunctionSpace(mesh, element)
V = U.sub(0).collapse()

"""
dmp = DofMapPlotter(U)
dmp.plot()
dmp.show()
dmp = DofMapPlotter(V)
dmp.plot()
dmp.show()
"""

reduced_mesh = ReducedMesh((V, U))
dofs = [(2, 1), (48, 33), (40, 12), (31, 39)]

for pair in dofs:
    log(PROGRESS, "Adding " + str(pair))
    reduced_mesh.append(pair)
    
    """
    plot(reduced_mesh.reduced_mesh_cells_marker)
    interactive()
    plot(reduced_mesh.get_reduced_mesh())
    interactive()
    """
    """
    dmp = DofMapPlotter(reduced_mesh.get_reduced_function_spaces()[0])
    dmp.plot()
    dmp.show()
    """
    
    if not skip_reduced_mesh_save:
        reduced_mesh.save("test_reduced_mesh.output_dir", "test_reduced_mesh_collapsed")
        
def compute_collapsed_error(reduced_mesh):
    reduced_V = reduced_mesh.get_reduced_function_spaces()
    dofs = reduced_mesh.get_dofs_list()
    reduced_dofs = reduced_mesh.get_reduced_dofs_list()

    u = TrialFunction(U)
    (u_0, u_1) = split(u)
    v = TestFunction(V)

    trial = 1
    test = 0
    u_N = TrialFunction(reduced_V[trial])
    v_N = TestFunction(reduced_V[test])
    (u_N_0, u_N_1) = split(u_N)
    
    A = assemble(inner(u_0, v)*dx + u_1*v[0]*dx)
    A_N = assemble(inner(u_N_0, v_N)*dx + u_N_1*v_N[0]*dx)

    A_dofs = evaluate_and_vectorize_sparse_matrix_at_dofs(A, dofs)
    A_N_reduced_dofs = evaluate_and_vectorize_sparse_matrix_at_dofs(A_N, reduced_dofs)

    log(PROGRESS, "A at dofs:\n" + str(A_dofs))
    log(PROGRESS, "A_N at reduced dofs:\n" + str(A_N_reduced_dofs))
    log(PROGRESS, "Error:\n" + str(A_dofs - A_N_reduced_dofs))
    
    assert isclose(A_dofs, A_N_reduced_dofs).all()

log(PROGRESS, "*** Collapsed case, offline computation ***")
compute_collapsed_error(reduced_mesh)

# Also test I/O
reduced_mesh_loaded = ReducedMesh((V, U))
reduced_mesh_loaded.load("test_reduced_mesh.output_dir", "test_reduced_mesh_collapsed")

log(PROGRESS, "*** Collapsed case, online computation ***")
compute_collapsed_error(reduced_mesh_loaded)