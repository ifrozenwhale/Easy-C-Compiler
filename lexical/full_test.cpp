//较为完整的测试程序
int func(int t){ // 带参数函数定义
    return (2 + t); // 返回值使用表达式
}
int a, b, c; // 全局、多变量声明
void test(); // 函数声明
int main(){ // 主函数
    int num1 = 1, num2 = 2, op, ans; // 多变量声明，并赋初值

    ans = get(num1, num2, op); // 系统函数调用
    int a, b, c; // 其他位置的变量声明
    if (op == 0) { // if 判断语句
        ans = num1 + num2; // 表达式赋值
    };
    if (op == 1) {
        ans = num1; // 变量赋值
        if (op <= 2) { // if语句嵌套
            ans = num2 | num1; // 二元运算符
        };
    };

    if (op - 3 == 1) { // 表达式逻辑判断
        func(10); // 函数调用
    }else{
        ans = 15 + 2; // 常数表达式赋值
    }
    put(ans); // 系统函数调用
    return 0; // main函数返回值
}