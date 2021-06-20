int test(int a, int b);  // 声明函数
int add(int a, int b) {
    c = 5;  // ERROR 未定义的变量错误
    return 0;
}
int main() {
    test(1, 2);
    int a = 1, b = 2;
    int c;
    add(a, b);
    sub(a, b);  // ERROR 未定义的函数
    return 0;
}


