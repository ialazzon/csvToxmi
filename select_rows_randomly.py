import pandas
import random

n = 3667623-1 #number of rows in the file
s = 1000 #desired sample size
name_of_file = "resources"
file = "./KDD/"+name_of_file+".csv"
skip = sorted(random.sample(range(n),n-s))
df = pandas.read_csv(file, skiprows=skip)
df.to_csv("./KDD/"+name_of_file+"_s.csv",index=False)