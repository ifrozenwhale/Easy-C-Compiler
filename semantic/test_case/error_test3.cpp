int x, y;
int test() { return 0; }
int test() { return 1; }  // ERROR 非法的
int main() {
    int x;  // 合法的
    int a;
    int x;  // ERROR 非法的，已经在当前作用域定义
    x = 5;
    if (x == 5) {
        int a = 1;  // 合法的
        int a;      // ERROR 非法的
    } else {
        int a = 1;  // 合法的
        int a;      // ERROR 非法的
    }
    return 0;
}
