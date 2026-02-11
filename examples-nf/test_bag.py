from bag import Bag

bag = Bag(["Mango","Apple", "Pear"])

# Foreach loop
for fruit in bag:
    print(fruit)

# Composition 
composedString = [f + "s" for f in bag] # Pluralize the fruits
print(composedString)

# IndexOfMixIn = Bag(["Mango","Apple", "Pear"])
# print(IndexOfMixIn.index_of("Apple"))