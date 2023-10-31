import sys
from auction import main  

def generate_args(reserve: int):
    return ["--reserve", str(reserve)] + sys.argv[1:]

if __name__ == "__main__":
    reserve_prices = [i*10 for i in range(2)]
    result_strings = []
    for reserve_price in reserve_prices:
        args = generate_args(reserve_price)
        output = main(args)
        result_strings.append(output)

    for result in result_strings:
        print(result)