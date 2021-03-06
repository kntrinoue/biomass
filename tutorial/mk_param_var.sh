#!/bin/sh

# script to extract parameters from param_const.py
grep '\[C' ../biomass/model/param_const.py | \
sed 's/x\[C\.//g' | \
sed 's/\].*//g' | \
awk '!seen[$0]++' | \
sed -e 's/[[:space:]]\+//g' | \
sed -e "s/\(.*\)/'\1'/" | \
sed 's/$/,/' |
sed -e 's/^/	/g' |
sed -e 's/    //g' > param_var_mid

echo 'param_names = [\' > first_line

echo "	##
	'len_f_params'\
]
for idx,name in enumerate(param_names):
    exec('%s=%d'%(name,idx))" > last_line


cat first_line param_var_mid last_line > ../biomass/model/name2idx/parameters.py

rm first_line
rm param_var_mid
rm last_line

echo "done processing parameters"

# script to extract variables from differential_equation.py
grep 'dydt\[V' ../biomass/model/differential_equation.py | \
sed 's/dydt\[V\.//g' | \
sed 's/\].*//g' | \
awk '!seen[$0]++' | \
sed -e 's/[[:space:]]\+//g' | \
sed -e "s/\(.*\)/'\1'/" | \
sed 's/$/,/' |
sed -e 's/^/	/g' |
sed -e 's/    //g' > var_var_mid

echo 'var_names = [\' > first_line

echo "	##
	'len_f_vars'\
]
for idx,name in enumerate(var_names):
    exec('%s=%d'%(name,idx))" > last_line


cat first_line var_var_mid last_line > ../biomass/model/name2idx/variables.py

rm first_line
rm var_var_mid
rm last_line

echo "done processing variables"
