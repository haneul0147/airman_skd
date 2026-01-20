def subset_sum(nums, target):
    result = []

    def backtrack(start, current, total):
        if total == target:
            result.append(current.copy())
            return
        if total > target:
            return

        for i in range(start, len(nums)):
            current.append(nums[i])
            backtrack(i + 1, current, total + nums[i])
            current.pop()

    backtrack(0, [], 0)
    return result


nums = [12053580, 45557600, 17544120, 13786960, 43557140, 25940816, 11719400, 720760, 785000, 5957983, 3142040, 42036940, 14833170, 105695315, 1224420200]
target = 114955280

print(subset_sum(nums, target))
