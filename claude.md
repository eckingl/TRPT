## 核心工作流程 
**重要：每个任务必须遵循此流程，不可跳过任何阶段**
### 1. 研究阶段（RESEARCH）
在开始任何任务前，必须先执行：
- 检查现有代码库中的类似实现- 
- 使用 Glob/Grep 搜索相关代码-
-  理解项目架构和依赖关系- 
-  阅读相关文件的注释和文档 
-  **不确定时联网搜索：**
-  新技术/框架的最佳实践
-  特定库的最新 API 文档
- 错误消息的解决方案 
- ### 2. 计划阶段（PLAN） 
- 研究完成后，必须输出： 
- **文件清单**:-要修改/创建的文件列表
-**实现方案**：关键步骤和技术选型
- **风险识别**：潜在问题和边缘情况
- **待确认问题**：需要用户澄清的问题
 **重要：获得用户确认后再开始编码** 
### 3. 实现阶段（IMPLEMENT）
获得确认后，按照计划执行：
- 遵循项目现有代码风格- 完整的错误处理（绝不跳过）
- 编写时同步添加测试- 运行 linter/formatter/type-checker
 **完成标准：** 
 - Linter 零警告零错误- 所有测试通过- 类型检查通过- 代码已格式化 --- 
 **复杂架构问题：先深度思考再提出方案**

## 复杂任务处理
对于以下类型的任务，在计划阶段需要进行深度思考：
- 涉及多个模块的架构变更
- 新技术/框架的引入
- 性能优化方案
- 数据库 Schema 设计 
**深度思考要求：**
1. 列出至少 2-3 种可行方案
2. 分析每种方案的优缺点
3. 说明推荐方案的理由
4. 识别潜在的技术债务

### 场景化工作流程 ###
Bug 修复流程
1. **研究**：复现问题 → 定位根因 → 检查相关代码
2. **计划**：说明根因 → 修复方案 → 影响范围
3. **实现**：最小化改动 → 添加回归测试 → 验证修复 
### 新功能流程
1. **研究**：理解需求 → 搜索复用点 → 确认技术栈
2. **计划**：模块设计 → 接口定义 → 测试策略
3. **实现**：渐进开发 → 同步测试 → 更新文档 
### 重构流程
1. **研究**：分析现状 → 识别问题 → 评估影响
2. **计划**：重构方案 → 分步计划 → 回滚预案
3. **实现**：小步迭代 → 保持测试通过 → 及时提交

## 质量红线
 
**重要：以下规则是绝对底线，没有任何例外情况**
 
### 提交前强制检查（必须全部通过）
 
在提交任何代码之前，必须确保以下检查全部通过：
 
1. **Linter 检查**
   - 命令：`npm run lint`
   - 标准：零警告、零错误
   - 绝不使用 `eslint-disable` 绕过规则
 
2. **测试检查**
   - 命令：`npm test`
   - 标准：所有测试必须通过
   - 新增代码必须有对应测试
 
3. **格式化检查**
   - 命令：`npm run format:check`
   - 标准：所有文件已正确格式化
 
4. **类型检查**（TypeScript 项目）
   - 命令：`npm run type-check`
   - 标准：TypeScript 严格模式下无错误
 
### 绝对禁止清单（绝不允许）
 
以下行为在任何情况下都不允许：
 
**代码质量**
- 绝不提交未通过测试的代码
- 绝不使用 TODO/FIXME 作为最终代码
- 绝不跳过错误处理
- 绝不吞掉异常（空 catch 块）
- 绝不使用魔法数字
 
**类型安全**
- 绝不使用 any 类型（用 unknown 替代）
- 绝不使用 @ts-ignore
- 绝不禁用 ESLint 规则
 
**安全相关**
- 绝不硬编码密钥/凭证
- 绝不在日志中输出敏感信息
- 绝不跳过输入验证
 
### 违反红线的处理
 
如果发现代码违反以上任何一条红线：
1. 必须立即修复
2. 不能使用任何方式绕过
3. 不能以"临时方案"为由例外

# 变量：snake_case，名词性
user_name = 'john'
item_count = 10
is_active = True
 
# 函数：snake_case，动词开头
def get_user_by_id(user_id: str) -> User:
    pass
 
def calculate_total(items: list[Item]) -> float:
    pass
 
def validate_email(email: str) -> bool:
    pass
 
# 常量：SCREAMING_SNAKE_CASE
MAX_RETRY_COUNT = 3
API_BASE_URL = 'https://api.example.com'
# 类：PascalCase，名词
class UserService:
    pass
 
class OrderRepository:
    pass
 
# 协议/抽象类：PascalCase
from typing import Protocol
 
class UserRepositoryProtocol(Protocol):
    def get_by_id(self, user_id: str) -> User: ...
 
# 类型别名：PascalCase
UserRole = Literal['admin', 'user', 'guest']
✅ 好的命名          ❌ 差的命名
isActive            active
hasPermission       permission
canEdit             editable
shouldUpdate        update
isValid             valid
## 命名规范（Python）
 
### 文件命名
- 模块文件：snake_case.py（如 user_service.py）
- 测试文件：test_*.py 或 *_test.py
 
