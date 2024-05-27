! vim:set sw=4 ts=8 fileencoding=ascii:
! SPDX-License-Identifier: BSD-3-Clause
! Copyright (c) 2013, Martin Gaitan
! Copyright (c) 2024, Serguei E. Leontiev (leo@sai.msu.ru)
!
! FILE: solve.f90
subroutine solve(A, b, x, n)
    ! solve the matrix equation A*x=b using LAPACK
    implicit none

    real*8, dimension(n,n), intent(in) :: A
    real*8, dimension(n), intent(in) :: b
    real*8, dimension(n), intent(out) :: x

    integer :: pivot(n), ok

    integer, intent(in) :: n
    x = b

    ! find the solution using the LAPACK routine SGESV
    call DGESV(n, 1, A, n, pivot, x, n, ok)
end subroutine
