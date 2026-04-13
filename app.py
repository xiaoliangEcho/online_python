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
PROBLEMS = {
    # ========== 简单 (1-5) ==========
    "1": {
        "id": "1",
        "title": "两数之和",
        "difficulty": "简单",
        "tags": ["数组", "哈希表"],
        "description": """给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。

你可以假设每种输入只会对应一个答案，并且你不能使用两次相同的元素。

**示例：**
```
输入：nums = [2,7,11,15], target = 9
输出：[0,1]
解释：因为 nums[0] + nums[1] == 9 ，返回 [0, 1] 。
```
""",
        "template": """def twoSum(nums, target):
    \"\"\"
    :type nums: List[int]
    :type target: int
    :rtype: List[int]
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": "twoSum([2, 7, 11, 15], 9)", "expected": "[0, 1]"},
            {"input": "twoSum([3, 2, 4], 6)", "expected": "[1, 2]"},
            {"input": "twoSum([3, 3], 6)", "expected": "[0, 1]"}
        ],
        "solution": """def twoSum(nums, target):
    hash_map = {}
    for i, num in enumerate(nums):
        if target - num in hash_map:
            return [hash_map[target - num], i]
        hash_map[num] = i
    return []
""",
        "hints": ["可以使用哈希表优化查找", "遍历数组时，检查target-num是否已存在"]
    },
    "2": {
        "id": "2",
        "title": "反转链表",
        "difficulty": "简单",
        "tags": ["链表", "递归"],
        "description": """给你单链表的头节点 head，请你反转链表，并返回反转后的链表。

**示例：**
```
输入：head = 1 -> 2 -> 3 -> 4 -> 5
输出：5 -> 4 -> 3 -> 2 -> 1
```

为了简化，我们用列表表示链表，你需要反转列表。
""",
        "template": """def reverseList(head):
    \"\"\"
    :type head: List[int]
    :rtype: List[int]
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": "reverseList([1, 2, 3, 4, 5])", "expected": "[5, 4, 3, 2, 1]"},
            {"input": "reverseList([1, 2])", "expected": "[2, 1]"},
            {"input": "reverseList([])", "expected": "[]"}
        ],
        "solution": """def reverseList(head):
    return head[::-1]
""",
        "hints": ["Python列表切片[::-1]可以反转", "或者用双指针方法"]
    },
    "3": {
        "id": "3",
        "title": "有效的括号",
        "difficulty": "简单",
        "tags": ["栈", "字符串"],
        "description": """给定一个只包括 '('，')'，'{'，'}'，'['，']' 的字符串 s，判断字符串是否有效。

有效字符串需满足：
1. 左括号必须用相同类型的右括号闭合
2. 左括号必须以正确的顺序闭合
3. 每个右括号都有一个对应的相同类型的左括号

**示例：**
```
输入：s = "()[]{}"
输出：True

输入：s = "(]"
输出：False
```
""",
        "template": """def isValid(s):
    \"\"\"
    :type s: str
    :rtype: bool
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": 'isValid("()")', "expected": "True"},
            {"input": 'isValid("()[]{}")', "expected": "True"},
            {"input": 'isValid("(]")', "expected": "False"},
            {"input": 'isValid("([)]")', "expected": "False"},
            {"input": 'isValid("{[]}")', "expected": "True"}
        ],
        "solution": """def isValid(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in mapping:
            top = stack.pop() if stack else '#'
            if mapping[char] != top:
                return False
        else:
            stack.append(char)
    return not stack
""",
        "hints": ["使用栈数据结构", "遇到右括号时检查栈顶是否匹配"]
    },
    "4": {
        "id": "4",
        "title": "爬楼梯",
        "difficulty": "简单",
        "tags": ["动态规划", "数学"],
        "description": """假设你正在爬楼梯。需要 n 阶你才能到达楼顶。

每次你可以爬 1 或 2 个台阶。你有多少种不同的方法可以爬到楼顶？

**示例：**
```
输入：n = 3
输出：3
解释：有三种方法可以爬到楼顶。
1. 1 阶 + 1 阶 + 1 阶
2. 1 阶 + 2 阶
3. 2 阶 + 1 阶
```
""",
        "template": """def climbStairs(n):
    \"\"\"
    :type n: int
    :rtype: int
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": "climbStairs(2)", "expected": "2"},
            {"input": "climbStairs(3)", "expected": "3"},
            {"input": "climbStairs(5)", "expected": "8"},
            {"input": "climbStairs(10)", "expected": "89"}
        ],
        "solution": """def climbStairs(n):
    if n <= 2:
        return n
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b
""",
        "hints": ["这是斐波那契数列的变种", "可以用动态规划或迭代优化"]
    },
    "5": {
        "id": "5",
        "title": "二分查找",
        "difficulty": "简单",
        "tags": ["数组", "二分查找"],
        "description": """给定一个 n 个元素有序的（升序）整型数组 nums 和一个目标值 target，写一个函数搜索 nums 中的 target，如果目标值存在返回下标，否则返回 -1。

**示例：**
```
输入：nums = [-1, 0, 3, 5, 9, 12], target = 9
输出：4
解释：9 出现在 nums 中并且下标为 4
```
""",
        "template": """def search(nums, target):
    \"\"\"
    :type nums: List[int]
    :type target: int
    :rtype: int
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": "search([-1, 0, 3, 5, 9, 12], 9)", "expected": "4"},
            {"input": "search([-1, 0, 3, 5, 9, 12], 2)", "expected": "-1"},
            {"input": "search([5], 5)", "expected": "0"}
        ],
        "solution": """def search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
""",
        "hints": ["使用左右指针", "每次比较中间元素"]
    },
    
    # ========== 中等 (6-10) ==========
    "6": {
        "id": "6",
        "title": "最大子数组和",
        "difficulty": "中等",
        "tags": ["数组", "动态规划"],
        "description": """给你一个整数数组 nums，请你找出一个具有最大和的连续子数组（子数组最少包含一个元素），返回其最大和。

**示例：**
```
输入：nums = [-2,1,-3,4,-1,2,1,-5,4]
输出：6
解释：连续子数组 [4,-1,2,1] 的和最大，为 6。
```
""",
        "template": """def maxSubArray(nums):
    \"\"\"
    :type nums: List[int]
    :rtype: int
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": "maxSubArray([-2, 1, -3, 4, -1, 2, 1, -5, 4])", "expected": "6"},
            {"input": "maxSubArray([1])", "expected": "1"},
            {"input": "maxSubArray([5, 4, -1, 7, 8])", "expected": "23"}
        ],
        "solution": """def maxSubArray(nums):
    max_sum = nums[0]
    current_sum = nums[0]
    for num in nums[1:]:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    return max_sum
""",
        "hints": ["动态规划思想", "维护当前最大和和全局最大和"]
    },
    "7": {
        "id": "7",
        "title": "合并两个有序链表",
        "difficulty": "中等",
        "tags": ["链表", "递归"],
        "description": """将两个升序链表合并为一个新的升序链表并返回。

为了简化，我们用列表表示链表。

**示例：**
```
输入：list1 = [1, 2, 4], list2 = [1, 3, 4]
输出：[1, 1, 2, 3, 4, 4]
```
""",
        "template": """def mergeTwoLists(list1, list2):
    \"\"\"
    :type list1: List[int]
    :type list2: List[int]
    :rtype: List[int]
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": "mergeTwoLists([1, 2, 4], [1, 3, 4])", "expected": "[1, 1, 2, 3, 4, 4]"},
            {"input": "mergeTwoLists([], [])", "expected": "[]"},
            {"input": "mergeTwoLists([], [0])", "expected": "[0]"}
        ],
        "solution": """def mergeTwoLists(list1, list2):
    result = []
    i, j = 0, 0
    while i < len(list1) and j < len(list2):
        if list1[i] <= list2[j]:
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1
    result.extend(list1[i:])
    result.extend(list2[j:])
    return result
""",
        "hints": ["使用双指针", "比较两个指针位置的元素"]
    },
    "8": {
        "id": "8",
        "title": "买卖股票的最佳时机",
        "difficulty": "中等",
        "tags": ["数组", "动态规划"],
        "description": """给定一个数组 prices，它的第 i 个元素 prices[i] 是一支给定股票第 i 天的价格。

如果你最多只允许完成一笔交易（即买入和卖出一只股票），设计一个算法来计算你所能获取的最大利润。

**示例：**
```
输入：[7, 1, 5, 3, 6, 4]
输出：5
解释：在第 2 天（价格 = 1）买入，在第 5 天（价格 = 6）卖出，最大利润 = 6-1 = 5。
```
""",
        "template": """def maxProfit(prices):
    \"\"\"
    :type prices: List[int]
    :rtype: int
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": "maxProfit([7, 1, 5, 3, 6, 4])", "expected": "5"},
            {"input": "maxProfit([7, 6, 4, 3, 1])", "expected": "0"},
            {"input": "maxProfit([1, 2])", "expected": "1"}
        ],
        "solution": """def maxProfit(prices):
    min_price = float('inf')
    max_profit = 0
    for price in prices:
        if price < min_price:
            min_price = price
        elif price - min_price > max_profit:
            max_profit = price - min_price
    return max_profit
""",
        "hints": ["记录最低价格", "计算当前价格与最低价的差"]
    },
    "9": {
        "id": "9",
        "title": "无重复字符的最长子串",
        "difficulty": "中等",
        "tags": ["哈希表", "字符串", "滑动窗口"],
        "description": """给定一个字符串 s，请你找出其中不含有重复字符的最长子串的长度。

**示例：**
```
输入：s = "abcabcbb"
输出：3
解释：因为无重复字符的最长子串是 "abc"，所以其长度为 3。
```
""",
        "template": """def lengthOfLongestSubstring(s):
    \"\"\"
    :type s: str
    :rtype: int
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": 'lengthOfLongestSubstring("abcabcbb")', "expected": "3"},
            {"input": 'lengthOfLongestSubstring("bbbbb")', "expected": "1"},
            {"input": 'lengthOfLongestSubstring("pwwkew")', "expected": "3"}
        ],
        "solution": """def lengthOfLongestSubstring(s):
    char_set = set()
    left = 0
    max_len = 0
    for right in range(len(s)):
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        char_set.add(s[right])
        max_len = max(max_len, right - left + 1)
    return max_len
""",
        "hints": ["使用滑动窗口", "用集合记录窗口内的字符"]
    },
    "10": {
        "id": "10",
        "title": "三数之和",
        "difficulty": "中等",
        "tags": ["数组", "双指针", "排序"],
        "description": """给你一个整数数组 nums，判断是否存在三元组 [nums[i], nums[j], nums[k]] 满足 i != j、i != k 且 j != k，同时还满足 nums[i] + nums[j] + nums[k] == 0。

请你返回所有和为 0 且不重复的三元组。

**示例：**
```
输入：nums = [-1,0,1,2,-1,-4]
输出：[[-1,-1,2],[-1,0,1]]
```
""",
        "template": """def threeSum(nums):
    \"\"\"
    :type nums: List[int]
    :rtype: List[List[int]]
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": "threeSum([-1, 0, 1, 2, -1, -4])", "expected": "[[-1, -1, 2], [-1, 0, 1]]"},
            {"input": "threeSum([0, 1, 1])", "expected": "[]"},
            {"input": "threeSum([0, 0, 0])", "expected": "[[0, 0, 0]]"}
        ],
        "solution": """def threeSum(nums):
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i-1]:
            continue
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left+1]:
                    left += 1
                while left < right and nums[right] == nums[right-1]:
                    right -= 1
                left += 1
                right -= 1
    return result
""",
        "hints": ["先排序", "固定一个数，用双指针找另外两个"]
    },
    
    # ========== 困难 (11-15) ==========
    "11": {
        "id": "11",
        "title": "接雨水",
        "difficulty": "困难",
        "tags": ["栈", "数组", "双指针", "动态规划"],
        "description": """给定 n 个非负整数表示每个宽度为 1 的柱子的高度图，计算按此排列的柱子，下雨之后能接多少雨水。

**示例：**
```
输入：height = [0,1,0,2,1,0,1,3,2,1,2,1]
输出：6
解释：上面是由数组 [0,1,0,2,1,0,1,3,2,1,2,1] 表示的高度图，在这种情况下，可以接 6 个单位的雨水。
```
""",
        "template": """def trap(height):
    \"\"\"
    :type height: List[int]
    :rtype: int
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": "trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])", "expected": "6"},
            {"input": "trap([4, 2, 0, 3, 2, 5])", "expected": "9"}
        ],
        "solution": """def trap(height):
    if not height:
        return 0
    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    water = 0
    while left < right:
        if left_max < right_max:
            left += 1
            left_max = max(left_max, height[left])
            water += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            water += right_max - height[right]
    return water
""",
        "hints": ["双指针从两端向中间移动", "记录左右最大高度"]
    },
    "12": {
        "id": "12",
        "title": "最长回文子串",
        "difficulty": "困难",
        "tags": ["字符串", "动态规划"],
        "description": """给你一个字符串 s，找到 s 中最长的回文子串。

**示例：**
```
输入：s = "babad"
输出："bab"
解释："aba" 同样是符合题意的答案。
```
""",
        "template": """def longestPalindrome(s):
    \"\"\"
    :type s: str
    :rtype: str
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": 'longestPalindrome("babad")', "expected": '"bab"'},
            {"input": 'longestPalindrome("cbbd")', "expected": '"bb"'},
            {"input": 'longestPalindrome("a")', "expected": '"a"'}
        ],
        "solution": """def longestPalindrome(s):
    if len(s) < 2:
        return s
    start, max_len = 0, 1
    for i in range(len(s)):
        # 奇数长度
        left, right = i - 1, i + 1
        while left >= 0 and right < len(s) and s[left] == s[right]:
            if right - left + 1 > max_len:
                start = left
                max_len = right - left + 1
            left -= 1
            right += 1
        # 偶数长度
        left, right = i - 1, i
        while left >= 0 and right < len(s) and s[left] == s[right]:
            if right - left + 1 > max_len:
                start = left
                max_len = right - left + 1
            left -= 1
            right += 1
    return s[start:start + max_len]
""",
        "hints": ["中心扩展法", "从每个位置向两边扩展"]
    },
    "13": {
        "id": "13",
        "title": "编辑距离",
        "difficulty": "困难",
        "tags": ["字符串", "动态规划"],
        "description": """给你两个单词 word1 和 word2，请返回将 word1 转换成 word2 所使用的最少操作数。

你可以对一个单词进行如下三种操作：
- 插入一个字符
- 删除一个字符
- 替换一个字符

**示例：**
```
输入：word1 = "horse", word2 = "ros"
输出：3
解释：
horse -> rorse (将 'h' 替换为 'r')
rorse -> rose (删除 'r')
rose -> ros (删除 'e')
```
""",
        "template": """def minDistance(word1, word2):
    \"\"\"
    :type word1: str
    :type word2: str
    :rtype: int
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": 'minDistance("horse", "ros")', "expected": "3"},
            {"input": 'minDistance("intention", "execution")', "expected": "5"}
        ],
        "solution": """def minDistance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
    return dp[m][n]
""",
        "hints": ["二维动态规划", "dp[i][j]表示word1前i个字符到word2前j个字符的最小编辑距离"]
    },
    "14": {
        "id": "14",
        "title": "合并K个升序链表",
        "difficulty": "困难",
        "tags": ["链表", "分治", "堆"],
        "description": """给你一个链表数组，每个链表都已经按升序排列。

请你将所有链表合并到一个升序链表中，返回合并后的链表。

为了简化，我们用列表表示链表。

**示例：**
```
输入：lists = [[1,4,5],[1,3,4],[2,6]]
输出：[1,1,2,3,4,4,5,6]
```
""",
        "template": """def mergeKLists(lists):
    \"\"\"
    :type lists: List[List[int]]
    :rtype: List[int]
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": "mergeKLists([[1, 4, 5], [1, 3, 4], [2, 6]])", "expected": "[1, 1, 2, 3, 4, 4, 5, 6]"},
            {"input": "mergeKLists([])", "expected": "[]"},
            {"input": "mergeKLists([[]])", "expected": "[]"}
        ],
        "solution": """import heapq
def mergeKLists(lists):
    result = []
    heap = []
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))
    while heap:
        val, list_idx, elem_idx = heapq.heappop(heap)
        result.append(val)
        if elem_idx + 1 < len(lists[list_idx]):
            heapq.heappush(heap, (lists[list_idx][elem_idx + 1], list_idx, elem_idx + 1))
    return result
""",
        "hints": ["使用最小堆", "每次取出最小的元素"]
    },
    "15": {
        "id": "15",
        "title": "最长有效括号",
        "difficulty": "困难",
        "tags": ["栈", "字符串", "动态规划"],
        "description": """给你一个只包含 '(' 和 ')' 的字符串，找出最长有效（格式正确且连续）括号子串的长度。

**示例：**
```
输入：s = "(()"
输出：2
解释：最长有效括号子串是 "()"

输入：s = ")()())"
输出：4
解释：最长有效括号子串是 "()()"
```
""",
        "template": """def longestValidParentheses(s):
    \"\"\"
    :type s: str
    :rtype: int
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": 'longestValidParentheses("(()")', "expected": "2"},
            {"input": 'longestValidParentheses(")()())")', "expected": "4"},
            {"input": 'longestValidParentheses("")', "expected": "0"}
        ],
        "solution": """def longestValidParentheses(s):
    stack = [-1]
    max_len = 0
    for i, char in enumerate(s):
        if char == '(':
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)
            else:
                max_len = max(max_len, i - stack[-1])
    return max_len
