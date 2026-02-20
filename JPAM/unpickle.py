from itertools import groupby


class Person:
    def __init__(self, name, gender, age):
        self.name = name
        self.gender = gender
        self.age = age
        
        
people = [Person('A', 'F', 20), Person('B', 'M', 30), Person('C', 'F', 16), Person('D', 'M', 40)]

avg_age_female = sum(x.age for x in people if x.gender == 'F') / len([x for x in people if x.gender == 'F'])
avg_age_male = sum((x.age for x in people if x.gender == 'M')) / len([x for x in people if x.gender == 'M'])

# print(avg_age_female)
# print(avg_age_male)


people_sorted = sorted(people, key=lambda x: x.gender)
for g, p in groupby(people_sorted, lambda x: x.gender):
    cum_age, count = 0, 0
    ppl = list(p)
    print(sum(x.age for x in ppl) / len(ppl))

