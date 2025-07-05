from random import randint


def __select_item_index(prefix: list[int]) -> int:
    weight = randint(1, prefix[-1])
    left, right = 0, len(prefix)
    print(weight)

    while left < right:
        mid = (left + right) // 2

        left_val = prefix[mid - 1] if mid > 0 else -float("inf")
        right_val = prefix[mid] if mid < len(prefix) else float("inf")

        if left_val < weight <= right_val:
            return mid if mid > 0 else 0

        elif weight <= left_val:
            right = mid
        else:
            left = mid + 1

    return len(prefix) - 1


prefix = [10, 12]

for i in range(10):
    j = __select_item_index(prefix)
    print(j, prefix[j], "inf" if j + 1 == len(prefix) else prefix[j + 1])
