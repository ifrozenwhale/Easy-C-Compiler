bool x, y, z;
void test(int a, bool b);
// 定义全局的结构体
struct Course{
    int sid;
    int credit;
    bool necessary;
};
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
    struct Student{
        int sid; // 和 struct Course 重名
        int a; // 和 a 重名
        bool x; // 和 x 重名
        int gender; // 不重名
    };
    struct Student stu;
    struct Course cor;
    cor.sid = 1;
    stu.sid = cor.sid;

    return 0;
}
