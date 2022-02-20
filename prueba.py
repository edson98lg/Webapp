num = '14012022'

new_num = list(num)

print(num)

print(new_num)

año = (''.join(new_num[0:4]))
mes = (''.join(new_num[4:6]))
dia = (''.join(new_num[6:9]))

fecha = [año, mes, dia]
fecha = ('-'.join(fecha))
print(fecha)