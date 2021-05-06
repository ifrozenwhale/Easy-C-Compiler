# 语法分析器

## TODO
- [x] 基础框架搭建

- [x] first集、follow集

- [x] 预测分析表

    - [x] 构建
    - [x] [csv保存](./results/table.csv)

- [x] 基本的C子集文法

    - [x] 全局变量定义、函数声明、定义

        ```cpp
        int func(int t){ // 函数定义
            return (2 + t);
        }
        int a, b, c; // 全局变量声明
        void test(); // 函数声明
        int main(){ // 主函数
            int num1 = 1, num2 = 2, op, ans; // 多变量声明、赋值
            get(num1, num2, op); // 识别函数调用
            if (op == 0) { // if 语句
                ans = num1 + num2; // 二元运算
            };
            if (op == 1) {
                ans = num1; // 赋值
            };
            if (op == 2) {
                ans = num2 | num1; // 逻辑运算
            };
            if (op - 3 == 1) { // 运算逻辑判断
                func(10);
            }else{
                ans = 15 + 2; // 常数赋值运算
            }
            put(ans);
        }    
        ```

    - [ ] 函数调用赋值

        ```cpp
        int func(int t){
            return (2 + t);
        }
        int main(){
        	int x = func(5);
        }
        ```

        

- [x] 自顶向下分析分析

    ![image-20210507025506075](https://frozenwhale.oss-cn-beijing.aliyuncs.com/img/image-20210507025506075.png)

- [ ] 错误处理

    - [x] 错误识别
    - [ ] 错误恢复

- [x] 语法分析树

    - [x] 数据结构实现
    - [x] 结构化打印（彩色）、[保存](./results/tree.txt)

    ![image-20210507025150612](https://frozenwhale.oss-cn-beijing.aliyuncs.com/img/image-20210507025150612.png)

    

