import tools

def bad_kernel_test():
  tools.executeAppExpectError(__file__,'bad_kernel_test.i',"A \w+ is not a registered Kernel")

def bad_bc_test():
  tools.executeAppExpectError(__file__,'bad_bc_test.i',"A \w+ is not a registered BC")

def bad_material_test():
  tools.executeAppExpectError(__file__,'bad_material_test.i',"A \w+ is not a registered Material")

def bad_executioner_test():
  tools.executeAppExpectError(__file__,'bad_executioner_test.i',"A \w+ is not a registered Executioner")

def no_output_dir_test():
  tools.executeAppExpectError(__file__,'no_output_dir_test.i',"Can not write to directory: \S+ for file base: \S+")

def missing_mesh_test():
  tools.executeAppExpectError(__file__,'missing_mesh_test.i',"cannot locate specified file:\s+\w+")

def bad_material_block_test():
  tools.executeAppExpectError(__file__,'bad_material_block_test.i','Material block \S+ specified in the input file does not exist')

def bad_kernel_var_test():
  tools.executeAppExpectError(__file__,'bad_kernel_var_test.i','variable foo does not exist in this system')

def bad_bc_var_test():
  tools.executeAppExpectError(__file__,'bad_bc_var_test.i','variable foo does not exist in this system')

def incomplete_kernel_block_coverage_test():
  tools.executeAppExpectError(__file__,'incomplete_kernel_block_coverage_test.i','The following block\(s\) lack an active kernel:')

def missing_mesh_bcs_test():
  tools.executeAppExpectError(__file__,'missing_mesh_bcs_test.i','The following boundary ids from your input file do not exist in the input mesh \d+')

def invalid_steady_exec_test():
  tools.executeAppExpectError(__file__,'invalid_steady_exec_test.i','You have specified time kernels in your steady state simulation')

def stateful_adaptive_error_test():
  tools.executeAppExpectError(__file__,'stateful_adaptive_error_test.i','Cannot use Material classes with stateful properties while utilizing adaptivity')
