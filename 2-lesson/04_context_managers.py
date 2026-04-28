# with open("example.txt", "w") as f:
#     f.write("Hello, world!")
#


    class ManagedResource:
        def __enter__(self):
            print("Resource opened")
            return "resource"
        
        def __exit__(self, exc_type, exc_value, traceback):
            print("Resource closed")

    with ManagedResource() as res:
        print(f"Using {res}")


import time
from contextlib import contextmanager

@contextmanager
def timer(name="Code block"):
    start = time.time()
    yield
    end = time.time()
    print(f"{name} took {end - start:.4f} seconds")

with timer("Processing"):
    sum(range(10**6))


    