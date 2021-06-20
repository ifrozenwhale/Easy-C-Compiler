int x, y;
int main(){
    x = 1; // 正确，因为全局变量x
    int a = 5;
    bool c = false;
    if (a == 5){
        y = 2; // 正确，全局变量y
        d = 1; // 错误，未定义
        int a = 1; // 正确，在不同的作用域
    }
}


