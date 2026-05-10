#!/usr/bin/env sh

for f in "$@" ; do
    case "${f}" in
     *.yml|*.yaml)
	 printf "${f}\0"
	 ;;
    esac
done | xargs -0 yamllint