""",
        "hints": ["使用栈记录索引", "栈底元素为最后一个未匹配的右括号索引"]
    },
    
    # ========== 非常困难 (16-20) ==========
    "16": {
        "id": "16",
        "title": "正则表达式匹配",
        "difficulty": "非常困难",
        "tags": ["递归", "字符串", "动态规划"],
        "description": """给你一个字符串 s 和一个字符规律 p，请你来实现一个支持 '.' 和 '*' 的正则表达式匹配。

- '.' 匹配任意单个字符
- '*' 匹配零个或多个前面的那一个元素

**示例：**
```
输入：s = "aa", p = "a*"
输出：True
解释：因为 '*' 代表可以匹配零个或多个前面的那一个元素, 在这里前面的元素就是 'a'。因此，字符串 "aa" 可被视为 "a" 重复了两次。
```
""",
        "template": """def isMatch(s, p):
    \"\"\"
    :type s: str
    :type p: str
    :rtype: bool
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": 'isMatch("aa", "a")', "expected": "False"},
            {"input": 'isMatch("aa", "a*")', "expected": "True"},
            {"input": 'isMatch("ab", ".*")', "expected": "True"}
        ],
        "solution": """def isMatch(s, p):
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(2, n + 1):
        if p[j-1] == '*':
            dp[0][j] = dp[0][j-2]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j-1] == '*':
                dp[i][j] = dp[i][j-2] or (dp[i-1][j] and (s[i-1] == p[j-2] or p[j-2] == '.'))
            else:
                dp[i][j] = dp[i-1][j-1] and (s[i-1] == p[j-1] or p[j-1] == '.')
    return dp[m][n]
""",
        "hints": ["动态规划", "dp[i][j]表示s前i个字符和p前j个字符是否匹配"]
    },
    "17": {
        "id": "17",
        "title": "N皇后",
        "difficulty": "非常困难",
        "tags": ["数组", "回溯"],
        "description": """按照国际象棋的规则，皇后可以攻击与之处在同一行或同一列或同一斜线上的棋子。

n 皇后问题研究的是如何将 n 个皇后放置在 n×n 的棋盘上，并且使皇后彼此之间不能相互攻击。

给你一个整数 n，返回所有不同的 n 皇后问题的解决方案。

**示例：**
```
输入：n = 4
输出：[[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]
解释：4 皇后问题存在两个不同的解法。
```
""",
        "template": """def solveNQueens(n):
    \"\"\"
    :type n: int
    :rtype: List[List[str]]
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": "solveNQueens(4)", "expected": '[[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]'},
            {"input": "solveNQueens(1)", "expected": '[["Q"]]'}
        ],
        "solution": """def solveNQueens(n):
    def backtrack(row):
        if row == n:
            result.append([''.join(board[i]) for i in range(n)])
            return
        for col in range(n):
            if col in cols or row - col in diag1 or row + col in diag2:
                continue
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)
            board[row][col] = 'Q'
            backtrack(row + 1)
            board[row][col] = '.'
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)
    
    result = []
    board = [['.'] * n for _ in range(n)]
    cols, diag1, diag2 = set(), set(), set()
    backtrack(0)
    return result
