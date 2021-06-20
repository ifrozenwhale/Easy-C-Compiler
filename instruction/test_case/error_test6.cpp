// 测试函数不匹配
int add(int a, int b){
    int c = 1;
    return c;
}
bool valid(int a){
    bool res = true;
    return res;
}

int main(){

    int c, a = 1, b = 2, t = 0;
    add(a, b);
    add(a, b, t); // ERROR_1 数量不匹配
    bool x = false;
    c = add(a, x); // ERROR_2 参数类型不匹配
    bool y;
    y = add(a, b); // ERROR_3 返回值当做右值，赋值类型不匹配
    valid(a);
    valid(x); // ERROR_4 参数类型不匹配
}