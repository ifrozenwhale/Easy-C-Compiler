int num0, nu.m1, out, op;  // 不合法的变量名
num1 = 333x;               // 不合法的10进制整数
num2 = 33391;              // 超出9999的10进制整数
num3 = 123.9;              // 非整数
num4 = 0666;               //
num5 = 0912;               // 8进制错误表达
num6 = 0x0012;             //
num7 = 0x10T4;             // 16进制不合法表达
op = 1;
while (op ~0) {     // 不合法的关系运算符
    if (op == 1) {  // 不合法的关系运算符
        out = num1;
    };
    if (op == 2) {
        out = num2;
    };
    if (op == 2) {
        out = num3;
    }; else {
        0aa = 51;  // 不合法的变量
    }
    put(out);
    get(op);
};