# import time
# from datetime import timedelta

from timeit import timeit


def fact_no_tail(n):
    if n > 0:
        return n*fact_no_tail(n-1)
    else:
        return 1


def fact(n):
    def tail(n, acc):
        if n > 0:
            return tail(n-1, acc*n)
        else:
            return acc
    return tail(n, 1)


def PointsCombinations(lst):
    length = len(lst)
    if length == 0:
        return []
    elif length == 1:
        return lst
    elif length == 2:
        return [[lst[0], lst[1]], [lst[1], lst[0]]]
    else:
        result = []
        for i in range(length):
            nlst = PointsCombinations(lst[:i] + lst[(i + 1):])
            nlength = len(nlst)
            for j in range(nlength):
                result.append([lst[i]]+nlst[j])
        return result


if __name__ == "__main__":
    test_iterations_number = 1
    test_function = PointsCombinations
    test_function_name = test_function.__name__

    test_function_setup = "from __main__ import " + test_function_name

    ftime = lambda arg: timeit(test_function_name + "(" + str(arg) + ")",
                               test_function_setup,
                               number = test_iterations_number)
    print "Functions are loaded"
