struct Course{
    int id;
    bool valid;
    int credit;
};

int a, b, c;
struct Student{
    int id;
    bool gender;
};
int main(){
    struct Student stu; // 定义结构体类型变量
    stu.id = 1;
    stu.gender = false;
    struct Course cor;
    cor.id = false; // ERROR 类型不匹配
    cor.name = 0; // ERROR 结构体域中没有此变量
    cor.id = stu.id;
    return 0;
}

