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
    "20": {
        "id": "20",
        "title": "滑动窗口最大值",
        "difficulty": "非常困难",
        "tags": ["队列", "数组", "滑动窗口", "单调队列", "堆"],
        "description": """给你一个整数数组 nums，有一个大小为 k 的滑动窗口从数组的最左侧移动到数组的最右侧。你只可以看到在滑动窗口内的 k 个数字。滑动窗口每次只向右移动一位。

返回滑动窗口中的最大值。

**示例：**
```
输入：nums = [1,3,-1,-3,5,3,6,7], k = 3
输出：[3,3,5,5,6,7]
解释：
滑动窗口的位置                最大值
---------------               -----
[1  3  -1] -3  5  3  6  7       3
 1 [3  -1  -3] 5  3  6  7       3
 1  3 [-1  -3  5] 3  6  7       5
 1  3  -1 [-3  5  3] 6  7       5
 1  3  -1  -3 [5  3  6] 7       6
 1  3  -1  -3  5 [3  6  7]      7
```
""",
        "template": """def maxSlidingWindow(nums, k):
    \"\"\"
    :type nums: List[int]
    :type k: int
    :rtype: List[int]
    \"\"\"
    # 在这里编写你的代码
    pass
""",
        "test_cases": [
            {"input": "maxSlidingWindow([1, 3, -1, -3, 5, 3, 6, 7], 3)", "expected": "[3, 3, 5, 5, 6, 7]"},
            {"input": "maxSlidingWindow([1], 1)", "expected": "[1]"}
        ],
        "solution": """from collections import deque
def maxSlidingWindow(nums, k):
    dq = deque()
    result = []
    for i in range(len(nums)):
        while dq and dq[0] < i - k + 1:
            dq.popleft()
        while dq and nums[dq[-1]] < nums[i]:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
""",
        "hints": ["使用单调队列", "队列中存储索引，保持递减顺序"]
    },
    # ========== LeetCode 792: Binary Search ==========
    "21": {
        "id": "21",
        "title": "Binary Search",
        "difficulty": "简单",
        "tags": ['Array', 'Binary Search'],
        "description": 'Given an array of integers `nums` which is sorted in ascending order, and an integer `target`, write a function to search `target` in `nums`. If `target` exists, then return its index. Otherwise, return `-1`.\n\nYou must write an algorithm with `O(log n)` runtime complexity.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** nums = [-1,0,3,5,9,12], target = 9\n**Output:** 4\n**Explanation:** 9 exists in nums and its index is 4\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** nums = [-1,0,3,5,9,12], target = 2\n**Output:** -1\n**Explanation:** 2 does not exist in nums so return -1\n\n```\n\n&nbsp;\n\n**Constraints:**\n\n\t- `1 &l',
        "template": 'class Solution:\n    def search(self, nums: List[int], target: int) -> int:\n        ',
        "test_cases": [{"input": "[-1,0,3,5,9,12]", "expected": "9"}, {"input": "[-1,0,3,5,9,12]", "expected": "2"}]
    },
    # ========== LeetCode 153: Find Minimum in Rotated Sorted Array ==========
    "22": {
        "id": "22",
        "title": "Find Minimum in Rotated Sorted Array",
        "difficulty": "中等",
        "tags": ['Array', 'Binary Search'],
        "description": 'Suppose an array of length `n` sorted in ascending order is **rotated** between `1` and `n` times. For example, the array `nums = [0,1,2,4,5,6,7]` might become:\n\n\t- `[4,5,6,7,0,1,2]` if it was rotated `4` times.\n\n\t- `[0,1,2,4,5,6,7]` if it was rotated `7` times.\n\nNotice that **rotating** an array `[a[0], a[1], a[2], ..., a[n-1]]` 1 time results in the array `[a[n-1], a[0], a[1], a[2], ..., a[n-2]]`.\n\nGiven the sorted rotated array `nums` of **unique** elements, return the minimum element of this array.\n\nYou must write an algorithm that runs in&nbsp;`O(log n) time`.\n\n&nbsp;\n\n**Example 1:**\n\n```',
        "template": 'class Solution:\n    def findMin(self, nums: List[int]) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 33: Search in Rotated Sorted Array ==========
    "23": {
        "id": "23",
        "title": "Search in Rotated Sorted Array",
        "difficulty": "中等",
        "tags": ['Array', 'Binary Search'],
        "description": 'There is an integer array `nums` sorted in ascending order (with **distinct** values).\n\nPrior to being passed to your function, `nums` is **possibly left rotated** at an unknown index `k` (`1 &lt;= k &lt; nums.length`) such that the resulting array is `[nums[k], nums[k+1], ..., nums[n-1], nums[0], nums[1], ..., nums[k-1]]` (**0-indexed**). For example, `[0,1,2,4,5,6,7]` might be left rotated by&nbsp;`3`&nbsp;indices and become `[4,5,6,7,0,1,2]`.\n\nGiven the array `nums` **after** the possible rotation and an integer `target`, return the index of `target` if it is in `nums`, or `-1` if it is not',
        "template": 'class Solution:\n    def search(self, nums: List[int], target: int) -> int:\n        ',
        "test_cases": [{"input": "[4,5,6,7,0,1,2]", "expected": "0"}, {"input": "[4,5,6,7,0,1,2]", "expected": "3"}, {"input": "[1]", "expected": "0"}]
    },
    # ========== LeetCode 882: Peak Index in a Mountain Array ==========
    "24": {
        "id": "24",
        "title": "Peak Index in a Mountain Array",
        "difficulty": "中等",
        "tags": ['Array', 'Binary Search'],
        "description": 'You are given an integer **mountain** array `arr` of length `n` where the values increase to a **peak element** and then decrease.\n\nReturn the index of the peak element.\n\nYour task is to solve it in `O(log(n))` time complexity.\n\n&nbsp;\n\n**Example 1:**\n\n**Input:** arr = [0,1,0]\n\n**Output:** 1\n\n**Example 2:**\n\n**Input:** arr = [0,2,1,0]\n\n**Output:** 1\n\n**Example 3:**\n\n**Input:** arr = [0,10,5,2]\n\n**Output:** 1\n\n&nbsp;\n\n**Constraints:**\n\n\t- `3 &lt;= arr.length &lt;= 105`\n\n\t- `0 &lt;= arr[i] &lt;= 106`\n\n\t- `arr` is **guaranteed** to be a mountain array.',
        "template": 'class Solution:\n    def peakIndexInMountainArray(self, arr: List[int]) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 278: First Bad Version ==========
    "25": {
        "id": "25",
        "title": "First Bad Version",
        "difficulty": "简单",
        "tags": ['Binary Search', 'Interactive'],
        "description": 'You are a product manager and currently leading a team to develop a new product. Unfortunately, the latest version of your product fails the quality check. Since each version is developed based on the previous version, all the versions after a bad version are also bad.\n\nSuppose you have `n` versions `[1, 2, ..., n]` and you want to find out the first bad one, which causes all the following ones to be bad.\n\nYou are given an API `bool isBadVersion(version)` which returns whether `version` is bad. Implement a function to find the first bad version. You should minimize the number of calls to the A',
        "template": '# The isBadVersion API is already defined for you.\n# def isBadVersion(version: int) -> bool:\n\nclass Solution:\n    def firstBadVersion(self, n: int) -> int:\n        ',
        "test_cases": [{"input": "5", "expected": "4"}, {"input": "1", "expected": "1"}]
    },
    # ========== LeetCode 35: Search Insert Position ==========
    "26": {
        "id": "26",
        "title": "Search Insert Position",
        "difficulty": "简单",
        "tags": ['Array', 'Binary Search'],
        "description": 'Given a sorted array of distinct integers and a target value, return the index if the target is found. If not, return the index where it would be if it were inserted in order.\n\nYou must&nbsp;write an algorithm with&nbsp;`O(log n)` runtime complexity.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** nums = [1,3,5,6], target = 5\n**Output:** 2\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** nums = [1,3,5,6], target = 2\n**Output:** 1\n\n```\n\n**Example 3:**\n\n```\n\n**Input:** nums = [1,3,5,6], target = 7\n**Output:** 4\n\n```\n\n&nbsp;\n\n**Constraints:**\n\n\t- `1 &lt;= nums.length &lt;= 104`\n\n\t- `-104 &lt;= nums[i] &lt;= 104`\n\n',
        "template": 'class Solution:\n    def searchInsert(self, nums: List[int], target: int) -> int:\n        ',
        "test_cases": [{"input": "[1,3,5,6]", "expected": "5"}, {"input": "[1,3,5,6]", "expected": "2"}, {"input": "[1,3,5,6]", "expected": "7"}]
    },
    # ========== LeetCode 69: Sqrt(x) ==========
    "27": {
        "id": "27",
        "title": "Sqrt(x)",
        "difficulty": "简单",
        "tags": ['Math', 'Binary Search'],
        "description": 'Given a non-negative integer `x`, return the square root of `x` rounded down to the nearest integer. The returned integer should be **non-negative** as well.\n\nYou **must not use** any built-in exponent function or operator.\n\n\t- For example, do not use `pow(x, 0.5)` in c++ or `x ** 0.5` in python.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** x = 4\n**Output:** 2\n**Explanation:** The square root of 4 is 2, so we return 2.\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** x = 8\n**Output:** 2\n**Explanation:** The square root of 8 is 2.82842..., and since we round it down to the nearest integer, 2 is returned.\n\n```',
        "template": 'class Solution:\n    def mySqrt(self, x: int) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 367: Valid Perfect Square ==========
    "28": {
        "id": "28",
        "title": "Valid Perfect Square",
        "difficulty": "简单",
        "tags": ['Math', 'Binary Search'],
        "description": 'Given a positive integer num, return `true` if `num` is a perfect square or `false` otherwise.\n\nA **perfect square** is an integer that is the square of an integer. In other words, it is the product of some integer with itself.\n\nYou must not use any built-in library function, such as `sqrt`.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** num = 16\n**Output:** true\n**Explanation:** We return true because 4 * 4 = 16 and 4 is an integer.\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** num = 14\n**Output:** false\n**Explanation:** We return false because 3.742 * 3.742 = 14 and 3.742 is not an integer.\n\n```\n\n&nbsp;\n\n',
        "template": 'class Solution:\n    def isPerfectSquare(self, num: int) -> bool:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 374: Guess Number Higher or Lower ==========
    "29": {
        "id": "29",
        "title": "Guess Number Higher or Lower",
        "difficulty": "简单",
        "tags": ['Binary Search', 'Interactive'],
        "description": 'We are playing the Guess Game. The game is as follows:\n\nI pick a number from `1` to `n`. You have to guess which number I picked (the number I picked stays the same throughout the game).\n\nEvery time you guess wrong, I will tell you whether the number I picked is higher or lower than your guess.\n\nYou call a pre-defined API `int guess(int num)`, which returns three possible results:\n\n\t- `-1`: Your guess is higher than the number I picked (i.e. `num &gt; pick`).\n\n\t- `1`: Your guess is lower than the number I picked (i.e. `num &lt; pick`).\n\n\t- `0`: your guess is equal to the number I picked (i.e. ',
        "template": '# The guess API is already defined for you.\n# @param num, your guess\n# @return -1 if num is higher than the picked number\n#          1 if num is lower than the picked number\n#          otherwise return 0\n# def guess(num: int) -> int:\n\nclass Solution:\n    def guessNumber(self, n: int) -> int:\n        ',
        "test_cases": [{"input": "10", "expected": "6"}, {"input": "1", "expected": "1"}, {"input": "2", "expected": "1"}]
    },
    # ========== LeetCode 74: Search a 2D Matrix ==========
    "30": {
        "id": "30",
        "title": "Search a 2D Matrix",
        "difficulty": "中等",
        "tags": ['Array', 'Binary Search', 'Matrix'],
        "description": 'You are given an `m x n` integer matrix `matrix` with the following two properties:\n\n\t- Each row is sorted in non-decreasing order.\n\n\t- The first integer of each row is greater than the last integer of the previous row.\n\nGiven an integer `target`, return `true` if `target` is in `matrix` or `false` otherwise.\n\nYou must write a solution in `O(log(m * n))` time complexity.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3\n**Output:** true\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 13\n**Outpu',
        "template": 'class Solution:\n    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:\n        ',
        "test_cases": [{"input": "[[1,3,5,7],[10,11,16,20],[23,30,34,60]]", "expected": "3"}, {"input": "[[1,3,5,7],[10,11,16,20],[23,30,34,60]]", "expected": "13"}]
    },
    # ========== LeetCode 1: Two Sum ==========
    "31": {
        "id": "31",
        "title": "Two Sum",
        "difficulty": "简单",
        "tags": ['Array', 'Hash Table'],
        "description": 'Given an array of integers `nums`&nbsp;and an integer `target`, return indices of the two numbers such that they add up to `target`.\n\nYou may assume that each input would have **exactly one solution**, and you may not use the same element twice.\n\nYou can return the answer in any order.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** nums = [2,7,11,15], target = 9\n**Output:** [0,1]\n**Explanation:** Because nums[0] + nums[1] == 9, we return [0, 1].\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** nums = [3,2,4], target = 6\n**Output:** [1,2]\n\n```\n\n**Example 3:**\n\n```\n\n**Input:** nums = [3,3], target = 6\n**Output:*',
        "template": 'class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        ',
        "test_cases": [{"input": "[2,7,11,15]", "expected": "9"}, {"input": "[3,2,4]", "expected": "6"}, {"input": "[3,3]", "expected": "6"}]
    },
    # ========== LeetCode 167: Two Sum II - Input Array Is Sorted ==========
    "32": {
        "id": "32",
        "title": "Two Sum II - Input Array Is Sorted",
        "difficulty": "中等",
        "tags": ['Array', 'Two Pointers', 'Binary Search'],
        "description": 'Given a **1-indexed** array of integers `numbers` that is already **sorted in non-decreasing order**, find two numbers such that they add up to a specific `target` number. Let these two numbers be `numbers[index1]` and `numbers[index2]` where `1 &lt;= index1 &lt; index2 &lt;= numbers.length`.\n\nReturn the indices of the two numbers&nbsp;`index1` and `index2`, **each incremented by one,** as an integer array `[index1, index2]` of length 2.\n\nThe tests are generated such that there is **exactly one solution**. You **may not** use the same element twice.\n\nYour solution must use only constant extra ',
        "template": 'class Solution:\n    def twoSum(self, numbers: List[int], target: int) -> List[int]:\n        ',
        "test_cases": [{"input": "[2,7,11,15]", "expected": "9"}, {"input": "[2,3,4]", "expected": "6"}, {"input": "[-1,0]", "expected": "-1"}]
    },
    # ========== LeetCode 15: 3Sum ==========
    "33": {
        "id": "33",
        "title": "3Sum",
        "difficulty": "中等",
        "tags": ['Array', 'Two Pointers', 'Sorting'],
        "description": 'Given an integer array nums, return all the triplets `[nums[i], nums[j], nums[k]]` such that `i != j`, `i != k`, and `j != k`, and `nums[i] + nums[j] + nums[k] == 0`.\n\nNotice that the solution set must not contain duplicate triplets.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** nums = [-1,0,1,2,-1,-4]\n**Output:** [[-1,-1,2],[-1,0,1]]\n**Explanation:** \nnums[0] + nums[1] + nums[2] = (-1) + 0 + 1 = 0.\nnums[1] + nums[2] + nums[4] = 0 + 1 + (-1) = 0.\nnums[0] + nums[3] + nums[4] = (-1) + 2 + (-1) = 0.\nThe distinct triplets are [-1,0,1] and [-1,-1,2].\nNotice that the order of the output and the order of ',
        "template": 'class Solution:\n    def threeSum(self, nums: list[int]) -> list[list[int]]:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 11: Container With Most Water ==========
    "34": {
        "id": "34",
        "title": "Container With Most Water",
        "difficulty": "中等",
        "tags": ['Array', 'Two Pointers', 'Greedy'],
        "description": 'You are given an integer array `height` of length `n`. There are `n` vertical lines drawn such that the two endpoints of the `ith` line are `(i, 0)` and `(i, height[i])`.\n\nFind two lines that together with the x-axis form a container, such that the container contains the most water.\n\nReturn the maximum amount of water a container can store.\n\n**Notice** that you may not slant the container.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** height = [1,8,6,2,5,4,8,3,7]\n**Output:** 49\n**Explanation:** The above vertical lines are represented by array [1,8,6,2,5,4,8,3,7]. In this case, the max area of wate',
        "template": 'class Solution:\n    def maxArea(self, height: List[int]) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 125: Valid Palindrome ==========
    "35": {
        "id": "35",
        "title": "Valid Palindrome",
        "difficulty": "简单",
        "tags": ['Two Pointers', 'String'],
        "description": 'A phrase is a **palindrome** if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward. Alphanumeric characters include letters and numbers.\n\nGiven a string `s`, return `true` if it is a **palindrome**, or `false` otherwise.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** s = &quot;A man, a plan, a canal: Panama&quot;\n**Output:** true\n**Explanation:** &quot;amanaplanacanalpanama&quot; is a palindrome.\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** s = &quot;race a car&quot;\n**Output:** false\n**Explanation:** &quot;rac',
        "template": 'class Solution:\n    def isPalindrome(self, s: str) -> bool:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 283: Move Zeroes ==========
    "36": {
        "id": "36",
        "title": "Move Zeroes",
        "difficulty": "简单",
        "tags": ['Array', 'Two Pointers'],
        "description": 'Given an integer array `nums`, move all `0`&#39;s to the end of it while maintaining the relative order of the non-zero elements.\n\n**Note** that you must do this in-place without making a copy of the array.\n\n&nbsp;\n\n**Example 1:**\n\n```\n**Input:** nums = [0,1,0,3,12]\n**Output:** [1,3,12,0,0]\n\n```\n\n**Example 2:**\n\n```\n**Input:** nums = [0]\n**Output:** [0]\n\n```\n\n&nbsp;\n\n**Constraints:**\n\n\t- `1 &lt;= nums.length &lt;= 104`\n\n\t- `-231 &lt;= nums[i] &lt;= 231 - 1`\n\n&nbsp;\n\n**Follow up:** Could you minimize the total number of operations done?',
        "template": 'class Solution:\n    def moveZeroes(self, nums: List[int]) -> None:\n        """\n        Do not return anything, modify nums in-place instead.\n        """\n        ',
        "test_cases": []
    },
    # ========== LeetCode 26: Remove Duplicates from Sorted Array ==========
    "37": {
        "id": "37",
        "title": "Remove Duplicates from Sorted Array",
        "difficulty": "简单",
        "tags": ['Array', 'Two Pointers'],
        "description": 'Given an integer array `nums` sorted in **non-decreasing order**, remove the duplicates **in-place** such that each unique element appears only **once**. The **relative order** of the elements should be kept the **same**.\n\nConsider the number of unique elements in&nbsp;`nums` to be `k**\u200b\u200b\u200b\u200b\u200b\u200b\u200b**`\u200b\u200b\u200b\u200b\u200b\u200b\u200b. After removing duplicates, return the number of unique elements&nbsp;`k`.\n\nThe first&nbsp;`k`&nbsp;elements of&nbsp;`nums`&nbsp;should contain the unique numbers in **sorted order**. The remaining elements beyond index&nbsp;`k - 1`&nbsp;can be ignored.\n\n**Custom Judge:**\n\nThe judge will test y',
        "template": 'class Solution:\n    def removeDuplicates(self, nums: List[int]) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 27: Remove Element ==========
    "38": {
        "id": "38",
        "title": "Remove Element",
        "difficulty": "简单",
        "tags": ['Array', 'Two Pointers'],
        "description": 'Given an integer array `nums` and an integer `val`, remove all occurrences of `val` in `nums` **in-place**. The order of the elements may be changed. Then return the number of elements in `nums` which are not equal to `val`.\n\nConsider the number of elements in `nums` which are not equal to `val` be `k`, to get accepted, you need to do the following things:\n\n\t- Change the array `nums` such that the first `k` elements of `nums` contain the elements which are not equal to `val`. The remaining elements of `nums` are not important as well as the size of `nums`.\n\n\t- Return `k`.\n\n**Custom Judge:**\n\nT',
        "template": 'class Solution:\n    def removeElement(self, nums: List[int], val: int) -> int:\n        ',
        "test_cases": [{"input": "[3,2,2,3]", "expected": "3"}, {"input": "[0,1,2,2,3,0,4,2]", "expected": "2"}]
    },
    # ========== LeetCode 75: Sort Colors ==========
    "39": {
        "id": "39",
        "title": "Sort Colors",
        "difficulty": "中等",
        "tags": ['Array', 'Two Pointers', 'Sorting'],
        "description": 'Given an array `nums` with `n` objects colored red, white, or blue, sort them **in-place **so that objects of the same color are adjacent, with the colors in the order red, white, and blue.\n\nWe will use the integers `0`, `1`, and `2` to represent the color red, white, and blue, respectively.\n\nYou must solve this problem without using the library&#39;s sort function.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** nums = [2,0,2,1,1,0]\n**Output:** [0,0,1,1,2,2]\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** nums = [2,0,1]\n**Output:** [0,1,2]\n\n```\n\n&nbsp;\n\n**Constraints:**\n\n\t- `n == nums.length`\n\n\t- `1 &lt;= n &',
        "template": 'class Solution:\n    def sortColors(self, nums: List[int]) -> None:\n        """\n        Do not return anything, modify nums in-place instead.\n        """\n        ',
        "test_cases": []
    },
    # ========== LeetCode 344: Reverse String ==========
    "40": {
        "id": "40",
        "title": "Reverse String",
        "difficulty": "简单",
        "tags": ['Two Pointers', 'String'],
        "description": 'Write a function that reverses a string. The input string is given as an array of characters `s`.\n\nYou must do this by modifying the input array in-place with `O(1)` extra memory.\n\n&nbsp;\n\n**Example 1:**\n\n```\n**Input:** s = ["h","e","l","l","o"]\n**Output:** ["o","l","l","e","h"]\n\n```\n\n**Example 2:**\n\n```\n**Input:** s = ["H","a","n","n","a","h"]\n**Output:** ["h","a","n","n","a","H"]\n\n```\n\n&nbsp;\n\n**Constraints:**\n\n\t- `1 &lt;= s.length &lt;= 105`\n\n\t- `s[i]` is a printable ascii character.',
        "template": 'class Solution:\n    def reverseString(self, s: List[str]) -> None:\n        """\n        Do not return anything, modify s in-place instead.\n        """\n        ',
        "test_cases": []
    },
    # ========== LeetCode 3: Longest Substring Without Repeating Characters ==========
    "41": {
        "id": "41",
        "title": "Longest Substring Without Repeating Characters",
        "difficulty": "中等",
        "tags": ['Hash Table', 'String', 'Sliding Window'],
        "description": 'Given a string `s`, find the length of the **longest** **substring** without duplicate characters.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** s = &quot;abcabcbb&quot;\n**Output:** 3\n**Explanation:** The answer is &quot;abc&quot;, with the length of 3. Note that `&quot;bca&quot;` and `&quot;cab&quot;` are also correct answers.\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** s = &quot;bbbbb&quot;\n**Output:** 1\n**Explanation:** The answer is &quot;b&quot;, with the length of 1.\n\n```\n\n**Example 3:**\n\n```\n\n**Input:** s = &quot;pwwkew&quot;\n**Output:** 3\n**Explanation:** The answer is &quot;wke&quot;, with the l',
        "template": 'class Solution:\n    def lengthOfLongestSubstring(self, s: str) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 209: Minimum Size Subarray Sum ==========
    "42": {
        "id": "42",
        "title": "Minimum Size Subarray Sum",
        "difficulty": "中等",
        "tags": ['Array', 'Binary Search', 'Sliding Window', 'Prefix Sum'],
        "description": 'Given an array of positive integers `nums` and a positive integer `target`, return the **minimal length** of a subarray whose sum is greater than or equal to `target`. If there is no such subarray, return `0` instead.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** target = 7, nums = [2,3,1,2,4,3]\n**Output:** 2\n**Explanation:** The subarray [4,3] has the minimal length under the problem constraint.\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** target = 4, nums = [1,4,4]\n**Output:** 1\n\n```\n\n**Example 3:**\n\n```\n\n**Input:** target = 11, nums = [1,1,1,1,1,1,1,1]\n**Output:** 0\n\n```\n\n&nbsp;\n\n**Constraints:**\n\n\t- `',
        "template": 'class Solution:\n    def minSubArrayLen(self, target: int, nums: List[int]) -> int:\n        ',
        "test_cases": [{"input": "7", "expected": "[2,3,1,2,4,3]"}, {"input": "4", "expected": "[1,4,4]"}, {"input": "11", "expected": "[1,1,1,1,1,1,1,1]"}]
    },
    # ========== LeetCode 438: Find All Anagrams in a String ==========
    "43": {
        "id": "43",
        "title": "Find All Anagrams in a String",
        "difficulty": "中等",
        "tags": ['Hash Table', 'String', 'Sliding Window'],
        "description": 'Given two strings `s` and `p`, return an array of all the start indices of `p`&#39;s anagrams in `s`. You may return the answer in **any order**.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** s = &quot;cbaebabacd&quot;, p = &quot;abc&quot;\n**Output:** [0,6]\n**Explanation:**\nThe substring with start index = 0 is &quot;cba&quot;, which is an anagram of &quot;abc&quot;.\nThe substring with start index = 6 is &quot;bac&quot;, which is an anagram of &quot;abc&quot;.\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** s = &quot;abab&quot;, p = &quot;ab&quot;\n**Output:** [0,1,2]\n**Explanation:**\nThe substring with start',
        "template": 'class Solution:\n    def findAnagrams(self, s: str, p: str) -> List[int]:\n        ',
        "test_cases": [{"input": "\"cbaebabacd\"", "expected": "\"abc\""}, {"input": "\"abab\"", "expected": "\"ab\""}]
    },
    # ========== LeetCode 567: Permutation in String ==========
    "44": {
        "id": "44",
        "title": "Permutation in String",
        "difficulty": "中等",
        "tags": ['Hash Table', 'Two Pointers', 'String', 'Sliding Window'],
        "description": 'Given two strings `s1` and `s2`, return `true` if `s2` contains a permutation of `s1`, or `false` otherwise.\n\nIn other words, return `true` if one of `s1`&#39;s permutations is the substring of `s2`.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** s1 = &quot;ab&quot;, s2 = &quot;eidbaooo&quot;\n**Output:** true\n**Explanation:** s2 contains one permutation of s1 (&quot;ba&quot;).\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** s1 = &quot;ab&quot;, s2 = &quot;eidboaoo&quot;\n**Output:** false\n\n```\n\n&nbsp;\n\n**Constraints:**\n\n\t- `1 &lt;= s1.length, s2.length &lt;= 104`\n\n\t- `s1` and `s2` consist of lowercase English ',
        "template": 'class Solution:\n    def checkInclusion(self, s1: str, s2: str) -> bool:\n        ',
        "test_cases": [{"input": "\"ab\"", "expected": "\"eidbaooo\""}, {"input": "\"ab\"", "expected": "\"eidboaoo\""}]
    },
    # ========== LeetCode 643: Maximum Average Subarray I ==========
    "45": {
        "id": "45",
        "title": "Maximum Average Subarray I",
        "difficulty": "简单",
        "tags": ['Array', 'Sliding Window'],
        "description": 'You are given an integer array `nums` consisting of `n` elements, and an integer `k`.\n\nFind a contiguous subarray whose **length is equal to** `k` that has the maximum average value and return this value. Any answer with a calculation error less than `10-5` will be accepted.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** nums = [1,12,-5,-6,50,3], k = 4\n**Output:** 12.75000\n**Explanation:** Maximum average is (12 - 5 - 6 + 50) / 4 = 51 / 4 = 12.75\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** nums = [5], k = 1\n**Output:** 5.00000\n\n```\n\n&nbsp;\n\n**Constraints:**\n\n\t- `n == nums.length`\n\n\t- `1 &lt;= k &lt;= n &l',
        "template": 'class Solution:\n    def findMaxAverage(self, nums: List[int], k: int) -> float:\n        ',
        "test_cases": [{"input": "[1,12,-5,-6,50,3]", "expected": "4"}, {"input": "[5]", "expected": "1"}]
    },
    # ========== LeetCode 200: Number of Islands ==========
    "46": {
        "id": "46",
        "title": "Number of Islands",
        "difficulty": "中等",
        "tags": ['Array', 'Depth-First Search', 'Breadth-First Search', 'Union-Find', 'Matrix'],
        "description": 'Given an `m x n` 2D binary grid `grid` which represents a map of `&#39;1&#39;`s (land) and `&#39;0&#39;`s (water), return the number of islands.\n\nAn **island** is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are all surrounded by water.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** grid = [\n  [&quot;1&quot;,&quot;1&quot;,&quot;1&quot;,&quot;1&quot;,&quot;0&quot;],\n  [&quot;1&quot;,&quot;1&quot;,&quot;0&quot;,&quot;1&quot;,&quot;0&quot;],\n  [&quot;1&quot;,&quot;1&quot;,&quot;0&quot;,&quot;0&quot;,&quot;0&quot;],\n',
        "template": 'class Solution:\n    def numIslands(self, grid: List[List[str]]) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 695: Max Area of Island ==========
    "47": {
        "id": "47",
        "title": "Max Area of Island",
        "difficulty": "中等",
        "tags": ['Array', 'Depth-First Search', 'Breadth-First Search', 'Union-Find', 'Matrix'],
        "description": 'You are given an `m x n` binary matrix `grid`. An island is a group of `1`&#39;s (representing land) connected **4-directionally** (horizontal or vertical.) You may assume all four edges of the grid are surrounded by water.\n\nThe **area** of an island is the number of cells with a value `1` in the island.\n\nReturn the maximum **area** of an island in `grid`. If there is no island, return `0`.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** grid = [[0,0,1,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,1,1,1,0,0,0],[0,1,1,0,1,0,0,0,0,0,0,0,0],[0,1,0,0,1,1,0,0,1,0,1,0,0],[0,1,0,0,1,1,0,0,1,1,1,0,0],[0,0,0,0,0,0,0,0,',
        "template": 'class Solution:\n    def maxAreaOfIsland(self, grid: List[List[int]]) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 79: Word Search ==========
    "48": {
        "id": "48",
        "title": "Word Search",
        "difficulty": "中等",
        "tags": ['Array', 'String', 'Backtracking', 'Depth-First Search', 'Matrix'],
        "description": 'Given an `m x n` grid of characters `board` and a string `word`, return `true` if `word` exists in the grid.\n\nThe word can be constructed from letters of sequentially adjacent cells, where adjacent cells are horizontally or vertically neighboring. The same letter cell may not be used more than once.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** board = [[&quot;A&quot;,&quot;B&quot;,&quot;C&quot;,&quot;E&quot;],[&quot;S&quot;,&quot;F&quot;,&quot;C&quot;,&quot;S&quot;],[&quot;A&quot;,&quot;D&quot;,&quot;E&quot;,&quot;E&quot;]], word = &quot;ABCCED&quot;\n**Output:** true\n\n```\n\n**Example 2:**\n\n```\n\n**I',
        "template": 'class Solution:\n    def exist(self, board: List[List[str]], word: str) -> bool:\n        ',
        "test_cases": [{"input": "[[\"A\",\"B\",\"C\",\"E\"],[\"S\",\"F\",\"C\",\"S\"],[\"A\",\"D\",\"E\",\"E\"]]", "expected": "\"ABCCED\""}, {"input": "[[\"A\",\"B\",\"C\",\"E\"],[\"S\",\"F\",\"C\",\"S\"],[\"A\",\"D\",\"E\",\"E\"]]", "expected": "\"SEE\""}, {"input": "[[\"A\",\"B\",\"C\",\"E\"],[\"S\",\"F\",\"C\",\"S\"],[\"A\",\"D\",\"E\",\"E\"]]", "expected": "\"ABCB\""}]
    },
    # ========== LeetCode 733: Flood Fill ==========
    "49": {
        "id": "49",
        "title": "Flood Fill",
        "difficulty": "简单",
        "tags": ['Array', 'Depth-First Search', 'Breadth-First Search', 'Matrix'],
        "description": 'You are given an image represented by an `m x n` grid of integers `image`, where `image[i][j]` represents the pixel value of the image. You are also given three integers `sr`, `sc`, and `color`. Your task is to perform a **flood fill** on the image starting from the pixel `image[sr][sc]`.\n\nTo perform a **flood fill**:\n\n\t- Begin with the starting pixel and change its color to `color`.\n\n\t- Perform the same process for each pixel that is **directly adjacent** (pixels that share a side with the original pixel, either horizontally or vertically) and shares the **same color** as the starting pixel.\n',
        "template": 'class Solution:\n    def floodFill(self, image: List[List[int]], sr: int, sc: int, color: int) -> List[List[int]]:\n        ',
        "test_cases": [{"input": "[[1,1,1],[1,1,0],[1,0,1]]", "expected": "1"}, {"input": "[[0,0,0],[0,0,0]]", "expected": "0"}]
    },
    # ========== LeetCode 133: Clone Graph ==========
    "50": {
        "id": "50",
        "title": "Clone Graph",
        "difficulty": "中等",
        "tags": ['Hash Table', 'Depth-First Search', 'Breadth-First Search', 'Graph Theory'],
        "description": 'Given a reference of a node in a **connected** undirected graph.\n\nReturn a **deep copy** (clone) of the graph.\n\nEach node in the graph contains a value (`int`) and a list (`List[Node]`) of its neighbors.\n\n```\n\nclass Node {\n    public int val;\n    public List&lt;Node&gt; neighbors;\n}\n\n```\n\n&nbsp;\n\n**Test case format:**\n\nFor simplicity, each node&#39;s value is the same as the node&#39;s index (1-indexed). For example, the first node with `val == 1`, the second node with `val == 2`, and so on. The graph is represented in the test case using an adjacency list.\n\nAn adjacency list is a collection o',
        "template": '"""\n# Definition for a Node.\nclass Node:\n    def __init__(self, val = 0, neighbors = None):\n        self.val = val\n        self.neighbors = neighbors if neighbors is not None else []\n"""\n\nfrom typing import Optional\nclass Solution:\n    def cloneGraph(self, node: Optional[\'Node\']) -> Optional[\'Node\']:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 207: Course Schedule ==========
    "51": {
        "id": "51",
        "title": "Course Schedule",
        "difficulty": "中等",
        "tags": ['Depth-First Search', 'Breadth-First Search', 'Graph Theory', 'Topological Sort'],
        "description": 'There are a total of `numCourses` courses you have to take, labeled from `0` to `numCourses - 1`. You are given an array `prerequisites` where `prerequisites[i] = [ai, bi]` indicates that you **must** take course `bi` first if you want to take course `ai`.\n\n\t- For example, the pair `[0, 1]`, indicates that to take course `0` you have to first take course `1`.\n\nReturn `true` if you can finish all courses. Otherwise, return `false`.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** numCourses = 2, prerequisites = [[1,0]]\n**Output:** true\n**Explanation:** There are a total of 2 courses to take. \nTo take c',
        "template": 'class Solution:\n    def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:\n        ',
        "test_cases": [{"input": "2", "expected": "[[1,0]]"}, {"input": "2", "expected": "[[1,0],[0,1]]"}]
    },
    # ========== LeetCode 102: Binary Tree Level Order Traversal ==========
    "52": {
        "id": "52",
        "title": "Binary Tree Level Order Traversal",
        "difficulty": "中等",
        "tags": ['Tree', 'Breadth-First Search', 'Binary Tree'],
        "description": 'Given the `root` of a binary tree, return the level order traversal of its nodes&#39; values. (i.e., from left to right, level by level).\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** root = [3,9,20,null,null,15,7]\n**Output:** [[3],[9,20],[15,7]]\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** root = [1]\n**Output:** [[1]]\n\n```\n\n**Example 3:**\n\n```\n\n**Input:** root = []\n**Output:** []\n\n```\n\n&nbsp;\n\n**Constraints:**\n\n\t- The number of nodes in the tree is in the range `[0, 2000]`.\n\n\t- `-1000 &lt;= Node.val &lt;= 1000`',
        "template": '# Definition for a binary tree node.\n# class TreeNode:\n#     def __init__(self, val=0, left=None, right=None):\n#         self.val = val\n#         self.left = left\n#         self.right = right\nclass Solution:\n    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 104: Maximum Depth of Binary Tree ==========
    "53": {
        "id": "53",
        "title": "Maximum Depth of Binary Tree",
        "difficulty": "简单",
        "tags": ['Tree', 'Depth-First Search', 'Breadth-First Search', 'Binary Tree'],
        "description": 'Given the `root` of a binary tree, return its maximum depth.\n\nA binary tree&#39;s **maximum depth**&nbsp;is the number of nodes along the longest path from the root node down to the farthest leaf node.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** root = [3,9,20,null,null,15,7]\n**Output:** 3\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** root = [1,null,2]\n**Output:** 2\n\n```\n\n&nbsp;\n\n**Constraints:**\n\n\t- The number of nodes in the tree is in the range `[0, 104]`.\n\n\t- `-100 &lt;= Node.val &lt;= 100`',
        "template": '# Definition for a binary tree node.\n# class TreeNode:\n#     def __init__(self, val=0, left=None, right=None):\n#         self.val = val\n#         self.left = left\n#         self.right = right\nclass Solution:\n    def maxDepth(self, root: Optional[TreeNode]) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 101: Symmetric Tree ==========
    "54": {
        "id": "54",
        "title": "Symmetric Tree",
        "difficulty": "简单",
        "tags": ['Tree', 'Depth-First Search', 'Breadth-First Search', 'Binary Tree'],
        "description": 'Given the `root` of a binary tree, check whether it is a mirror of itself (i.e., symmetric around its center).\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** root = [1,2,2,3,4,4,3]\n**Output:** true\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** root = [1,2,2,null,3,null,3]\n**Output:** false\n\n```\n\n&nbsp;\n\n**Constraints:**\n\n\t- The number of nodes in the tree is in the range `[1, 1000]`.\n\n\t- `-100 &lt;= Node.val &lt;= 100`\n\n&nbsp;\n\n**Follow up:** Could you solve it both recursively and iteratively?',
        "template": '# Definition for a binary tree node.\n# class TreeNode:\n#     def __init__(self, val=0, left=None, right=None):\n#         self.val = val\n#         self.left = left\n#         self.right = right\nclass Solution:\n    def isSymmetric(self, root: Optional[TreeNode]) -> bool:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 226: Invert Binary Tree ==========
    "55": {
        "id": "55",
        "title": "Invert Binary Tree",
        "difficulty": "简单",
        "tags": ['Tree', 'Depth-First Search', 'Breadth-First Search', 'Binary Tree'],
        "description": 'Given the `root` of a binary tree, invert the tree, and return its root.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** root = [4,2,7,1,3,6,9]\n**Output:** [4,7,2,9,6,3,1]\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** root = [2,1,3]\n**Output:** [2,3,1]\n\n```\n\n**Example 3:**\n\n```\n\n**Input:** root = []\n**Output:** []\n\n```\n\n&nbsp;\n\n**Constraints:**\n\n\t- The number of nodes in the tree is in the range `[0, 100]`.\n\n\t- `-100 &lt;= Node.val &lt;= 100`',
        "template": '# Definition for a binary tree node.\n# class TreeNode:\n#     def __init__(self, val=0, left=None, right=None):\n#         self.val = val\n#         self.left = left\n#         self.right = right\nclass Solution:\n    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 70: Climbing Stairs ==========
    "56": {
        "id": "56",
        "title": "Climbing Stairs",
        "difficulty": "简单",
        "tags": ['Math', 'Dynamic Programming', 'Memoization'],
        "description": 'You are climbing a staircase. It takes `n` steps to reach the top.\n\nEach time you can either climb `1` or `2` steps. In how many distinct ways can you climb to the top?\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** n = 2\n**Output:** 2\n**Explanation:** There are two ways to climb to the top.\n1. 1 step + 1 step\n2. 2 steps\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** n = 3\n**Output:** 3\n**Explanation:** There are three ways to climb to the top.\n1. 1 step + 1 step + 1 step\n2. 1 step + 2 steps\n3. 2 steps + 1 step\n\n```\n\n&nbsp;\n\n**Constraints:**\n\n\t- `1 &lt;= n &lt;= 45`',
        "template": 'class Solution:\n    def climbStairs(self, n: int) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 198: House Robber ==========
    "57": {
        "id": "57",
        "title": "House Robber",
        "difficulty": "中等",
        "tags": ['Array', 'Dynamic Programming'],
        "description": 'You are a professional robber planning to rob houses along a street. Each house has a certain amount of money stashed, the only constraint stopping you from robbing each of them is that adjacent houses have security systems connected and it will automatically contact the police if two adjacent houses were broken into on the same night.\n\nGiven an integer array `nums` representing the amount of money of each house, return the maximum amount of money you can rob tonight without alerting the police.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** nums = [1,2,3,1]\n**Output:** 4\n**Explanation:** Rob house ',
        "template": 'class Solution:\n    def rob(self, nums: List[int]) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 62: Unique Paths ==========
    "58": {
        "id": "58",
        "title": "Unique Paths",
        "difficulty": "中等",
        "tags": ['Math', 'Dynamic Programming', 'Combinatorics'],
        "description": 'There is a robot on an `m x n` grid. The robot is initially located at the **top-left corner** (i.e., `grid[0][0]`). The robot tries to move to the **bottom-right corner** (i.e., `grid[m - 1][n - 1]`). The robot can only move either down or right at any point in time.\n\nGiven the two integers `m` and `n`, return the number of possible unique paths that the robot can take to reach the bottom-right corner.\n\nThe test cases are generated so that the answer will be less than or equal to `2 * 109`.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** m = 3, n = 7\n**Output:** 28\n\n```\n\n**Example 2:**\n\n```\n\n**Input',
        "template": 'class Solution:\n    def uniquePaths(self, m: int, n: int) -> int:\n        ',
        "test_cases": [{"input": "3", "expected": "7"}, {"input": "3", "expected": "2"}]
    },
    # ========== LeetCode 322: Coin Change ==========
    "59": {
        "id": "59",
        "title": "Coin Change",
        "difficulty": "中等",
        "tags": ['Array', 'Dynamic Programming', 'Breadth-First Search'],
        "description": 'You are given an integer array `coins` representing coins of different denominations and an integer `amount` representing a total amount of money.\n\nReturn the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return `-1`.\n\nYou may assume that you have an infinite number of each kind of coin.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** coins = [1,2,5], amount = 11\n**Output:** 3\n**Explanation:** 11 = 5 + 5 + 1\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** coins = [2], amount = 3\n**Output:** -1\n\n```\n\n**Example 3:**\n\n```\n\n*',
        "template": 'class Solution:\n    def coinChange(self, coins: List[int], amount: int) -> int:\n        ',
        "test_cases": [{"input": "[1,2,5]", "expected": "11"}, {"input": "[2]", "expected": "3"}, {"input": "[1]", "expected": "0"}]
    },
    # ========== LeetCode 300: Longest Increasing Subsequence ==========
    "60": {
        "id": "60",
        "title": "Longest Increasing Subsequence",
        "difficulty": "中等",
        "tags": ['Array', 'Binary Search', 'Dynamic Programming'],
        "description": 'Given an integer array `nums`, return the length of the longest **strictly increasing ****subsequence**.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** nums = [10,9,2,5,3,7,101,18]\n**Output:** 4\n**Explanation:** The longest increasing subsequence is [2,3,7,101], therefore the length is 4.\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** nums = [0,1,0,3,2,3]\n**Output:** 4\n\n```\n\n**Example 3:**\n\n```\n\n**Input:** nums = [7,7,7,7,7,7,7]\n**Output:** 1\n\n```\n\n&nbsp;\n\n**Constraints:**\n\n\t- `1 &lt;= nums.length &lt;= 2500`\n\n\t- `-104 &lt;= nums[i] &lt;= 104`\n\n&nbsp;\n\nFollow up:&nbsp;Can you come up with an algorithm that r',
        "template": 'class Solution:\n    def lengthOfLIS(self, nums: List[int]) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 53: Maximum Subarray ==========
    "61": {
        "id": "61",
        "title": "Maximum Subarray",
        "difficulty": "中等",
        "tags": ['Array', 'Divide and Conquer', 'Dynamic Programming'],
        "description": 'Given an integer array `nums`, find the subarray with the largest sum, and return its sum.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** nums = [-2,1,-3,4,-1,2,1,-5,4]\n**Output:** 6\n**Explanation:** The subarray [4,-1,2,1] has the largest sum 6.\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** nums = [1]\n**Output:** 1\n**Explanation:** The subarray [1] has the largest sum 1.\n\n```\n\n**Example 3:**\n\n```\n\n**Input:** nums = [5,4,-1,7,8]\n**Output:** 23\n**Explanation:** The subarray [5,4,-1,7,8] has the largest sum 23.\n\n```\n\n&nbsp;\n\n**Constraints:**\n\n\t- `1 &lt;= nums.length &lt;= 105`\n\n\t- `-104 &lt;= nums[i] &lt;= 10',
        "template": 'class Solution:\n    def maxSubArray(self, nums: List[int]) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 121: Best Time to Buy and Sell Stock ==========
    "62": {
        "id": "62",
        "title": "Best Time to Buy and Sell Stock",
        "difficulty": "简单",
        "tags": ['Array', 'Dynamic Programming'],
        "description": 'You are given an array `prices` where `prices[i]` is the price of a given stock on the `ith` day.\n\nYou want to maximize your profit by choosing a **single day** to buy one stock and choosing a **different day in the future** to sell that stock.\n\nReturn the maximum profit you can achieve from this transaction. If you cannot achieve any profit, return `0`.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** prices = [7,1,5,3,6,4]\n**Output:** 5\n**Explanation:** Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5.\nNote that buying on day 2 and selling on day 1 is not allowed because you ',
        "template": 'class Solution:\n    def maxProfit(self, prices: List[int]) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 120: Triangle ==========
    "63": {
        "id": "63",
        "title": "Triangle",
        "difficulty": "中等",
        "tags": ['Array', 'Dynamic Programming'],
        "description": 'Given a `triangle` array, return the minimum path sum from top to bottom.\n\nFor each step, you may move to an adjacent number of the row below. More formally, if you are on index `i` on the current row, you may move to either index `i` or index `i + 1` on the next row.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** triangle = [[2],[3,4],[6,5,7],[4,1,8,3]]\n**Output:** 11\n**Explanation:** The triangle looks like:\n   2\n  3 4\n 6 5 7\n4 1 8 3\nThe minimum path sum from top to bottom is 2 + 3 + 5 + 1 = 11 (underlined above).\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** triangle = [[-10]]\n**Output:** -10\n\n```\n\n&nbsp',
        "template": 'class Solution:\n    def minimumTotal(self, triangle: List[List[int]]) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 747: Min Cost Climbing Stairs ==========
    "64": {
        "id": "64",
        "title": "Min Cost Climbing Stairs",
        "difficulty": "简单",
        "tags": ['Array', 'Dynamic Programming'],
        "description": 'You are given an integer array `cost` where `cost[i]` is the cost of `ith` step on a staircase. Once you pay the cost, you can either climb one or two steps.\n\nYou can either start from the step with index `0`, or the step with index `1`.\n\nReturn the minimum cost to reach the top of the floor.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** cost = [10,15,20]\n**Output:** 15\n**Explanation:** You will start at index 1.\n- Pay 15 and climb two steps to reach the top.\nThe total cost is 15.\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** cost = [1,100,1,1,1,100,1,1,100,1]\n**Output:** 6\n**Explanation:** You will start ',
        "template": 'class Solution:\n    def minCostClimbingStairs(self, cost: List[int]) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 416: Partition Equal Subset Sum ==========
    "65": {
        "id": "65",
        "title": "Partition Equal Subset Sum",
        "difficulty": "中等",
        "tags": ['Array', 'Dynamic Programming'],
        "description": 'Given an integer array `nums`, return `true` if you can partition the array into two subsets such that the sum of the elements in both subsets is equal or `false` otherwise.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input:** nums = [1,5,11,5]\n**Output:** true\n**Explanation:** The array can be partitioned as [1, 5, 5] and [11].\n\n```\n\n**Example 2:**\n\n```\n\n**Input:** nums = [1,2,3,5]\n**Output:** false\n**Explanation:** The array cannot be partitioned into equal sum subsets.\n\n```\n\n&nbsp;\n\n**Constraints:**\n\n\t- `1 &lt;= nums.length &lt;= 200`\n\n\t- `1 &lt;= nums[i] &lt;= 100`',
        "template": 'class Solution:\n    def canPartition(self, nums: List[int]) -> bool:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 20: Valid Parentheses ==========
    "66": {
        "id": "66",
        "title": "Valid Parentheses",
        "difficulty": "简单",
        "tags": ['String', 'Stack'],
        "description": 'Given a string `s` containing just the characters `&#39;(&#39;`, `&#39;)&#39;`, `&#39;{&#39;`, `&#39;}&#39;`, `&#39;[&#39;` and `&#39;]&#39;`, determine if the input string is valid.\n\nAn input string is valid if:\n\n\t- Open brackets must be closed by the same type of brackets.\n\n\t- Open brackets must be closed in the correct order.\n\n\t- Every close bracket has a corresponding open bracket of the same type.\n\n&nbsp;\n\n**Example 1:**\n\n**Input:** s = &quot;()&quot;\n\n**Output:** true\n\n**Example 2:**\n\n**Input:** s = &quot;()[]{}&quot;\n\n**Output:** true\n\n**Example 3:**\n\n**Input:** s = &quot;(]&quot;\n\n**Ou',
        "template": 'class Solution:\n    def isValid(self, s: str) -> bool:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 155: Min Stack ==========
    "67": {
        "id": "67",
        "title": "Min Stack",
        "difficulty": "中等",
        "tags": ['Stack', 'Design'],
        "description": 'Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.\n\nImplement the `MinStack` class:\n\n\t- `MinStack()` initializes the stack object.\n\n\t- `void push(int val)` pushes the element `val` onto the stack.\n\n\t- `void pop()` removes the element on the top of the stack.\n\n\t- `int top()` gets the top element of the stack.\n\n\t- `int getMin()` retrieves the minimum element in the stack.\n\nYou must implement a solution with `O(1)` time complexity for each function.\n\n&nbsp;\n\n**Example 1:**\n\n```\n\n**Input**\n[&quot;MinStack&quot;,&quot;push&quot;,&quot;push&quot;,&quot;',
        "template": 'class MinStack:\n\n    def __init__(self):\n        \n\n    def push(self, val: int) -> None:\n        \n\n    def pop(self) -> None:\n        \n\n    def top(self) -> int:\n        \n\n    def getMin(self) -> int:\n        \n\n\n# Your MinStack object will be instantiated and called as such:\n# obj = MinStack()\n# obj.push(val)\n# obj.pop()\n# param_3 = obj.top()\n# param_4 = obj.getMin()',
        "test_cases": [{"input": "[\"MinStack\",\"push\",\"push\",\"push\",\"getMin\",\"pop\",\"top\",\"getMin\"]", "expected": "[[],[-2],[0],[-3],[],[],[],[]]"}]
    },
    # ========== LeetCode 150: Evaluate Reverse Polish Notation ==========
    "68": {
        "id": "68",
        "title": "Evaluate Reverse Polish Notation",
        "difficulty": "中等",
        "tags": ['Array', 'Math', 'Stack'],
        "description": 'You are given an array of strings `tokens` that represents an arithmetic expression in a Reverse Polish Notation.\n\nEvaluate the expression. Return an integer that represents the value of the expression.\n\n**Note** that:\n\n\t- The valid operators are `&#39;+&#39;`, `&#39;-&#39;`, `&#39;*&#39;`, and `&#39;/&#39;`.\n\n\t- Each operand may be an integer or another expression.\n\n\t- The division between two integers always **truncates toward zero**.\n\n\t- There will not be any division by zero.\n\n\t- The input represents a valid arithmetic expression in a reverse polish notation.\n\n\t- The answer and all the int',
        "template": 'class Solution:\n    def evalRPN(self, tokens: List[str]) -> int:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 739: Daily Temperatures ==========
    "69": {
        "id": "69",
        "title": "Daily Temperatures",
        "difficulty": "中等",
        "tags": ['Array', 'Stack', 'Monotonic Stack'],
        "description": 'Given an array of integers `temperatures` represents the daily temperatures, return an array `answer` such that `answer[i]` is the number of days you have to wait after the `ith` day to get a warmer temperature. If there is no future day for which this is possible, keep `answer[i] == 0` instead.\n\n&nbsp;\n\n**Example 1:**\n\n```\n**Input:** temperatures = [73,74,75,71,69,72,76,73]\n**Output:** [1,1,4,2,1,1,0,0]\n\n```\n\n**Example 2:**\n\n```\n**Input:** temperatures = [30,40,50,60]\n**Output:** [1,1,1,0]\n\n```\n\n**Example 3:**\n\n```\n**Input:** temperatures = [30,60,90]\n**Output:** [1,1,0]\n\n```\n\n&nbsp;\n\n**Const',
        "template": 'class Solution:\n    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:\n        ',
        "test_cases": []
    },
    # ========== LeetCode 883: Car Fleet ==========
    "70": {
        "id": "70",
        "title": "Car Fleet",
        "difficulty": "中等",
        "tags": ['Array', 'Stack', 'Sorting', 'Monotonic Stack'],
        "description": 'There are `n` cars at given miles away from the starting mile 0, traveling to reach the mile `target`.\n\nYou are given two integer arrays&nbsp;`position` and `speed`, both of length `n`, where `position[i]` is the starting mile of the `ith` car and `speed[i]` is the speed of the `ith` car in miles per hour.\n\nA car cannot pass another car, but it can catch up and then travel next to it at the speed of the slower car.\n\nA **car fleet** is a single car or a group of cars driving next to each other. The speed of the car fleet is the **minimum** speed of any car in the fleet.\n\nIf a car catches up to ',
        "template": 'class Solution:\n    def carFleet(self, target: int, position: List[int], speed: List[int]) -> int:\n        ',
        "test_cases": [{"input": "12", "expected": "[10,8,0,5,3]"}, {"input": "10", "expected": "[3]"}, {"input": "100", "expected": "[0,2,4]"}]
    }

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
