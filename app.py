from flask import Flask, render_template, jsonify, request, g
from flask_cors import CORS
import subprocess
import json
import os
import tempfile
import time
import ast
import re
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'visits.db')

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visits
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  ip TEXT,
                  path TEXT,
                  user_agent TEXT,
                  referer TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def record_visit():
    """记录访问"""
    try:
        db = get_db()
        db.execute(
            'INSERT INTO visits (ip, path, user_agent, referer) VALUES (?, ?, ?, ?)',
            (request.remote_addr, request.path, request.headers.get('User-Agent', ''), request.headers.get('Referer', ''))
        )
        db.commit()
    except Exception as e:
        print(f"记录访问失败: {e}")

# 在每个请求前记录访问（排除静态资源和API）
@app.before_request
def before_request():
    if not request.path.startswith('/api/') and not request.path.startswith('/static'):
        record_visit()

# 题目数据 - 增加到20道题，包含四个难度
PROBLEMS = {'1': {'id': '1', 'title': '两数之和', 'difficulty': '简单', 'tags': ['数组', '哈希表'], 'description': '给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。\n\n你可以假设每种输入只会对应一个答案，并且你不能使用两次相同的元素。\n\n**示例：**\n```\n输入：nums = [2,7,11,15], target = 9\n输出：[0,1]\n解释：因为 nums[0] + nums[1] == 9 ，返回 [0, 1] 。\n```\n', 'template': 'def twoSum(nums, target):\n    """\n    :type nums: List[int]\n    :type target: int\n    :rtype: List[int]\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'twoSum([2, 7, 11, 15], 9)', 'expected': '[0, 1]'}, {'input': 'twoSum([3, 2, 4], 6)', 'expected': '[1, 2]'}, {'input': 'twoSum([3, 3], 6)', 'expected': '[0, 1]'}], 'solution': 'def twoSum(nums, target):\n    hash_map = {}\n    for i, num in enumerate(nums):\n        if target - num in hash_map:\n            return [hash_map[target - num], i]\n        hash_map[num] = i\n    return []\n', 'hints': ['可以使用哈希表优化查找', '遍历数组时，检查target-num是否已存在']}, '2': {'id': '2', 'title': '反转链表', 'difficulty': '简单', 'tags': ['链表', '递归'], 'description': '给你单链表的头节点 head，请你反转链表，并返回反转后的链表。\n\n**示例：**\n```\n输入：head = 1 -> 2 -> 3 -> 4 -> 5\n输出：5 -> 4 -> 3 -> 2 -> 1\n```\n\n为了简化，我们用列表表示链表，你需要反转列表。\n', 'template': 'def reverseList(head):\n    """\n    :type head: List[int]\n    :rtype: List[int]\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'reverseList([1, 2, 3, 4, 5])', 'expected': '[5, 4, 3, 2, 1]'}, {'input': 'reverseList([1, 2])', 'expected': '[2, 1]'}, {'input': 'reverseList([])', 'expected': '[]'}], 'solution': 'def reverseList(head):\n    return head[::-1]\n', 'hints': ['Python列表切片[::-1]可以反转', '或者用双指针方法']}, '3': {'id': '3', 'title': '有效的括号', 'difficulty': '简单', 'tags': ['栈', '字符串'], 'description': '给定一个只包括 \'(\'，\')\'，\'{\'，\'}\'，\'[\'，\']\' 的字符串 s，判断字符串是否有效。\n\n有效字符串需满足：\n1. 左括号必须用相同类型的右括号闭合\n2. 左括号必须以正确的顺序闭合\n3. 每个右括号都有一个对应的相同类型的左括号\n\n**示例：**\n```\n输入：s = "()[]{}"\n输出：True\n\n输入：s = "(]"\n输出：False\n```\n', 'template': 'def isValid(s):\n    """\n    :type s: str\n    :rtype: bool\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'isValid("()")', 'expected': 'True'}, {'input': 'isValid("()[]{}")', 'expected': 'True'}, {'input': 'isValid("(]")', 'expected': 'False'}, {'input': 'isValid("([)]")', 'expected': 'False'}, {'input': 'isValid("{[]}")', 'expected': 'True'}], 'solution': "def isValid(s):\n    stack = []\n    mapping = {')': '(', '}': '{', ']': '['}\n    for char in s:\n        if char in mapping:\n            top = stack.pop() if stack else '#'\n            if mapping[char] != top:\n                return False\n        else:\n            stack.append(char)\n    return not stack\n", 'hints': ['使用栈数据结构', '遇到右括号时检查栈顶是否匹配']}, '4': {'id': '4', 'title': '爬楼梯', 'difficulty': '简单', 'tags': ['动态规划', '数学'], 'description': '假设你正在爬楼梯。需要 n 阶你才能到达楼顶。\n\n每次你可以爬 1 或 2 个台阶。你有多少种不同的方法可以爬到楼顶？\n\n**示例：**\n```\n输入：n = 3\n输出：3\n解释：有三种方法可以爬到楼顶。\n1. 1 阶 + 1 阶 + 1 阶\n2. 1 阶 + 2 阶\n3. 2 阶 + 1 阶\n```\n', 'template': 'def climbStairs(n):\n    """\n    :type n: int\n    :rtype: int\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'climbStairs(2)', 'expected': '2'}, {'input': 'climbStairs(3)', 'expected': '3'}, {'input': 'climbStairs(5)', 'expected': '8'}, {'input': 'climbStairs(10)', 'expected': '89'}], 'solution': 'def climbStairs(n):\n    if n <= 2:\n        return n\n    a, b = 1, 2\n    for _ in range(3, n + 1):\n        a, b = b, a + b\n    return b\n', 'hints': ['这是斐波那契数列的变种', '可以用动态规划或迭代优化']}, '5': {'id': '5', 'title': '二分查找', 'difficulty': '简单', 'tags': ['数组', '二分查找'], 'description': '给定一个 n 个元素有序的（升序）整型数组 nums 和一个目标值 target，写一个函数搜索 nums 中的 target，如果目标值存在返回下标，否则返回 -1。\n\n**示例：**\n```\n输入：nums = [-1, 0, 3, 5, 9, 12], target = 9\n输出：4\n解释：9 出现在 nums 中并且下标为 4\n```\n', 'template': 'def search(nums, target):\n    """\n    :type nums: List[int]\n    :type target: int\n    :rtype: int\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'search([-1, 0, 3, 5, 9, 12], 9)', 'expected': '4'}, {'input': 'search([-1, 0, 3, 5, 9, 12], 2)', 'expected': '-1'}, {'input': 'search([5], 5)', 'expected': '0'}], 'solution': 'def search(nums, target):\n    left, right = 0, len(nums) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if nums[mid] == target:\n            return mid\n        elif nums[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1\n', 'hints': ['使用左右指针', '每次比较中间元素']}, '6': {'id': '6', 'title': '最大子数组和', 'difficulty': '中等', 'tags': ['数组', '动态规划'], 'description': '给你一个整数数组 nums，请你找出一个具有最大和的连续子数组（子数组最少包含一个元素），返回其最大和。\n\n**示例：**\n```\n输入：nums = [-2,1,-3,4,-1,2,1,-5,4]\n输出：6\n解释：连续子数组 [4,-1,2,1] 的和最大，为 6。\n```\n', 'template': 'def maxSubArray(nums):\n    """\n    :type nums: List[int]\n    :rtype: int\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'maxSubArray([-2, 1, -3, 4, -1, 2, 1, -5, 4])', 'expected': '6'}, {'input': 'maxSubArray([1])', 'expected': '1'}, {'input': 'maxSubArray([5, 4, -1, 7, 8])', 'expected': '23'}], 'solution': 'def maxSubArray(nums):\n    max_sum = nums[0]\n    current_sum = nums[0]\n    for num in nums[1:]:\n        current_sum = max(num, current_sum + num)\n        max_sum = max(max_sum, current_sum)\n    return max_sum\n', 'hints': ['动态规划思想', '维护当前最大和和全局最大和']}, '7': {'id': '7', 'title': '合并两个有序链表', 'difficulty': '中等', 'tags': ['链表', '递归'], 'description': '将两个升序链表合并为一个新的升序链表并返回。\n\n为了简化，我们用列表表示链表。\n\n**示例：**\n```\n输入：list1 = [1, 2, 4], list2 = [1, 3, 4]\n输出：[1, 1, 2, 3, 4, 4]\n```\n', 'template': 'def mergeTwoLists(list1, list2):\n    """\n    :type list1: List[int]\n    :type list2: List[int]\n    :rtype: List[int]\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'mergeTwoLists([1, 2, 4], [1, 3, 4])', 'expected': '[1, 1, 2, 3, 4, 4]'}, {'input': 'mergeTwoLists([], [])', 'expected': '[]'}, {'input': 'mergeTwoLists([], [0])', 'expected': '[0]'}], 'solution': 'def mergeTwoLists(list1, list2):\n    result = []\n    i, j = 0, 0\n    while i < len(list1) and j < len(list2):\n        if list1[i] <= list2[j]:\n            result.append(list1[i])\n            i += 1\n        else:\n            result.append(list2[j])\n            j += 1\n    result.extend(list1[i:])\n    result.extend(list2[j:])\n    return result\n', 'hints': ['使用双指针', '比较两个指针位置的元素']}, '8': {'id': '8', 'title': '买卖股票的最佳时机', 'difficulty': '中等', 'tags': ['数组', '动态规划'], 'description': '给定一个数组 prices，它的第 i 个元素 prices[i] 是一支给定股票第 i 天的价格。\n\n如果你最多只允许完成一笔交易（即买入和卖出一只股票），设计一个算法来计算你所能获取的最大利润。\n\n**示例：**\n```\n输入：[7, 1, 5, 3, 6, 4]\n输出：5\n解释：在第 2 天（价格 = 1）买入，在第 5 天（价格 = 6）卖出，最大利润 = 6-1 = 5。\n```\n', 'template': 'def maxProfit(prices):\n    """\n    :type prices: List[int]\n    :rtype: int\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'maxProfit([7, 1, 5, 3, 6, 4])', 'expected': '5'}, {'input': 'maxProfit([7, 6, 4, 3, 1])', 'expected': '0'}, {'input': 'maxProfit([1, 2])', 'expected': '1'}], 'solution': "def maxProfit(prices):\n    min_price = float('inf')\n    max_profit = 0\n    for price in prices:\n        if price < min_price:\n            min_price = price\n        elif price - min_price > max_profit:\n            max_profit = price - min_price\n    return max_profit\n", 'hints': ['记录最低价格', '计算当前价格与最低价的差']}, '9': {'id': '9', 'title': '无重复字符的最长子串', 'difficulty': '中等', 'tags': ['哈希表', '字符串', '滑动窗口'], 'description': '给定一个字符串 s，请你找出其中不含有重复字符的最长子串的长度。\n\n**示例：**\n```\n输入：s = "abcabcbb"\n输出：3\n解释：因为无重复字符的最长子串是 "abc"，所以其长度为 3。\n```\n', 'template': 'def lengthOfLongestSubstring(s):\n    """\n    :type s: str\n    :rtype: int\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'lengthOfLongestSubstring("abcabcbb")', 'expected': '3'}, {'input': 'lengthOfLongestSubstring("bbbbb")', 'expected': '1'}, {'input': 'lengthOfLongestSubstring("pwwkew")', 'expected': '3'}], 'solution': 'def lengthOfLongestSubstring(s):\n    char_set = set()\n    left = 0\n    max_len = 0\n    for right in range(len(s)):\n        while s[right] in char_set:\n            char_set.remove(s[left])\n            left += 1\n        char_set.add(s[right])\n        max_len = max(max_len, right - left + 1)\n    return max_len\n', 'hints': ['使用滑动窗口', '用集合记录窗口内的字符']}, '10': {'id': '10', 'title': '三数之和', 'difficulty': '中等', 'tags': ['数组', '双指针', '排序'], 'description': '给你一个整数数组 nums，判断是否存在三元组 [nums[i], nums[j], nums[k]] 满足 i != j、i != k 且 j != k，同时还满足 nums[i] + nums[j] + nums[k] == 0。\n\n请你返回所有和为 0 且不重复的三元组。\n\n**示例：**\n```\n输入：nums = [-1,0,1,2,-1,-4]\n输出：[[-1,-1,2],[-1,0,1]]\n```\n', 'template': 'def threeSum(nums):\n    """\n    :type nums: List[int]\n    :rtype: List[List[int]]\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'threeSum([-1, 0, 1, 2, -1, -4])', 'expected': '[[-1, -1, 2], [-1, 0, 1]]'}, {'input': 'threeSum([0, 1, 1])', 'expected': '[]'}, {'input': 'threeSum([0, 0, 0])', 'expected': '[[0, 0, 0]]'}], 'solution': 'def threeSum(nums):\n    nums.sort()\n    result = []\n    for i in range(len(nums) - 2):\n        if i > 0 and nums[i] == nums[i-1]:\n            continue\n        left, right = i + 1, len(nums) - 1\n        while left < right:\n            total = nums[i] + nums[left] + nums[right]\n            if total < 0:\n                left += 1\n            elif total > 0:\n                right -= 1\n            else:\n                result.append([nums[i], nums[left], nums[right]])\n                while left < right and nums[left] == nums[left+1]:\n                    left += 1\n                while left < right and nums[right] == nums[right-1]:\n                    right -= 1\n                left += 1\n                right -= 1\n    return result\n', 'hints': ['先排序', '固定一个数，用双指针找另外两个']}, '11': {'id': '11', 'title': '接雨水', 'difficulty': '困难', 'tags': ['栈', '数组', '双指针', '动态规划'], 'description': '给定 n 个非负整数表示每个宽度为 1 的柱子的高度图，计算按此排列的柱子，下雨之后能接多少雨水。\n\n**示例：**\n```\n输入：height = [0,1,0,2,1,0,1,3,2,1,2,1]\n输出：6\n解释：上面是由数组 [0,1,0,2,1,0,1,3,2,1,2,1] 表示的高度图，在这种情况下，可以接 6 个单位的雨水。\n```\n', 'template': 'def trap(height):\n    """\n    :type height: List[int]\n    :rtype: int\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])', 'expected': '6'}, {'input': 'trap([4, 2, 0, 3, 2, 5])', 'expected': '9'}], 'solution': 'def trap(height):\n    if not height:\n        return 0\n    left, right = 0, len(height) - 1\n    left_max, right_max = height[left], height[right]\n    water = 0\n    while left < right:\n        if left_max < right_max:\n            left += 1\n            left_max = max(left_max, height[left])\n            water += left_max - height[left]\n        else:\n            right -= 1\n            right_max = max(right_max, height[right])\n            water += right_max - height[right]\n    return water\n', 'hints': ['双指针从两端向中间移动', '记录左右最大高度']}, '12': {'id': '12', 'title': '最长回文子串', 'difficulty': '困难', 'tags': ['字符串', '动态规划'], 'description': '给你一个字符串 s，找到 s 中最长的回文子串。\n\n**示例：**\n```\n输入：s = "babad"\n输出："bab"\n解释："aba" 同样是符合题意的答案。\n```\n', 'template': 'def longestPalindrome(s):\n    """\n    :type s: str\n    :rtype: str\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'longestPalindrome("babad")', 'expected': '"bab"'}, {'input': 'longestPalindrome("cbbd")', 'expected': '"bb"'}, {'input': 'longestPalindrome("a")', 'expected': '"a"'}], 'solution': 'def longestPalindrome(s):\n    if len(s) < 2:\n        return s\n    start, max_len = 0, 1\n    for i in range(len(s)):\n        # 奇数长度\n        left, right = i - 1, i + 1\n        while left >= 0 and right < len(s) and s[left] == s[right]:\n            if right - left + 1 > max_len:\n                start = left\n                max_len = right - left + 1\n            left -= 1\n            right += 1\n        # 偶数长度\n        left, right = i - 1, i\n        while left >= 0 and right < len(s) and s[left] == s[right]:\n            if right - left + 1 > max_len:\n                start = left\n                max_len = right - left + 1\n            left -= 1\n            right += 1\n    return s[start:start + max_len]\n', 'hints': ['中心扩展法', '从每个位置向两边扩展']}, '13': {'id': '13', 'title': '编辑距离', 'difficulty': '困难', 'tags': ['字符串', '动态规划'], 'description': '给你两个单词 word1 和 word2，请返回将 word1 转换成 word2 所使用的最少操作数。\n\n你可以对一个单词进行如下三种操作：\n- 插入一个字符\n- 删除一个字符\n- 替换一个字符\n\n**示例：**\n```\n输入：word1 = "horse", word2 = "ros"\n输出：3\n解释：\nhorse -> rorse (将 \'h\' 替换为 \'r\')\nrorse -> rose (删除 \'r\')\nrose -> ros (删除 \'e\')\n```\n', 'template': 'def minDistance(word1, word2):\n    """\n    :type word1: str\n    :type word2: str\n    :rtype: int\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'minDistance("horse", "ros")', 'expected': '3'}, {'input': 'minDistance("intention", "execution")', 'expected': '5'}], 'solution': 'def minDistance(word1, word2):\n    m, n = len(word1), len(word2)\n    dp = [[0] * (n + 1) for _ in range(m + 1)]\n    for i in range(m + 1):\n        dp[i][0] = i\n    for j in range(n + 1):\n        dp[0][j] = j\n    for i in range(1, m + 1):\n        for j in range(1, n + 1):\n            if word1[i-1] == word2[j-1]:\n                dp[i][j] = dp[i-1][j-1]\n            else:\n                dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1\n    return dp[m][n]\n', 'hints': ['二维动态规划', 'dp[i][j]表示word1前i个字符到word2前j个字符的最小编辑距离']}, '14': {'id': '14', 'title': '合并K个升序链表', 'difficulty': '困难', 'tags': ['链表', '分治', '堆'], 'description': '给你一个链表数组，每个链表都已经按升序排列。\n\n请你将所有链表合并到一个升序链表中，返回合并后的链表。\n\n为了简化，我们用列表表示链表。\n\n**示例：**\n```\n输入：lists = [[1,4,5],[1,3,4],[2,6]]\n输出：[1,1,2,3,4,4,5,6]\n```\n', 'template': 'def mergeKLists(lists):\n    """\n    :type lists: List[List[int]]\n    :rtype: List[int]\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'mergeKLists([[1, 4, 5], [1, 3, 4], [2, 6]])', 'expected': '[1, 1, 2, 3, 4, 4, 5, 6]'}, {'input': 'mergeKLists([])', 'expected': '[]'}, {'input': 'mergeKLists([[]])', 'expected': '[]'}], 'solution': 'import heapq\ndef mergeKLists(lists):\n    result = []\n    heap = []\n    for i, lst in enumerate(lists):\n        if lst:\n            heapq.heappush(heap, (lst[0], i, 0))\n    while heap:\n        val, list_idx, elem_idx = heapq.heappop(heap)\n        result.append(val)\n        if elem_idx + 1 < len(lists[list_idx]):\n            heapq.heappush(heap, (lists[list_idx][elem_idx + 1], list_idx, elem_idx + 1))\n    return result\n', 'hints': ['使用最小堆', '每次取出最小的元素']}, '15': {'id': '15', 'title': '最长有效括号', 'difficulty': '困难', 'tags': ['栈', '字符串', '动态规划'], 'description': '给你一个只包含 \'(\' 和 \')\' 的字符串，找出最长有效（格式正确且连续）括号子串的长度。\n\n**示例：**\n```\n输入：s = "(()"\n输出：2\n解释：最长有效括号子串是 "()"\n\n输入：s = ")()())"\n输出：4\n解释：最长有效括号子串是 "()()"\n```\n', 'template': 'def longestValidParentheses(s):\n    """\n    :type s: str\n    :rtype: int\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'longestValidParentheses("(()")', 'expected': '2'}, {'input': 'longestValidParentheses(")()())")', 'expected': '4'}, {'input': 'longestValidParentheses("")', 'expected': '0'}], 'solution': "def longestValidParentheses(s):\n    stack = [-1]\n    max_len = 0\n    for i, char in enumerate(s):\n        if char == '(':\n            stack.append(i)\n        else:\n            stack.pop()\n            if not stack:\n                stack.append(i)\n            else:\n                max_len = max(max_len, i - stack[-1])\n    return max_len\n", 'hints': ['使用栈记录索引', '栈底元素为最后一个未匹配的右括号索引']}, '16': {'id': '16', 'title': '正则表达式匹配', 'difficulty': '非常困难', 'tags': ['递归', '字符串', '动态规划'], 'description': '给你一个字符串 s 和一个字符规律 p，请你来实现一个支持 \'.\' 和 \'*\' 的正则表达式匹配。\n\n- \'.\' 匹配任意单个字符\n- \'*\' 匹配零个或多个前面的那一个元素\n\n**示例：**\n```\n输入：s = "aa", p = "a*"\n输出：True\n解释：因为 \'*\' 代表可以匹配零个或多个前面的那一个元素, 在这里前面的元素就是 \'a\'。因此，字符串 "aa" 可被视为 "a" 重复了两次。\n```\n', 'template': 'def isMatch(s, p):\n    """\n    :type s: str\n    :type p: str\n    :rtype: bool\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'isMatch("aa", "a")', 'expected': 'False'}, {'input': 'isMatch("aa", "a*")', 'expected': 'True'}, {'input': 'isMatch("ab", ".*")', 'expected': 'True'}], 'solution': "def isMatch(s, p):\n    m, n = len(s), len(p)\n    dp = [[False] * (n + 1) for _ in range(m + 1)]\n    dp[0][0] = True\n    for j in range(2, n + 1):\n        if p[j-1] == '*':\n            dp[0][j] = dp[0][j-2]\n    for i in range(1, m + 1):\n        for j in range(1, n + 1):\n            if p[j-1] == '*':\n                dp[i][j] = dp[i][j-2] or (dp[i-1][j] and (s[i-1] == p[j-2] or p[j-2] == '.'))\n            else:\n                dp[i][j] = dp[i-1][j-1] and (s[i-1] == p[j-1] or p[j-1] == '.')\n    return dp[m][n]\n", 'hints': ['动态规划', 'dp[i][j]表示s前i个字符和p前j个字符是否匹配']}, '17': {'id': '17', 'title': 'N皇后', 'difficulty': '非常困难', 'tags': ['数组', '回溯'], 'description': '按照国际象棋的规则，皇后可以攻击与之处在同一行或同一列或同一斜线上的棋子。\n\nn 皇后问题研究的是如何将 n 个皇后放置在 n×n 的棋盘上，并且使皇后彼此之间不能相互攻击。\n\n给你一个整数 n，返回所有不同的 n 皇后问题的解决方案。\n\n**示例：**\n```\n输入：n = 4\n输出：[[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]\n解释：4 皇后问题存在两个不同的解法。\n```\n', 'template': 'def solveNQueens(n):\n    """\n    :type n: int\n    :rtype: List[List[str]]\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'solveNQueens(4)', 'expected': '[[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]'}, {'input': 'solveNQueens(1)', 'expected': '[["Q"]]'}], 'solution': "def solveNQueens(n):\n    def backtrack(row):\n        if row == n:\n            result.append([''.join(board[i]) for i in range(n)])\n            return\n        for col in range(n):\n            if col in cols or row - col in diag1 or row + col in diag2:\n                continue\n            cols.add(col)\n            diag1.add(row - col)\n            diag2.add(row + col)\n            board[row][col] = 'Q'\n            backtrack(row + 1)\n            board[row][col] = '.'\n            cols.remove(col)\n            diag1.remove(row - col)\n            diag2.remove(row + col)\n    \n    result = []\n    board = [['.'] * n for _ in range(n)]\n    cols, diag1, diag2 = set(), set(), set()\n    backtrack(0)\n    return result\n", 'hints': ['回溯算法', '用集合记录列、对角线的占用情况']}, '18': {'id': '18', 'title': '最小覆盖子串', 'difficulty': '非常困难', 'tags': ['哈希表', '字符串', '滑动窗口'], 'description': '给你一个字符串 s、一个字符串 t。返回 s 中涵盖 t 所有字符的最小子串。如果 s 中不存在涵盖 t 所有字符的子串，则返回空字符串。\n\n**示例：**\n```\n输入：s = "ADOBECODEBANC", t = "ABC"\n输出："BANC"\n解释：最小覆盖子串 "BANC" 包含来自字符串 t 的 \'A\'、\'B\' 和 \'C\'。\n```\n', 'template': 'def minWindow(s, t):\n    """\n    :type s: str\n    :type t: str\n    :rtype: str\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'minWindow("ADOBECODEBANC", "ABC")', 'expected': '"BANC"'}, {'input': 'minWindow("a", "a")', 'expected': '"a"'}, {'input': 'minWindow("a", "aa")', 'expected': '""'}], 'solution': 'from collections import Counter\ndef minWindow(s, t):\n    if not s or not t:\n        return ""\n    dict_t = Counter(t)\n    required = len(dict_t)\n    l, r = 0, 0\n    formed = 0\n    window_counts = {}\n    ans = float(\'inf\'), None, None\n    while r < len(s):\n        character = s[r]\n        window_counts[character] = window_counts.get(character, 0) + 1\n        if character in dict_t and window_counts[character] == dict_t[character]:\n            formed += 1\n        while l <= r and formed == required:\n            character = s[l]\n            if r - l + 1 < ans[0]:\n                ans = (r - l + 1, l, r)\n            window_counts[character] -= 1\n            if character in dict_t and window_counts[character] < dict_t[character]:\n                formed -= 1\n            l += 1\n        r += 1\n    return "" if ans[0] == float(\'inf\') else s[ans[1]:ans[2]+1]\n', 'hints': ['滑动窗口', '用字典记录字符出现次数']}, '19': {'id': '19', 'title': '单词拆分 II', 'difficulty': '非常困难', 'tags': ['字典树', '记忆化搜索', '哈希表', '字符串', '动态规划', '回溯'], 'description': '给定一个字符串 s 和一个字符串字典 wordDict，在字符串 s 中增加空格来构建一个句子，使得句子中所有的单词都在字典中。以任意顺序返回所有这些可能的句子。\n\n**示例：**\n```\n输入：s = "catsanddog", wordDict = ["cat","cats","and","sand","dog"]\n输出：["cats and dog","cat sand dog"]\n```\n', 'template': 'def wordBreak(s, wordDict):\n    """\n    :type s: str\n    :type wordDict: List[str]\n    :rtype: List[str]\n    """\n    # 在这里编写你的代码\n    pass\n', 'test_cases': [{'input': 'wordBreak("catsanddog", ["cat","cats","and","sand","dog"])', 'expected': '["cats and dog","cat sand dog"]'}, {'input': 'wordBreak("pineapplepenapple", ["apple","pen","applepen","pine","pineapple"])', 'expected': '["pine apple pen apple","pineapple pen apple","pine applepen apple"]'}], 'solution': 'def wordBreak(s, wordDict):\n    word_set = set(wordDict)\n    memo = {}\n    def backtrack(start):\n        if start in memo:\n            return memo[start]\n        if start == len(s):\n            return [""]\n        res = []\n        for end in range(start + 1, len(s) + 1):\n            word = s[start:end]\n            if word in word_set:\n                for sentence in backtrack(end):\n                    if sentence:\n                        res.append(word + " " + sentence)\n                    else:\n                        res.append(word)\n        memo[start] = res\n        return res\n    return backtrack(0)\n', 'hints': ['记忆化搜索', '回溯生成所有可能的句子']}, '21': {'id': '21', 'title': '有序数组查找', 'difficulty': '简单', 'tags': ['数组', '二分查找'], 'description': '给定一个已排序的整数数组 nums 和目标值 target，返回目标值的索引。如果不存在，返回 -1。要求时间复杂度 O(log n)。', 'template': 'def binary_search(nums, target):\n    pass', 'test_cases': [{'input': 'binary_search([1, 3, 5, 7, 9], 5)', 'expected': '2'}, {'input': 'binary_search([1, 3, 5, 7, 9], 6)', 'expected': '-1'}, {'input': 'binary_search([-1, 0, 3, 5, 9, 12], 9)', 'expected': '4'}], 'solution': 'def binary_search(nums, target):\n    left, right = 0, len(nums) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if nums[mid] == target:\n            return mid\n        elif nums[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1', 'hints': ['经典二分查找', '时间复杂度 O(log n)']}, '22': {'id': '22', 'title': '旋转数组找最小值', 'difficulty': '中等', 'tags': ['数组', '二分查找'], 'description': '一个升序数组在某点被旋转了，例如 [0,1,2,4,5,6,7] 变成 [4,5,6,7,0,1,2]。找出旋转后数组中的最小元素。要求 O(log n)。', 'template': 'def find_min(nums):\n    pass', 'test_cases': [{'input': 'find_min([4, 5, 6, 7, 0, 1, 2])', 'expected': '0'}, {'input': 'find_min([3, 4, 5, 1, 2])', 'expected': '1'}, {'input': 'find_min([1])', 'expected': '1'}], 'solution': 'def find_min(nums):\n    left, right = 0, len(nums) - 1\n    while left < right:\n        mid = (left + right) // 2\n        if nums[mid] > nums[right]:\n            left = mid + 1\n        else:\n            right = mid\n    return nums[left]', 'hints': ['二分查找旋转数组最小值', '比较 mid 和 right']}, '23': {'id': '23', 'title': '旋转数组查找', 'difficulty': '中等', 'tags': ['数组', '二分查找'], 'description': '一个升序数组被旋转后，在其中查找目标值，返回索引，找不到返回 -1。要求 O(log n)。', 'template': 'def search_rotated(nums, target):\n    pass', 'test_cases': [{'input': 'search_rotated([4,5,6,7,0,1,2], 0)', 'expected': '4'}, {'input': 'search_rotated([4,5,6,7,0,1,2], 3)', 'expected': '-1'}, {'input': 'search_rotated([1], 1)', 'expected': '0'}], 'solution': 'def search_rotated(nums, target):\n    left, right = 0, len(nums) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if nums[mid] == target:\n            return mid\n        if nums[left] <= nums[mid]:\n            if nums[left] <= target < nums[mid]:\n                right = mid - 1\n            else:\n                left = mid + 1\n        else:\n            if nums[mid] < target <= nums[right]:\n                left = mid + 1\n            else:\n                right = mid - 1\n    return -1', 'hints': ['判断哪半边有序', '在有序半边二分']}, '24': {'id': '24', 'title': '山脉数组峰值', 'difficulty': '中等', 'tags': ['数组', '二分查找'], 'description': '山脉数组：先严格递增，后严格递减。给定山脉数组，返回峰值索引。要求 O(log n)。', 'template': 'def peak_index(arr):\n    pass', 'test_cases': [{'input': 'peak_index([1, 3, 5, 4, 2])', 'expected': '2'}, {'input': 'peak_index([0, 2, 1, 0])', 'expected': '1'}, {'input': 'peak_index([0, 1, 0])', 'expected': '1'}], 'solution': 'def peak_index(arr):\n    left, right = 0, len(arr) - 1\n    while left < right:\n        mid = (left + right) // 2\n        if arr[mid] > arr[mid + 1]:\n            right = mid\n        else:\n            left = mid + 1\n    return left', 'hints': ['峰值大于相邻元素', '二分往大的方向走']}, '25': {'id': '25', 'title': '查找第一个错误版本', 'difficulty': '简单', 'tags': ['二分查找'], 'description': '产品从某个版本开始有 bug。给定版本总数 n 和函数 isBadVersion(version)，找出第一个出 bug 的版本。', 'template': 'def first_bad_version(n):\n    # 假设 isBadVersion(i) 可用\n    pass', 'test_cases': [{'input': 'first_bad_version(5)', 'expected': '4'}, {'input': 'first_bad_version(1)', 'expected': '1'}], 'solution': 'def first_bad_version(n):\n    left, right = 1, n\n    while left < right:\n        mid = (left + right) // 2\n        if isBadVersion(mid):\n            right = mid\n        else:\n            left = mid + 1\n    return left', 'hints': ['找第一个 True', '左边界二分']}, '26': {'id': '26', 'title': '查找插入位置', 'difficulty': '简单', 'tags': ['数组', '二分查找'], 'description': '给定已排序的不重复整数数组和目标值，如果找到返回索引，否则返回应该插入的位置。要求 O(log n)。', 'template': 'def search_insert(nums, target):\n    pass', 'test_cases': [{'input': 'search_insert([1,3,5,6], 5)', 'expected': '2'}, {'input': 'search_insert([1,3,5,6], 2)', 'expected': '1'}, {'input': 'search_insert([1,3,5,6], 7)', 'expected': '4'}], 'solution': 'def search_insert(nums, target):\n    left, right = 0, len(nums)\n    while left < right:\n        mid = (left + right) // 2\n        if nums[mid] < target:\n            left = mid + 1\n        else:\n            right = mid\n    return left', 'hints': ['二分找插入位置', '返回 left']}, '27': {'id': '27', 'title': '整数平方根', 'difficulty': '简单', 'tags': ['数学', '二分查找'], 'description': '给定非负整数 x，返回 x 的平方根的整数部分（向下取整）。不能使用内置 sqrt 函数。', 'template': 'def my_sqrt(x):\n    pass', 'test_cases': [{'input': 'my_sqrt(4)', 'expected': '2'}, {'input': 'my_sqrt(8)', 'expected': '2'}, {'input': 'my_sqrt(9)', 'expected': '3'}], 'solution': 'def my_sqrt(x):\n    if x < 2:\n        return x\n    left, right = 2, x // 2\n    while left <= right:\n        mid = (left + right) // 2\n        if mid * mid == x:\n            return mid\n        elif mid * mid < x:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return right', 'hints': ['二分找平方根', '返回 right']}, '28': {'id': '28', 'title': '判断完全平方数', 'difficulty': '简单', 'tags': ['数学', '二分查找'], 'description': '给定正整数 num，判断它是否是完全平方数。不能使用内置 sqrt 函数。', 'template': 'def is_perfect_square(num):\n    pass', 'test_cases': [{'input': 'is_perfect_square(16)', 'expected': 'True'}, {'input': 'is_perfect_square(14)', 'expected': 'False'}, {'input': 'is_perfect_square(1)', 'expected': 'True'}], 'solution': 'def is_perfect_square(num):\n    if num < 2:\n        return True\n    left, right = 2, num // 2\n    while left <= right:\n        mid = (left + right) // 2\n        if mid * mid == num:\n            return True\n        elif mid * mid < num:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return False', 'hints': ['二分判断完全平方数']}, '29': {'id': '29', 'title': '猜数字游戏', 'difficulty': '简单', 'tags': ['二分查找'], 'description': '在 1 到 n 之间猜一个数字，每次猜测会返回 -1(大了)、1(小了)或 0(对了)。给定 n 和 guess 函数，找出答案。', 'template': 'def guess_number(n):\n    # 假设 guess(num) 可用\n    pass', 'test_cases': [{'input': 'guess_number(10)', 'expected': '6'}, {'input': 'guess_number(1)', 'expected': '1'}], 'solution': 'def guess_number(n):\n    left, right = 1, n\n    while left <= right:\n        mid = (left + right) // 2\n        res = guess(mid)\n        if res == 0:\n            return mid\n        elif res == -1:\n            right = mid - 1\n        else:\n            left = mid + 1\n    return -1', 'hints': ['二分查找', 'guess 返回比较结果']}, '30': {'id': '30', 'title': '二维矩阵查找', 'difficulty': '中等', 'tags': ['数组', '二分查找', '矩阵'], 'description': '给定 m×n 矩阵，每行递增，每行第一个数大于上一行最后一个数。判断目标值是否在矩阵中。', 'template': 'def search_matrix(matrix, target):\n    pass', 'test_cases': [{'input': 'search_matrix([[1,3,5,7],[10,11,16,20],[23,30,34,50]], 3)', 'expected': 'True'}, {'input': 'search_matrix([[1,3,5,7],[10,11,16,20],[23,30,34,50]], 13)', 'expected': 'False'}], 'solution': 'def search_matrix(matrix, target):\n    if not matrix or not matrix[0]:\n        return False\n    m, n = len(matrix), len(matrix[0])\n    left, right = 0, m * n - 1\n    while left <= right:\n        mid = (left + right) // 2\n        val = matrix[mid // n][mid % n]\n        if val == target:\n            return True\n        elif val < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return False', 'hints': ['二维转一维索引', 'mid//n 得行, mid%n 得列']}, '31': {'id': '31', 'title': '两数之和', 'difficulty': '简单', 'tags': ['数组', '哈希表'], 'description': '给定整数数组和目标值，找出数组中和为目标值的两个数的索引。假设只有一个答案。', 'template': 'def two_sum(nums, target):\n    pass', 'test_cases': [{'input': 'two_sum([2, 7, 11, 15], 9)', 'expected': '[0, 1]'}, {'input': 'two_sum([3, 2, 4], 6)', 'expected': '[1, 2]'}, {'input': 'two_sum([3, 3], 6)', 'expected': '[0, 1]'}], 'solution': 'def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        if target - num in seen:\n            return [seen[target - num], i]\n        seen[num] = i\n    return []', 'hints': ['哈希表', '时间 O(n)']}, '32': {'id': '32', 'title': '有序数组两数之和', 'difficulty': '中等', 'tags': ['数组', '双指针'], 'description': '给定已排序的整数数组和目标值，找出两个数使其和等于目标值。返回索引（从1开始）。', 'template': 'def two_sum_sorted(numbers, target):\n    pass', 'test_cases': [{'input': 'two_sum_sorted([2, 7, 11, 15], 9)', 'expected': '[1, 2]'}, {'input': 'two_sum_sorted([2, 3, 4], 6)', 'expected': '[1, 3]'}], 'solution': 'def two_sum_sorted(numbers, target):\n    left, right = 0, len(numbers) - 1\n    while left < right:\n        s = numbers[left] + numbers[right]\n        if s == target:\n            return [left + 1, right + 1]\n        elif s < target:\n            left += 1\n        else:\n            right -= 1\n    return []', 'hints': ['双指针两端逼近', '利用有序性']}, '33': {'id': '33', 'title': '三数之和', 'difficulty': '中等', 'tags': ['数组', '双指针'], 'description': '给定整数数组，找出所有和为 0 的三元组。结果中不能有重复。', 'template': 'def three_sum(nums):\n    pass', 'test_cases': [{'input': 'three_sum([-1, 0, 1, 2, -1, -4])', 'expected': '[[-1, -1, 2], [-1, 0, 1]]'}, {'input': 'three_sum([0, 0, 0])', 'expected': '[[0, 0, 0]]'}], 'solution': 'def three_sum(nums):\n    nums.sort()\n    result = []\n    for i in range(len(nums) - 2):\n        if i > 0 and nums[i] == nums[i-1]:\n            continue\n        left, right = i + 1, len(nums) - 1\n        while left < right:\n            s = nums[i] + nums[left] + nums[right]\n            if s == 0:\n                result.append([nums[i], nums[left], nums[right]])\n                while left < right and nums[left] == nums[left+1]:\n                    left += 1\n                left += 1\n                right -= 1\n            elif s < 0:\n                left += 1\n            else:\n                right -= 1\n    return result', 'hints': ['排序+双指针', '注意去重']}, '34': {'id': '34', 'title': '盛最多水的容器', 'difficulty': '中等', 'tags': ['数组', '双指针'], 'description': '给定柱子高度数组，找出两个柱子使其与 x 轴构成的容器能盛最多水。', 'template': 'def max_area(height):\n    pass', 'test_cases': [{'input': 'max_area([1, 8, 6, 2, 5, 4, 8, 3, 7])', 'expected': '49'}, {'input': 'max_area([1, 1])', 'expected': '1'}], 'solution': 'def max_area(height):\n    left, right = 0, len(height) - 1\n    max_water = 0\n    while left < right:\n        water = (right - left) * min(height[left], height[right])\n        max_water = max(max_water, water)\n        if height[left] < height[right]:\n            left += 1\n        else:\n            right -= 1\n    return max_water', 'hints': ['双指针从两端开始', '移动较矮的指针']}, '35': {'id': '35', 'title': '验证回文串', 'difficulty': '简单', 'tags': ['字符串', '双指针'], 'description': '判断字符串是否是回文串，忽略大小写和非字母数字字符。', 'template': 'def is_palindrome(s):\n    pass', 'test_cases': [{'input': 'is_palindrome("A man, a plan, a canal: Panama")', 'expected': 'True'}, {'input': 'is_palindrome("race a car")', 'expected': 'False'}], 'solution': "def is_palindrome(s):\n    s = ''.join(c.lower() for c in s if c.isalnum())\n    return s == s[::-1]", 'hints': ['双指针或反转字符串', '忽略非字母数字']}, '36': {'id': '36', 'title': '移动零', 'difficulty': '简单', 'tags': ['数组', '双指针'], 'description': '将数组中的所有 0 移到末尾，保持非零元素的相对顺序。原地操作。', 'template': 'def move_zeroes(nums):\n    pass', 'test_cases': [{'input': 'move_zeroes([0, 1, 0, 3, 12])', 'expected': '[1, 3, 12, 0, 0]'}, {'input': 'move_zeroes([0])', 'expected': '[0]'}], 'solution': 'def move_zeroes(nums):\n    slow = 0\n    for fast in range(len(nums)):\n        if nums[fast] != 0:\n            nums[slow], nums[fast] = nums[fast], nums[slow]\n            slow += 1', 'hints': ['快慢指针', '非零元素往前移']}, '37': {'id': '37', 'title': '删除有序数组重复项', 'difficulty': '简单', 'tags': ['数组', '双指针'], 'description': '给定有序数组，原地删除重复元素，使每个元素只出现一次。返回新长度。', 'template': 'def remove_duplicates(nums):\n    pass', 'test_cases': [{'input': 'remove_duplicates([1, 1, 2])', 'expected': '2'}, {'input': 'remove_duplicates([0, 0, 1, 1, 1, 2, 2, 3, 3, 4])', 'expected': '5'}], 'solution': 'def remove_duplicates(nums):\n    if not nums:\n        return 0\n    slow = 0\n    for fast in range(1, len(nums)):\n        if nums[fast] != nums[slow]:\n            slow += 1\n            nums[slow] = nums[fast]\n    return slow + 1', 'hints': ['快慢指针', '返回新长度']}, '38': {'id': '38', 'title': '移除元素', 'difficulty': '简单', 'tags': ['数组', '双指针'], 'description': '原地移除数组中所有等于 val 的元素。返回新长度。', 'template': 'def remove_element(nums, val):\n    pass', 'test_cases': [{'input': 'remove_element([3, 2, 2, 3], 3)', 'expected': '2'}, {'input': 'remove_element([0, 1, 2, 2, 3, 0, 4, 2], 2)', 'expected': '5'}], 'solution': 'def remove_element(nums, val):\n    slow = 0\n    for fast in range(len(nums)):\n        if nums[fast] != val:\n            nums[slow] = nums[fast]\n            slow += 1\n    return slow', 'hints': ['快慢指针过滤', '返回新长度']}, '39': {'id': '39', 'title': '颜色分类', 'difficulty': '中等', 'tags': ['数组', '排序'], 'description': '给定包含 0、1、2 的数组，原地排序。要求一趟扫描。', 'template': 'def sort_colors(nums):\n    pass', 'test_cases': [{'input': 'sort_colors([2, 0, 2, 1, 1, 0])', 'expected': '[0, 0, 1, 1, 2, 2]'}, {'input': 'sort_colors([2, 0, 1])', 'expected': '[0, 1, 2]'}], 'solution': 'def sort_colors(nums):\n    p0, p2 = 0, len(nums) - 1\n    i = 0\n    while i <= p2:\n        if nums[i] == 0:\n            nums[i], nums[p0] = nums[p0], nums[i]\n            p0 += 1\n            i += 1\n        elif nums[i] == 2:\n            nums[i], nums[p2] = nums[p2], nums[i]\n            p2 -= 1\n        else:\n            i += 1', 'hints': ['荷兰国旗问题', '三指针分区']}, '40': {'id': '40', 'title': '反转字符串', 'difficulty': '简单', 'tags': ['字符串', '双指针'], 'description': '原地反转字符数组。', 'template': 'def reverse_string(s):\n    pass', 'test_cases': [{'input': 'reverse_string(["h", "e", "l", "l", "o"])', 'expected': '["o", "l", "l", "e", "h"]'}, {'input': 'reverse_string(["H", "a", "n", "n", "a", "h"])', 'expected': '["h", "a", "n", "n", "a", "H"]'}, {'input': 'reverse_string(["a"])', 'expected': '["a"]'}, {'input': 'reverse_string([])', 'expected': '[]'}], 'solution': 'def reverse_string(s):\n    left, right = 0, len(s) - 1\n    while left < right:\n        s[left], s[right] = s[right], s[left]\n        left += 1\n        right -= 1', 'hints': ['双指针原地交换', '时间 O(n)']}, '41': {'id': '41', 'title': '无重复字符最长子串', 'difficulty': '中等', 'tags': ['字符串', '滑动窗口'], 'description': '给定字符串，找出不含重复字符的最长子串的长度。', 'template': 'def length_of_longest_substring(s):\n    pass', 'test_cases': [{'input': 'length_of_longest_substring("abcabcbb")', 'expected': '3'}, {'input': 'length_of_longest_substring("bbbbb")', 'expected': '1'}, {'input': 'length_of_longest_substring("pwwkew")', 'expected': '3'}], 'solution': 'def length_of_longest_substring(s):\n    char_set = set()\n    left = max_len = 0\n    for right in range(len(s)):\n        while s[right] in char_set:\n            char_set.remove(s[left])\n            left += 1\n        char_set.add(s[right])\n        max_len = max(max_len, right - left + 1)\n    return max_len', 'hints': ['滑动窗口', 'set 维护无重复字符']}, '42': {'id': '42', 'title': '长度最小子数组', 'difficulty': '中等', 'tags': ['数组', '滑动窗口'], 'description': '给定正整数数组和目标值，找出和≥目标值的最短连续子数组长度。不存在返回0。', 'template': 'def min_subarray_len(target, nums):\n    pass', 'test_cases': [{'input': 'min_subarray_len(7, [2, 3, 1, 2, 4, 3])', 'expected': '2'}, {'input': 'min_subarray_len(4, [1, 4, 4])', 'expected': '1'}, {'input': 'min_subarray_len(11, [1, 1, 1, 1, 1, 1, 1, 1])', 'expected': '0'}], 'solution': "def min_subarray_len(target, nums):\n    left = 0\n    total = 0\n    min_len = float('inf')\n    for right in range(len(nums)):\n        total += nums[right]\n        while total >= target:\n            min_len = min(min_len, right - left + 1)\n            total -= nums[left]\n            left += 1\n    return min_len if min_len != float('inf') else 0", 'hints': ['滑动窗口', '维护窗口和 >= target']}, '43': {'id': '43', 'title': '找到字符串中所有字母异位词', 'difficulty': '中等', 'tags': ['字符串', '滑动窗口'], 'description': '给定字符串 s 和 p，找出 s 中所有 p 的字母异位词（排列相同）的起始索引。', 'template': 'def find_anagrams(s, p):\n    pass', 'test_cases': [{'input': 'find_anagrams("cbaebabacd", "abc")', 'expected': '[0, 6]'}, {'input': 'find_anagrams("abab", "ab")', 'expected': '[0, 1, 2]'}], 'solution': 'def find_anagrams(s, p):\n    from collections import Counter\n    need = Counter(p)\n    left = 0\n    result = []\n    for right in range(len(s)):\n        if s[right] in need:\n            need[s[right]] -= 1\n        if right - left + 1 > len(p):\n            if s[left] in need:\n                need[s[left]] += 1\n            left += 1\n        if right - left + 1 == len(p) and all(v == 0 for v in need.values()):\n            result.append(left)\n    return result', 'hints': ['固定窗口大小', 'Counter 判断异位词']}, '44': {'id': '44', 'title': '字符串排列', 'difficulty': '中等', 'tags': ['字符串', '滑动窗口'], 'description': '判断 s2 是否包含 s1 的某个排列。', 'template': 'def check_inclusion(s1, s2):\n    pass', 'test_cases': [{'input': 'check_inclusion("ab", "eidbaooo")', 'expected': 'True'}, {'input': 'check_inclusion("ab", "eidboaoo")', 'expected': 'False'}], 'solution': 'def check_inclusion(s1, s2):\n    from collections import Counter\n    need = Counter(s1)\n    left = 0\n    for right in range(len(s2)):\n        if s2[right] in need:\n            need[s2[right]] -= 1\n        if right - left + 1 > len(s1):\n            if s2[left] in need:\n                need[s2[left]] += 1\n            left += 1\n        if right - left + 1 == len(s1) and all(v == 0 for v in need.values()):\n            return True\n    return False', 'hints': ['滑动窗口', '判断排列']}, '45': {'id': '45', 'title': '最大平均子数组', 'difficulty': '简单', 'tags': ['数组', '滑动窗口'], 'description': '给定整数数组和整数 k，找出长度为 k 的连续子数组的最大平均值。', 'template': 'def find_max_average(nums, k):\n    pass', 'test_cases': [{'input': 'find_max_average([1, 12, -5, -6, 50, 3], 4)', 'expected': '12.75'}, {'input': 'find_max_average([5], 1)', 'expected': '5.0'}], 'solution': 'def find_max_average(nums, k):\n    total = sum(nums[:k])\n    max_avg = total / k\n    for i in range(k, len(nums)):\n        total += nums[i] - nums[i-k]\n        max_avg = max(max_avg, total / k)\n    return max_avg', 'hints': ['固定窗口大小 k', '滑动求平均']}, '46': {'id': '46', 'title': '岛屿数量', 'difficulty': '中等', 'tags': ['图', 'DFS', 'BFS'], 'description': "给定二维网格，'1'表示陆地，'0'表示水，计算岛屿数量。", 'template': 'def num_islands(grid):\n    pass', 'test_cases': [{'input': 'num_islands([["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]])', 'expected': '1'}, {'input': 'num_islands([["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]])', 'expected': '3'}], 'solution': "def num_islands(grid):\n    if not grid:\n        return 0\n    count = 0\n    def dfs(g, i, j):\n        if i < 0 or j < 0 or i >= len(g) or j >= len(g[0]) or g[i][j] != '1':\n            return\n        g[i][j] = '#'\n        dfs(g, i+1, j); dfs(g, i-1, j); dfs(g, i, j+1); dfs(g, i, j-1)\n    for i in range(len(grid)):\n        for j in range(len(grid[0])):\n            if grid[i][j] == '1':\n                dfs(grid, i, j)\n                count += 1\n    return count", 'hints': ['DFS/BFS 遍历', '访问过标记为 #']}, '47': {'id': '47', 'title': '岛屿最大面积', 'difficulty': '中等', 'tags': ['图', 'DFS', 'BFS'], 'description': '给定二维网格，计算最大岛屿的面积。', 'template': 'def max_area_of_island(grid):\n    pass', 'test_cases': [{'input': 'max_area_of_island([[0,0,1,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,1,1,1,0,0,0],[0,1,1,0,1,0,0,0,0,0,0,0,0],[0,1,0,0,1,1,0,0,1,0,1,0,0],[0,1,0,0,1,1,0,0,1,1,1,0,0],[0,0,0,0,0,0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,1,1,1,0,0,0],[0,0,0,0,0,0,0,1,1,0,0,0,0]])', 'expected': '6'}, {'input': 'max_area_of_island([[0,0,0,0,0,0,0,0]])', 'expected': '0'}, {'input': 'max_area_of_island([[1,1,1],[1,1,1]])', 'expected': '6'}, {'input': 'max_area_of_island([[1]])', 'expected': '1'}], 'solution': 'def max_area_of_island(grid):\n    def dfs(g, i, j):\n        if i < 0 or j < 0 or i >= len(g) or j >= len(g[0]) or g[i][j] != 1:\n            return 0\n        g[i][j] = 0\n        return 1 + dfs(g, i+1, j) + dfs(g, i-1, j) + dfs(g, i, j+1) + dfs(g, i, j-1)\n    max_area = 0\n    for i in range(len(grid)):\n        for j in range(len(grid[0])):\n            if grid[i][j] == 1:\n                max_area = max(max_area, dfs(grid, i, j))\n    return max_area', 'hints': ['DFS 计算面积', '返回岛屿大小']}, '48': {'id': '48', 'title': '单词搜索', 'difficulty': '中等', 'tags': ['图', 'DFS', '回溯'], 'description': '给定二维字符网格和单词，判断单词是否存在于网格中。单词由相邻单元格组成。', 'template': 'def exist(board, word):\n    pass', 'test_cases': [{'input': 'exist([["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], "ABCCED")', 'expected': 'True'}, {'input': 'exist([["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], "SEE")', 'expected': 'True'}, {'input': 'exist([["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], "ABCB")', 'expected': 'False'}], 'solution': "def exist(board, word):\n    m, n = len(board), len(board[0])\n    def dfs(i, j, k):\n        if k == len(word):\n            return True\n        if i < 0 or j < 0 or i >= m or j >= n or board[i][j] != word[k]:\n            return False\n        temp = board[i][j]\n        board[i][j] = '#'\n        found = dfs(i+1,j,k+1) or dfs(i-1,j,k+1) or dfs(i,j+1,k+1) or dfs(i,j-1,k+1)\n        board[i][j] = temp\n        return found\n    for i in range(m):\n        for j in range(n):\n            if dfs(i, j, 0):\n                return True\n    return False", 'hints': ['DFS 回溯', '临时标记防重复']}, '49': {'id': '49', 'title': '图像渲染', 'difficulty': '简单', 'tags': ['图', 'DFS', 'BFS'], 'description': '给定图像和起始点，将与起始点相连的相同颜色区域染成新颜色。', 'template': 'def flood_fill(image, sr, sc, color):\n    pass', 'test_cases': [{'input': 'flood_fill([[1,1,1],[1,1,0],[1,0,1]], 1, 1, 2)', 'expected': '[[2,2,2],[2,2,0],[2,0,1]]'}, {'input': 'flood_fill([[0,0,0],[0,0,0]], 0, 0, 2)', 'expected': '[[2,2,2],[2,2,2]]'}, {'input': 'flood_fill([[1]], 0, 0, 2)', 'expected': '[[2]]'}], 'solution': 'def flood_fill(image, sr, sc, color):\n    if image[sr][sc] == color:\n        return image\n    old = image[sr][sc]\n    def dfs(i, j):\n        if i < 0 or j < 0 or i >= len(image) or j >= len(image[0]) or image[i][j] != old:\n            return\n        image[i][j] = color\n        dfs(i+1, j); dfs(i-1, j); dfs(i, j+1); dfs(i, j-1)\n    dfs(sr, sc)\n    return image', 'hints': ['DFS 填充', '注意颜色相同的情况']}, '50': {'id': '50', 'title': '克隆图', 'difficulty': '中等', 'tags': ['图', 'DFS', 'BFS'], 'description': '给定无向连通图的节点，返回图的深拷贝。', 'template': 'def clone_graph(node):\n    pass', 'test_cases': [{'input': 'clone_graph(Node(1))', 'expected': 'clone'}], 'solution': 'def clone_graph(node):\n    if not node:\n        return None\n    visited = {}\n    def dfs(n):\n        if n in visited:\n            return visited[n]\n        clone = Node(n.val)\n        visited[n] = clone\n        for neighbor in n.neighbors:\n            clone.neighbors.append(dfs(neighbor))\n        return clone\n    return dfs(node)', 'hints': ['DFS 深拷贝', '字典记录已克隆节点']}, '51': {'id': '51', 'title': '课程安排', 'difficulty': '中等', 'tags': ['图', 'DFS', '拓扑排序'], 'description': '给定课程数和先修要求，判断能否完成所有课程。', 'template': 'def can_finish(num_courses, prerequisites):\n    pass', 'test_cases': [{'input': 'can_finish(2, [[1,0]])', 'expected': 'True'}, {'input': 'can_finish(2, [[1,0],[0,1]])', 'expected': 'False'}], 'solution': 'def can_finish(numCourses, prerequisites):\n    from collections import defaultdict, deque\n    graph = defaultdict(list)\n    indegree = [0] * numCourses\n    for c, p in prerequisites:\n        graph[p].append(c)\n        indegree[c] += 1\n    queue = deque([i for i in range(numCourses) if indegree[i] == 0])\n    count = 0\n    while queue:\n        node = queue.popleft()\n        count += 1\n        for n in graph[node]:\n            indegree[n] -= 1\n            if indegree[n] == 0:\n                queue.append(n)\n    return count == numCourses', 'hints': ['拓扑排序', 'BFS 入度为 0 的节点']}, '52': {'id': '52', 'title': '二叉树层序遍历', 'difficulty': '中等', 'tags': ['树', 'BFS'], 'description': '给定二叉树，返回层序遍历结果（按层分组）。', 'template': 'def level_order(root):\n    pass', 'test_cases': [{'input': 'level_order([3,9,20,null,null,15,7])', 'expected': '[[3],[9,20],[15,7]]'}, {'input': 'level_order([1])', 'expected': '[[1]]'}, {'input': 'level_order([])', 'expected': '[]'}, {'input': 'level_order([1,2,3,4,5])', 'expected': '[[1],[2,3],[4,5]]'}], 'solution': 'def level_order(root):\n    if not root:\n        return []\n    from collections import deque\n    result = []\n    queue = deque([root])\n    while queue:\n        level = []\n        for _ in range(len(queue)):\n            node = queue.popleft()\n            level.append(node.val)\n            if node.left:\n                queue.append(node.left)\n            if node.right:\n                queue.append(node.right)\n        result.append(level)\n    return result', 'hints': ['BFS 层序遍历', '每层单独记录']}, '53': {'id': '53', 'title': '二叉树最大深度', 'difficulty': '简单', 'tags': ['树', 'DFS'], 'description': '给定二叉树，返回其最大深度。', 'template': 'def max_depth(root):\n    pass', 'test_cases': [{'input': 'max_depth([3,9,20,null,null,15,7])', 'expected': '3'}, {'input': 'max_depth([1])', 'expected': '1'}], 'solution': 'def max_depth(root):\n    if not root:\n        return 0\n    return 1 + max(max_depth(root.left), max_depth(root.right))', 'hints': ['DFS 递归', '最大深度 = 1 + max(左, 右)']}, '54': {'id': '54', 'title': '对称二叉树', 'difficulty': '简单', 'tags': ['树', 'DFS'], 'description': '判断二叉树是否左右对称。', 'template': 'def is_symmetric(root):\n    pass', 'test_cases': [{'input': 'is_symmetric([1,2,2,3,4,4,3])', 'expected': 'True'}, {'input': 'is_symmetric([1,2,2,null,3,null,3])', 'expected': 'False'}], 'solution': 'def is_symmetric(root):\n    def is_mirror(left, right):\n        if not left and not right:\n            return True\n        if not left or not right:\n            return False\n        return left.val == right.val and is_mirror(left.left, right.right) and is_mirror(left.right, right.left)\n    return is_mirror(root.left, root.right) if root else True', 'hints': ['递归比较镜像', '左子树的左 = 右子树的右']}, '55': {'id': '55', 'title': '翻转二叉树', 'difficulty': '简单', 'tags': ['树', 'DFS'], 'description': '翻转二叉树（交换每个节点的左右子树）。', 'template': 'def invert_tree(root):\n    pass', 'test_cases': [{'input': 'invert_tree([4,2,7,1,3,6,9])', 'expected': '[4,7,2,9,6,3,1]'}, {'input': 'invert_tree([1,2])', 'expected': '[1,null,2]'}, {'input': 'invert_tree([])', 'expected': '[]'}, {'input': 'invert_tree([1])', 'expected': '[1]'}], 'solution': 'def invert_tree(root):\n    if not root:\n        return None\n    root.left, root.right = root.right, root.left\n    invert_tree(root.left)\n    invert_tree(root.right)\n    return root', 'hints': ['递归交换左右子树', '时间 O(n)']}, '56': {'id': '56', 'title': '爬楼梯', 'difficulty': '简单', 'tags': ['动态规划'], 'description': '每次可以爬 1 或 2 个台阶，问爬到第 n 阶有多少种方法。', 'template': 'def climb_stairs(n):\n    pass', 'test_cases': [{'input': 'climb_stairs(2)', 'expected': '2'}, {'input': 'climb_stairs(3)', 'expected': '3'}, {'input': 'climb_stairs(5)', 'expected': '8'}], 'solution': 'def climb_stairs(n):\n    if n <= 2:\n        return n\n    a, b = 1, 2\n    for _ in range(3, n + 1):\n        a, b = b, a + b\n    return b', 'hints': ['动态规划', 'dp[i] = dp[i-1] + dp[i-2]']}, '57': {'id': '57', 'title': '打家劫舍', 'difficulty': '中等', 'tags': ['动态规划'], 'description': '给定数组表示每间房屋的金额，相邻房屋不能同时被盗，求最大金额。', 'template': 'def rob(nums):\n    pass', 'test_cases': [{'input': 'rob([1, 2, 3, 1])', 'expected': '4'}, {'input': 'rob([2, 7, 9, 3, 1])', 'expected': '12'}], 'solution': 'def rob(nums):\n    if not nums:\n        return 0\n    if len(nums) == 1:\n        return nums[0]\n    prev2, prev1 = 0, nums[0]\n    for i in range(1, len(nums)):\n        curr = max(prev1, prev2 + nums[i])\n        prev2, prev1 = prev1, curr\n    return prev1', 'hints': ['动态规划', 'dp[i] = max(dp[i-1], dp[i-2] + nums[i])']}, '58': {'id': '58', 'title': '不同路径', 'difficulty': '中等', 'tags': ['动态规划'], 'description': '机器人从 m×n 网格左上角走到右下角，只能向右或向下，问有多少种路径。', 'template': 'def unique_paths(m, n):\n    pass', 'test_cases': [{'input': 'unique_paths(3, 7)', 'expected': '28'}, {'input': 'unique_paths(3, 2)', 'expected': '3'}], 'solution': 'def unique_paths(m, n):\n    dp = [[1] * n for _ in range(m)]\n    for i in range(1, m):\n        for j in range(1, n):\n            dp[i][j] = dp[i-1][j] + dp[i][j-1]\n    return dp[m-1][n-1]', 'hints': ['动态规划', 'dp[i][j] = dp[i-1][j] + dp[i][j-1]']}, '59': {'id': '59', 'title': '零钱兑换', 'difficulty': '中等', 'tags': ['动态规划'], 'description': '给定硬币面额和目标金额，计算凑成目标金额的最少硬币数。', 'template': 'def coin_change(coins, amount):\n    pass', 'test_cases': [{'input': 'coin_change([1, 2, 5], 11)', 'expected': '3'}, {'input': 'coin_change([2], 3)', 'expected': '-1'}], 'solution': "def coin_change(coins, amount):\n    dp = [float('inf')] * (amount + 1)\n    dp[0] = 0\n    for coin in coins:\n        for i in range(coin, amount + 1):\n            dp[i] = min(dp[i], dp[i - coin] + 1)\n    return dp[amount] if dp[amount] != float('inf') else -1", 'hints': ['完全背包问题', 'dp[i] 表示最小硬币数']}, '60': {'id': '60', 'title': '最长递增子序列', 'difficulty': '中等', 'tags': ['动态规划'], 'description': '给定数组，找出最长严格递增子序列的长度。', 'template': 'def length_of_lis(nums):\n    pass', 'test_cases': [{'input': 'length_of_lis([10, 9, 2, 5, 3, 7, 101, 18])', 'expected': '4'}, {'input': 'length_of_lis([0, 1, 0, 3, 2, 3])', 'expected': '4'}], 'solution': 'def length_of_lis(nums):\n    dp = [1] * len(nums)\n    for i in range(1, len(nums)):\n        for j in range(i):\n            if nums[i] > nums[j]:\n                dp[i] = max(dp[i], dp[j] + 1)\n    return max(dp) if dp else 0', 'hints': ['动态规划', 'dp[i] 表示以 i 结尾的最长递增子序列']}, '61': {'id': '61', 'title': '最大子数组和', 'difficulty': '中等', 'tags': ['动态规划'], 'description': '给定整数数组，找出具有最大和的连续子数组。', 'template': 'def max_sub_array(nums):\n    pass', 'test_cases': [{'input': 'max_sub_array([-2, 1, -3, 4, -1, 2, 1, -5, 4])', 'expected': '6'}, {'input': 'max_sub_array([1])', 'expected': '1'}], 'solution': 'def max_sub_array(nums):\n    max_sum = current_sum = nums[0]\n    for i in range(1, len(nums)):\n        current_sum = max(nums[i], current_sum + nums[i])\n        max_sum = max(max_sum, current_sum)\n    return max_sum', 'hints': ['Kadane 算法', '当前和为负则重新开始']}, '62': {'id': '62', 'title': '买卖股票最佳时机', 'difficulty': '简单', 'tags': ['动态规划'], 'description': '给定股价数组，选择某天买入和某天卖出，计算最大利润。', 'template': 'def max_profit(prices):\n    pass', 'test_cases': [{'input': 'max_profit([7, 1, 5, 3, 6, 4])', 'expected': '5'}, {'input': 'max_profit([7, 6, 4, 3, 1])', 'expected': '0'}], 'solution': "def max_profit(prices):\n    min_price = float('inf')\n    max_profit = 0\n    for price in prices:\n        min_price = min(min_price, price)\n        max_profit = max(max_profit, price - min_price)\n    return max_profit", 'hints': ['记录最低买入价', '计算最大利润']}, '63': {'id': '63', 'title': '三角形最小路径和', 'difficulty': '中等', 'tags': ['动态规划'], 'description': '给定三角形，从顶到底找最小路径和，每步只能移到下一行相邻位置。', 'template': 'def minimum_total(triangle):\n    pass', 'test_cases': [{'input': 'minimum_total([[2],[3,4],[6,5,7],[4,1,8,3]])', 'expected': '11'}, {'input': 'minimum_total([[1]])', 'expected': '1'}, {'input': 'minimum_total([[1],[2,3]])', 'expected': '3'}, {'input': 'minimum_total([[-10]])', 'expected': '-10'}], 'solution': 'def minimum_total(triangle):\n    dp = triangle[-1][:]\n    for i in range(len(triangle) - 2, -1, -1):\n        for j in range(len(triangle[i])):\n            dp[j] = triangle[i][j] + min(dp[j], dp[j + 1])\n    return dp[0]', 'hints': ['从底向上 DP', 'dp[j] 最小路径和']}, '64': {'id': '64', 'title': '最小花费爬楼梯', 'difficulty': '简单', 'tags': ['动态规划'], 'description': '给定数组表示爬每阶的花费，可从下标 0 或 1 开始，求到达顶部的最小花费。', 'template': 'def min_cost_climbing_stairs(cost):\n    pass', 'test_cases': [{'input': 'min_cost_climbing_stairs([10, 15, 20])', 'expected': '15'}, {'input': 'min_cost_climbing_stairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1])', 'expected': '6'}], 'solution': 'def min_cost_climbing_stairs(cost):\n    n = len(cost)\n    dp = [0] * (n + 1)\n    for i in range(2, n + 1):\n        dp[i] = min(dp[i-1] + cost[i-1], dp[i-2] + cost[i-2])\n    return dp[n]', 'hints': ['动态规划', '可从 0 或 1 开始']}, '65': {'id': '65', 'title': '分割等和子集', 'difficulty': '中等', 'tags': ['动态规划'], 'description': '给定数组，判断能否分成两个和相等的子集。', 'template': 'def can_partition(nums):\n    pass', 'test_cases': [{'input': 'can_partition([1, 5, 11, 5])', 'expected': 'True'}, {'input': 'can_partition([1, 2, 3, 5])', 'expected': 'False'}], 'solution': 'def can_partition(nums):\n    total = sum(nums)\n    if total % 2 != 0:\n        return False\n    target = total // 2\n    dp = [False] * (target + 1)\n    dp[0] = True\n    for num in nums:\n        for i in range(target, num - 1, -1):\n            dp[i] = dp[i] or dp[i - num]\n    return dp[target]', 'hints': ['01 背包问题', '目标和为 sum/2']}, '66': {'id': '66', 'title': '有效括号', 'difficulty': '简单', 'tags': ['栈', '字符串'], 'description': '给定只含括号的字符串，判断括号是否有效配对。', 'template': 'def is_valid(s):\n    pass', 'test_cases': [{'input': 'is_valid("()")', 'expected': 'True'}, {'input': 'is_valid("()[]{}")', 'expected': 'True'}, {'input': 'is_valid("(]")', 'expected': 'False'}, {'input': 'is_valid("([)]")', 'expected': 'False'}], 'solution': "def is_valid(s):\n    stack = []\n    mapping = {')': '(', ']': '[', '}': '{'}\n    for ch in s:\n        if ch in mapping:\n            if not stack or stack.pop() != mapping[ch]:\n                return False\n        else:\n            stack.append(ch)\n    return not stack", 'hints': ['栈匹配括号', '右括号检查栈顶']}, '67': {'id': '67', 'title': '最小栈', 'difficulty': '中等', 'tags': ['栈', '设计'], 'description': '设计一个支持 push、pop、top 和在 O(1) 时间内获取最小元素的栈。', 'template': 'class MinStack:\n    def __init__(self):\n        pass\n    def push(self, val):\n        pass\n    def pop(self):\n        pass\n    def top(self):\n        pass\n    def getMin(self):\n        pass', 'test_cases': [{'input': 'MinStack(push(-2), push(0), push(-3), getMin())', 'expected': '-3'}, {'input': 'MinStack(push(1), push(2), getMin())', 'expected': '1'}, {'input': 'MinStack(push(5), push(3), push(4), getMin())', 'expected': '3'}]}, '68': {'id': '68', 'title': '逆波兰表达式求值', 'difficulty': '中等', 'tags': ['栈'], 'description': '给定逆波兰表达式（后缀表达式），求其值。', 'template': 'def eval_rpn(tokens):\n    pass', 'test_cases': [{'input': 'eval_rpn(["2","1","+","3","*"])', 'expected': '9'}, {'input': 'eval_rpn(["4","13","5","/","+"])', 'expected': '6'}], 'solution': "def eval_rpn(tokens):\n    stack = []\n    for token in tokens:\n        if token in '+-*/':\n            b, a = stack.pop(), stack.pop()\n            if token == '+':\n                stack.append(a + b)\n            elif token == '-':\n                stack.append(a - b)\n            elif token == '*':\n                stack.append(a * b)\n            else:\n                stack.append(int(a / b))\n        else:\n            stack.append(int(token))\n    return stack[0]", 'hints': ['栈计算后缀表达式', '数字入栈，运算符计算']}, '69': {'id': '69', 'title': '每日温度', 'difficulty': '中等', 'tags': ['栈', '数组'], 'description': '给定每日温度数组，返回数组 answer，answer[i] 表示要等几天才能有更高温度。', 'template': 'def daily_temperatures(temperatures):\n    pass', 'test_cases': [{'input': 'daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73])', 'expected': '[1, 1, 4, 2, 1, 1, 0, 0]'}, {'input': 'daily_temperatures([30, 40, 50, 60])', 'expected': '[1, 1, 1, 0]'}], 'solution': 'def daily_temperatures(temperatures):\n    n = len(temperatures)\n    result = [0] * n\n    stack = []\n    for i in range(n):\n        while stack and temperatures[i] > temperatures[stack[-1]]:\n            prev = stack.pop()\n            result[prev] = i - prev\n        stack.append(i)\n    return result', 'hints': ['单调栈', '遇到更高温度计算天数']}, '70': {'id': '70', 'title': '车队', 'difficulty': '中等', 'tags': ['栈', '排序'], 'description': 'N 辆车沿单行道行驶，给定位置和速度，后车追上前车会合并成车队。求到达目标时的车队数量。', 'template': 'def car_fleet(target, position, speed):\n    pass', 'test_cases': [{'input': 'car_fleet(12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3])', 'expected': '3'}, {'input': 'car_fleet(10, [3], [3])', 'expected': '1'}, {'input': 'car_fleet(100, [0, 2, 4], [4, 2, 1])', 'expected': '1'}, {'input': 'car_fleet(10, [6, 8], [3, 2])', 'expected': '2'}], 'solution': 'def car_fleet(target, position, speed):\n    cars = sorted(zip(position, speed), reverse=True)\n    stack = []\n    for pos, spd in cars:\n        time = (target - pos) / spd\n        if not stack or time > stack[-1]:\n            stack.append(time)\n    return len(stack)', 'hints': ['按位置排序', '计算到达时间']}}
def run_python_code(code, timeout=5):
    """安全执行 Python 代码（Docker 沙箱）"""
    try:
        # 使用 Docker 沙箱执行代码
        result = subprocess.run(
            [
                'docker', 'run', '--rm',
                '--network=none',           # 禁止网络访问
                '--memory=128m',            # 内存限制 128MB
                '--cpus=0.5',               # CPU 限制 0.5 核
                '--pids-limit=50',          # 进程数限制
                '--security-opt=no-new-privileges',  # 禁止提权
                '--cap-drop=ALL',           # 移除所有 Linux capabilities
                '--security-opt', 'seccomp=unconfined',  # 使用默认 seccomp 配置
                '--read-only',              # 只读文件系统（仅允许 /tmp）
                '--tmpfs', '/tmp:size=10M,mode=1777',  # 临时目录
                '-i',                       # 交互模式
                'python-sandbox:latest',    # 沙箱镜像
            ],
            input=code,
            capture_output=True,
            text=True,
            timeout=timeout + 2  # Docker 额外给 2 秒
        )
        
        if result.returncode == 0:
            return {"success": True, "output": result.stdout.strip()}
        else:
            return {"success": False, "output": result.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": f"代码执行超时（{timeout}秒）"}
    except Exception as e:
        return {"success": False, "output": str(e)}

def analyze_code(code, problem_id):
    """分析代码质量"""
    analysis = {
        "score": 100,  # 从100分开始扣
        "comments": [],
        "suggestions": []
    }
    
    # 基本检查
    if not code.strip():
        analysis["score"] = 0
        analysis["comments"].append("❌ 代码为空")
        return analysis
    
    # 检查是否有注释 - 没有注释扣50分
    has_comment = False
    if "#" in code:
        # 检查是否是真正的注释（不是字符串内的#）
        lines = code.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                has_comment = True
                break
    if '"""' in code or "'''" in code:
        has_comment = True
    
    if has_comment:
        analysis["comments"].append("✅ 代码包含注释")
    else:
        analysis["score"] -= 50
        analysis["comments"].append("❌ 代码缺少注释 (-50分)")
        analysis["suggestions"].append("💡 建议添加代码注释，说明函数功能和关键逻辑")
    
    # 检查是否有pass
    if "pass" in code and "def " in code:
        analysis["score"] -= 30
        analysis["comments"].append("⚠️ 函数中包含 pass，可能未完成实现 (-30分)")
    
    # 检查代码长度
    lines = [l for l in code.split('\n') if l.strip()]
    if len(lines) < 3:
        analysis["comments"].append("⚠️ 代码行数较少，可能实现不完整")
    
    # 检查是否使用了数据结构
    if "dict" in code or "{" in code:
        analysis["comments"].append("✅ 使用了字典/哈希表")
    
    if "for" in code or "while" in code:
        analysis["comments"].append("✅ 使用了循环结构")
    
    # 针对题目的特定建议
    if problem_id in PROBLEMS:
        problem = PROBLEMS[problem_id]
        tags = problem.get("tags", [])
        
        if "动态规划" in tags and "dp" not in code.lower():
            analysis["suggestions"].append("💡 本题可用动态规划优化，建议尝试使用 dp 数组")
        
        if "双指针" in tags and "left" not in code.lower() and "right" not in code.lower():
            analysis["suggestions"].append("💡 本题可用双指针方法，建议尝试左右指针")
        
        if "递归" in tags and "return" not in code:
            analysis["suggestions"].append("💡 递归解法需要有返回值")
    
    # 确保分数在0-100之间
    analysis["score"] = min(100, max(0, analysis["score"]))
    
    if analysis["score"] >= 80:
        analysis["comments"].insert(0, "🎉 代码质量优秀！")
    elif analysis["score"] >= 60:
        analysis["comments"].insert(0, "📝 代码质量良好")
    else:
        analysis["comments"].insert(0, "⚠️ 代码需要改进")
    
    return analysis

@app.route('/')
def index():
    return render_template('index.html', problems=PROBLEMS)

@app.route('/api/problems')
def get_problems():
    difficulty_filter = request.args.get('difficulty', 'all')
    
    problems = []
    for p in PROBLEMS.values():
        if difficulty_filter == 'all' or p["difficulty"] == difficulty_filter:
            problems.append({
                "id": p["id"],
                "title": p["title"],
                "difficulty": p["difficulty"],
                "tags": p.get("tags", [])
            })
    
    return jsonify(problems)

@app.route('/api/problem/<problem_id>')
def get_problem(problem_id):
    if problem_id in PROBLEMS:
        problem = PROBLEMS[problem_id]
        
        # 获取函数名（从 template 中提取）
        template = problem["template"]
        func_match = re.search(r'def (\w+)\(', template)
        func_name = func_match.group(1) if func_match else "solution"
        
        # 生成测试用例调用代码
        test_calls = []
        for tc in problem["test_cases"]:
            # input 格式如 "twoSum([2, 7, 11, 15], 9)"
            test_calls.append(f"    print({tc['input']})  # 预期: {tc['expected']}")
        
        main_code = f'''

if __name__ == "__main__":
    # 测试用例
{chr(10).join(test_calls)}
'''
        full_template = template.rstrip() + main_code
        
        return jsonify({
            "id": problem["id"],
            "title": problem["title"],
            "difficulty": problem["difficulty"],
            "description": problem["description"],
            "template": full_template,
            "test_cases": problem["test_cases"],
            "tags": problem.get("tags", []),
            "hints": problem.get("hints", [])
        })
    return jsonify({"error": "题目不存在"}), 404

@app.route('/api/run', methods=['POST'])
def run_code():
    code = request.json.get('code', '')
    result = run_python_code(code)
    return jsonify(result)

@app.route('/api/submit/<problem_id>', methods=['POST'])
def submit_code(problem_id):
    if problem_id not in PROBLEMS:
        return jsonify({"error": "题目不存在"}), 404
    
    code = request.json.get('code', '')
    
    # 过滤掉 if __name__ == "__main__" 部分，只保留函数定义
    main_index = code.find('if __name__ == "__main__"')
    if main_index != -1:
        code = code[:main_index].rstrip()
    
    problem = PROBLEMS[problem_id]
    
    results = []
    all_passed = True
    
    for test_case in problem["test_cases"]:
        test_code = f"{code}\nprint({test_case['input']})"
        result = run_python_code(test_code)
        
        if result["success"]:
            actual = result["output"]
            expected = test_case["expected"]
            passed = actual == expected
            if not passed:
                all_passed = False
            results.append({
                "input": test_case["input"],
                "expected": expected,
                "actual": actual,
                "passed": passed
            })
        else:
            all_passed = False
            results.append({
                "input": test_case["input"],
                "expected": test_case["expected"],
                "actual": result["output"],
                "passed": False,
                "error": True
            })
    
    return jsonify({
        "all_passed": all_passed,
        "results": results
    })

@app.route('/api/analyze/<problem_id>', methods=['POST'])
def analyze(problem_id):
    """分析代码质量"""
    if problem_id not in PROBLEMS:
        return jsonify({"error": "题目不存在"}), 404
    
    code = request.json.get('code', '')
    analysis = analyze_code(code, problem_id)
    
    return jsonify(analysis)

@app.route('/api/solution/<problem_id>')
def get_solution(problem_id):
    if problem_id in PROBLEMS:
        problem = PROBLEMS[problem_id]
        solution = problem["solution"]
        
        # 获取函数名
        func_match = re.search(r'def (\w+)\(', solution)
        func_name = func_match.group(1) if func_match else "solution"
        
        # 生成测试用例调用
        test_calls = []
        for tc in problem["test_cases"]:
            test_calls.append(f"    print({tc['input']})  # 预期: {tc['expected']}")
        
        main_code = f'''

if __name__ == "__main__":
    # 测试用例
{chr(10).join(test_calls)}
'''
        full_solution = solution.rstrip() + main_code
        
        return jsonify({
            "solution": full_solution,
            "hints": problem.get("hints", [])
        })
    return jsonify({"error": "题目不存在"}), 404

@app.route('/api/hints/<problem_id>')
def get_hints(problem_id):
    if problem_id in PROBLEMS:
        return jsonify({"hints": PROBLEMS[problem_id].get("hints", [])})
    return jsonify({"error": "题目不存在"}), 404

@app.route('/free')
def free_editor():
    """自由编辑模式"""
    return render_template('free.html')

# ========== 访问统计功能 ==========

# 统计页面密码（从环境变量读取）
import os
STATS_PASSWORD = os.environ.get('STATS_PASSWORD', 'admin123')
STATS_TOKEN = os.environ.get('STATS_TOKEN', 'python_stats_2026')

def check_stats_auth():
    """检查统计页面权限"""
    token = request.cookies.get('stats_token')
    return token == STATS_TOKEN

@app.route('/stats')
def stats_page():
    """统计页面"""
    if not check_stats_auth():
        return render_template('stats_login.html')
    return render_template('stats.html')

@app.route('/api/stats/login', methods=['POST'])
def stats_login():
    """统计页面登录"""
    password = request.json.get('password', '')
    if password == STATS_PASSWORD:
        response = jsonify({'success': True})
        response.set_cookie('stats_token', STATS_TOKEN, max_age=86400*30)  # 30天有效
        return response
    return jsonify({'success': False, 'error': '密码错误'})

@app.route('/api/stats/logout')
def stats_logout():
    """退出登录"""
    response = jsonify({'success': True})
    response.delete_cookie('stats_token')
    return response

@app.route('/api/stats/check_auth')
def stats_check_auth():
    """检查登录状态"""
    return jsonify({'authenticated': check_stats_auth()})

@app.route('/api/stats/overview')
def stats_overview():
    """总览统计"""
    if not check_stats_auth():
        return jsonify({'error': '未授权'}), 401
    
    db = get_db()
    
    # 总访问量
    total = db.execute('SELECT COUNT(*) as count FROM visits').fetchone()['count']
    
    # 今日访问量
    today = db.execute(
        "SELECT COUNT(*) as count FROM visits WHERE date(timestamp) = date('now', 'localtime')"
    ).fetchone()['count']
    
    # 独立IP数
    unique_ips = db.execute('SELECT COUNT(DISTINCT ip) as count FROM visits').fetchone()['count']
    
    # 页面访问量
    page_views = db.execute(
        'SELECT path, COUNT(*) as count FROM visits GROUP BY path ORDER BY count DESC LIMIT 10'
    ).fetchall()
    
    return jsonify({
        'total': total,
        'today': today,
        'unique_ips': unique_ips,
        'page_views': [dict(row) for row in page_views]
    })

@app.route('/api/stats/daily')
def stats_daily():
    """每日访问统计"""
    if not check_stats_auth():
        return jsonify({'error': '未授权'}), 401
    db = get_db()
    
    days = request.args.get('days', 7, type=int)
    
    daily = db.execute(f'''
        SELECT date(timestamp) as date, COUNT(*) as count
        FROM visits
        WHERE timestamp >= date('now', '-{days} days', 'localtime')
        GROUP BY date(timestamp)
        ORDER BY date DESC
    ''').fetchall()
    
    return jsonify([dict(row) for row in daily])

@app.route('/api/stats/hourly')
def stats_hourly():
    """今日每小时访问统计"""
    if not check_stats_auth():
        return jsonify({'error': '未授权'}), 401
    db = get_db()
    
    hourly = db.execute('''
        SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
        FROM visits
        WHERE date(timestamp) = date('now', 'localtime')
        GROUP BY hour
        ORDER BY hour
    ''').fetchall()
    
    return jsonify([dict(row) for row in hourly])

@app.route('/api/stats/sources')
def stats_sources():
    """访问来源统计"""
    if not check_stats_auth():
        return jsonify({'error': '未授权'}), 401
    db = get_db()
    
    # IP 来源
    ip_stats = db.execute('''
        SELECT ip, COUNT(*) as count,
               MIN(timestamp) as first_visit,
               MAX(timestamp) as last_visit
        FROM visits
        GROUP BY ip
        ORDER BY count DESC
        LIMIT 20
    ''').fetchall()
    
    # Referer 来源
    referer_stats = db.execute('''
        SELECT 
            CASE 
                WHEN referer = '' OR referer IS NULL THEN '直接访问'
                ELSE referer
            END as source,
            COUNT(*) as count
        FROM visits
        GROUP BY source
        ORDER BY count DESC
        LIMIT 10
    ''').fetchall()
    
    # User-Agent 统计
    ua_stats = db.execute('''
        SELECT 
            CASE 
                WHEN user_agent LIKE '%Mobile%' THEN '移动端'
                WHEN user_agent LIKE '%Windows%' THEN 'Windows'
                WHEN user_agent LIKE '%Mac%' THEN 'Mac'
                WHEN user_agent LIKE '%Linux%' THEN 'Linux'
                ELSE '其他'
            END as platform,
            COUNT(*) as count
        FROM visits
        GROUP BY platform
        ORDER BY count DESC
    ''').fetchall()
    
    return jsonify({
        'ip_stats': [dict(row) for row in ip_stats],
        'referer_stats': [dict(row) for row in referer_stats],
        'platform_stats': [dict(row) for row in ua_stats]
    })

@app.route('/api/stats/recent')
def stats_recent():
    """最近访问记录"""
    if not check_stats_auth():
        return jsonify({'error': '未授权'}), 401
    db = get_db()
    
    limit = request.args.get('limit', 50, type=int)
    
    recent = db.execute(f'''
        SELECT ip, path, user_agent, referer, timestamp
        FROM visits
        ORDER BY timestamp DESC
        LIMIT {limit}
    ''').fetchall()
    
    return jsonify([dict(row) for row in recent])

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    print("🚀 Python 在线练习平台启动中...")
    print(f"📖 访问地址: http://localhost:5088")
    print(f"🆓 自由模式: http://localhost:5088/free")
    print(f"📊 访问统计: http://localhost:5088/stats")
    print(f"📚 已加载 {len(PROBLEMS)} 道题目")
    
    # 统计各难度题目数量
    difficulties = {}
    for p in PROBLEMS.values():
        d = p["difficulty"]
        difficulties[d] = difficulties.get(d, 0) + 1
    
    for d, count in difficulties.items():
        print(f"   - {d}: {count} 道")
    
    # 生产环境不使用 debug 模式
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5088, debug=debug_mode)
