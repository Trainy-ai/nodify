# -------------------------------------------------------------------------
# Copyright (c) Trainy, Inc. All rights reserved.
# --------------------------------------------------------------------------

def pop_list(range_list, index):
    next_index = index + 1
    if next_index >= len(range_list):
        return None, len(range_list)
    next_item = range_list[next_index]
    return next_item, next_index


def subtract_ranges_lists(range_list1, range_list2):
    """
    Subtracts out time where time intervals in `range_list2`
    overlap with `range_list1`
    """
    range_list_dst = []
    if len(range_list1) == 0:
        return range_list_dst
    if len(range_list2) == 0:
        range_list_dst = list(range_list1)
        return range_list_dst
    r1 = range_list1[0]
    r2 = range_list2[0]
    i1 = i2 = 0
    while i1 < len(range_list1):
        if i2 == len(range_list2):
            range_list_dst.append(r1)
            r1, i1 = pop_list(range_list1, i1)
        elif r2[1] <= r1[0]:
            r2, i2 = pop_list(range_list2, i2)
        elif r2[0] <= r1[0] and r2[1] < r1[1]:
            r1 = (r2[1], r1[1])
            r2, i2 = pop_list(range_list2, i2)
        elif r2[0] <= r1[0]:
            assert r2[1] >= r1[1]
            r2 = (r1[1], r2[1])
            r1, i1 = pop_list(range_list1, i1)
        elif r2[0] < r1[1]:
            assert r2[0] > r1[0]
            range_list_dst.append((r1[0], r2[0]))
            r1 = (r2[0], r1[1])
        else:
            assert r2[0] >= r1[1]
            range_list_dst.append(r1)
            r1, i1 = pop_list(range_list1, i1)
    return range_list_dst


def fraction_uncovered(range_list1, range_list2):
    """
    Given a list of m intervals `range_list1`, for each of the
    m intervals, calculates the fraction uncovered by intervals in
    range_list2
    """
    i2 = 0
    result = []
    for i1, r1 in enumerate(range_list1):
        size1 = r1[1] - r1[0]
        overlap = 0
        while i2 < len(range_list2) and range_list2[i2][0] < r1[1]:
            r2 = range_list2[i2]
            overlap += min(r2[1], r1[1]) - r2[0]
            i2 += 1
        result.append(1.0 - overlap / size1)
    return result
