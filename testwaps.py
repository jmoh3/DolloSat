from waps import sampler

sampler = sampler(cnfFile="formulas/m5_n10_s2.formula.cnf")
print(sampler)
sampler.compile()
sampler.parse()
sampler.annotate()
samples = sampler.sample()

print(list(samples))