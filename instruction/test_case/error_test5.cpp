// 测试类型匹配
int main(){
    int x = 1;
    bool a = false;
    int y = false; // ERROR
    bool b = 2; // ERROR
    y = 1;
    b = true;
    if (x == y){
        if (a == b){
            if (x == a){ // ERROR
                x = a; // ERROR
            }
        }
        while (y > b){ // ERROR
            y = y - 1;
            y = y - b; // ERROR
        }
    }
    return 0;
}


