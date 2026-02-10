#import Marketplace from nf.marketplace

def hello_world(i: int) -> str:
    return "Hello, World!" + str(i)

for i in range(5):
    print(hello_world(i))

