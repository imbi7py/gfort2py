! SPDX-License-Identifier: GPL-2.0+

module com

	use iso_fortran_env, only: output_unit, real128
	
	implicit none
	
	! Parameters
	integer, parameter :: dp = selected_real_kind(p=15)
	integer, parameter :: qp = selected_real_kind(p=30)
	integer, parameter :: lp = selected_int_kind(8)
	
	
	integer :: x_int, y_int, z_int
	common  x_int, y_int, z_int
	
	integer :: x_int1, y_int1, z_int1
	common  /com_mod/ x_int1, y_int1, z_int1
	
	
	contains



	subroutine sub_setup_common()
	
		integer ::  a_int,b_int,c_int
		common  /comm1/ a_int,b_int,c_int
	
	
	end subroutine sub_setup_common


end module com