# 语义分析

## 功能实现

- [x] 语义检查，包括

  - [x] 不同作用域变量可以重名，同一作用域变量不可重名
  - [x] 函数必须保证唯一
  - [x] 变量必须先定义再使用（可以在声明时赋初值）
  - [x] 变量使用前必须进行赋初值
  - [x] 不能进行隐性或者强制的类型转换，如将 int 类型的值赋值给 bool，包括函数返回值类型检查
  - [x] bool 类型不能参与 `+`、`-`、`*` 等计算
  - [x] bool 类型和 int 类型二者不能够进行计算
  - [x] 函数调用参数类型和数量必须同时匹配

- [x] 错误管理

  - 通过定义错误类，封装错误，统一进行管理。

  - 错误信息包括：错误发生的位置（行、列），错误发生的原因（分类），错误涉及的具体变量和详细信息。

    如重复定义变量，给出错误格式：

    `[ERROR] at position (17, 11), caused by: variable d is already defined in position (8, 137)`

- [x] 表达式计算

  - [x] 表达式值计算（处理括号、优先级）
  - [ ] 表达式 AST 生成
  - [ ] 处理结合顺序等问题

## 当前测试样例

```c++
bool x, y, z;
void test(int a, bool b);
int add(int a, int b){
    int d = a + b;
    return d;
}
int main(){
    int a, b = 2, c = 1, d = f; // 全局、多变量声明
    get(a, b);
    if (c > b){
        a = c * 2 + b * 10; // should be 2 + 20 = 22
    } else{
        c = a;
    }
    v = 1;
    // a = m;
    int d = 5; // re defined
    b = 2;
    c = 3;
    a = add(b, c); // 正常函数调用
    x = add(b, c); // 赋值类型不匹配（bool-int)
    a = add(b, b, c); // 参数数目不匹配
    a = add(x, y); // 参数类型不匹配
    while (a > x){ // 不同类型不能够比较
        a = a - 1;
        x = false;
        x = x + x; // bool 不能进行计算
    }
    a = c * (2 + b) * 10; // should be 120
    b = c * 2 + b * 10; // should be 6 + 20 = 26
    return 0;
}

```

给出错误信息：

![image-20210601020342843](https://frozenwhale.oss-cn-beijing.aliyuncs.com/img/image-20210601020342843.png)

