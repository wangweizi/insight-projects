import math


class PercentileFinder(object):
    def find_by_percentile(self, nums, percentile):
        rank = len(nums) - int(math.ceil((percentile/100.0) * len(nums))) + 1
        return self.find_kth_largest(nums, rank)

    def find_kth_largest(self, nums, k):
        pivot = nums[0]
        tail = 0

        for i in range(1, len(nums)):
            if nums[i] > pivot:
                tail += 1
                nums[tail], nums[i] = nums[i], nums[tail]

        nums[tail], nums[0] = nums[0], nums[tail]

        if tail + 1 == k:
            return pivot
        elif tail + 1 < k:
            return self.find_kth_largest(nums[tail+1:], k - tail - 1)
        else:
            return self.find_kth_largest(nums[:tail], k)