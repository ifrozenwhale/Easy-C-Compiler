// 测试使用为初始化的错误
int x, y;
int test(){
    y = 2;
    y = x; // ERROR x没有初始化
    return x; // ERROR x没有初始化
}
int main(){
    int y;
    int x = 5;
    x = y; // ERROR 这里的y没有被初始化
    if (y == 5) { // ERROR y没有被初始化
        x = 1 + y; // ERROR y没有被初始化
    }
    return 0;
}