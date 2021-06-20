//输入数据num1,num2,op，根据op确定操作进行运算，最后输出运算结果ans
func(int t){  // 缺少函数类型声明
    return (2 + t) // 缺少分号
}
int a, int b; // 重复类型声明
c; // 缺少变量类型声明
void test(; // error
int main(){
    int num1 = 1, num2 = 2, op, ans;
    get(num1; num2, int op); // 不该出现的分号；不该出现的类型声明
    if (op == 0){
        ans = num1 + num2;
    }
    if (op == 1) {
        ans = num1;
    };
    if (op <= 2) {
        ans = num2 | num1;
    };
    if (op - 3 == 1) {
        func(10);
    }else{
        ans = 15 + 2;
    }
    put(ans);
    void wrongFunc(); // 不允许嵌套定义
}