### 标识符命名
- 变量/函数：snake_case（如 get_user_by_id）
- 类：PascalCase（如 UserService）
- 常量：SCREAMING_SNAKE_CASE（如 MAX_RETRY）
- 私有成员：_leading_underscore（如 _internal_method）
- 布尔值：is/has/can/should 前缀（如 is_active）
 
### 命名原则
- 遵循 PEP 8 规范
- 变量名用名词，函数名用动词
- 避免单字符命名（循环变量除外）
- # ❌ 差：一个函数做多件事
def process_user(user: User) -> None:
    # 验证用户
    if not user.email:
        raise ValueError('Invalid email')
    # 保存到数据库
    db.save(user)
    # 发送欢迎邮件
    send_email(user.email, 'Welcome!')
    # 记录日志
    logger.info('User created')
 
# ✅ 好：每个函数只做一件事
def validate_user(user: User) -> None:
    if not user.email:
        raise ValueError('Invalid email')
 
def save_user(user: User) -> None:
    db.save(user)
 
def send_welcome_email(email: str) -> None:
    send_email(email, 'Welcome!')
 
def create_user(user: User) -> None:
    validate_user(user)
    save_user(user)
    send_welcome_email(user.email)
    logger.info('User created')
# ❌ 差：参数过多
def create_user(
    name: str,
    email: str,
    age: int,
    address: str,
    phone: str,
    role: str
) -> User:
    pass
 
# ✅ 好：使用 dataclass
@dataclass
class CreateUserParams:
    name: str
    email: str
    age: int
    address: str
    phone: str
    role: str
 
def create_user(params: CreateUserParams) -> User:
    pass
from typing import Optional
 
# ✅ 明确返回类型
def get_user_by_id(user_id: str) -> Optional[User]:
    user = db.find(user_id)
    return user if user else None
 
# ✅ 使用 Result 模式（或返回元组）
from dataclasses import dataclass
from typing import Generic, TypeVar, Union
 
T = TypeVar('T')
E = TypeVar('E')
 
@dataclass
class Ok(Generic[T]):
    value: T
 
@dataclass
class Err(Generic[E]):
    error: E
 
Result = Union[Ok[T], Err[E]]
 
def parse_json(s: str) -> Result[dict, str]:
    try:
        return Ok(json.loads(s))
    except json.JSONDecodeError as e:
        return Err(str(e))
        
## 函数规范
 
### 长度限制
- 单个函数不超过 30 行（推荐）
- 绝对上限 50 行，超过必须拆分
- 嵌套层级不超过 3 层
 
### 单一职责
- 一个函数只做一件事
- 函数名必须准确描述功能
- 如果函数名需要用 "and" 连接，说明应该拆分
 
### 参数限制
- 参数不超过 4 个
- 超过时使用对象/DTO 封装
- 布尔参数尽量避免（用枚举或分成两个函数）
 
### 返回值
- 必须声明返回类型
- 避免返回 null（使用 Optional/Result 模式）
- 一个函数只有一种返回类型

# ❌ 差：bare except
try:
    fetch_data()
except:  # 捕获所有异常，包括 KeyboardInterrupt
    print('Error')
 
# ❌ 差：过于宽泛
try:
    fetch_data()
except Exception as e:
    pass  # 吞掉异常
 
# ✅ 好：捕获具体异常
try:
    fetch_data()
except ConnectionError as e:
    logger.error(f'Connection failed: {e}')
    raise
except TimeoutError as e:
    logger.error(f'Request timed out: {e}')
    raise
 
# ✅ 更好：自定义异常类
class ApiError(Exception):
    def __init__(self, message: str, status_code: int, context: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.context = context or {}
 
def handle_error(error: Exception) -> None:
    if isinstance(error, ApiError):
        logger.error(f'API Error {error.status_code}: {error}', extra=error.context)
    else:
        logger.error(f'Error: {error}')

from typing import Optional
 
# ✅ 使用 Optional 类型注解
def get_user_name(user: Optional[User]) -> str:
    if user is None:
        return 'Anonymous'
    return user.name or 'Anonymous'
 
# ✅ 使用 or 提供默认值
display_name = user_name or 'Anonymous'
 
# ✅ getattr 带默认值
name = getattr(user, 'name', 'Anonymous')

## 错误处理规范（Python）
 
### 异常处理
- 绝不使用 bare except
- 捕获具体的异常类型
- 使用 raise from 保留异常链
 
### 自定义异常
- 继承合适的内置异常类
- 包含有意义的错误信息和上下文
- 遵循异常类命名规范（*Error 或 *Exception）
 
### 空值处理
- 使用 Optional 类型注解
- 使用 is None 而非 == None
- 使用 or 运算符提供默认值

# 1. 标准库
import os
import sys
from datetime import datetime
 
# 2. 第三方库
import requests
from pydantic import BaseModel
 
# 3. 本地模块
from app.services.user import UserService
from app.utils.logger import logger
 
from .validators import validate_user
from .types import User

def get_user_by_id(user_id: str) -> Optional[User]:
    """根据用户 ID 获取用户信息
 
    Args:
        user_id: 用户唯一标识符
 
    Returns:
        用户对象，如果不存在返回 None
 
    Raises:
        ApiError: 当数据库连接失败时
 
    Example:
        >>> user = get_user_by_id('123')
        >>> if user:
        ...     print(user.name)
    """
    # ...


    