""",
        "hints": ["回溯算法", "用集合记录列、对角线的占用情况"]
    },
    "18": {
        "id": "18",
        "title": "最小覆盖子串",
        "difficulty": "非常困难",
        "tags": ["哈希表", "字符串", "滑动窗口"],
        "description": """给你一个字符串 s、一个字符串 t。返回 s 中涵盖 t 所有字符的最小子串。如果 s 中不存在涵盖 t 所有字符的子串，则返回空字符串。

**示例：**
```
输入：s = "ADOBECODEBANC", t = "ABC"
输出："BANC"
解释：最小覆盖子串 "BANC" 包含来自字符串 t 的 'A'、'B' 和 'C'。
```
""",
        "template": """def minWindow(s, t):
    \"\"\"
    :type s: str
    :type t: str
    :rtype: str
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": 'minWindow("ADOBECODEBANC", "ABC")', "expected": '"BANC"'},
            {"input": 'minWindow("a", "a")', "expected": '"a"'},
            {"input": 'minWindow("a", "aa")', "expected": '""'}
        ],
        "solution": """from collections import Counter
def minWindow(s, t):
    if not s or not t:
        return ""
    dict_t = Counter(t)
    required = len(dict_t)
    l, r = 0, 0
    formed = 0
    window_counts = {}
    ans = float('inf'), None, None
    while r < len(s):
        character = s[r]
        window_counts[character] = window_counts.get(character, 0) + 1
        if character in dict_t and window_counts[character] == dict_t[character]:
            formed += 1
        while l <= r and formed == required:
            character = s[l]
            if r - l + 1 < ans[0]:
                ans = (r - l + 1, l, r)
            window_counts[character] -= 1
            if character in dict_t and window_counts[character] < dict_t[character]:
                formed -= 1
            l += 1
        r += 1
    return "" if ans[0] == float('inf') else s[ans[1]:ans[2]+1]
""",
        "hints": ["滑动窗口", "用字典记录字符出现次数"]
    },
    "19": {
        "id": "19",
        "title": "单词拆分 II",
        "difficulty": "非常困难",
        "tags": ["字典树", "记忆化搜索", "哈希表", "字符串", "动态规划", "回溯"],
        "description": """给定一个字符串 s 和一个字符串字典 wordDict，在字符串 s 中增加空格来构建一个句子，使得句子中所有的单词都在字典中。以任意顺序返回所有这些可能的句子。

**示例：**
```
输入：s = "catsanddog", wordDict = ["cat","cats","and","sand","dog"]
输出：["cats and dog","cat sand dog"]
```
""",
        "template": """def wordBreak(s, wordDict):
    \"\"\"
    :type s: str
    :type wordDict: List[str]
    :rtype: List[str]
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": 'wordBreak("catsanddog", ["cat","cats","and","sand","dog"])', "expected": '["cats and dog","cat sand dog"]'},
            {"input": 'wordBreak("pineapplepenapple", ["apple","pen","applepen","pine","pineapple"])', "expected": '["pine apple pen apple","pineapple pen apple","pine applepen apple"]'}
        ],
        "solution": """def wordBreak(s, wordDict):
    word_set = set(wordDict)
    memo = {}
    def backtrack(start):
        if start in memo:
            return memo[start]
        if start == len(s):
            return [""]
        res = []
        for end in range(start + 1, len(s) + 1):
            word = s[start:end]
            if word in word_set:
                for sentence in backtrack(end):
                    if sentence:
                        res.append(word + " " + sentence)
                    else:
                        res.append(word)
        memo[start] = res
        return res
    return backtrack(0)
""",
        "hints": ["记忆化搜索", "回溯生成所有可能的句子"]
    },

    "21": {
        "id": "21",
        "title": "有序数组查找",
        "difficulty": "简单",
        "tags": ["\u6570\u7ec4", "\u4e8c\u5206\u67e5\u627e"],
        "description": '给定一个已排序的整数数组 nums 和目标值 target，返回目标值的索引。如果不存在，返回 -1。要求时间复杂度 O(log n)。',
        "template": 'def binary_search(nums, target):\n    pass',
        "test_cases": [{"input": "[1, 3, 5, 7, 9], 5", "expected": "2"}, {"input": "[1, 3, 5, 7, 9], 6", "expected": "-1"}, {"input": "[-1, 0, 3, 5, 9, 12], 9", "expected": "4"}]
    },

    "22": {
        "id": "22",
        "title": "旋转数组找最小值",
        "difficulty": "中等",
        "tags": ["\u6570\u7ec4", "\u4e8c\u5206\u67e5\u627e"],
        "description": '一个升序数组在某点被旋转了，例如 [0,1,2,4,5,6,7] 变成 [4,5,6,7,0,1,2]。找出旋转后数组中的最小元素。要求 O(log n)。',
        "template": 'def find_min(nums):\n    pass',
        "test_cases": [{"input": "[4, 5, 6, 7, 0, 1, 2]", "expected": "0"}, {"input": "[3, 4, 5, 1, 2]", "expected": "1"}, {"input": "[1]", "expected": "1"}]
    },

    "23": {
        "id": "23",
        "title": "旋转数组查找",
        "difficulty": "中等",
        "tags": ["\u6570\u7ec4", "\u4e8c\u5206\u67e5\u627e"],
        "description": '一个升序数组被旋转后，在其中查找目标值，返回索引，找不到返回 -1。要求 O(log n)。',
        "template": 'def search_rotated(nums, target):\n    pass',
        "test_cases": [{"input": "[4,5,6,7,0,1,2], 0", "expected": "4"}, {"input": "[4,5,6,7,0,1,2], 3", "expected": "-1"}, {"input": "[1], 1", "expected": "0"}]
    },

    "24": {
        "id": "24",
        "title": "山脉数组峰值",
        "difficulty": "中等",
        "tags": ["\u6570\u7ec4", "\u4e8c\u5206\u67e5\u627e"],
        "description": '山脉数组：先严格递增，后严格递减。给定山脉数组，返回峰值索引。要求 O(log n)。',
        "template": 'def peak_index(arr):\n    pass',
        "test_cases": [{"input": "[1, 3, 5, 4, 2]", "expected": "2"}, {"input": "[0, 2, 1, 0]", "expected": "1"}, {"input": "[0, 1, 0]", "expected": "1"}]
    },

    "25": {
        "id": "25",
        "title": "查找第一个错误版本",
        "difficulty": "简单",
        "tags": ["\u4e8c\u5206\u67e5\u627e"],
        "description": '产品从某个版本开始有 bug。给定版本总数 n 和函数 isBadVersion(version)，找出第一个出 bug 的版本。',
        "template": 'def first_bad_version(n):\n    # 假设 isBadVersion(i) 可用\n    pass',
        "test_cases": [{"input": "5", "expected": "4"}, {"input": "1", "expected": "1"}]
    },

    "26": {
        "id": "26",
        "title": "查找插入位置",
        "difficulty": "简单",
        "tags": ["\u6570\u7ec4", "\u4e8c\u5206\u67e5\u627e"],
        "description": '给定已排序的不重复整数数组和目标值，如果找到返回索引，否则返回应该插入的位置。要求 O(log n)。',
        "template": 'def search_insert(nums, target):\n    pass',
        "test_cases": [{"input": "[1,3,5,6], 5", "expected": "2"}, {"input": "[1,3,5,6], 2", "expected": "1"}, {"input": "[1,3,5,6], 7", "expected": "4"}]
    },

    "27": {
        "id": "27",
        "title": "整数平方根",
        "difficulty": "简单",
        "tags": ["\u6570\u5b66", "\u4e8c\u5206\u67e5\u627e"],
        "description": '给定非负整数 x，返回 x 的平方根的整数部分（向下取整）。不能使用内置 sqrt 函数。',
        "template": 'def my_sqrt(x):\n    pass',
        "test_cases": [{"input": "4", "expected": "2"}, {"input": "8", "expected": "2"}, {"input": "9", "expected": "3"}]
    },

    "28": {
        "id": "28",
        "title": "判断完全平方数",
        "difficulty": "简单",
        "tags": ["\u6570\u5b66", "\u4e8c\u5206\u67e5\u627e"],
        "description": '给定正整数 num，判断它是否是完全平方数。不能使用内置 sqrt 函数。',
        "template": 'def is_perfect_square(num):\n    pass',
        "test_cases": [{"input": "16", "expected": "True"}, {"input": "14", "expected": "False"}, {"input": "1", "expected": "True"}]
    },

    "29": {
        "id": "29",
        "title": "猜数字游戏",
        "difficulty": "简单",
        "tags": ["\u4e8c\u5206\u67e5\u627e"],
        "description": '在 1 到 n 之间猜一个数字，每次猜测会返回 -1(大了)、1(小了)或 0(对了)。给定 n 和 guess 函数，找出答案。',
        "template": 'def guess_number(n):\n    # 假设 guess(num) 可用\n    pass',
        "test_cases": [{"input": "10", "expected": "6"}, {"input": "1", "expected": "1"}]
    },

    "30": {
        "id": "30",
        "title": "二维矩阵查找",
        "difficulty": "中等",
        "tags": ["\u6570\u7ec4", "\u4e8c\u5206\u67e5\u627e", "\u77e9\u9635"],
        "description": '给定 m×n 矩阵，每行递增，每行第一个数大于上一行最后一个数。判断目标值是否在矩阵中。',
        "template": 'def search_matrix(matrix, target):\n    pass',
        "test_cases": [{"input": "[[1,3,5,7],[10,11,16,20],[23,30,34,50]], 3", "expected": "True"}, {"input": "[[1,3,5,7],[10,11,16,20],[23,30,34,50]], 13", "expected": "False"}]
    },

    "31": {
        "id": "31",
        "title": "两数之和",
        "difficulty": "简单",
        "tags": ["\u6570\u7ec4", "\u54c8\u5e0c\u8868"],
        "description": '给定整数数组和目标值，找出数组中和为目标值的两个数的索引。假设只有一个答案。',
        "template": 'def two_sum(nums, target):\n    pass',
        "test_cases": [{"input": "[2, 7, 11, 15], 9", "expected": "[0, 1]"}, {"input": "[3, 2, 4], 6", "expected": "[1, 2]"}, {"input": "[3, 3], 6", "expected": "[0, 1]"}]
    },

    "32": {
        "id": "32",
        "title": "有序数组两数之和",
        "difficulty": "中等",
        "tags": ["\u6570\u7ec4", "\u53cc\u6307\u9488"],
        "description": '给定已排序的整数数组和目标值，找出两个数使其和等于目标值。返回索引（从1开始）。',
        "template": 'def two_sum_sorted(numbers, target):\n    pass',
        "test_cases": [{"input": "[2, 7, 11, 15], 9", "expected": "[1, 2]"}, {"input": "[2, 3, 4], 6", "expected": "[1, 3]"}]
    },

    "33": {
        "id": "33",
        "title": "三数之和",
        "difficulty": "中等",
        "tags": ["\u6570\u7ec4", "\u53cc\u6307\u9488"],
        "description": '给定整数数组，找出所有和为 0 的三元组。结果中不能有重复。',
        "template": 'def three_sum(nums):\n    pass',
        "test_cases": [{"input": "[-1, 0, 1, 2, -1, -4]", "expected": "[[-1, -1, 2], [-1, 0, 1]]"}, {"input": "[0, 0, 0]", "expected": "[[0, 0, 0]]"}]
    },

    "34": {
        "id": "34",
        "title": "盛最多水的容器",
        "difficulty": "中等",
        "tags": ["\u6570\u7ec4", "\u53cc\u6307\u9488"],
        "description": '给定柱子高度数组，找出两个柱子使其与 x 轴构成的容器能盛最多水。',
        "template": 'def max_area(height):\n    pass',
        "test_cases": [{"input": "[1, 8, 6, 2, 5, 4, 8, 3, 7]", "expected": "49"}, {"input": "[1, 1]", "expected": "1"}]
    },

    "35": {
        "id": "35",
        "title": "验证回文串",
        "difficulty": "简单",
        "tags": ["\u5b57\u7b26\u4e32", "\u53cc\u6307\u9488"],
        "description": '判断字符串是否是回文串，忽略大小写和非字母数字字符。',
        "template": 'def is_palindrome(s):\n    pass',
        "test_cases": [{"input": "\"A man, a plan, a canal: Panama\"", "expected": "True"}, {"input": "\"race a car\"", "expected": "False"}]
    },

    "36": {
        "id": "36",
        "title": "移动零",
        "difficulty": "简单",
        "tags": ["\u6570\u7ec4", "\u53cc\u6307\u9488"],
        "description": '将数组中的所有 0 移到末尾，保持非零元素的相对顺序。原地操作。',
        "template": 'def move_zeroes(nums):\n    pass',
        "test_cases": [{"input": "[0, 1, 0, 3, 12]", "expected": "[1, 3, 12, 0, 0]"}, {"input": "[0]", "expected": "[0]"}]
    },

    "37": {
        "id": "37",
        "title": "删除有序数组重复项",
        "difficulty": "简单",
        "tags": ["\u6570\u7ec4", "\u53cc\u6307\u9488"],
        "description": '给定有序数组，原地删除重复元素，使每个元素只出现一次。返回新长度。',
        "template": 'def remove_duplicates(nums):\n    pass',
        "test_cases": [{"input": "[1, 1, 2]", "expected": "2"}, {"input": "[0, 0, 1, 1, 1, 2, 2, 3, 3, 4]", "expected": "5"}]
    },

    "38": {
        "id": "38",
        "title": "移除元素",
        "difficulty": "简单",
        "tags": ["\u6570\u7ec4", "\u53cc\u6307\u9488"],
        "description": '原地移除数组中所有等于 val 的元素。返回新长度。',
        "template": 'def remove_element(nums, val):\n    pass',
        "test_cases": [{"input": "[3, 2, 2, 3], 3", "expected": "2"}, {"input": "[0, 1, 2, 2, 3, 0, 4, 2], 2", "expected": "5"}]
    },

    "39": {
        "id": "39",
        "title": "颜色分类",
        "difficulty": "中等",
        "tags": ["\u6570\u7ec4", "\u6392\u5e8f"],
        "description": '给定包含 0、1、2 的数组，原地排序。要求一趟扫描。',
        "template": 'def sort_colors(nums):\n    pass',
        "test_cases": [{"input": "[2, 0, 2, 1, 1, 0]", "expected": "[0, 0, 1, 1, 2, 2]"}, {"input": "[2, 0, 1]", "expected": "[0, 1, 2]"}]
    },

    "40": {
        "id": "40",
        "title": "反转字符串",
        "difficulty": "简单",
        "tags": ["\u5b57\u7b26\u4e32", "\u53cc\u6307\u9488"],
        "description": '原地反转字符数组。',
        "template": 'def reverse_string(s):\n    pass',
        "test_cases": [{"input": "[\"h\", \"e\", \"l\", \"l\", \"o\"]", "expected": "[\"o\", \"l\", \"l\", \"e\", \"h\"]"}]
    },

    "41": {
        "id": "41",
        "title": "无重复字符最长子串",
        "difficulty": "中等",
        "tags": ["\u5b57\u7b26\u4e32", "\u6ed1\u52a8\u7a97\u53e3"],
        "description": '给定字符串，找出不含重复字符的最长子串的长度。',
        "template": 'def length_of_longest_substring(s):\n    pass',
        "test_cases": [{"input": "\"abcabcbb\"", "expected": "3"}, {"input": "\"bbbbb\"", "expected": "1"}, {"input": "\"pwwkew\"", "expected": "3"}]
    },

    "42": {
        "id": "42",
        "title": "长度最小子数组",
        "difficulty": "中等",
        "tags": ["\u6570\u7ec4", "\u6ed1\u52a8\u7a97\u53e3"],
        "description": '给定正整数数组和目标值，找出和≥目标值的最短连续子数组长度。不存在返回0。',
        "template": 'def min_subarray_len(target, nums):\n    pass',
        "test_cases": [{"input": "7, [2, 3, 1, 2, 4, 3]", "expected": "2"}, {"input": "4, [1, 4, 4]", "expected": "1"}, {"input": "11, [1, 1, 1, 1, 1, 1, 1, 1]", "expected": "0"}]
    },

    "43": {
        "id": "43",
        "title": "找到字符串中所有字母异位词",
        "difficulty": "中等",
        "tags": ["\u5b57\u7b26\u4e32", "\u6ed1\u52a8\u7a97\u53e3"],
        "description": '给定字符串 s 和 p，找出 s 中所有 p 的字母异位词（排列相同）的起始索引。',
        "template": 'def find_anagrams(s, p):\n    pass',
        "test_cases": [{"input": "\"cbaebabacd\", \"abc\"", "expected": "[0, 6]"}, {"input": "\"abab\", \"ab\"", "expected": "[0, 1, 2]"}]
    },

    "44": {
        "id": "44",
        "title": "字符串排列",
        "difficulty": "中等",
        "tags": ["\u5b57\u7b26\u4e32", "\u6ed1\u52a8\u7a97\u53e3"],
        "description": '判断 s2 是否包含 s1 的某个排列。',
        "template": 'def check_inclusion(s1, s2):\n    pass',
        "test_cases": [{"input": "\"ab\", \"eidbaooo\"", "expected": "True"}, {"input": "\"ab\", \"eidboaoo\"", "expected": "False"}]
    },

    "45": {
        "id": "45",
        "title": "最大平均子数组",
        "difficulty": "简单",
        "tags": ["\u6570\u7ec4", "\u6ed1\u52a8\u7a97\u53e3"],
        "description": '给定整数数组和整数 k，找出长度为 k 的连续子数组的最大平均值。',
        "template": 'def find_max_average(nums, k):\n    pass',
        "test_cases": [{"input": "[1, 12, -5, -6, 50, 3], 4", "expected": "12.75"}, {"input": "[5], 1", "expected": "5.0"}]
    },

    "46": {
        "id": "46",
        "title": "岛屿数量",
        "difficulty": "中等",
        "tags": ["\u56fe", "DFS", "BFS"],
        "description": "给定二维网格，'1'表示陆地，'0'表示水，计算岛屿数量。",
        "template": 'def num_islands(grid):\n    pass',
        "test_cases": [{"input": "[[\"1\",\"1\",\"1\",\"1\",\"0\"],[\"1\",\"1\",\"0\",\"1\",\"0\"],[\"1\",\"1\",\"0\",\"0\",\"0\"],[\"0\",\"0\",\"0\",\"0\",\"0\"]]", "expected": "1"}, {"input": "[[\"1\",\"1\",\"0\",\"0\",\"0\"],[\"1\",\"1\",\"0\",\"0\",\"0\"],[\"0\",\"0\",\"1\",\"0\",\"0\"],[\"0\",\"0\",\"0\",\"1\",\"1\"]]", "expected": "3"}]
    },

    "47": {
        "id": "47",
        "title": "岛屿最大面积",
        "difficulty": "中等",
        "tags": ["\u56fe", "DFS", "BFS"],
        "description": '给定二维网格，计算最大岛屿的面积。',
        "template": 'def max_area_of_island(grid):\n    pass',
        "test_cases": [{"input": "[[0,0,1,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,1,1,1,0,0,0],[0,1,1,0,1,0,0,0,0,0,0,0,0],[0,1,0,0,1,1,0,0,1,0,1,0,0],[0,1,0,0,1,1,0,0,1,1,1,0,0],[0,0,0,0,0,0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,1,1,1,0,0,0],[0,0,0,0,0,0,0,1,1,0,0,0,0]]", "expected": "6"}]
    },

    "48": {
        "id": "48",
        "title": "单词搜索",
        "difficulty": "中等",
        "tags": ["\u56fe", "DFS", "\u56de\u6eaf"],
        "description": '给定二维字符网格和单词，判断单词是否存在于网格中。单词由相邻单元格组成。',
        "template": 'def exist(board, word):\n    pass',
        "test_cases": [{"input": "[[\"A\",\"B\",\"C\",\"E\"],[\"S\",\"F\",\"C\",\"S\"],[\"A\",\"D\",\"E\",\"E\"]], \"ABCCED\"", "expected": "True"}, {"input": "[[\"A\",\"B\",\"C\",\"E\"],[\"S\",\"F\",\"C\",\"S\"],[\"A\",\"D\",\"E\",\"E\"]], \"SEE\"", "expected": "True"}, {"input": "[[\"A\",\"B\",\"C\",\"E\"],[\"S\",\"F\",\"C\",\"S\"],[\"A\",\"D\",\"E\",\"E\"]], \"ABCB\"", "expected": "False"}]
    },

    "49": {
        "id": "49",
        "title": "图像渲染",
        "difficulty": "简单",
        "tags": ["\u56fe", "DFS", "BFS"],
        "description": '给定图像和起始点，将与起始点相连的相同颜色区域染成新颜色。',
        "template": 'def flood_fill(image, sr, sc, color):\n    pass',
        "test_cases": [{"input": "[[1,1,1],[1,1,0],[1,0,1]], 1, 1, 2", "expected": "[[2,2,2],[2,2,0],[2,0,1]]"}]
    },

    "50": {
        "id": "50",
        "title": "克隆图",
        "difficulty": "中等",
        "tags": ["\u56fe", "DFS", "BFS"],
        "description": '给定无向连通图的节点，返回图的深拷贝。',
        "template": 'def clone_graph(node):\n    pass',
        "test_cases": [{"input": "Node(1)", "expected": "clone"}]
    },

    "51": {
        "id": "51",
        "title": "课程安排",
        "difficulty": "中等",
        "tags": ["\u56fe", "DFS", "\u62d3\u6251\u6392\u5e8f"],
        "description": '给定课程数和先修要求，判断能否完成所有课程。',
        "template": 'def can_finish(num_courses, prerequisites):\n    pass',
        "test_cases": [{"input": "2, [[1,0]]", "expected": "True"}, {"input": "2, [[1,0],[0,1]]", "expected": "False"}]
    },

    "52": {
        "id": "52",
        "title": "二叉树层序遍历",
        "difficulty": "中等",
        "tags": ["\u6811", "BFS"],
        "description": '给定二叉树，返回层序遍历结果（按层分组）。',
        "template": 'def level_order(root):\n    pass',
        "test_cases": [{"input": "[3,9,20,null,null,15,7]", "expected": "[[3],[9,20],[15,7]]"}]
    },

    "53": {
        "id": "53",
        "title": "二叉树最大深度",
        "difficulty": "简单",
        "tags": ["\u6811", "DFS"],
        "description": '给定二叉树，返回其最大深度。',
        "template": 'def max_depth(root):\n    pass',
        "test_cases": [{"input": "[3,9,20,null,null,15,7]", "expected": "3"}, {"input": "[1]", "expected": "1"}]
    },

    "54": {
        "id": "54",
        "title": "对称二叉树",
        "difficulty": "简单",
        "tags": ["\u6811", "DFS"],
        "description": '判断二叉树是否左右对称。',
        "template": 'def is_symmetric(root):\n    pass',
        "test_cases": [{"input": "[1,2,2,3,4,4,3]", "expected": "True"}, {"input": "[1,2,2,null,3,null,3]", "expected": "False"}]
    },

    "55": {
        "id": "55",
        "title": "翻转二叉树",
        "difficulty": "简单",
        "tags": ["\u6811", "DFS"],
        "description": '翻转二叉树（交换每个节点的左右子树）。',
        "template": 'def invert_tree(root):\n    pass',
        "test_cases": [{"input": "[4,2,7,1,3,6,9]", "expected": "[4,7,2,9,6,3,1]"}]
    },

    "56": {
        "id": "56",
        "title": "爬楼梯",
        "difficulty": "简单",
        "tags": ["\u52a8\u6001\u89c4\u5212"],
        "description": '每次可以爬 1 或 2 个台阶，问爬到第 n 阶有多少种方法。',
        "template": 'def climb_stairs(n):\n    pass',
        "test_cases": [{"input": "2", "expected": "2"}, {"input": "3", "expected": "3"}, {"input": "5", "expected": "8"}]
    },

    "57": {
        "id": "57",
        "title": "打家劫舍",
        "difficulty": "中等",
        "tags": ["\u52a8\u6001\u89c4\u5212"],
        "description": '给定数组表示每间房屋的金额，相邻房屋不能同时被盗，求最大金额。',
        "template": 'def rob(nums):\n    pass',
        "test_cases": [{"input": "[1, 2, 3, 1]", "expected": "4"}, {"input": "[2, 7, 9, 3, 1]", "expected": "12"}]
    },

    "58": {
        "id": "58",
        "title": "不同路径",
        "difficulty": "中等",
        "tags": ["\u52a8\u6001\u89c4\u5212"],
        "description": '机器人从 m×n 网格左上角走到右下角，只能向右或向下，问有多少种路径。',
        "template": 'def unique_paths(m, n):\n    pass',
        "test_cases": [{"input": "3, 7", "expected": "28"}, {"input": "3, 2", "expected": "3"}]
    },

    "59": {
        "id": "59",
        "title": "零钱兑换",
        "difficulty": "中等",
        "tags": ["\u52a8\u6001\u89c4\u5212"],
        "description": '给定硬币面额和目标金额，计算凑成目标金额的最少硬币数。',
        "template": 'def coin_change(coins, amount):\n    pass',
        "test_cases": [{"input": "[1, 2, 5], 11", "expected": "3"}, {"input": "[2], 3", "expected": "-1"}]
    },

    "60": {
        "id": "60",
        "title": "最长递增子序列",
        "difficulty": "中等",
        "tags": ["\u52a8\u6001\u89c4\u5212"],
        "description": '给定数组，找出最长严格递增子序列的长度。',
        "template": 'def length_of_lis(nums):\n    pass',
        "test_cases": [{"input": "[10, 9, 2, 5, 3, 7, 101, 18]", "expected": "4"}, {"input": "[0, 1, 0, 3, 2, 3]", "expected": "4"}]
    },

    "61": {
        "id": "61",
        "title": "最大子数组和",
        "difficulty": "中等",
        "tags": ["\u52a8\u6001\u89c4\u5212"],
        "description": '给定整数数组，找出具有最大和的连续子数组。',
        "template": 'def max_sub_array(nums):\n    pass',
        "test_cases": [{"input": "[-2, 1, -3, 4, -1, 2, 1, -5, 4]", "expected": "6"}, {"input": "[1]", "expected": "1"}]
    },

    "62": {
        "id": "62",
        "title": "买卖股票最佳时机",
        "difficulty": "简单",
        "tags": ["\u52a8\u6001\u89c4\u5212"],
        "description": '给定股价数组，选择某天买入和某天卖出，计算最大利润。',
        "template": 'def max_profit(prices):\n    pass',
        "test_cases": [{"input": "[7, 1, 5, 3, 6, 4]", "expected": "5"}, {"input": "[7, 6, 4, 3, 1]", "expected": "0"}]
    },

    "63": {
        "id": "63",
        "title": "三角形最小路径和",
        "difficulty": "中等",
        "tags": ["\u52a8\u6001\u89c4\u5212"],
        "description": '给定三角形，从顶到底找最小路径和，每步只能移到下一行相邻位置。',
        "template": 'def minimum_total(triangle):\n    pass',
        "test_cases": [{"input": "[[2],[3,4],[6,5,7],[4,1,8,3]]", "expected": "11"}]
    },

    "64": {
        "id": "64",
        "title": "最小花费爬楼梯",
        "difficulty": "简单",
        "tags": ["\u52a8\u6001\u89c4\u5212"],
        "description": '给定数组表示爬每阶的花费，可从下标 0 或 1 开始，求到达顶部的最小花费。',
        "template": 'def min_cost_climbing_stairs(cost):\n    pass',
        "test_cases": [{"input": "[10, 15, 20]", "expected": "15"}, {"input": "[1, 100, 1, 1, 1, 100, 1, 1, 100, 1]", "expected": "6"}]
    },

    "65": {
        "id": "65",
        "title": "分割等和子集",
        "difficulty": "中等",
        "tags": ["\u52a8\u6001\u89c4\u5212"],
        "description": '给定数组，判断能否分成两个和相等的子集。',
        "template": 'def can_partition(nums):\n    pass',
        "test_cases": [{"input": "[1, 5, 11, 5]", "expected": "True"}, {"input": "[1, 2, 3, 5]", "expected": "False"}]
    },

    "66": {
        "id": "66",
        "title": "有效括号",
        "difficulty": "简单",
        "tags": ["\u6808", "\u5b57\u7b26\u4e32"],
        "description": '给定只含括号的字符串，判断括号是否有效配对。',
        "template": 'def is_valid(s):\n    pass',
        "test_cases": [{"input": "\"()\"", "expected": "True"}, {"input": "\"()[]{}\"", "expected": "True"}, {"input": "\"(]\"", "expected": "False"}, {"input": "\"([)]\"", "expected": "False"}]
    },

    "67": {
        "id": "67",
        "title": "最小栈",
        "difficulty": "中等",
        "tags": ["\u6808", "\u8bbe\u8ba1"],
        "description": '设计一个支持 push、pop、top 和在 O(1) 时间内获取最小元素的栈。',
        "template": 'class MinStack:\n    def __init__(self):\n        pass\n    def push(self, val):\n        pass\n    def pop(self):\n        pass\n    def top(self):\n        pass\n    def getMin(self):\n        pass',
        "test_cases": [{"input": "push(-2), push(0), push(-3), getMin()", "expected": "-3"}]
    },

    "68": {
        "id": "68",
        "title": "逆波兰表达式求值",
        "difficulty": "中等",
        "tags": ["\u6808"],
        "description": '给定逆波兰表达式（后缀表达式），求其值。',
        "template": 'def eval_rpn(tokens):\n    pass',
        "test_cases": [{"input": "[\"2\",\"1\",\"+\",\"3\",\"*\"]", "expected": "9"}, {"input": "[\"4\",\"13\",\"5\",\"/\",\"+\"]", "expected": "6"}]
    },

    "69": {
        "id": "69",
        "title": "每日温度",
        "difficulty": "中等",
        "tags": ["\u6808", "\u6570\u7ec4"],
        "description": '给定每日温度数组，返回数组 answer，answer[i] 表示要等几天才能有更高温度。',
        "template": 'def daily_temperatures(temperatures):\n    pass',
        "test_cases": [{"input": "[73, 74, 75, 71, 69, 72, 76, 73]", "expected": "[1, 1, 4, 2, 1, 1, 0, 0]"}, {"input": "[30, 40, 50, 60]", "expected": "[1, 1, 1, 0]"}]
    },

    "70": {
        "id": "70",
        "title": "车队",
        "difficulty": "中等",
        "tags": ["\u6808", "\u6392\u5e8f"],
        "description": 'N 辆车沿单行道行驶，给定位置和速度，后车追上前车会合并成车队。求到达目标时的车队数量。',
        "template": 'def car_fleet(target, position, speed):\n    pass',
        "test_cases": [{"input": "12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3]", "expected": "3"}]
    },
}
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
