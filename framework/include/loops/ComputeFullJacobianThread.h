//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#ifndef COMPUTEFULLJACOBIANTHREAD_H
#define COMPUTEFULLJACOBIANTHREAD_H

#include "ComputeJacobianThread.h"

// Forward declarations
class FEProblemBase;
class NonlinearSystemBase;
class Kernel;

class ComputeFullJacobianThread : public ComputeJacobianThread
{
public:
  ComputeFullJacobianThread(FEProblemBase & fe_problem, const std::set<TagID> & tags);

  // Splitting Constructor
  ComputeFullJacobianThread(ComputeFullJacobianThread & x, Threads::split split);

  virtual ~ComputeFullJacobianThread();

  void join(const ComputeJacobianThread & /*y*/) {}

protected:
  virtual void computeJacobian() override;
  virtual void computeFaceJacobian(BoundaryID bnd_id) override;
  virtual void computeInternalFaceJacobian(const Elem * neighbor) override;
  virtual void computeInternalInterFaceJacobian(BoundaryID bnd_id) override;
  NonlinearSystemBase & _nl;

  // Reference to BC storage structures
  const MooseObjectWarehouse<IntegratedBCBase> & _integrated_bcs;

  // Reference to DGKernel storage
  const MooseObjectWarehouse<DGKernel> & _dg_kernels;

  // Reference to interface kernel storage
  const MooseObjectWarehouse<InterfaceKernel> & _interface_kernels;
};

#endif // COMPUTEFULLJACOBIANTHREAD_H
