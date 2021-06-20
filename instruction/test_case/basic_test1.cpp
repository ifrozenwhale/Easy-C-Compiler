//输入数据num1,num2,op，根据op确定操作进行运算，最后输出运算结果ans
int main(){
    int num1,num2,op, ans;
    num1 = 1; // 模拟 get赋值
    num2 = 2; // 模拟 get 赋值
    op = 5; // 模拟 get 赋值
    get3(num1,num2,op); // 使用getN区分参数数目，假定都为 int
    if(op==0)
    {
        ans = num1 + num2;
    };
    if(op==1)
    {
        ans = num1 - num2;
    };
    if(op==2)
    {
        ans = num1 & num2;
    };
    if(op==3)
    {
        ans = num1 | num2;
    };
    put(ans);
    return 0;
}
