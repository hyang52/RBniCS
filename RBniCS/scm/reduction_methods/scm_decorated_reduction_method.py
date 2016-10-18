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
## @file scm.py
#  @brief Implementation of the empirical interpolation method for the interpolation of parametrized functions
#
#  @author Francesco Ballarin <francesco.ballarin@sissa.it>
#  @author Gianluigi Rozza    <gianluigi.rozza@sissa.it>
#  @author Alberto   Sartori  <alberto.sartori@sissa.it>

from RBniCS.utils.decorators import Extends, override, ReductionMethodDecoratorFor
from RBniCS.scm.problems import SCM
from RBniCS.scm.reduction_methods.scm_approximation_reduction_method import SCMApproximationReductionMethod

@ReductionMethodDecoratorFor(SCM)
def SCMDecoratedReductionMethod(DifferentialProblemReductionMethod_DerivedClass):
    
    @Extends(DifferentialProblemReductionMethod_DerivedClass, preserve_class_name=True)
    class SCMDecoratedReductionMethod_Class(DifferentialProblemReductionMethod_DerivedClass):
        @override
        def __init__(self, truth_problem):
            # Call the parent initialization
            DifferentialProblemReductionMethod_DerivedClass.__init__(self, truth_problem)
            
            # Storage for SCM reduction method
            self.SCM_reduction = SCMApproximationReductionMethod(self.truth_problem.SCM_approximation, type(self.truth_problem).__name__ + "/scm")
            
        ###########################     SETTERS     ########################### 
        ## @defgroup Setters Set properties of the reduced order approximation
        #  @{
    
        # Propagate the values of all setters also to the SCM object
        
        ## OFFLINE: set maximum reduced space dimension (stopping criterion)
        @override
        def set_Nmax(self, Nmax, **kwargs):
            DifferentialProblemReductionMethod_DerivedClass.set_Nmax(self, Nmax, **kwargs)
            assert "SCM" in kwargs
            Nmax_SCM = kwargs["SCM"]
            assert isinstance(Nmax_SCM, int)
            self.SCM_reduction.set_Nmax(Nmax_SCM) # kwargs are not needed

            
        ## OFFLINE: set the elements in the training set \xi_train.
        @override
        def set_xi_train(self, ntrain, enable_import=True, sampling=None, **kwargs):
            import_successful = DifferentialProblemReductionMethod_DerivedClass.set_xi_train(self, ntrain, enable_import, sampling, **kwargs)
            # Set xi_train of SCM reduction
            assert "SCM" in kwargs
            ntrain_SCM = kwargs["SCM"]
            import_successful_SCM = self.SCM_reduction.set_xi_train(ntrain_SCM, enable_import=True, sampling=sampling) # kwargs are not needed
            # Return
            return import_successful and import_successful_SCM
            
        ## ERROR ANALYSIS: set the elements in the test set \xi_test.
        @override
        def set_xi_test(self, ntest, enable_import=False, sampling=None, **kwargs):
            import_successful = DifferentialProblemReductionMethod_DerivedClass.set_xi_test(self, ntest, enable_import, sampling, **kwargs)
            # Set xi_test of SCM reduction
            assert "SCM" in kwargs
            ntest_SCM = kwargs["SCM"]
            import_successful_SCM = self.SCM_reduction.set_xi_test(ntest_SCM, enable_import, sampling) # kwargs are not needed
            # Return
            return import_successful and import_successful_SCM
            
        #  @}
        ########################### end - SETTERS - end ########################### 
        
        ###########################     OFFLINE STAGE     ########################### 
        ## @defgroup OfflineStage Methods related to the offline stage
        #  @{
    
        ## Perform the offline phase of the reduced order model
        @override
        def offline(self):
            # Perform first the SCM offline phase, ...
            bak_first_mu = tuple(list(self.truth_problem.mu))
            self.SCM_reduction.offline()
            # ..., and then call the parent method.
            self.truth_problem.set_mu(bak_first_mu)
            return DifferentialProblemReductionMethod_DerivedClass.offline(self)
    
        #  @}
        ########################### end - OFFLINE STAGE - end ###########################
    
        ###########################     ERROR ANALYSIS     ########################### 
        ## @defgroup ErrorAnalysis Error analysis
        #  @{
    
        # Compute the error of the reduced order approximation with respect to the full order one
        # over the test set
        @override
        def error_analysis(self, N=None, **kwargs):
            # Perform first the SCM error analysis, ...
            if (
                "with_respect_to" not in kwargs # otherwise we assume the user was interested in computing the error w.r.t. 
                                                # an exact coercivity constant, 
                                                # so he probably is not interested in the error analysis of SCM
                    and
                "N_SCM" not in kwargs           # otherwise we assume the user was interested in computing the error for a fixed number of SCM basis
                                                # functions, thus he has already carried out the error analysis of SCM
            ):
                self.SCM_reduction.error_analysis(N)
            # ..., and then call the parent method.
            DifferentialProblemReductionMethod_DerivedClass.error_analysis(self, N, **kwargs)
            
        #  @}
        ########################### end - ERROR ANALYSIS - end ########################### 
        
    # return value (a class) for the decorator
    return SCMDecoratedReductionMethod_Class
    
