# 文法版本记录
- `cfg_v4.` 能够识别函数体内的语句（将主体代码放进main)
- `cfg_v5` 能够是被多个函数声明、定义，如
    ```cpp
    int func(int t){
        return 2;
    }
    void test();
    int main(){
        //
    }  
  
  ```
 - `cfg_v6` 尝试允许函数外声明变量