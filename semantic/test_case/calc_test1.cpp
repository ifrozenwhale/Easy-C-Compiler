// 测试表达式
int main(){
    int a = 1 + 2; // 3
    int b = 1 + 2 * 3; // 7
    int c = 2 * 3 + 1; // 7
    int d = (1+2) * (2+3); // 15
    int e = 1 + 2 * 3 - 4; // 3
    int f = a + b/(d/e) - c*3 - d*e; // 3+ 7/5 -21-45=-62

}