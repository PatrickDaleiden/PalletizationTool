from mip import Model, xsum, maximize, BINARY, CONTINUOUS, INTEGER

# length, width, height, volume, weight
boxes = [[12, 24, 16, 4608, 15],
         [24, 12, 16, 4608, 15],
         [24, 24, 8, 4608, 20],
         [24, 24, 8, 4608, 20]]

combinations = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

pallet_origin = (100, 100, 100)
pallet_dimensions = (36, 24, 16, 60)

m = Model('palletization')

p = [m.add_var(var_type=BINARY, name="p[%d]" % i) for i in range(len(boxes))]
x = [m.add_var(var_type=CONTINUOUS, name="[x%d]" % j) for j in range(len(boxes))]
y = [m.add_var(var_type=CONTINUOUS, name="[y%d]" % k) for k in range(len(boxes))]
z = [m.add_var(var_type=CONTINUOUS, name="[z%d]" % l) for l in range(len(boxes))]
u = [m.add_var(var_type=BINARY, name="[u%d]" % u) for u in range(3 * len(combinations))]
m.objective = maximize(xsum(boxes[i][3] * p[i] for i in range(len(boxes))))

bin_vars = [(u[3*i], u[3*i + 1], u[3*i + 2]) for i in range(len(combinations))]

for idx, c in enumerate(combinations):
    m.add_constr(x[c[1]] - x[c[0]] <= -1 * boxes[c[1]][0] + 500 * (bin_vars[idx][1] + bin_vars[idx][2]))
    m.add_constr(x[c[0]] - x[c[1]] <= -1 * boxes[c[0]][0] + 500 * (bin_vars[idx][0] + bin_vars[idx][2]))
    m.add_constr(y[c[1]] - y[c[0]] <= -1 * boxes[c[1]][1] + 500 * (bin_vars[idx][0] + bin_vars[idx][1]))
    m.add_constr(y[c[0]] - y[c[1]] <= -1 * boxes[c[0]][1] + 500 * (2 - (bin_vars[idx][0] + bin_vars[idx][1])))
    m.add_constr(z[c[1]] - z[c[0]] <= -1 * boxes[c[1]][2] + 500 * (2 - (bin_vars[idx][1] + bin_vars[idx][2])))
    m.add_constr(z[c[0]] - z[c[1]] <= -1 * boxes[c[0]][2] + 500 * (2 - (bin_vars[idx][0] + bin_vars[idx][2])))
    m.add_constr(bin_vars[idx][0] + bin_vars[idx][1] + bin_vars[idx][2] >= 1)
    m.add_constr(bin_vars[idx][0] + bin_vars[idx][1] + bin_vars[idx][2] <= 2)

for i in range(len(boxes)):
    m.add_constr(x[i] >= pallet_origin[0] * p[i])
    m.add_constr(y[i] >= pallet_origin[1] * p[i])
    m.add_constr(z[i] >= pallet_origin[2] * p[i])
    m.add_constr(x[i] <= pallet_origin[0] + pallet_dimensions[0] - boxes[i][0])
    m.add_constr(y[i] <= pallet_origin[1] + pallet_dimensions[1] - boxes[i][1])
    m.add_constr(z[i] <= pallet_origin[2] + pallet_dimensions[2] - boxes[i][2])

m += xsum(boxes[i][4] * p[i] for i in range(len(boxes))) <= pallet_dimensions[3]

m.optimize()

if m.num_solutions:
    for i in range(len(boxes)):
        print('P%d: %d' % (i, p[i].x))
        print('x%d: %f' % (i, x[i].x))
        print('y%d: %f' % (i, y[i].x))
        print('z%d: %f' % (i, z[i].x))
    print("num_solutions: %d" % m.num_solutions)


