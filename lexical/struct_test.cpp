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
    struct Student stu;
    stu.id = 1;
    stu.gender = false;
    return 0;
}